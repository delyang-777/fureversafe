# FureverSafe - QUICK START (30 seconds)

## 🚀 Get Running NOW

### Step 1: Install (2 minutes)
```bash
pip install -r requirements.txt
```

### Step 2: Launch (1 click)
```bash
start_servers.bat
```

### Step 3: Use (Done!)
```
Open: http://127.0.0.1:8000
Use the chatbot!
```

---

## 📋 What Happens

1. **Batch file** activates virtual environment
2. **Terminal 1** starts AI server (port 5000)
3. **Terminal 2** starts Flask app (port 8000)
4. **Browser** opens to localhost
5. **Chatbot** works instantly!

---

## ✅ Verify It Works

```bash
# Check AI server
curl http://127.0.0.1:5000/health
# Response: {"status":"ok","model_loaded":true}
```

---

## 💡 Key Points

- **Two servers** run independently
- **Flask** → HTTP request → **AI server**
- **No blocking** = instant web response
- **Scalable** = can add more Flask instances
- **Production ready** = can deploy anywhere

---

## 🐛 If Something Breaks

| Problem | Fix |
|---------|-----|
| "Module not found" | `pip install -r requirements.txt` |
| "Can't connect" | Check both terminals are running |
| "Model not found" | Check `datasets/fureversafe_lora_model/` exists |
| Port 5000 in use | `set AI_SERVER_PORT=5001` |

---

## 📚 For More Info

- `DUAL_SERVER_SETUP.md` - Full setup guide
- `AI_INTEGRATION_QUICKREF.md` - Quick reference
- `INTEGRATION_CHECKLIST.md` - Detailed checklist

---

**Status: ✅ READY TO GO!**

Just run: `start_servers.bat`
