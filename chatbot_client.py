"""
FureverSafe Chatbot Client - Communicates with AI Server
Replaces the old chatbot_service.py that loaded models directly
"""

import requests
import logging
import os
from typing import Generator

logger = logging.getLogger(__name__)

# AI Server configuration
AI_SERVER_URL = os.environ.get("AI_SERVER_URL", "http://127.0.0.1:5000")
AI_SERVER_TIMEOUT = 30

# Cache for connection status
_ai_server_healthy = False


def check_ai_server_health() -> bool:
    """Check if AI server is available"""
    global _ai_server_healthy
    
    try:
        response = requests.get(
            f"{AI_SERVER_URL}/health",
            timeout=5
        )
        _ai_server_healthy = response.status_code == 200 and response.json().get("model_loaded")
        return _ai_server_healthy
    except Exception as e:
        logger.warning(f"AI server health check failed: {str(e)}")
        _ai_server_healthy = False
        return False


def process_chatbot_message(message: str, max_tokens: int = 100, temperature: float = 0.2) -> str:
    """
    Send a message to the AI server and get a response
    
    Args:
        message: User message
        max_tokens: Maximum tokens to generate
        temperature: Temperature for generation
        
    Returns:
        Response text from AI server
    """
    if not message or not message.strip():
        return "Please ask me something!"
    
    try:
        response = requests.post(
            f"{AI_SERVER_URL}/api/chat",
            json={
                "message": message.strip(),
                "max_tokens": max_tokens,
                "temperature": temperature
            },
            timeout=AI_SERVER_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json().get("response", "No response from AI server")
        else:
            error_detail = response.json().get("detail", "Unknown error")
            logger.error(f"AI server error ({response.status_code}): {error_detail}")
            return f"AI server error: {error_detail}"
            
    except requests.exceptions.Timeout:
        logger.error("AI server request timed out")
        return "The AI server is taking too long to respond. Please try again."
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to AI server at {AI_SERVER_URL}")
        return "I'm currently offline. Please try again later or contact support."
    except Exception as e:
        logger.error(f"Chatbot client error: {str(e)}")
        return f"An error occurred: {str(e)}"


def process_chatbot_message_stream(message: str, max_tokens: int = 100, temperature: float = 0.2) -> Generator[str, None, None]:
    """
    Send a message to the AI server and stream tokens
    
    Args:
        message: User message
        max_tokens: Maximum tokens to generate
        temperature: Temperature for generation
        
    Yields:
        Token strings as they are generated
    """
    if not message or not message.strip():
        yield "Please ask me something!"
        return
    
    try:
        response = requests.post(
            f"{AI_SERVER_URL}/api/chat-stream",
            json={
                "message": message.strip(),
                "max_tokens": max_tokens,
                "temperature": temperature
            },
            timeout=AI_SERVER_TIMEOUT,
            stream=True
        )
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data: "):
                        try:
                            import json
                            data = json.loads(line[6:])  # Remove "data: " prefix
                            
                            if "token" in data:
                                yield data["token"]
                            elif "error" in data:
                                logger.error(f"Stream error: {data['error']}")
                                yield f" [Error: {data['error']}]"
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON: {line}")
        else:
            logger.error(f"AI server stream error: {response.status_code}")
            yield f"[Error from AI server: HTTP {response.status_code}]"
            
    except requests.exceptions.Timeout:
        logger.error("AI server streaming request timed out")
        yield "[Error: AI server timeout]"
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to AI server for streaming at {AI_SERVER_URL}")
        yield "[Error: Cannot connect to AI server]"
    except Exception as e:
        logger.error(f"Streaming error: {str(e)}")
        yield f"[Error: {str(e)}]"


def init_ai_model(app):
    """
    Initialize AI model - now just checks if server is available
    This is called by Flask app for compatibility
    """
    logger.info("FureverSafe AI Chatbot Client initialized")
    logger.info(f"AI Server URL: {AI_SERVER_URL}")
    
    # Check server health on startup (non-blocking)
    if check_ai_server_health():
        logger.info("✓ AI server is healthy")
    else:
        logger.warning("⚠ AI server is not available or model not loaded")
        logger.warning("  Flask will continue but chatbot endpoints will fail")
        logger.warning("  Make sure to start the AI server: python ai_server.py")
