# Gen AI Analytics Backend API

## Overview
A FastAPI backend that simulates a Gen AI analytics tool, converting natural language queries into structured data requests with:
- JWT Authentication
- Natural language processing
- Mock database with sample data
- Interactive API documentation

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation
```bash
git clone https://github.com/yourusername/gen-ai-analytics-backend.git
cd gen-ai-analytics-backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
pip install -r requirements.txt

Run Locally
uvicorn main:app --reload
Access docs at http://localhost:8000/docs

API Endpoints
Endpoint    Method	    Description
/token	    POST	    Get JWT token
/query	    POST	    Process natural language query
/explain	POST	    Explain query interpretation
/validate	POST	    Validate query feasibility
/health	    GET	        Service status

Example Usage
1. Get access token:
curl -X POST "http://localhost:8000/token" \
     -d "username=analyst&password=analystpass"

2. Make authenticated query:
curl -X POST "http://localhost:8000/query" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"query": "Show top 5 customers"}'

Sample Queries
1. "What were sales last quarter?"
2. "List products with inventory under 100"
3. "Compare revenue by region"
4. "Average employee salary by department"

Deployment
Render
1. Create new Web Service
2. Set build command: pip install -r requirements.txt
3. Set start command: gunicorn -k uvicorn.workers.UvicornWorker main:app

Environment Variables
SECRET_KEY=your_random_key_here
DATABASE_URL=sqlite:///data.db

License
MIT


This version:
1. Uses clean markdown formatting
2. Includes all essential sections
3. Has ready-to-use code blocks
4. Maintains consistent spacing
5. Provides direct copy-paste ability
6. Includes minimal but sufficient documentation
