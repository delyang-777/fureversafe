"""
FurEverSafe Chatbot Service
Simple knowledge-based chatbot with responses for common questions
"""

import random
from difflib import SequenceMatcher

class ChatbotKnowledgeBase:
    """Knowledge base for chatbot responses"""
    
    def __init__(self):
        self.knowledge = {
            # Adoption-related
            'adopt|adoption|adopting|get a dog|find a dog|looking for': {
                'keywords': ['adopt', 'adoption', 'adopting', 'dog', 'get', 'find', 'looking'],
                'responses': [
                    'To adopt a dog on FurEverSafe, click "Adopt" in the menu to browse available dogs. Fill out an adoption application with your information and lifestyle. Our shelter partners will review your application and contact you soon!',
                    'Browse our adoption listings to find your perfect match! Consider factors like size, energy level, and breed characteristics when choosing a dog.',
                    'Ready to adopt? Check out our available dogs in the "Adopt" section. Each listing shows the dog\'s personality, health status, and special needs.',
                ]
            },
            
            # Dog profile creation
            'create|profile|dog profile|add dog|register': {
                'keywords': ['create', 'profile', 'add', 'register', 'dog'],
                'responses': [
                    'To create a dog profile: 1) Go to "My Dogs" 2) Click "Add New Dog" 3) Fill in name, breed, age, weight 4) Upload a photo 5) Click "Save"',
                    'Creating a dog profile is easy! Just navigate to your dashboard, enter your dog\'s details, and upload a photo. This helps us keep track of your furry friend!',
                ]
            },
            
            # Health and vaccination
            'health|sick|ill|vaccine|vaccination|vet|veterinarian': {
                'keywords': ['health', 'sick', 'vaccine', 'vaccination', 'vet', 'doctor'],
                'responses': [
                    'For health concerns, always consult with a veterinarian. You can track your dog\'s vaccinations and appointments in their health record section.',
                    'Keep your dog healthy! Update vaccination records, schedule regular vet checkups, and monitor for any health changes. If your dog is sick, please see a vet immediately.',
                    'Track all health records in your dog\'s profile: vaccinations, appointments, health records, and medications. This helps ensure your dog stays healthy!',
                ]
            },
            
            # Lost and found
            'lost|found|missing|report': {
                'keywords': ['lost', 'found', 'missing', 'report'],
                'responses': [
                    'If your dog is lost, go to "Lost & Found" and create a lost dog report. Include a photo, description, and location. Our community will help search!',
                    'Found a dog? Report it in our "Lost & Found" section. This helps reunite lost dogs with their owners.',
                    'Lost your dog? Don\'t panic! Post in our Lost & Found section and contact local shelters and vets. Many lost dogs are found within a few days.',
                ]
            },
            
            # Training and behavior
            'train|training|behavior|bark|bite|behave': {
                'keywords': ['train', 'training', 'behavior', 'bark', 'bite'],
                'responses': [
                    'Check our "Education" section for training tips and resources. Topics include housebreaking, basic commands, socialization, and addressing behavioral issues.',
                    'Training takes patience and consistency. Start with basic commands like "sit" and "stay". Use positive reinforcement with treats and praise!',
                    'For serious behavioral issues, consult a professional dog trainer. Our educational resources can help with common problems like barking or jumping.',
                ]
            },
            
            # Nutrition and diet
            'food|feed|diet|nutrition|eat': {
                'keywords': ['food', 'diet', 'nutrition', 'eat', 'feed'],
                'responses': [
                    'Proper nutrition is crucial for dog health. Choose quality dog food appropriate for your dog\'s age and size. Always provide fresh water and follow feeding guidelines.',
                    'Avoid toxic foods like chocolate, grapes, onions, and xylitol. Consult your vet about the best diet for your dog\'s specific needs.',
                    'Feed your dog appropriate portions based on their age, weight, and activity level. Check our educational resources for nutrition guides!',
                ]
            },
            
            # Emergency
            'emergency|urgent|help|emergency vet': {
                'keywords': ['emergency', 'urgent', 'help'],
                'responses': [
                    'If it\'s a medical emergency, call your vet or emergency animal clinic immediately! Don\'t wait. Signs of emergency: difficulty breathing, severe bleeding, unconsciousness.',
                    'In case of emergency, call your local emergency vet clinic right away. Don\'t delay professional help if your dog is in critical condition.',
                ]
            },
            
            # Educational resources
            'learn|education|resources|article|guide': {
                'keywords': ['learn', 'education', 'article', 'guide', 'resources'],
                'responses': [
                    'Visit our "Education" section for articles and resources about dog care, training, health, and welfare. Learn from our expert contributors!',
                    'We have comprehensive educational resources covering training, nutrition, health, and animal welfare. Check them out in the Education section!',
                ]
            },
            
            # Account and features
            'account|login|register|profile|settings': {
                'keywords': ['account', 'login', 'register', 'profile', 'settings'],
                'responses': [
                    'To create an account, click "Register" at the top right. Choose your account type (Dog Owner, Vet, or Shelter) and fill in your details.',
                    'You can update your profile settings in your dashboard. Manage your dogs, view applications, and track your activities there.',
                ]
            },
            
            # Appointments
            'appointment|schedule|book|vet appointment': {
                'keywords': ['appointment', 'schedule', 'book'],
                'responses': [
                    'To schedule an appointment: 1) Go to your dog\'s profile 2) Click "Appointments" 3) Click "Schedule Appointment" 4) Choose date/time 5) Confirm',
                    'Schedule vet appointments right through your dog\'s profile! You\'ll receive reminders before the appointment.',
                ]
            },
            
            # General greeting
            'hi|hello|hey|how are you|help|what can': {
                'keywords': ['hi', 'hello', 'hey', 'help', 'what'],
                'responses': [
                    'Hello! 👋 I\'m your FurEverSafe assistant. I can help you with adoption, health tracking, training tips, lost dog reports, and more. What would you like to know?',
                    'Hi there! 🐕 Feel free to ask me about dog adoption, health care, training, educational resources, or anything FurEverSafe related!',
                ]
            },
        }
    
    def get_response(self, user_input: str) -> str:
        """Generate a response based on user input"""
        user_input_lower = user_input.lower()
        
        # Find the best matching category
        best_match = None
        best_score = 0
        
        for category, data in self.knowledge.items():
            for keyword in data['keywords']:
                if keyword in user_input_lower:
                    score = len(keyword) / len(user_input_lower)
                    if score > best_score:
                        best_score = score
                        best_match = data
        
        # If we found a match, return a random response
        if best_match and best_score > 0.1:
            return random.choice(best_match['responses'])
        
        # Default response if no match found
        default_responses = [
            'I\'m not sure about that specific question. Try asking about adoption, health care, training, lost dogs, or visit our Education section for more resources.',
            'That\'s a great question! Please check our Education section or contact our support team for more detailed information.',
            'I can help with adoption, health tracking, training, and more. Can you ask your question differently or be more specific?',
        ]
        
        return random.choice(default_responses)


# Initialize knowledge base
chatbot_kb = ChatbotKnowledgeBase()


def process_chatbot_message(message: str) -> str:
    """Process a user message and return a response"""
    if not message or not message.strip():
        return "Please ask me something! 😊"
    
    # Clean up input
    message = message.strip()
    
    # Get response from knowledge base
    response = chatbot_kb.get_response(message)
    
    return response
