# Credit Card Parser - Deployment Guide

## Architecture

```
Frontend (Vercel - Static) → Backend (Render - FastAPI) → PDF Parser
```

## 🚀 Backend Deployment on Render

### Step 1: Test Locally First

```bash
# Install dependencies
pip install -r requirements.txt

# Run backend
python main.py

# Or use uvicorn directly
uvicorn main:app --reload
```

Visit: http://127.0.0.1:8000
API Docs: http://127.0.0.1:8000/docs

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Add FastAPI backend for Render deployment"
git push
```

### Step 3: Deploy on Render

1. Go to [render.com](https://render.com)
2. Sign in with GitHub
3. Click **New +** → **Web Service**
4. Connect your repository: `virti1331/CC-Statement-Parser`
5. Configure:
   - **Name**: `cc-statement-parser`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
   - **Instance Type**: Free tier is fine

6. Click **Create Web Service**

### Step 4: Get Your Backend URL

After deployment completes, you'll get a URL like:
```
https://cc-statement-parser.onrender.com
```

Test it:
```
https://cc-statement-parser.onrender.com/
```

You should see:
```json
{
  "status": "CC Parser Backend Live",
  "version": "1.0",
  "supported_banks": ["HDFC", "ICICI", "Axis", "Chase", "IDFC"]
}
```

### Step 5: Update Frontend with Backend URL

Edit `public/index.html` and `frontend/index.html`:

```javascript
const API_URL = "https://YOUR-RENDER-URL.onrender.com/parse";
```

Replace `YOUR-RENDER-URL` with your actual Render URL.

### Step 6: Deploy Frontend on Vercel

Frontend is already configured to deploy from the `public/` folder.

1. Go to Vercel dashboard
2. Your project will auto-deploy when you push the updated frontend
3. Done!

## 📝 API Endpoints

### GET /
Health check - returns backend status

### GET /health  
Health check endpoint

### POST /parse
Upload and parse credit card statement PDF

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (PDF file)

**Response:**
```json
{
  "success": true,
  "file": "statement.pdf",
  "data": {
    "issuer": "HDFC",
    "statement": { ... },
    "transactions": [ ... ]
  }
}
```

## 🔧 Local Development

Backend:
```bash
python main.py
# Runs on http://127.0.0.1:8000
```

Frontend:
```bash
# Just open public/index.html in browser
# Or use any static server
python -m http.server 3000
```

## 🎯 Environment Variables (Optional)

For frontend, you can override API URL:
```javascript
window.API_URL_OVERRIDE = "http://127.0.0.1:8000/parse";
```

## 📦 Project Structure

```
├── main.py                 # FastAPI backend
├── requirements.txt        # Python dependencies
├── backend/               # Parser logic
│   ├── main.py
│   └── parser/
├── public/                # Frontend (served by Vercel)
│   └── index.html
└── DEPLOYMENT.md          # This file
```

## ✅ That's It!

No serverless complexity. Just clean, reliable architecture.
