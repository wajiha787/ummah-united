"""
FastAPI Backend for Boycotted Brands Search with LLM Integration
Uses boycott_brands.json for brand data and Gemini 1.5 Flash for reasoning & recommendations.
"""
import os
from dotenv import load_dotenv

# Load .env automatically
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("GEMINI_API_KEY not found in environment variables. LLM features will be disabled.")

import google.generativeai as genai

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


import json
import hashlib
from typing import List, Dict, Optional, Any
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import io

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Boycotted Brands Search API",
    description="Search boycotted brands and get Pakistani alternatives with LLM insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class BrandResponse(BaseModel):
    brand: str
    category: str
    boycott_reason: str
    pakistani_alternatives: List[str]
    llm_summary: Optional[str] = None
    llm_recommendations: Optional[List[str]] = None

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class SearchResponse(BaseModel):
    query: str
    results: List[BrandResponse]
    total_results: int
    search_time: float

# Globals
BRANDS_DATA = []
CACHE = {}
CACHE_EXPIRY = {}
CACHE_TTL = 3600  # 1 hour cache TTL
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB max file size

# Load JSON
async def load_brands_data():
    global BRANDS_DATA
    try:
        json_path = Path("data/boycott_brands.json")
        if json_path.exists():
            content = json_path.read_text(encoding='utf-8')
            BRANDS_DATA = json.loads(content)
            logger.info(f"Loaded {len(BRANDS_DATA)} brands from JSON")
        else:
            logger.error("data/boycott_brands.json not found")
            BRANDS_DATA = []
    except Exception as e:
        logger.error(f"Error loading brands data: {e}")
        BRANDS_DATA = []

# Normalize text for fuzzy matching
def _normalize_text(value: str) -> str:
    if not isinstance(value, str):
        return ""
    normalized = unicodedata.normalize('NFKD', value)
    return normalized.encode('ascii', 'ignore').decode('ascii').casefold().strip()

# Fuzzy search
def search_brands(query: str, limit: int = 10) -> List[Dict]:
    if not query:
        return []
    query_norm = _normalize_text(query)
    results = []
    for brand in BRANDS_DATA:
        brand_norm = _normalize_text(brand.get("brand", ""))
        category_norm = _normalize_text(brand.get("category", ""))
        if query_norm == brand_norm:
            results.append({**brand, "match_score": 100})
        elif query_norm in brand_norm or brand_norm in query_norm:
            results.append({**brand, "match_score": 85})
        else:
            ratio = SequenceMatcher(None, query_norm, brand_norm).ratio()
            if ratio >= 0.8:
                results.append({**brand, "match_score": int(ratio * 80)})
            elif query_norm in category_norm:
                results.append({**brand, "match_score": 60})
    results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return results[:limit]

# Cache helpers
def get_cache_key(query: str) -> str:
    return hashlib.md5(query.lower().encode()).hexdigest()

def is_cache_valid(cache_key: str) -> bool:
    return cache_key in CACHE_EXPIRY and datetime.now() < CACHE_EXPIRY[cache_key]

# LLM insights
async def get_llm_insights(query: str, brand_data: Dict) -> Dict[str, Any]:
    if not GEMINI_API_KEY:
        return {
            "summary": brand_data["boycott_reason"],
            "recommendations": brand_data["pakistani_alternatives"]
        }
    try:
        prompt = f"""
Analyze this brand information and provide:
1. A simple, clear summary of why this brand is boycotted (max 2 sentences)
2. 3-5 specific recommendations for each Pakistani alternative (max 1 sentence each)

Brand: {brand_data['brand']}
Category: {brand_data['category']}
Boycott Reason: {brand_data['boycott_reason']}
Pakistani Alternatives: {', '.join(brand_data['pakistani_alternatives'])}

Format your response as:
Summary: [your summary here]
Recommendations: [alternative1: recommendation1], [alternative2: recommendation2], etc.
"""
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = await model.generate_content_async(prompt)
        content = response.text or ""
        summary = brand_data["boycott_reason"]
        recommendations = brand_data["pakistani_alternatives"]
        if "Summary:" in content:
            summary = content.split("Summary:")[1].split("Recommendations:")[0].strip()
        if "Recommendations:" in content:
            recs_text = content.split("Recommendations:")[1].strip()
            recommendations = [rec.strip() for rec in recs_text.split(",") if rec.strip()]
        return {"summary": summary, "recommendations": recommendations}
    except Exception as e:
        logger.error(f"LLM API error: {e}")
        return {"summary": brand_data["boycott_reason"], "recommendations": brand_data["pakistani_alternatives"]}

# Startup
@app.on_event("startup")
async def startup_event():
    await load_brands_data()

# Endpoints
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Boycotted Brands Search API", "version": "1.0.0"}

@app.get("/brands", response_model=List[BrandResponse], tags=["Brands"])
async def get_all_brands():
    return BRANDS_DATA

@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_endpoint(request: SearchRequest):
    query = request.query
    limit = request.limit or 10
    start = datetime.now()
    cache_key = get_cache_key(query)
    if is_cache_valid(cache_key) and cache_key in CACHE:
        cached_result = CACHE[cache_key]
        cached_result["search_time"] = (datetime.now() - start).total_seconds()
        return cached_result
    results = search_brands(query, limit)
    if not results:
        raise HTTPException(status_code=404, detail=f"No brands found for '{query}'")
    enhanced = []
    for brand in results:
        insights = await get_llm_insights(query, brand)
        enhanced.append(BrandResponse(**brand, llm_summary=insights["summary"], llm_recommendations=insights["recommendations"]))
    response = SearchResponse(query=query, results=enhanced, total_results=len(enhanced), search_time=(datetime.now()-start).total_seconds())
    CACHE[cache_key] = response.dict()
    CACHE_EXPIRY[cache_key] = datetime.now() + timedelta(seconds=CACHE_TTL)
    return response
