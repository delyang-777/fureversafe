# FurEverSafe Chatbot Integration Guide

## Overview

The AI chatbot has been integrated into your FurEverSafe website as a floating widget in the bottom-right corner. It provides instant assistance to users about dog adoption, health, training, and platform features.

## Features

✅ **24/7 Availability** - Always available to help users  
✅ **Smart Responses** - Context-aware answers based on user input  
✅ **Beautiful UI** - Purple-themed, matches FurEverSafe branding  
✅ **Responsive Design** - Works on desktop, tablet, and mobile  
✅ **Smooth Animations** - Professional look and feel  
✅ **Message History** - Users can scroll through conversation  
✅ **Typing Indicator** - Shows when bot is "thinking"  

---

## Files Created

| File | Purpose |
|------|---------|
| `templates/chatbot_widget.html` | Chatbot HTML & JavaScript |
| `static/css/chatbot.css` | Chatbot styling & animations |
| `chatbot_service.py` | Knowledge base & response logic |
| `app.py` (updated) | Added `/api/chatbot` endpoint |
| `templates/base.html` (updated) | Includes chatbot widget & CSS |

---

## How It Works

### 1. User Interaction Flow
```
User clicks chatbot icon
    ↓
Chatbot widget opens
    ↓
User types message
    ↓
Message sent to /api/chatbot endpoint
    ↓
Server processes with chatbot_service.py
    ↓
Response sent back to frontend
    ↓
Message displayed in chat
```

### 2. Chatbot Intelligence

The chatbot uses a **knowledge base matching system**:
- Analyzes user input for keywords
- Matches keywords to predefined categories
- Returns appropriate response
- Falls back to general response if no match

### 3. Categories Supported

The chatbot can help with:
- ✅ Dog adoption
- ✅ Creating dog profiles
- ✅ Health & vaccinations
- ✅ Lost & found dogs
- ✅ Training & behavior
- ✅ Nutrition & diet
- ✅ Emergency situations
- ✅ Educational resources
- ✅ Scheduling appointments
- ✅ Account management

---

## Usage

### For Users
1. Look for the **purple chat icon** in the bottom-right corner
2. Click it to open the chatbot
3. Type your question
4. Press Enter or click the send button
5. Read the response
6. Continue the conversation or close to minimize

### For Developers

#### Testing the Chatbot

**Via API:**
```bash
curl -X POST http://localhost:5000/api/chatbot \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I adopt a dog?"}'
```

**Response:**
```json
{
  "response": "To adopt a dog on FurEverSafe, click \"Adopt\" in the menu to browse available dogs...",
  "success": true
}
```

#### Adding New Responses

Edit `chatbot_service.py` to add new categories:

```python
'your_keywords|or|patterns': {
    'keywords': ['keyword1', 'keyword2'],
    'responses': [
        'First possible response',
        'Second possible response',
    ]
},
```

#### Customizing Appearance

Edit `static/css/chatbot.css`:
- Change colors in `.chatbot-toggle` and `.chatbot-widget`
- Adjust width/height of widget
- Modify animations
- Update font sizes

---

## Customization

### Change Primary Color
In `static/css/chatbot.css`:
```css
background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
```

### Change Widget Position
In `static/css/chatbot.css`:
```css
.chatbot-container {
    bottom: 20px;  /* Change vertical position */
    right: 20px;   /* Change horizontal position */
}
```

### Change Widget Size
In `static/css/chatbot.css`:
```css
.chatbot-widget {
    width: 400px;   /* Change width */
    height: 600px;  /* Change height */
}
```

### Hide Chatbot on Specific Pages
Add to your template:
```html
<style>
    .chatbot-container { display: none; }
</style>
```

---

## Response Examples

### Example 1: Adoption Question
**User:** "I want to adopt a dog"  
**Bot:** "To adopt a dog on FurEverSafe, click "Adopt" in the menu to browse available dogs. Fill out an adoption application with your information and lifestyle. Our shelter partners will review your application and contact you soon!"

### Example 2: Health Question
**User:** "My dog is sick"  
**Bot:** "For health concerns, always consult with a veterinarian. You can track your dog's vaccinations and appointments in their health record section."

### Example 3: Feature Question
**User:** "How do I create a dog profile?"  
**Bot:** "To create a dog profile: 1) Go to "My Dogs" 2) Click "Add New Dog" 3) Fill in name, breed, age, weight 4) Upload a photo 5) Click "Save""

---

## Integration with Fine-Tuned Model (Optional)

Currently, the chatbot uses a **knowledge base system**. To upgrade to a fine-tuned AI model:

### Step 1: Train the Model
```bash
cd datasets
llamafactory-cli train llamafactory_config.yaml
```

### Step 2: Update chatbot_service.py
```python
from transformers import pipeline

class AdvancedChatbot:
    def __init__(self):
        self.pipe = pipeline(
            "text-generation",
            model="./fureversafe-mistral-tuned"
        )
    
    def get_response(self, message):
        response = self.pipe(message, max_length=256)
        return response[0]['generated_text']

chatbot = AdvancedChatbot()
```

### Step 3: Update app.py
```python
@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    message = data.get('message', '')
    response = chatbot.get_response(message)
    return jsonify({'response': response, 'success': True})
```

---

## Performance & Analytics

### Monitor Chatbot Usage
Add to your dashboard:
```python
@app.route('/admin/chatbot-stats')
def chatbot_stats():
    # Track popular questions
    # Monitor response times
    # Analyze user satisfaction
    pass
```

### Optimize Response Time
- Keep knowledge base organized
- Remove duplicate keywords
- Cache frequent responses
- Consider load balancing

---

## Mobile Optimization

The chatbot is fully responsive:
- **Desktop**: 400px × 600px widget (bottom-right)
- **Tablet**: Maintains size, scales content
- **Mobile**: Full-screen on small devices

### On Mobile Devices
- Widget becomes full-screen
- Easier to type on small screens
- Touch-friendly buttons
- Optimized message display

---

## Troubleshooting

### Issue: Chatbot not responding
**Solution:** 
```bash
# Check if endpoint is working
curl -X POST http://localhost:5000/api/chatbot \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

### Issue: Styling looks off
**Solution:**
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+Shift+R)
- Check if chatbot.css is loaded

### Issue: Slow responses
**Solution:**
- Reduce knowledge base size
- Cache responses
- Consider async requests

### Issue: Widget won't open
**Solution:**
- Check browser console for errors
- Verify chatbot_widget.html is included
- Check CSS file is loaded

---

## API Reference

### POST /api/chatbot

**Request:**
```json
{
  "message": "How do I adopt a dog?"
}
```

**Response (Success):**
```json
{
  "response": "To adopt a dog on FurEverSafe...",
  "success": true
}
```

**Response (Error):**
```json
{
  "response": "Sorry, I encountered an error.",
  "success": false
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request (no message)
- `500`: Server error

---

## Future Enhancements

### Planned Features
- [ ] Chat history saved to database
- [ ] User satisfaction rating
- [ ] Admin dashboard for questions
- [ ] Multi-language support
- [ ] Integration with NLP models
- [ ] Real-time collaborative chat
- [ ] Video tutorials integration
- [ ] Sentiment analysis

### Roadmap
1. **Phase 1**: Basic knowledge base (✅ Done)
2. **Phase 2**: Fine-tuned LLM model (Ready)
3. **Phase 3**: Analytics dashboard (To-do)
4. **Phase 4**: Advanced ML features (To-do)

---

## Support & Maintenance

### Regular Maintenance
- Update knowledge base monthly
- Add new FAQs as they arise
- Monitor for error patterns
- Review user feedback

### Adding New Knowledge
When new features are added to FurEverSafe:
1. Create FAQ responses
2. Add to chatbot_service.py
3. Test thoroughly
4. Deploy with version number

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-28 | Initial release with knowledge base |
| 1.1 | TBD | Fine-tuned LLM integration |
| 2.0 | TBD | Analytics & admin dashboard |

---

## File Locations

```
FurEverSafe/
├── templates/
│   ├── base.html (updated)
│   └── chatbot_widget.html (new)
├── static/
│   └── css/
│       └── chatbot.css (new)
├── chatbot_service.py (new)
└── app.py (updated)
```

---

**Chatbot is now live! 🎉 Users can start asking questions immediately.**

For questions or issues, refer to the troubleshooting section or check the console logs.
