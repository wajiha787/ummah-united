# Gemini API Setup Guide

## Why Gemini API is needed
The search functionality uses Google's Gemini AI to provide:
- **Product descriptions** for all searched products
- **Dynamic analysis** for products not in the boycott database
- **Enhanced responses** with contextual information

## Current Issue
The system is currently using fallback responses because no Gemini API key is configured.

## How to Set Up Gemini API Key

### Step 1: Get Your API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### Step 2: Configure the API Key
Create a `.env` file in the backend directory:

```bash
cd backend
touch .env
```

Add your API key to the `.env` file:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### Step 3: Restart the Backend
```bash
# Stop the current server (Ctrl+C)
# Then restart it
python main.py
```

## Testing the Setup
After setting up the API key, search for products like:
- McDonald's
- Coca-Cola
- Nike

You should now see:
- ✅ Product descriptions from Gemini AI
- ✅ Enhanced responses
- ✅ Console logs showing "🤖 Using Gemini AI for product description..."

## Fallback Behavior
If no API key is set, the system will:
- Use basic fallback descriptions
- Still provide boycott information from JSON
- Still show Pakistani alternatives
- Work without AI features

## Troubleshooting
- Make sure the `.env` file is in the `backend/` directory
- Ensure the API key is valid and not expired
- Check console logs for error messages
- Restart the server after adding the API key 