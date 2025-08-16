# Ummah United Backend API

A comprehensive FastAPI backend that provides multiple services for the Ummah United platform, including FAQ assistance, Quran/Hadith queries, and boycotted brands search with LLM integration.

## 🚀 Features

### FAQ System (Sophia)
- **AI-Powered FAQ**: Gemini-powered assistant for Gaza relief and donation queries
- **Smart Responses**: Contextual answers about humanitarian aid and Islamic charity
- **No Asterisks**: Clean formatting without special characters

### Quran & Hadith System
- **Islamic Knowledge**: Specialized assistant for Quranic verses and Hadith about Palestine
- **Historical Context**: Information about the Holy Land and Islamic history
- **Authentic Sources**: Reliable information from Islamic texts

### Product Search System
- **Brand Search**: Search through 100+ boycotted brands with natural language queries
- **LLM Integration**: Gemini-powered analysis for boycott reasons and alternative recommendations
- **Smart Caching**: In-memory caching to reduce API calls and improve performance
- **Comprehensive Database**: Brands across multiple categories with detailed boycott reasons
- **Fuzzy Search**: Intelligent matching with partial and similar brand names
- **Pakistani Alternatives**: Curated list of local and ethical alternatives

## 📋 Requirements

- Python 3.8+
- Gemini API key
- FastAPI and related dependencies

## 🛠️ Installation

### 1. Setup Environment

```bash
# Navigate to the backend directory
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the `backend` directory:

```env
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Application Settings
DEBUG=True
LOG_LEVEL=INFO
```

**Important**: You must obtain a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey) to use the LLM features.

## 🚀 Running the Application

### Development Mode

```bash
# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python main.py
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/health` | GET | Health check and system status |

### FAQ System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/faq` | POST | Get AI-powered FAQ responses about Gaza relief |

**Request Body:**
```json
{
  "user_question": "How can I donate to Gaza relief efforts?"
}
```

**Response:**
```json
{
  "answer": "There are several ways to donate to Gaza relief efforts...",
  "success": true
}
```

### Quran & Hadith System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/quran` | POST | Get Islamic knowledge about Palestine and the Holy Land |

**Request Body:**
```json
{
  "user_question": "What does the Quran say about Palestine?"
}
```

**Response:**
```json
{
  "answer": "The Quran mentions Palestine and the Holy Land in several verses...",
  "success": true
}
```

### Product Search System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/brands` | GET | Get all brands in the database |
| `/api/search` | POST | Search brands with natural language queries |

**Search Request Body:**
```json
{
  "query": "nike shoes",
  "limit": 10
}
```

**Search Response:**
```json
{
  "query": "nike shoes",
  "results": [
    {
      "brand": "Nike",
      "category": "Clothing & Fashion",
      "boycott_reason": "Supporting occupation through business operations and endorsements",
      "pakistani_alternatives": ["Local sportswear brands", "Adidas Pakistan", "Puma Pakistan"],
      "llm_summary": "AI-enhanced summary of boycott reasons",
      "llm_recommendations": ["Enhanced alternative recommendations"]
    }
  ],
  "total_results": 1,
  "search_time": 0.5
}
```

## 🔍 Search Features

### Brand Categories
- **Food & Restaurants**: Fast food chains and restaurants
- **Beverages**: Soft drinks, coffee, and energy drinks
- **Clothing & Fashion**: Sportswear and fashion brands
- **Technology**: Tech companies, hardware, and software

### Search Capabilities
- **Exact Match**: Direct brand name searches
- **Partial Match**: Searches with partial brand names
- **Fuzzy Search**: Intelligent matching for similar names
- **Category Search**: Filter by product categories
- **AI Enhancement**: LLM-powered insights and recommendations

### Caching
- **In-Memory Cache**: Reduces API calls for repeated searches
- **TTL**: 1-hour cache expiration
- **Performance**: Faster response times for cached queries

## 🗄️ Data Management

### Brands Database
The system uses a JSON file (`data/boycott_brands.json`) containing:
- Brand names and categories
- Detailed boycott reasons
- Pakistani alternatives
- Structured for easy updates and maintenance

### Data Structure
```json
{
  "brand": "Brand Name",
  "category": "Category",
  "boycott_reason": "Detailed reason for boycott",
  "pakistani_alternatives": ["Alternative 1", "Alternative 2", ...]
}
```

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Required for LLM features
- `DEBUG`: Enable debug mode (optional)
- `LOG_LEVEL`: Set logging level (optional)

### API Configuration
- **CORS**: Configured for frontend integration
- **Rate Limiting**: Built-in protection against abuse
- **Error Handling**: Comprehensive error responses
- **Validation**: Pydantic models for request/response validation

## 🚀 Performance

### Optimization Features
- **Async Processing**: Non-blocking operations
- **Smart Caching**: Reduces redundant API calls
- **Fuzzy Search**: Efficient text matching algorithms
- **Connection Pooling**: Optimized database connections

### Monitoring
- **Health Checks**: `/health` endpoint for monitoring
- **Response Times**: Built-in timing for search operations
- **Error Logging**: Comprehensive error tracking
- **API Documentation**: Auto-generated docs at `/docs`

## 🔒 Security

### API Security
- **Input Validation**: Pydantic models validate all inputs
- **CORS Protection**: Configured for specific origins
- **Error Handling**: No sensitive information in error messages
- **Rate Limiting**: Protection against abuse

### Data Security
- **Environment Variables**: Secure API key storage
- **Input Sanitization**: Clean and validate all inputs
- **Output Filtering**: Remove sensitive data from responses

## 📖 Usage Examples

### Frontend Integration

```javascript
// Search for brands
const searchBrands = async (query) => {
  const response = await fetch('/api/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, limit: 10 })
  });
  return response.json();
};

// Get FAQ answer
const getFAQAnswer = async (question) => {
  const response = await fetch('/api/faq', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_question: question })
  });
  return response.json();
};

// Get Quran/Hadith answer
const getQuranAnswer = async (question) => {
  const response = await fetch('/api/quran', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_question: question })
  });
  return response.json();
};
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the Ummah United platform and is designed to support humanitarian efforts and Islamic values.

## 🆘 Support

For support or questions:
- Check the API documentation at `/docs`
- Review the health endpoint at `/health`
- Contact the development team

---

**Note**: This backend is designed to work seamlessly with the Ummah United frontend application. Make sure both frontend and backend are properly configured and running for full functionality. 