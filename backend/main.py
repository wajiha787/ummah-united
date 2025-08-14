from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Ummah United API", version="1.0.0")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:5174"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class FAQRequest(BaseModel):
    user_question: str

class QuranRequest(BaseModel):
    user_question: str

class FAQResponse(BaseModel):
    answer: str
    success: bool

class QuranResponse(BaseModel):
    answer: str
    success: bool

@app.get("/")
async def root():
    return {"message": "Ummah United API - FAQ & Quran System"}

@app.post("/api/faq", response_model=FAQResponse)
async def get_faq_answer(request: FAQRequest):
    try:
        if not os.getenv("GEMINI_API_KEY"):
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        # Create the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # System prompt for FAQ about Gaza relief and donations
        system_prompt = """You are a helpful AI assistant for Ummah United, a platform supporting Gaza emergency relief efforts. 

Your role is to answer questions about:
- Gaza humanitarian crisis and relief efforts
- How to donate and support Palestinian families
- Information about verified donation campaigns
- Alkhidmat Foundation Pakistan and their work
- General questions about humanitarian aid
- Islamic principles of charity and helping those in need

GUIDELINES:
- Be informative, compassionate, and accurate
- Provide practical advice about donations and relief efforts
- If asked about specific donation amounts, suggest reasonable amounts but emphasize any amount helps
- For technical questions about the platform, provide helpful guidance
- Keep responses clear and concise (under 200 words)
- Be respectful of Islamic values and humanitarian principles
- If you don't know something specific, suggest contacting the organization directly
- IMPORTANT: Do NOT use asterisk (*) signs anywhere in your response
- Use bullet points with dashes (-) or other symbols instead of asterisks
- Write in plain text without any special formatting characters

RESPONSE FORMAT:
Provide a helpful, informative answer that directly addresses the user's question about Gaza relief, donations, or humanitarian aid. Use clear, simple formatting without asterisks."""

        # Combine system prompt and user question
        full_prompt = f"{system_prompt}\n\nUser Question: {request.user_question}\n\nProvide a helpful answer without using any asterisk (*) signs:"
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        # Get the answer and remove any asterisks that might still appear
        answer = response.text.strip()
        
        # Remove all asterisk characters from the response
        answer = answer.replace('*', '')
        
        return FAQResponse(answer=answer, success=True)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing FAQ: {str(e)}")

@app.post("/api/quran", response_model=QuranResponse)
async def get_quran_answer(request: QuranRequest):
    try:
        if not os.getenv("GEMINI_API_KEY"):
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        # Create the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # System prompt for Quran and Hadith queries about Palestine
        system_prompt = """You are an Islamic knowledge assistant specializing in Quranic verses, Hadith, and Islamic history related to Palestine and the Holy Land.

Your role is to answer questions about:
- Quranic verses mentioning Palestine, Jerusalem, or the Holy Land
- Hadith (Prophet Muhammad's sayings) about Palestine and Jerusalem
- Stories of prophets related to Palestine (Ibrahim, Musa, Isa, etc.)
- Islamic history of Palestine and Jerusalem
- The significance of al-Masjid al-Aqsa in Islam
- Stories of the Children of Israel in the Quran
- Islamic perspective on the Holy Land
- Historical events in Palestine mentioned in Islamic texts

GUIDELINES:
- Provide accurate information from authentic Islamic sources
- Include relevant Quranic verses with proper references (Surah:Ayah format)
- Mention Hadith with proper attribution when applicable
- Explain the historical and spiritual significance
- Be respectful and scholarly in your approach
- Keep responses informative but concise (under 300 words)
- Use proper Islamic terminology
- IMPORTANT: Do NOT use asterisk (*) signs anywhere in your response
- Use bullet points with dashes (-) or other symbols instead of asterisks
- Write in plain text without any special formatting characters

RESPONSE FORMAT:
Provide a comprehensive answer that includes relevant Quranic verses, Hadith, and historical context about Palestine and the Holy Land. Use clear, simple formatting without asterisks."""

        # Combine system prompt and user question
        full_prompt = f"{system_prompt}\n\nUser Question: {request.user_question}\n\nProvide a comprehensive Islamic answer without using any asterisk (*) signs:"
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        # Get the answer and remove any asterisks that might still appear
        answer = response.text.strip()
        
        # Remove all asterisk characters from the response
        answer = answer.replace('*', '')
        
        return QuranResponse(answer=answer, success=True)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Quran query: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Ummah United FAQ & Quran System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 