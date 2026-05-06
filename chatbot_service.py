"""
FureverSafe Chatbot Service
Intent-based response matching aligned with the retrained Kaggle notebook.

Supports 26 intents (0-25):
  0-22  → original intents (from unique_outputs[0..22])
  23    → greeting  (EXTRA_INTENTS[23])
  24    → thanks    (EXTRA_INTENTS[24])
  25    → goodbye   (EXTRA_INTENTS[25])

Dataset file: datasets/fureversafe_clean.jsonl  (produced by fureversafe_retrain_kaggle.ipynb)
Fallback:     datasets/fureversafe_chatbot_training.jsonl  (legacy)
"""

import os
import json
import logging
import re

logger = logging.getLogger(__name__)

_config = None
_responses = None        # list indexed by intent 0-25
_intent_patterns = None  # compiled patterns per intent

# ---------------------------------------------------------------------------
# Intent rules — aligned with notebook INTENT_INPUTS / EXTRA_INTENTS
# Each tuple: (response_index, [regex_patterns...])
# Ordered most-specific first to avoid false matches.
# ---------------------------------------------------------------------------
_INTENT_RULES = [
    # ── Emergency / medical ─────────────────────────────────────────────────
    (17, [r"\bchocolate\b", r"\bate\s+chocolate", r"\bcocoa\b", r"\btheobromine\b",
          r"\bbrownie\b", r"\bchocolate\s+(bar|cake|chip)"]),

    (9,  [r"\bpoison\b", r"\btoxic\b", r"\bingested?\b", r"\bate\s+something\s+(bad|toxic|poison)",
          r"\bbleach\b", r"\bchemical\b", r"\bgrapes?\b", r"\braisins?\b",
          r"\bxylitol\b", r"\bonion\b", r"\bgarlic\b", r"\bantifree",
          r"\brat\s+poison\b", r"\binsecticide\b", r"\bfertilizer\b",
          r"\bate\s+(bleach|medication|medicine|pill|antifreeze|fertilizer|paint|glue)"]),

    (4,  [r"\bdog\s+(is\s+)?sick\b", r"\bsick\s+(dog|puppy|pup)\b", r"\bnot\s+feeling\s+well\b",
          r"\bvomit", r"\bdiarrhea\b", r"\blethar", r"\bnot\s+eating\b",
          r"\bwon'?t\s+eat\b", r"\bdog.+ill\b", r"\bdog\s+(has\s+a\s+)?fever\b",
          r"\bdog\s+(is\s+)?coughing\b", r"\bdog\s+(is\s+)?shaking\b",
          r"\bdog\s+(is\s+)?wheezing\b", r"\bblood\s+in\s+stool\b"]),

    # ── Lost / found ─────────────────────────────────────────────────────────
    (5,  [r"\blost\s+(my\s+)?(dog|puppy|pup|pet)\b", r"\b(dog|puppy|pup)\s+(is\s+)?lost\b",
          r"\bcan'?t\s+find\s+(my\s+)?(dog|puppy|pup)\b", r"\bmissing\s+(dog|puppy)\b",
          r"\b(dog|puppy|pup)\s+ran\s+away\b", r"\b(dog|puppy|pup)\s+escaped\b",
          r"\b(dog|puppy|pup)\s+got\s+(out|loose)\b", r"\b(dog|puppy|pup)\s+disappeared\b",
          r"\b(dog|puppy|pup)\s+bolted\b"]),

    (6,  [r"\bfound\s+a?\s*(stray|lost|wander|abandon|homeless)\s*(dog|puppy|pup)\b",
          r"\bstray\s+(dog|puppy|pup)\b", r"\bdog\s+appears?\s+lost\b",
          r"\bwandering\s+(dog|puppy|pup)\b", r"\bfound\s+stray\b",
          r"\bfound\s+a\s+(dog|puppy|pup)\b", r"\b(dog|puppy|pup)\s+showed?\s+up\b"]),

    # ── Health ───────────────────────────────────────────────────────────────
    (8,  [r"\bhealth\s+(problem|concern|issue|question)\b", r"\bsomething\s+wrong\s+with\s+my\s+dog\b",
          r"\bworried\s+about.+health\b", r"\b(dog|puppy|pup)\s+health\b",
          r"\bpreventive\s+(care|health)\b", r"\bkeep\s+my\s+(dog|puppy)\s+healthy\b"]),

    # ── Behaviour ────────────────────────────────────────────────────────────
    (13, [r"\bacting\s+(weird|strange|different|off|out\s+of\s+character)\b",
          r"\bbehavior\s+change\b", r"\bbehav(e|iour|ior).+different\b",
          r"\b(dog|puppy|pup)\s+(is\s+)?(anxious|hiding|clingy|withdrawn|depressed|restless|pacing)\b",
          r"\b(dog|puppy|pup)\s+(is\s+)?not\s+(himself|herself|the\s+same)\b"]),

    (19, [r"\baggress", r"\bbiting\s+(people|me|others|kids|someone)\b",
          r"\battack", r"\bsnap", r"\bgrowl", r"\bsnarl",
          r"\blunge", r"\bfood\s+aggress", r"\bresource\s+guard", r"\bterritorial\b",
          r"\b(dog|puppy)\s+bit\s+(someone|me|another)\b"]),

    (12, [r"\bpuppy\s+(keeps?|won'?t\s+stop|always|started)\s+bit",
          r"\bpuppy\s+nipp", r"\bpuppy\s+mouth",
          r"\bpuppy\s+teeth\b", r"\bpuppy\s+bite", r"\bpuppy\s+biting\b",
          r"\bteething\s+puppy\b"]),

    # ── Vet / medical care ───────────────────────────────────────────────────
    (10, [r"\bvet\s+appointment\b", r"\bschedule.+vet\b", r"\bbook.+vet\b",
          r"\bvet\s+visit\b", r"\bvet\s+(check\s*up|booking|consultation)\b",
          r"\bappointment\b", r"\btake\s+my\s+(dog|puppy)\s+to\s+the\s+vet\b"]),

    (11, [r"\bvaccin", r"\bshot\b", r"\bimmuniz", r"\brabies\b", r"\bparvo\b",
          r"\bdistemper\b", r"\bbordete", r"\bleptospir", r"\bbooster\s+(shot|vaccine)\b",
          r"\boverdue\s+on\s+(shot|vaccine)\b"]),

    # ── Training ─────────────────────────────────────────────────────────────
    (18, [r"\btraining\s+(not|isn'?t)\s+working\b", r"\bstill\s+won'?t\b",
          r"\btraining\s+(help|fail|regress|plateau)\b",
          r"\bdog\s+forgot\s+(his|her)?\s*training\b",
          r"\b(nothing|nothing\s+I\s+do)\s+works\s+(for|with)\s+training\b",
          r"\btraining\s+fell\s+apart\b", r"\bprofessional\s+trainer\b",
          r"\bhire\s+a\s+(dog\s+)?trainer\b", r"\bdog\s+(is\s+)?untrainable\b"]),

    (15, [r"\bwon'?t\s+listen\b", r"\bdoesn'?t\s+listen\b", r"\bnot\s+listen",
          r"\bignor(e|ing)\s+me\b", r"\bdisobedien", r"\bstubborn\s+(dog|puppy)\b",
          r"\bselective\s+hearing\b", r"\bdog\s+refuses\s+(to\s+)?commands?\b"]),

    (14, [r"\btrain.+command\b", r"\bteach.+(sit|stay|come|down|heel|shake|roll)\b",
          r"\bbasic\s+(obedience|training)\b", r"\bhow\s+to\s+train\b",
          r"\bclicker\s+training\b", r"\bcrate\s+training\b",
          r"\bpotty\s+training\b", r"\bleash\s+training\b",
          r"\bpositive\s+reinforcement\b"]),

    # ── Feeding / nutrition ──────────────────────────────────────────────────
    (16, [r"\bfood\b", r"\bfeed\b", r"\bnutrition\b", r"\bdiet\b", r"\bkibble\b",
          r"\bwet\s+food\b", r"\bdry\s+food\b", r"\braw\s+(food|diet)\b",
          r"\bcan\s+dogs?\s+eat\b", r"\bportion\s+size\b", r"\bfeeding\s+schedule\b",
          r"\bdog\s+food\s+(allerg|sensitive|stomach)\b"]),

    # ── Adoption ─────────────────────────────────────────────────────────────
    (1,  [r"\badoption\s+process\b", r"\bhow\s+(do\s+i\s+|to\s+)?adopt\b",
          r"\badoption\s+(application|form|fee|step|requirement|procedure)\b",
          r"\bapply\s+to\s+adopt\b", r"\badopt\s+from\b",
          r"\bwhat.+adoption.+like\b", r"\bhow\s+long.+adoption\b",
          r"\bnavigat.+(adoption|platform|site)\b", r"\bplatform\s+feature\b"]),

    (0,  [r"\badopt\b", r"\bwant\s+a?\s*(dog|puppy|pup)\b",
          r"\blooking\s+for\s+a?\s*(dog|puppy|pup)\b",
          r"\bnew\s+(dog|puppy|pup)\b", r"\bget\s+a?\s*(dog|puppy|pup)\b",
          r"\bfind\s+a?\s*(dog|puppy|pup)\b", r"\brescue\s+a?\s*(dog|puppy|pup)\b",
          r"\bwant\s+to\s+rescue\b", r"\bgive\s+a\s+(dog|puppy)\s+a\s+(home|forever home)\b"]),

    # ── First-time owner ─────────────────────────────────────────────────────
    (2,  [r"\bfirst\s*(-|\s)?time\s+(dog\s+)?(owner|adopter|parent|getting)\b",
          r"\bnever\s+(had|owned|had\s+a)\s+(dog|pet|puppy)\b",
          r"\bnew\s+(dog|pet)\s+owner\b", r"\bbeginner\s+(dog|pet)\b",
          r"\bno\s+(dog|pet|prior)?\s*experience\b",
          r"\bfirst\s+(dog|pet|puppy)\s+ever\b"]),

    # ── Breed recommendations ────────────────────────────────────────────────
    (3,  [r"\bwhat\s+(kind|type|breed)\b", r"\bbreed\b", r"\brecommend\s+a?\s*(dog|breed)\b",
          r"\bwhich\s+(dog|breed)\b", r"\bbest\s+(dog|breed|puppy)\s+for\b",
          r"\b(dog|breed)\s+for\s+(me|apartment|family|seniors|kids|active|allergies)\b",
          r"\bbreed\s+(selector|quiz|comparison)\b"]),

    # ── Dog profile ──────────────────────────────────────────────────────────
    (7,  [r"\bdog\s+profile\b", r"\bcreate.+profile\b", r"\badd.+(dog|pet)\b",
          r"\bregister.+(dog|pet)\b", r"\bset\s*up.+profile\b",
          r"\bmy\s+dogs?\s+page\b", r"\bupload.+(dog|photo|photo\s+of)\b",
          r"\blist\s+my\s+dog\b"]),

    # ── Volunteering ─────────────────────────────────────────────────────────
    (20, [r"\bvolunteer\b", r"\bhelp\s+(at\s+)?(a\s+)?shelter\b",
          r"\bshelter\s+work\b", r"\bdonate\s+time\b",
          r"\bfoster\s+(a\s+)?(dog|puppy|pet)\b", r"\bwalk\s+shelter\s+dogs?\b"]),

    # ── Senior dogs ──────────────────────────────────────────────────────────
    (22, [r"\bsenior\s+(dog|puppy|pet)\b", r"\bold\s+(dog|puppy|pet)\b",
          r"\belderly\s+(dog|puppy|pet)\b", r"\baging\s+(dog|puppy|pet)\b",
          r"\b(dog|puppy)\s+(is\s+)?old\b", r"\barthritis\s+in\s+(dog|senior)\b",
          r"\bdementia\s+(in\s+)?(dog|senior)\b", r"\bend\s+of\s+life.+dog\b"]),

    # ── Dog happiness / enrichment ────────────────────────────────────────────
    (21, [r"\bhappy\s+(dog|puppy)\b", r"\bmake.+(dog|puppy).+happy\b",
          r"\b(dog|puppy)\s+activ", r"\benrich", r"\bexercise\b",
          r"\bplay\b", r"\bfun\b", r"\bbored\s+(dog|puppy)\b",
          r"\btire\s+out\s+my\s+(dog|puppy)\b", r"\bpuzzle\s+toy\b",
          r"\bmental\s+stimulation\b"]),
]

# ---------------------------------------------------------------------------
# Hard-coded responses for the 3 new intents (23/24/25)
# These are the exact strings from EXTRA_INTENTS in the notebook.
# ---------------------------------------------------------------------------
_EXTRA_RESPONSES = {
    23: (
        "Hi there! Welcome to FurEverSafe! I'm your AI assistant and I can help you with:\n\n"
        "- Dog adoption and the adoption process\n"
        "- Pet health concerns and emergencies\n"
        "- Lost and found dogs\n"
        "- Training and behavior advice\n"
        "- Nutrition and feeding\n"
        "- Vet appointments and vaccinations\n"
        "- Volunteering at shelters\n"
        "- Setting up your dog's profile\n\n"
        "What can I help you with today?"
    ),
    24: (
        "You're welcome! Happy to help. If you have any more questions about "
        "dog adoption, health, training, or anything else, feel free to ask anytime!"
    ),
    25: (
        "Goodbye! Take care of yourself and your furry friends. "
        "Feel free to come back anytime you need help!"
    ),
}

_FALLBACK_REPLY = (
    "I'm not sure I understand that question. I can help with:\n\n"
    "- Dog adoption and the adoption process\n"
    "- Pet health concerns and emergencies\n"
    "- Lost and found dogs\n"
    "- Training and behavior\n"
    "- Nutrition and feeding\n"
    "- Vet appointments and vaccinations\n"
    "- Volunteering at shelters\n\n"
    "Could you rephrase your question?"
)

# ---------------------------------------------------------------------------
# Meta patterns — matched before intent rules
# ---------------------------------------------------------------------------
_GREETING_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        r"^(hi|hello|hey|howdy|greetings|yo)(\s|!|$)",
        r"^good\s+(morning|afternoon|evening)",
        r"^what'?s\s+up",
        r"^(who|what)\s+are\s+you",
        r"^what\s+can\s+you\s+(do|help)",
        r"^(help|menu|options|start)$",
        r"^tell\s+me\s+about\s+yourself",
        r"^what\s+is\s+fureversafe",
        r"^(hi\s+bot|hey\s+bot|hello\s+bot)$",
    ]
]

_THANKS_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        r"^(thanks?|thank\s+you|ty|thx)",
        r"\bappreciate\s+it\b",
        r"\bthat\s+(helps?|was\s+helpful)\b",
        r"\bmuch\s+appreciated\b",
        r"^(great|perfect|awesome)\s+thanks",
    ]
]

_GOODBYE_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        r"^(bye|goodbye|see\s+ya|later|good\s+night)",
        r"^(i'?m\s+done|that'?s\s+all|no\s+more|nothing\s+else|all\s+good)",
        r"^(gotta\s+go|i'?m\s+leaving|done\s+for\s+now)",
        r"^take\s+care",
    ]
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_responses(jsonl_path: str) -> list[str]:
    """Load ordered unique responses from the JSONL dataset.

    For the clean dataset the responses are in slots 0-22 (23 intents from
    unique_outputs) plus 3 hard-coded extra responses at indices 23-25.
    """
    logger.info("Loading responses from: %s", os.path.basename(jsonl_path))
    seen: dict[str, int] = {}
    responses: list[str] = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            output = entry.get("output", "")
            if output and output not in seen:
                seen[output] = len(responses)
                responses.append(output)

    # Append the 3 extra responses at fixed indices 23, 24, 25
    for idx in sorted(_EXTRA_RESPONSES):
        resp = _EXTRA_RESPONSES[idx]
        if resp not in seen:
            responses.append(resp)

    logger.info("Loaded %d unique responses (including extras)", len(responses))
    return responses


def _compile_intent_patterns() -> list:
    """Pre-compile regex patterns for fast matching."""
    compiled = []
    for resp_idx, patterns in _INTENT_RULES:
        compiled_patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
        compiled.append((resp_idx, compiled_patterns))
    return compiled


def _match_meta(user_message: str) -> str | None:
    """Check greeting / thanks / goodbye before intent matching."""
    text = user_message.strip()
    for p in _GREETING_PATTERNS:
        if p.search(text):
            return _EXTRA_RESPONSES[23]
    for p in _THANKS_PATTERNS:
        if p.search(text):
            return _EXTRA_RESPONSES[24]
    for p in _GOODBYE_PATTERNS:
        if p.search(text):
            return _EXTRA_RESPONSES[25]
    return None


def _match_intent(user_message: str) -> int | None:
    """Match user message to the best response index using keyword patterns."""
    text = user_message.lower().strip()
    for resp_idx, patterns in _intent_patterns:
        for pattern in patterns:
            if pattern.search(text):
                return resp_idx
    return None


def _get_response(resp_idx: int) -> str:
    """Safely retrieve response text by index."""
    if _responses is None:
        return "The AI model is not loaded. Please contact the administrator."
    # Extra intents 23-25 are always available directly
    if resp_idx in _EXTRA_RESPONSES:
        return _EXTRA_RESPONSES[resp_idx]
    if resp_idx < len(_responses):
        return _responses[resp_idx]
    return _FALLBACK_REPLY


# ---------------------------------------------------------------------------
# Public API (called by app.py)
# ---------------------------------------------------------------------------

def init_ai_model(app):
    """Initialise the chatbot with intent-based response matching.

    Tries the clean retrained dataset first; falls back to the legacy file.
    """
    global _config, _responses, _intent_patterns
    _config = app.config

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Prefer the clean dataset produced by the retrain notebook
    candidates = [
        os.path.join(base_dir, "datasets", "fureversafe_clean.jsonl"),
        os.path.join(base_dir, "datasets", "fureversafe_chatbot_training.jsonl"),
    ]

    jsonl_path = None
    for path in candidates:
        if os.path.isfile(path):
            jsonl_path = path
            break

    if jsonl_path:
        _responses = _load_responses(jsonl_path)
        _intent_patterns = _compile_intent_patterns()
        logger.info(
            "AI backend: intent matching (%d responses) from %s",
            len(_responses), os.path.basename(jsonl_path),
        )
    else:
        logger.error(
            "No training dataset found. Checked: %s",
            ", ".join(os.path.basename(p) for p in candidates),
        )


def process_chatbot_message(message: str) -> str:
    """Generate a response for the given user message."""
    if not message or not message.strip():
        return "Please ask me something!"
    if _responses is None:
        return "The AI model is not loaded. Please contact the administrator."

    meta = _match_meta(message.strip())
    if meta:
        return meta

    resp_idx = _match_intent(message.strip())
    return _get_response(resp_idx) if resp_idx is not None else _FALLBACK_REPLY


def process_chatbot_message_stream(message: str):
    """Yield response in word chunks to simulate streaming."""
    if not message or not message.strip():
        yield "Please ask me something!"
        return
    if _responses is None:
        yield "The AI model is not loaded. Please contact the administrator."
        return

    meta = _match_meta(message.strip())
    if meta:
        text = meta
    else:
        resp_idx = _match_intent(message.strip())
        text = _get_response(resp_idx) if resp_idx is not None else _FALLBACK_REPLY

    words = text.split(" ")
    for i, word in enumerate(words):
        yield word if i == 0 else " " + word