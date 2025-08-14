# Ummah United Backend API

This is the backend API for the Ummah United platform, providing FAQ functionality powered by Google's Gemini AI.

## Features

- **FAQ System**: AI-powered question answering about Gaza relief, donations, and humanitarian aid
- **Gemini AI Integration**: Uses Google's Gemini 1.5 Flash model for intelligent responses
- **RESTful API**: Clean API endpoints for frontend integration

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Environment Variables

Create a `.env` file in the backend directory:

```bash
# Backend directory
cd backend

# Create .env file
touch .env
```

Add your Gemini API key to the `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key
5. Paste it in your `.env` file

### 4. Run the Backend

```bash
# From the backend directory
python main.py
```

The server will start on `http://localhost:8000`

### 5. Test the API

You can test the FAQ endpoint:

```bash
curl -X POST "http://localhost:8000/api/faq" \
  -H "Content-Type: application/json" \
  -d '{"user_question": "How can I donate to help Gaza?"}'
```

## API Endpoints

### POST /api/faq

Submit a question and get an AI-powered answer.

**Request Body:**
```json
{
  "user_question": "Your question here"
}
```

**Response:**
```json
{
  "answer": "AI-generated answer",
  "success": true
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Ummah United FAQ System"
}
```

## System Prompt

The FAQ system is configured with a specialized prompt that helps the AI understand:

- Gaza humanitarian crisis and relief efforts
- How to donate and support Palestinian families
- Information about verified donation campaigns
- Alkhidmat Foundation Pakistan and their work
- General questions about humanitarian aid
- Islamic principles of charity and helping those in need

## Frontend Integration

The frontend is configured to proxy API requests to the backend. Make sure:

1. Backend is running on `http://localhost:8000`
2. Frontend is running on `http://localhost:5173`
3. The proxy configuration in `vite.config.js` is active

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your Gemini API key is correctly set in the `.env` file
2. **CORS Error**: The backend includes CORS middleware for common frontend ports
3. **Connection Error**: Ensure both frontend and backend are running

### Logs

Check the console output for any error messages when starting the backend.

## Development

To modify the system prompt or add new endpoints, edit the `main.py` file. The current system is designed to be easily extensible for additional AI-powered features. 