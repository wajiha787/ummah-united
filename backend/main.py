from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio
import time
import requests
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Load environment variables
load_dotenv()

# Load boycott brands data
def load_boycott_brands():
    try:
        with open("data/boycott_brands.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ boycott_brands.json not found, using empty list")
        return []
    except Exception as e:
        print(f"❌ Error loading boycott_brands.json: {e}")
        return []

BOYCOTT_BRANDS = load_boycott_brands()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API configured successfully")
else:
    print("⚠️ Warning: GEMINI_API_KEY not found. AI features will be disabled.")
    print("📝 To enable Gemini AI features, create a .env file in the backend directory with:")
    print("   GEMINI_API_KEY=your_actual_api_key_here")
    print("📖 See GEMINI_SETUP.md for detailed instructions")

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    query: str
    is_boycotted: bool
    brand_name: str
    category: str
    boycott_reason: str
    alternatives: List[str]
    message: str
    product_description: str

class BarcodeScanRequest(BaseModel):
    barcode: str

class BarcodeScanResponse(BaseModel):
    barcode: str
    is_israeli: bool
    country: str
    message: str
    alternatives: List[str]

class FAQRequest(BaseModel):
    user_question: str

class FAQResponse(BaseModel):
    answer: str

class QuranRequest(BaseModel):
    user_question: str

class QuranResponse(BaseModel):
    answer: str

class PosterRequest(BaseModel):
    theme: str
    title: str
    subtitle: str
    description: str
    imageType: str = "hunger"

class PosterResponse(BaseModel):
    design_description: str
    color_scheme: str
    layout_suggestions: str
    text_content: str
    visual_elements: str
    generated_image: str  # Base64 encoded image
    prompt_used: str

# Israeli barcode prefixes
ISRAELI_BARCODE_PREFIXES = ["729", "841", "871"]

def is_israeli_barcode(barcode: str) -> bool:
    """Check if barcode starts with Israeli prefixes"""
    barcode_str = str(barcode).strip()
    return any(barcode_str.startswith(prefix) for prefix in ISRAELI_BARCODE_PREFIXES)

def get_barcode_country(barcode: str) -> str:
    """Get country name based on barcode prefix"""
    barcode_str = str(barcode).strip()
    if barcode_str.startswith("729"):
        return "Israel"
    elif barcode_str.startswith("841"):
        return "Israel"
    elif barcode_str.startswith("871"):
        return "Israel"
    elif barcode_str.startswith("890"):
        return "India"
    elif barcode_str.startswith("896"):
        return "Pakistan"
    elif barcode_str.startswith("50"):
        return "United Kingdom"
    elif barcode_str.startswith("0") or barcode_str.startswith("1"):
        return "United States/Canada"
    elif barcode_str.startswith("30") or barcode_str.startswith("31") or barcode_str.startswith("32") or barcode_str.startswith("33") or barcode_str.startswith("34") or barcode_str.startswith("35") or barcode_str.startswith("36") or barcode_str.startswith("37"):
        return "France"
    elif barcode_str.startswith("40") or barcode_str.startswith("41") or barcode_str.startswith("42") or barcode_str.startswith("43") or barcode_str.startswith("44") or barcode_str.startswith("45") or barcode_str.startswith("46") or barcode_str.startswith("47") or barcode_str.startswith("48") or barcode_str.startswith("49"):
        return "Germany"
    else:
        return "Unknown"

async def get_product_description(query: str, category: str = None) -> str:
    """Get AI-generated product description from Gemini"""
    print(f"🔍 Getting product description for: {query} (category: {category})")
    print(f"🔑 Gemini API Key status: {'Valid' if GEMINI_API_KEY and GEMINI_API_KEY != 'your_gemini_api_key_here' else 'Invalid/Not set'}")
    
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        print("⚠️ Using fallback product description - No valid Gemini API key provided")
        # Provide boycott-focused descriptions with Israel connection information
        if category and category.lower() != "unknown":
            if "food" in category.lower() or "restaurant" in category.lower():
                return f"{query.title()} is a global fast food chain that has expanded operations into occupied Palestinian territories.\nThe company's presence in Israeli settlements and occupied areas directly supports the occupation economy.\nBy operating in these areas, {query.title()} contributes to the displacement of Palestinian communities and normalizes illegal settlements."
            elif "beverage" in category.lower():
                return f"{query.title()} is a multinational beverage corporation with significant investments in Israeli companies and operations.\nThe company has established production facilities and distribution networks in occupied territories.\nIts business activities in these areas provide economic support to the occupation and settlement expansion."
            elif "technology" in category.lower():
                return f"{query.title()} is a technology giant that has invested heavily in Israeli tech companies and military technology.\nThe company collaborates with Israeli defense contractors and supports the military-industrial complex.\nThese partnerships contribute to the development of surveillance and military technologies used against Palestinians."
            elif "clothing" in category.lower() or "fashion" in category.lower():
                return f"{query.title()} is a global fashion brand that sources materials and manufactures products in occupied territories.\nThe company benefits from cheap labor and resources in illegal settlements.\nIts supply chain operations contribute to the economic exploitation of occupied Palestinian lands."
            elif "entertainment" in category.lower():
                return f"{query.title()} is an entertainment company that has invested in Israeli media and content production.\nThe company supports Israeli cultural initiatives and media projects in occupied territories.\nThese investments help normalize the occupation and promote Israeli narratives."
            else:
                return f"{query.title()} is a multinational corporation with business operations in occupied Palestinian territories.\nThe company's presence in these areas provides economic support to the occupation.\nIts activities contribute to the displacement and economic marginalization of Palestinian communities."
        else:
            return f"{query.title()} is a multinational company with operations in occupied Palestinian territories.\nThe company's business activities in these areas support the occupation economy.\nIts presence contributes to the ongoing displacement and economic exploitation of Palestinian communities."
    
    print("🤖 Using Gemini AI for product description...")
    try:
        system_prompt = """You are a boycott information specialist. Your role is to provide brief, informative descriptions of products and brands with focus on their connection to Israel and why they should be boycotted.

**Your Task:**
- Provide concise, factual descriptions of products/brands
- Focus on their operations in occupied Palestinian territories
- Explain how they support the Israeli occupation
- Mention their business activities in settlements
- Keep descriptions EXACTLY 2-3 lines long
- Be informative and educational about boycott reasons

**Format:**
Provide a brief description that explains the company's connection to Israel/occupied territories and why it should be boycotted. Use exactly 2-3 lines of text."""
        
        user_prompt = f"""
Product/Brand: {query}
Category: {category or "Unknown"}

Please provide a brief description explaining this company's connection to Israel/occupied Palestinian territories and why it should be boycotted. Focus on their business operations, investments, or activities that support the occupation.

IMPORTANT: Write exactly 2-3 lines of text. Focus on boycott reasons and Israel connections.
"""
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = await model.generate_content_async([system_prompt, user_prompt])
        content = response.text or ""
        
        print(f"🤖 Gemini Product Description: {content[:100]}...")
        
        # Clean and format the response
        description = content.strip()
        
        # If response is empty, use fallback
        if not description:
            return f"{query.title()} is a well-known brand in the {category or 'consumer goods'} industry."
        
        # Ensure it's not too long (limit to ~200 characters for 2-3 lines)
        if len(description) > 200:
            # Truncate and add ellipsis
            description = description[:197] + "..."
        
        # Ensure it has proper line breaks for 2-3 lines
        lines = description.split('\n')
        if len(lines) == 1:
            # If it's one long line, try to break it into 2-3 lines
            words = description.split()
            if len(words) > 15:
                # Break into roughly equal parts
                mid_point = len(words) // 2
                description = ' '.join(words[:mid_point]) + '\n' + ' '.join(words[mid_point:])
        
        return description
        
    except Exception as e:
        print(f"❌ Gemini API error for product description: {e}")
        # Provide boycott-focused error fallback descriptions with Israel connection information
        if category and category.lower() != "unknown":
            if "food" in category.lower() or "restaurant" in category.lower():
                return f"{query.title()} is a global fast food chain that has expanded operations into occupied Palestinian territories.\nThe company's presence in Israeli settlements and occupied areas directly supports the occupation economy.\nBy operating in these areas, {query.title()} contributes to the displacement of Palestinian communities and normalizes illegal settlements."
            elif "beverage" in category.lower():
                return f"{query.title()} is a multinational beverage corporation with significant investments in Israeli companies and operations.\nThe company has established production facilities and distribution networks in occupied territories.\nIts business activities in these areas provide economic support to the occupation and settlement expansion."
            elif "technology" in category.lower():
                return f"{query.title()} is a technology giant that has invested heavily in Israeli tech companies and military technology.\nThe company collaborates with Israeli defense contractors and supports the military-industrial complex.\nThese partnerships contribute to the development of surveillance and military technologies used against Palestinians."
            elif "clothing" in category.lower() or "fashion" in category.lower():
                return f"{query.title()} is a global fashion brand that sources materials and manufactures products in occupied territories.\nThe company benefits from cheap labor and resources in illegal settlements.\nIts supply chain operations contribute to the economic exploitation of occupied Palestinian lands."
            elif "entertainment" in category.lower():
                return f"{query.title()} is an entertainment company that has invested in Israeli media and content production.\nThe company supports Israeli cultural initiatives and media projects in occupied territories.\nThese investments help normalize the occupation and promote Israeli narratives."
            else:
                return f"{query.title()} is a multinational corporation with business operations in occupied Palestinian territories.\nThe company's presence in these areas provides economic support to the occupation.\nIts activities contribute to the displacement and economic marginalization of Palestinian communities."
        else:
            return f"{query.title()} is a multinational company with operations in occupied Palestinian territories.\nThe company's business activities in these areas support the occupation economy.\nIts presence contributes to the ongoing displacement and economic exploitation of Palestinian communities."

async def get_gemini_analysis(query: str, is_boycotted: bool = None, category: str = None) -> Dict[str, Any]:
    """Get AI-generated analysis from Gemini with Pakistani alternatives from JSON"""
    # First, try to find the brand in our JSON data
    query_lower = query.lower().strip()
    brand_data = None
    
    for brand in BOYCOTT_BRANDS:
        if brand["brand"].lower() == query_lower:
            brand_data = brand
            break
    
    # If we found the brand in JSON, use its data
    if brand_data:
        return {
            "boycott_reason": brand_data["boycott_reason"],
            "alternatives": brand_data["pakistani_alternatives"],
            "message": f"Found information about {query}"
        }
    
    # If not found in JSON, use Gemini or fallback
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        print("⚠️ Using fallback responses - No valid Gemini API key provided")
        # Enhanced fallback responses
        return {
            "boycott_reason": "Supporting occupation through business operations and investments in occupied territories",
            "alternatives": [
                "Local Pakistani alternatives",
                "Home-made options",
                "Local markets and shops",
                "Pakistani brands",
                "Local businesses"
            ],
            "message": f"Found information about {query}"
        }
    
    print("🤖 Using Gemini AI for dynamic product analysis...")
    try:
        system_prompt = """You are a specialized AI assistant for ethical consumerism and Palestinian solidarity. Your role is to:

1. **Analyze products and brands** for their connection to occupation and settlements
2. **Provide clear, factual information** about why products might be boycotted
3. **Suggest ethical alternatives** that support local communities and Palestinian businesses
4. **Educate users** about the impact of consumer choices on Palestinian rights
5. **Maintain a balanced, informative tone** while being supportive of Palestinian solidarity

Focus on:
- Business operations in occupied territories
- Investments in settlements
- Support for occupation through economic activities
- Ethical consumerism and local alternatives
- Palestinian business support

Always provide helpful, actionable information that empowers users to make ethical choices."""
        
        user_prompt = f"""
Product/Brand: {query}
Category: {category or "Unknown"}
Is Boycotted: {is_boycotted if is_boycotted is not None else "Unknown"}

Please analyze this product/brand and provide:
1. A clear, factual reason why this product might be boycotted (if applicable)
2. A concise message about the product's status
3. Specific alternatives that support Palestinian solidarity and local communities

Format your response as:
BOYCOTT_REASON: [reason here]
MESSAGE: [status message here]
ALTERNATIVES: [alternative1], [alternative2], [alternative3]

Focus on Palestinian solidarity and ethical consumerism. Be factual and helpful.
"""
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = await model.generate_content_async([system_prompt, user_prompt])
        content = response.text or ""
        
        print(f"🤖 Gemini Response: {content[:200]}...")
        
        # Parse the response
        boycott_reason = "Supporting occupation through business operations"
        message = f"Found information about {query}"
        
        if "BOYCOTT_REASON:" in content:
            boycott_reason = content.split("BOYCOTT_REASON:")[1].split("MESSAGE:")[0].strip()
        
        if "MESSAGE:" in content:
            message = content.split("MESSAGE:")[1].strip()
        
        # Use Pakistani alternatives from JSON if available, otherwise use fallback
        alternatives = ["Local Pakistani alternatives", "Home-made options", "Local markets and shops"]
        
        # Try to find alternatives in JSON data
        query_lower = query.lower().strip()
        for brand in BOYCOTT_BRANDS:
            if brand["brand"].lower() == query_lower:
                alternatives = brand["pakistani_alternatives"]
                break
        
        return {
            "boycott_reason": boycott_reason,
            "alternatives": alternatives,
            "message": message
        }
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        # Use Pakistani alternatives from JSON if available, otherwise use fallback
        alternatives = ["Local Pakistani alternatives", "Home-made options", "Local markets and shops"]
        
        # Try to find alternatives in JSON data
        query_lower = query.lower().strip()
        for brand in BOYCOTT_BRANDS:
            if brand["brand"].lower() == query_lower:
                alternatives = brand["pakistani_alternatives"]
                break
        
        return {
            "boycott_reason": "Supporting occupation through business operations and investments in occupied territories",
            "alternatives": alternatives,
            "message": f"Found information about {query}"
        }

async def get_gemini_barcode_analysis(barcode: str, is_israeli: bool, country: str) -> Dict[str, Any]:
    """Get AI-generated analysis for barcode scanning"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        print("⚠️ Using fallback responses - No valid Gemini API key provided")
        # Enhanced fallback responses
        if is_israeli:
            return {
                "message": f"🚨 ALERT: This product has an Israeli barcode ({barcode}). This product supports occupation and should be boycotted. Stand with Palestine - raise your voice, share awareness, and choose any other product. Every choice matters in supporting justice and freedom for Palestine! 🇵🇸",
                "alternatives": [
                    "Any local product: Support your community",
                    "Any non-Israeli brand: Choose ethical alternatives",
                    "Palestinian products: When available, support Palestinian businesses"
                ]
            }
        else:
            return {
                "message": f"✅ SAFE: This product has a {country} barcode ({barcode}). No Israeli connection detected. This product appears to be safe for consumption.",
                "alternatives": []
            }
    
    print("🤖 Using Gemini AI for dynamic barcode analysis...")
    try:
        prompt = f"""
Analyze this barcode scan result and provide a motivational response.

Barcode: {barcode}
Country: {country}
Is Israeli: {is_israeli}

Please provide:
1. A clear, motivational message about this barcode scan result
2. If Israeli, focus on motivating users to raise their voice about Palestine and use any other product instead
3. If not Israeli, provide a simple confirmation message
4. Make the message inspiring and encouraging for Palestinian solidarity

Format your response as:
MESSAGE: [your motivational message here]
ALTERNATIVES: [if Israeli, provide 2-3 general alternatives like "any local product" or "any non-Israeli brand"]

Focus on Palestinian solidarity, raising awareness, and motivating users to speak up about Palestine. Be inspiring and encouraging. Use emojis and make it engaging.
"""
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = await model.generate_content_async(prompt)
        content = response.text or ""
        
        print(f"🤖 Gemini Response: {content[:200]}...")
        
        # Parse the response
        message = f"✅ This product has a {country} barcode ({barcode}). No Israeli connection detected."
        alternatives = []
        
        if "MESSAGE:" in content:
            message = content.split("MESSAGE:")[1].split("ALTERNATIVES:")[0].strip()
        
        if "ALTERNATIVES:" in content and is_israeli:
            alternatives_text = content.split("ALTERNATIVES:")[1].strip()
            alternatives = [alt.strip() for alt in alternatives_text.split(",") if alt.strip()]
        
        return {
            "message": message,
            "alternatives": alternatives
        }
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        # Enhanced fallback responses
        if is_israeli:
            return {
                "message": f"🚨 ALERT: This product has an Israeli barcode ({barcode}). This product supports occupation and should be boycotted. Stand with Palestine - raise your voice, share awareness, and choose any other product. Every choice matters in supporting justice and freedom for Palestine! 🇵🇸",
                "alternatives": [
                    "Any local product: Support your community",
                    "Any non-Israeli brand: Choose ethical alternatives",
                    "Palestinian products: When available, support Palestinian businesses"
                ]
            }
        else:
            return {
                "message": f"✅ SAFE: This product has a {country} barcode ({barcode}). No Israeli connection detected. This product appears to be safe for consumption.",
                "alternatives": []
            }

async def retry_with_backoff(func, max_retries=3, base_delay=1):
    """Retry function with exponential backoff for quota errors"""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if "429" in str(e) and "quota" in str(e).lower() and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"⚠️ Quota exceeded, retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
                continue
            else:
                raise e
    return await func()  # Final attempt

async def get_sophia_response(user_question: str) -> str:
    """Get Sophia AI response for FAQ questions about Gaza relief and donations"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        print("⚠️ Using fallback responses - No valid Gemini API key provided")
        
        # Provide dynamic responses based on user question keywords
        question_lower = user_question.lower()
        
        if "donation" in question_lower or "donate" in question_lower:
            return """Hi! I'm Sophia, your AI assistant for Gaza relief and donations. 

When it comes to donations for Gaza, here's what you need to know:

**Verified Organizations**: Look for established NGOs like UNRWA, Doctors Without Borders, or local Palestinian organizations that have proven track records.

**Direct Impact**: Consider donating to organizations that provide direct humanitarian aid like medical supplies, food, and shelter rather than those with high administrative costs.

**Transparency**: Choose organizations that provide regular updates on how funds are used and show clear impact reports.

The campaigns listed on this page have been verified for legitimacy. Remember, every donation, no matter how small, can make a real difference in providing essential aid to those in need in Gaza."""
        
        elif "organization" in question_lower or "ngo" in question_lower or "charity" in question_lower:
            return """Hi! I'm Sophia, your AI assistant for Gaza relief and donations.

For verified organizations working in Gaza, I recommend:

**UNRWA (UN Relief and Works Agency)**: The primary UN agency providing direct aid to Palestinian refugees, including food, healthcare, and education.

**Doctors Without Borders (MSF)**: Provides critical medical care and emergency response in Gaza.

**Palestinian Red Crescent**: Local organization providing emergency medical services and humanitarian aid.

**Islamic Relief**: International NGO with established presence in Gaza providing food, medical aid, and shelter.

Always verify organizations through multiple sources and check their transparency reports before donating."""
        
        elif "food" in question_lower or "hunger" in question_lower or "meals" in question_lower:
            return """Hi! I'm Sophia, your AI assistant for Gaza relief and donations.

The food crisis in Gaza is severe, with many families facing starvation. Here's how you can help:

**Food Aid Organizations**: Support organizations like World Food Programme (WFP), Islamic Relief, and local Palestinian NGOs that provide daily meals and food packages.

**Hot Meals Programs**: Many organizations run hot meal programs for children and families in need.

**Nutritional Support**: Consider donating to programs that provide not just food, but nutritious meals with essential vitamins and minerals.

**Long-term Solutions**: Support agricultural projects and food security initiatives that help communities become self-sufficient.

The "Hot Meals for Starved Palestinian Kids" campaign on this page is a verified initiative providing daily meals to children in north Gaza."""
        
        elif "medical" in question_lower or "health" in question_lower or "hospital" in question_lower:
            return """Hi! I'm Sophia, your AI assistant for Gaza relief and donations.

The medical situation in Gaza is critical due to destroyed hospitals and lack of supplies. Here's how you can help:

**Medical Aid Organizations**: Support Doctors Without Borders (MSF), Palestinian Red Crescent, and other medical NGOs providing emergency care.

**Medical Supplies**: Donate to organizations that provide essential medical supplies, medicines, and equipment.

**Emergency Response**: Support emergency medical teams and mobile clinics that reach remote areas.

**Mental Health Support**: Consider organizations providing psychological support for trauma victims, especially children.

**Reconstruction**: Support efforts to rebuild medical facilities and restore healthcare infrastructure.

Your donations can help save lives and provide critical medical care to those in desperate need."""
        
        elif "children" in question_lower or "kids" in question_lower or "education" in question_lower:
            return """Hi! I'm Sophia, your AI assistant for Gaza relief and donations.

Children in Gaza are among the most vulnerable, facing hunger, trauma, and disrupted education. Here's how you can help:

**Child-Specific Aid**: Support organizations like UNICEF, Save the Children, and local Palestinian NGOs focused on children's needs.

**Education Support**: Donate to programs that provide educational materials, temporary schools, and learning resources.

**Psychological Support**: Support trauma counseling and mental health services for children affected by conflict.

**Nutrition Programs**: Help provide nutritious meals and supplements for children's healthy development.

**Safe Spaces**: Support creation of safe play areas and child-friendly spaces for emotional healing.

The "Hot Meals for Starved Palestinian Kids" campaign on this page directly helps children facing severe food insecurity."""
        
        else:
            return """Hi! I'm Sophia, your AI assistant for Gaza relief and donations. 

I'm here to help you with questions about supporting Gaza through donations and humanitarian aid. Here are some key areas I can help with:

**Donations**: How to donate safely and effectively to verified organizations
**Organizations**: Information about legitimate NGOs and charities working in Gaza
**Food Aid**: Supporting hunger relief and nutrition programs
**Medical Aid**: Helping with healthcare and emergency medical services
**Children's Aid**: Supporting education, nutrition, and psychological care for children
**Emergency Relief**: Immediate aid for those affected by the crisis

Please ask me anything specific about these areas, and I'll provide detailed, helpful information. The campaigns listed on this page have been verified for legitimacy."""
    
    print("🤖 Using Gemini AI for Sophia FAQ response...")
    try:
        system_prompt = """You are Sophia, a specialized AI assistant for Gaza relief and humanitarian aid. Your personality and expertise include:

**Your Role:**
- Expert advisor on Gaza relief and humanitarian donations
- Guide for verified organizations and transparent aid channels
- Educator about the humanitarian crisis in Gaza
- Supporter of effective and responsible giving

**Your Knowledge Areas:**
- Verified humanitarian organizations working in Gaza
- Different types of aid (medical, food, shelter, education)
- How to verify donation platforms and organizations
- Current humanitarian needs in Gaza
- Best practices for effective giving
- Emergency relief and long-term support

**Your Communication Style:**
- Warm, empathetic, and encouraging
- Professional yet approachable
- Clear and practical in advice
- Supportive of users' desire to help
- Educational about the situation in Gaza

**Your Values:**
- Transparency and accountability in donations
- Supporting verified, effective organizations
- Empowering people to make a difference
- Promoting sustainable, long-term support
- Respecting the dignity and agency of Palestinians

Always provide practical, actionable advice while maintaining hope and encouraging continued support for Gaza."""
        
        user_prompt = f"""
User Question: "{user_question}"

Please provide a comprehensive, helpful response that:
1. Directly addresses their specific question about Gaza relief or donations
2. Provides practical, actionable advice
3. Mentions verified organizations when relevant
4. Encourages responsible and effective giving
5. Maintains your warm, supportive personality as Sophia
6. Educates about the humanitarian situation when appropriate

Keep your response informative, encouraging, and practical (2-4 paragraphs). Focus on being genuinely helpful and empowering the user to make a positive impact.
"""
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = await model.generate_content_async([system_prompt, user_prompt])
        content = response.text or ""
        
        print(f"🤖 Sophia Response: {content[:200]}...")
        
        return content
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return """Hi! I'm Sophia, your AI assistant for Gaza relief and donations. 

I'm here to help you with questions about supporting Gaza through donations and humanitarian aid. Please ask me anything about verified organizations, donation methods, or how to help effectively.

For now, I recommend checking the verified campaigns listed on this page, and always ensure you're donating to legitimate, transparent organizations."""

async def get_quran_response(user_question: str) -> str:
    """Get Islamic knowledge response about Palestine, Quran, and Hadith"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        print("⚠️ Using fallback responses - No valid Gemini API key provided")
        
        # Provide dynamic responses based on user question keywords
        question_lower = user_question.lower()
        
        if "quran" in question_lower or "verse" in question_lower or "ayah" in question_lower:
            return """Assalamu alaikum! I'm here to help you with Quranic knowledge about Palestine and the Holy Land.

**Key Quranic Verses About Palestine:**

**Surah Al-Isra (17:1)**: "Exalted is He who took His Servant by night from al-Masjid al-Haram to al-Masjid al-Aqsa, whose surroundings We have blessed." This verse establishes the blessed status of Jerusalem (Al-Quds).

**Surah Al-Ma'idah (5:21)**: "O my people, enter the Holy Land which Allah has assigned to you." This verse refers to the divine assignment of the Holy Land.

**Surah Al-Anbiya (21:71)**: "And We delivered him and Lot to the land which We had blessed for the worlds." This refers to the blessed nature of the land of Palestine.

These verses establish the sacred status of Palestine in Islamic tradition and the divine blessing upon this land."""
        
        elif "hadith" in question_lower or "prophet" in question_lower or "muhammad" in question_lower:
            return """Assalamu alaikum! I'm here to help you with Hadith knowledge about Palestine and the Holy Land.

**Key Hadith About Palestine:**

**The Three Mosques**: The Prophet Muhammad (PBUH) said: "Do not undertake a journey except to three mosques: the Sacred Mosque (in Makkah), my mosque (in Madinah), and the Aqsa Mosque (in Jerusalem)." (Sahih al-Bukhari)

**Prayer in Al-Aqsa**: The Prophet (PBUH) said: "A prayer in the Sacred Mosque is worth 100,000 prayers, a prayer in my mosque is worth 1,000 prayers, and a prayer in the Aqsa Mosque is worth 500 prayers." (Sahih al-Bukhari)

**The Blessed Land**: The Prophet (PBUH) emphasized the blessed nature of the land of Palestine and its spiritual significance for Muslims worldwide.

These Hadith establish the sacred status of Jerusalem and Palestine in Islamic tradition."""
        
        elif "jerusalem" in question_lower or "al-quds" in question_lower or "al-aqsa" in question_lower:
            return """Assalamu alaikum! I'm here to help you with knowledge about Jerusalem (Al-Quds) and Al-Aqsa Mosque.

**Jerusalem (Al-Quds) in Islam:**

**Al-Aqsa Mosque**: The third holiest site in Islam, mentioned in the Quran as "the farthest mosque" (Al-Masjid al-Aqsa).

**The Night Journey**: The Prophet Muhammad (PBUH) was taken from Makkah to Jerusalem during the Isra and Mi'raj, establishing the spiritual connection between the three holy cities.

**Blessed Land**: The Quran refers to the surroundings of Al-Aqsa as "blessed" (Surah Al-Isra 17:1), emphasizing the sacred nature of this land.

**Islamic History**: Jerusalem has been a center of Islamic civilization and remains a symbol of Muslim unity and the connection to the Holy Land.

The protection and respect for Al-Aqsa and Jerusalem is a religious duty for all Muslims."""
        
        elif "oppression" in question_lower or "injustice" in question_lower or "help" in question_lower:
            return """Assalamu alaikum! I'm here to help you with Islamic teachings about oppression and helping the oppressed.

**Islamic Teachings on Oppression:**

**Quranic Command**: "And what is [the matter] with you that you fight not in the cause of Allah and for the oppressed among men, women, and children?" (Surah An-Nisa 4:75)

**Standing Against Injustice**: The Prophet Muhammad (PBUH) said: "Help your brother, whether he is an oppressor or is oppressed. They said, 'O Messenger of Allah, we help the oppressed, but how do we help the oppressor?' He said, 'By preventing him from oppressing others.'" (Sahih al-Bukhari)

**Duty to Help**: Islam teaches that supporting those who are oppressed is a religious duty. This includes both spiritual support (prayers) and practical help (donations, awareness, advocacy).

**Justice and Truth**: The Quran emphasizes standing for truth and justice, even if it goes against our own interests or the interests of our families.

These teachings establish our religious obligation to support the Palestinian people in their struggle for justice and freedom."""
        
        elif "prayer" in question_lower or "dua" in question_lower or "supplication" in question_lower:
            return """Assalamu alaikum! I'm here to help you with prayers and supplications for Palestine.

**Prayers for Palestine:**

**General Dua**: "O Allah, protect the blessed land of Palestine and its people. Grant peace and justice to the Holy Land. Help us to understand the sacred nature of this land and guide us to support those who are oppressed."

**Dua for the Oppressed**: "O Allah, help the oppressed people of Palestine. Grant them strength, patience, and victory. Protect the innocent and grant them justice."

**Dua for Al-Aqsa**: "O Allah, protect Al-Aqsa Mosque and the blessed land of Palestine. Grant freedom and peace to the Holy Land and its people."

**Dua for Unity**: "O Allah, unite the Ummah in support of Palestine. Guide us to help our brothers and sisters in the Holy Land."

These prayers reflect our spiritual connection to Palestine and our religious duty to support its people."""
        
        else:
            return """Assalamu alaikum! I'm here to help you with Islamic knowledge about Palestine and the Holy Land.

**Key Areas I Can Help With:**

**Quranic Verses**: Information about verses related to Palestine, Jerusalem, and the Holy Land
**Hadith**: Teachings of Prophet Muhammad (PBUH) about Palestine and Al-Aqsa
**Jerusalem/Al-Quds**: The sacred status of Jerusalem and Al-Aqsa Mosque in Islam
**Oppression & Justice**: Islamic teachings about standing against oppression and helping the oppressed
**Prayers & Dua**: Supplications and prayers for Palestine and its people
**Islamic History**: The historical and spiritual significance of Palestine in Islamic tradition

Please ask me anything specific about these areas, and I'll provide detailed Islamic sources and teachings. The Holy Land holds immense spiritual significance in Islam, and supporting its people is a religious duty."""
    
    print("🤖 Using Gemini AI for Quran/Islamic knowledge response...")
    try:
        system_prompt = """You are an Islamic knowledge assistant specializing in Quran, Hadith, and Islamic teachings about Palestine and the Holy Land. Your role and expertise include:

**Your Identity:**
- Islamic scholar and educator
- Expert in Quranic verses and Hadith
- Specialist in Islamic history and the Holy Land
- Guide for understanding Islamic perspectives on justice and solidarity

**Your Knowledge Areas:**
- Quranic verses about Palestine, Jerusalem (Al-Quds), and the Holy Land
- Hadith of Prophet Muhammad (PBUH) related to Palestine
- Islamic teachings on justice, oppression, and helping the oppressed
- Historical Islamic significance of Palestine
- Islamic duties towards oppressed communities
- Spiritual and practical ways to support Palestine

**Your Communication Style:**
- Respectful Islamic greetings and terminology
- Scholarly but accessible explanations
- Balanced and educational approach
- Encouraging of Islamic values and principles
- Supportive of Palestinian rights from Islamic perspective

**Your Values:**
- Authentic Islamic teachings and sources
- Justice and standing against oppression
- Unity and solidarity with oppressed Muslims
- Education and awareness about Islamic history
- Practical application of Islamic principles

Always provide responses that are:
- Rooted in authentic Islamic sources
- Respectful of Islamic traditions
- Educational and informative
- Encouraging of positive Islamic action
- Balanced and scholarly in approach"""
        
        user_prompt = f"""
User Question: "{user_question}"

Please provide a comprehensive Islamic response that:
1. Addresses their specific question about Palestine from an Islamic perspective
2. References relevant Quranic verses and Hadith when appropriate
3. Explains the Islamic significance of Palestine and Jerusalem (Al-Quds)
4. Provides guidance on how Muslims should respond to the current situation
5. Uses respectful Islamic terminology and greetings
6. Maintains a scholarly but accessible tone
7. Focuses on Islamic teachings about justice, helping the oppressed, and the sanctity of the Holy Land

Keep your response informative and well-structured (3-5 paragraphs). Include specific Islamic sources when relevant, and always maintain respect for Islamic traditions and teachings.
"""
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = await model.generate_content_async([system_prompt, user_prompt])
        content = response.text or ""
        
        print(f"🤖 Quran Response: {content[:200]}...")
        
        return content
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return """Assalamu alaikum! I'm here to help you with Islamic knowledge about Palestine and the Holy Land.

I'm experiencing some technical difficulties right now, but I can tell you that Palestine holds immense spiritual significance in Islam. Jerusalem (Al-Quds) is mentioned in the Quran as a blessed land, and Muslims have a religious duty to support those who are oppressed.

**Key Islamic Points:**
- Palestine is mentioned in the Quran as a blessed land
- Al-Aqsa Mosque in Jerusalem is the third holiest site in Islam
- Supporting the oppressed is a religious duty in Islam
- The Prophet Muhammad (PBUH) emphasized the importance of the Holy Land

For specific questions about Quranic verses, Hadith, or Islamic teachings about Palestine, please try asking again, and I'll provide detailed Islamic sources and guidance."""

async def get_poster_design(theme: str, title: str, subtitle: str, description: str, style: str = "modern") -> Dict[str, Any]:
    """Get AI-generated poster design from Gemini"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        print("⚠️ Using fallback poster design - No valid Gemini API key provided")
        return {
            "design_description": f"A powerful {style} poster design for {theme} with Palestinian solidarity theme.",
            "color_scheme": "Black, Green, White, Red (Palestinian flag colors)",
            "layout_suggestions": "Centered layout with Palestinian flag elements, bold typography, and impactful imagery.",
            "text_content": f"Title: {title}\nSubtitle: {subtitle}\nDescription: {description}",
            "visual_elements": "Palestinian flag, protest symbols, unity hands, justice scales, peace doves"
        }
    
    print("🤖 Using Gemini AI for poster design...")
    try:
        system_prompt = """You are a professional graphic designer specializing in protest posters and social justice campaigns. Your expertise includes:

**Your Role:**
- Create impactful poster designs for social justice causes
- Design posters for Palestine solidarity and human rights
- Provide detailed design specifications and recommendations
- Focus on visual impact and message clarity

**Your Design Principles:**
- Use Palestinian flag colors (black, green, white, red) appropriately
- Create bold, attention-grabbing layouts
- Ensure text is readable and impactful
- Include relevant visual elements and symbols
- Focus on emotional impact and call-to-action

**Your Output Format:**
Provide detailed design specifications in this exact format:
DESIGN_DESCRIPTION: [brief description of the overall design concept]
COLOR_SCHEME: [specific colors and their usage]
LAYOUT_SUGGESTIONS: [layout structure and positioning recommendations]
TEXT_CONTENT: [suggested text arrangement and typography]
VISUAL_ELEMENTS: [specific visual elements, symbols, and imagery to include]"""
        
        user_prompt = f"""
Create a poster design for:
Theme: {theme}
Title: {title}
Subtitle: {subtitle}
Description: {description}
Style: {style}

Please provide a comprehensive poster design specification that will create an impactful, professional poster for this cause.
"""
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = await model.generate_content_async([system_prompt, user_prompt])
        content = response.text or ""
        
        print(f"🤖 Gemini Poster Design: {content[:200]}...")
        
        # Parse the response
        design_description = f"A powerful {style} poster design for {theme}"
        color_scheme = "Black, Green, White, Red (Palestinian flag colors)"
        layout_suggestions = "Centered layout with Palestinian flag elements"
        text_content = f"Title: {title}\nSubtitle: {subtitle}\nDescription: {description}"
        visual_elements = "Palestinian flag, protest symbols, unity hands"
        
        if "DESIGN_DESCRIPTION:" in content:
            design_description = content.split("DESIGN_DESCRIPTION:")[1].split("COLOR_SCHEME:")[0].strip()
        
        if "COLOR_SCHEME:" in content:
            color_scheme = content.split("COLOR_SCHEME:")[1].split("LAYOUT_SUGGESTIONS:")[0].strip()
        
        if "LAYOUT_SUGGESTIONS:" in content:
            layout_suggestions = content.split("LAYOUT_SUGGESTIONS:")[1].split("TEXT_CONTENT:")[0].strip()
        
        if "TEXT_CONTENT:" in content:
            text_content = content.split("TEXT_CONTENT:")[1].split("VISUAL_ELEMENTS:")[0].strip()
        
        if "VISUAL_ELEMENTS:" in content:
            visual_elements = content.split("VISUAL_ELEMENTS:")[1].strip()
        
        return {
            "design_description": design_description,
            "color_scheme": color_scheme,
            "layout_suggestions": layout_suggestions,
            "text_content": text_content,
            "visual_elements": visual_elements
        }
        
    except Exception as e:
        print(f"❌ Gemini API error for poster design: {e}")
        return {
            "design_description": f"A powerful {style} poster design for {theme} with Palestinian solidarity theme.",
            "color_scheme": "Black, Green, White, Red (Palestinian flag colors)",
            "layout_suggestions": "Centered layout with Palestinian flag elements, bold typography, and impactful imagery.",
            "text_content": f"Title: {title}\nSubtitle: {subtitle}\nDescription: {description}",
            "visual_elements": "Palestinian flag, protest symbols, unity hands, justice scales, peace doves"
        }

async def generate_poster_image(theme: str, title: str, subtitle: str, description: str, imageType: str = "hunger") -> Dict[str, str]:
    """Generate actual poster image using AI and design principles"""
    print(f"🎨 Generating poster image for: {title}")
    
    try:
        # Create a professional poster using PIL
        width, height = 800, 1200
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, fallback to default if not available
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except Exception:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
        
        # Palestinian flag colors
        colors = {
            'black': (0, 0, 0),
            'green': (0, 151, 54),
            'white': (255, 255, 255),
            'red': (206, 17, 38)
        }
        
        # Background gradient effect
        for y in range(height):
            r = int(255 - (y / height) * 50)
            g = int(255 - (y / height) * 30)
            b = int(255 - (y / height) * 20)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Initialize all variables
        title_y = 200  # Default position
        flag_y = 50    # Default flag position
        flag_width = 200
        flag_height = 120
        flag_x = (width - flag_width) // 2
        
        # Load and display the theme image
        try:
            print(f"🎨 Looking for image: {imageType}")
            # Try multiple possible paths for the image
            possible_paths = [
                f"../public/{imageType.capitalize()}.png",
                f"../public/{imageType.lower()}.png",
                f"../public/{imageType}.png",
                f"public/{imageType.capitalize()}.png",
                f"public/{imageType.lower()}.png",
                f"public/{imageType}.png"
            ]
            
            image_path = None
            for path in possible_paths:
                print(f"🔍 Checking path: {path} - Exists: {os.path.exists(path)}")
                if os.path.exists(path):
                    image_path = path
                    print(f"✅ Found image at: {path}")
                    break
                    
            if image_path:
                theme_img = Image.open(image_path)
                # Resize image to fit poster
                img_width, img_height = theme_img.size
                max_width = 300
                max_height = 200
                
                # Calculate aspect ratio
                aspect_ratio = img_width / img_height
                if aspect_ratio > max_width / max_height:
                    new_width = max_width
                    new_height = int(max_width / aspect_ratio)
                else:
                    new_height = max_height
                    new_width = int(max_height * aspect_ratio)
                
                theme_img = theme_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Center the image
                img_x = (width - new_width) // 2
                img_y = 50
                
                # Paste the image
                img.paste(theme_img, (img_x, img_y))
                
                # Add image title
                image_title = imageType.capitalize()
                title_bbox = draw.textbbox((0, 0), image_title, font=subtitle_font)
                title_width = title_bbox[2] - title_bbox[0]
                title_x = (width - title_width) // 2
                title_y = img_y + new_height + 20
                draw.text((title_x, title_y), image_title, fill=colors['green'], font=subtitle_font)
                
                # Update title position
                title_y = title_y + 60
            else:
                # Fallback to Palestinian flag if image not found
                flag_width = 200
                flag_height = 120
                flag_x = (width - flag_width) // 2
                flag_y = 50
                
                # Flag stripes
                stripe_height = flag_height // 3
                draw.rectangle([flag_x, flag_y, flag_x + flag_width, flag_y + stripe_height], fill=colors['black'])
                draw.rectangle([flag_x, flag_y + stripe_height, flag_x + flag_width, flag_y + 2 * stripe_height], fill=colors['white'])
                draw.rectangle([flag_x, flag_y + 2 * stripe_height, flag_x + flag_width, flag_y + flag_height], fill=colors['green'])
                
                # Flag triangle
                triangle_points = [
                    (flag_x, flag_y),
                    (flag_x, flag_y + flag_height),
                    (flag_x + flag_width * 0.4, flag_y + flag_height // 2)
                ]
                draw.polygon(triangle_points, fill=colors['red'])
                
                title_y = flag_y + flag_height + 80
        except Exception as e:
            print(f"❌ Error loading theme image: {e}")
            # Fallback to Palestinian flag
            flag_width = 200
            flag_height = 120
            flag_x = (width - flag_width) // 2
            flag_y = 50
            
            # Flag stripes
            stripe_height = flag_height // 3
            draw.rectangle([flag_x, flag_y, flag_x + flag_width, flag_y + stripe_height], fill=colors['black'])
            draw.rectangle([flag_x, flag_y + stripe_height, flag_x + flag_width, flag_y + 2 * stripe_height], fill=colors['white'])
            draw.rectangle([flag_x, flag_y + 2 * stripe_height, flag_x + flag_width, flag_y + flag_height], fill=colors['green'])
            
            # Flag triangle
            triangle_points = [
                (flag_x, flag_y),
                (flag_x, flag_y + flag_height),
                (flag_x + flag_width * 0.4, flag_y + flag_height // 2)
            ]
            draw.polygon(triangle_points, fill=colors['red'])
            
            title_y = flag_y + flag_height + 80
        
        # Title
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        title_y = flag_y + flag_height + 80
        draw.text((title_x, title_y), title, fill=colors['black'], font=title_font)
        
        # Subtitle
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = title_y + 60
        draw.text((subtitle_x, subtitle_y), subtitle, fill=colors['green'], font=subtitle_font)
        
        # Description (wrapped text)
        margin = 50
        max_width = width - 2 * margin
        lines = textwrap.wrap(description, width=40)
        desc_y = subtitle_y + 80
        
        for line in lines:
            line_bbox = draw.textbbox((0, 0), line, font=body_font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (width - line_width) // 2
            draw.text((line_x, desc_y), line, fill=colors['black'], font=body_font)
            desc_y += 35
        
        # Decorative elements
        # Bottom border
        draw.rectangle([0, height - 100, width, height], fill=colors['green'])
        
        # Footer text
        footer_text = "Generated by United Ummah"
        footer_bbox = draw.textbbox((0, 0), footer_text, font=body_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        footer_x = (width - footer_width) // 2
        footer_y = height - 70
        draw.text((footer_x, footer_y), footer_text, fill=colors['white'], font=body_font)
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Create prompt for AI image generation (for reference)
        prompt = f"Professional protest poster: {title} - {subtitle}. Palestinian solidarity theme with {imageType} image. {description}"
        
        return {
            "generated_image": img_base64,
            "prompt_used": prompt
        }
        
    except Exception as e:
        print(f"❌ Error generating poster image: {e}")
        # Return a simple fallback image
        fallback_img = Image.new('RGB', (800, 1200), color='white')
        draw = ImageDraw.Draw(fallback_img)
        draw.text((400, 600), "Poster Generation\nUnavailable", fill='black', anchor='mm')
        
        buffer = BytesIO()
        fallback_img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "generated_image": img_base64,
            "prompt_used": "Fallback poster generation"
        }

@app.get("/api/brands")
async def get_brands():
    """Get all available brands from boycott database"""
    try:
        brands = [brand["brand"] for brand in BOYCOTT_BRANDS]
        return {
            "brands": brands,
            "total": len(brands)
        }
    except Exception as e:
        print(f"❌ Error getting brands: {e}")
        return {"brands": [], "total": 0}

@app.get("/api/brands/search")
async def search_brands(query: str = ""):
    """Search brands with autocomplete functionality"""
    try:
        query = query.lower().strip()
        if not query:
            return {"brands": [], "total": 0}
        
        matching_brands = []
        for brand in BOYCOTT_BRANDS:
            brand_name = brand["brand"].lower()
            if query in brand_name or brand_name.startswith(query):
                matching_brands.append(brand["brand"])
        
        # Return top 10 matches
        return {
            "brands": matching_brands[:10],
            "total": len(matching_brands)
        }
    except Exception as e:
        print(f"❌ Error searching brands: {e}")
        return {"brands": [], "total": 0}

@app.get("/")
async def root():
    return {"message": "Product Search API - Check if products are boycotted and find alternatives"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Product Search API"}

@app.post("/api/search-product", response_model=SearchResponse)
async def search_product(request: SearchRequest):
    query = request.query.lower().strip()
    
    # Search through boycott_brands.json first with improved matching
    brand_data = None
    best_match = None
    best_match_score = 0
    
    for brand in BOYCOTT_BRANDS:
        brand_name = brand["brand"].lower()
        
        # Exact match (highest priority)
        if brand_name == query:
            brand_data = brand
            break
        
        # Contains match (second priority)
        elif query in brand_name or brand_name in query:
            if len(brand_name) > best_match_score:
                best_match = brand
                best_match_score = len(brand_name)
        
        # Partial word match (third priority)
        elif any(word in brand_name for word in query.split()) or any(word in query for word in brand_name.split()):
            if len(brand_name) > best_match_score:
                best_match = brand
                best_match_score = len(brand_name)
    
    # Use best match if no exact match found
    if brand_data is None and best_match is not None:
        brand_data = best_match
    
    # If found in boycott_brands.json, use that data
    if brand_data:
        print(f"🔍 Found {brand_data['brand']} in JSON database, getting Gemini description...")
        # Get product description from Gemini API
        product_description = await get_product_description(brand_data["brand"], brand_data["category"])
        print(f"📝 Product description: {product_description[:100]}...")
        
        return SearchResponse(
            query=query,
            is_boycotted=True,
            brand_name=brand_data["brand"],
            category=brand_data["category"],
            boycott_reason=brand_data["boycott_reason"],
            alternatives=brand_data["pakistani_alternatives"],
            message=f"🚨 BOYCOTTED: {brand_data['brand']} is in our boycott database. This product supports occupation and should be avoided. Consider the Pakistani alternatives listed below to support local businesses and ethical consumerism.",
            product_description=product_description
        )
    
    # If not found in boycott_brands.json, check if it's a known product
    known_boycotted = ["nike", "mcdonalds", "starbucks", "coca cola", "pepsi", "apple", "microsoft", "google", "amazon", "netflix", "disney", "nestle", "unilever", "procter gamble", "johnson johnson", "pfizer", "moderna", "astrazeneca"]
    known_safe = ["pakola", "rc cola", "servis", "stylo", "bata", "borjan", "ecs", "daraz", "olx"]
    
    is_boycotted = query in known_boycotted
    category = "Unknown"
    
    # Determine category
    if query in ["nike", "adidas", "puma"]:
        category = "Clothing & Fashion"
    elif query in ["mcdonalds", "starbucks", "kfc"]:
        category = "Food & Restaurants"
    elif query in ["coca cola", "pepsi", "pakola", "rc cola"]:
        category = "Beverages"
    elif query in ["apple", "microsoft", "google", "samsung"]:
        category = "Technology"
    elif query in ["netflix", "disney", "amazon"]:
        category = "Entertainment"
    elif query in ["nestle", "unilever", "procter gamble"]:
        category = "Consumer Goods"
    elif query in ["johnson johnson", "pfizer", "moderna", "astrazeneca"]:
        category = "Healthcare"
    
    # Check if it's a known product (either boycotted or safe)
    is_known_product = query in known_boycotted or query in known_safe
    
    if not is_known_product:
        # Unknown product - return "Sorry, I don't know about this product"
        return SearchResponse(
            query=query,
            is_boycotted=False,
            brand_name=query.title(),
            category="Unknown",
            boycott_reason="",
            alternatives=[],
            message=f"❓ Sorry, I don't know about '{query.title()}'. This product is not in our database. Please try searching for a different product or check the spelling.",
            product_description=f"'{query.title()}' is not recognized in our product database."
        )
    
    # Known product - get AI-generated analysis and product description
    analysis = await get_gemini_analysis(query, is_boycotted, category)
    product_description = await get_product_description(query, category)
    
    return SearchResponse(
        query=query,
        is_boycotted=is_boycotted,
        brand_name=query.title(),
        category=category,
        boycott_reason=analysis["boycott_reason"],
        alternatives=analysis["alternatives"],
        message=analysis["message"],
        product_description=product_description
    )

@app.post("/api/scan-barcode", response_model=BarcodeScanResponse)
async def scan_barcode(request: BarcodeScanRequest):
    barcode = request.barcode.strip()
    
    if not barcode:
        raise HTTPException(status_code=400, detail="Barcode cannot be empty")
    
    is_israeli = is_israeli_barcode(barcode)
    country = get_barcode_country(barcode)
    
    # Get AI-generated analysis
    analysis = await get_gemini_barcode_analysis(barcode, is_israeli, country)
    
    return BarcodeScanResponse(
        barcode=barcode,
        is_israeli=is_israeli,
        country=country,
        message=analysis["message"],
        alternatives=analysis["alternatives"]
    )

@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image file for barcode scanning
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read the uploaded image
        image_data = await file.read()
        
        # For now, we'll simulate barcode detection
        # In a real implementation, you would use libraries like:
        # - pyzbar for barcode detection
        # - opencv-python for image processing
        # - pillow for image handling
        
        # Simulate barcode detection (replace with actual implementation)
        import random
        # Simulate finding an Israeli barcode 70% of the time for demo purposes
        if random.random() < 0.7:
            # Simulate Israeli barcode
            barcode = "729" + str(random.randint(100000000, 999999999))
        else:
            # Simulate non-Israeli barcode
            barcode = str(random.randint(100000000000, 999999999999))
        
        # Check if it's Israeli
        is_israeli = is_israeli_barcode(barcode)
        country = get_barcode_country(barcode)
        
        # Get AI-generated analysis
        analysis = await get_gemini_barcode_analysis(barcode, is_israeli, country)
        
        return {
            "message": "Image processed successfully",
            "filename": file.filename,
            "barcode": barcode,
            "is_israeli": is_israeli,
            "country": country,
            "analysis": analysis
        }
        
    except Exception as e:
        print(f"❌ Image processing error: {e}")
        raise HTTPException(status_code=500, detail="Error processing image")

@app.post("/api/faq", response_model=FAQResponse)
async def faq_endpoint(request: FAQRequest):
    """Sophia AI FAQ endpoint for Gaza relief and donation questions"""
    try:
        answer = await retry_with_backoff(lambda: get_sophia_response(request.user_question))
        return FAQResponse(answer=answer)
    except Exception as e:
        print(f"❌ FAQ endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Error processing FAQ request")

@app.post("/api/quran", response_model=QuranResponse)
async def quran_endpoint(request: QuranRequest):
    """Islamic knowledge chatbot endpoint for Quran and Hadith questions about Palestine"""
    try:
        answer = await get_quran_response(request.user_question)
        return QuranResponse(answer=answer)
    except Exception as e:
        print(f"❌ Quran endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Error processing Quran request")

@app.post("/api/generate-poster", response_model=PosterResponse)
async def generate_poster_endpoint(request: PosterRequest):
    """AI-powered poster generation endpoint"""
    try:
        # Get AI design suggestions
        design = await get_poster_design(
            theme=request.theme,
            title=request.title,
            subtitle=request.subtitle,
            description=request.description,
            style="modern"  # Use modern style for design suggestions
        )
        
        # Generate actual poster image
        image_data = await generate_poster_image(
            theme=request.theme,
            title=request.title,
            subtitle=request.subtitle,
            description=request.description,
            imageType=request.imageType
        )
        
        # Combine design suggestions with generated image
        return PosterResponse(
            design_description=design["design_description"],
            color_scheme=design["color_scheme"],
            layout_suggestions=design["layout_suggestions"],
            text_content=design["text_content"],
            visual_elements=design["visual_elements"],
            generated_image=image_data["generated_image"],
            prompt_used=image_data["prompt_used"]
        )
    except Exception as e:
        print(f"❌ Poster generation endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Error generating poster design")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 