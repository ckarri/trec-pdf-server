# TREC AI Offer Generator — Deployment Guide

## Files in this package
- server.py          — Python backend (deploy to Railway)
- requirements.txt   — Python dependencies
- Procfile           — Railway start command
- railway.json       — Railway config
- offer_generator.html — Frontend (deploy to Netlify)
- trec_20_18.pdf     — TREC Main Contract
- 40-11.pdf          — Third Party Financing Addendum
- 36-10.pdf          — HOA Addendum

---

## STEP 1 — Deploy backend to Railway

1. Go to https://railway.app and sign up (free)

2. Click "New Project" → "Deploy from GitHub repo"
   OR use Railway CLI:
   ```
   npm install -g @railway/cli
   railway login
   railway init
   railway up
   ```
   
   Or the easiest way — drag and drop:
   - Go to railway.app/new
   - Select "Empty Project"
   - Click "Deploy from local directory"
   - Upload the entire folder contents

3. After deploy, go to your Railway project settings:
   - Click "Variables"
   - Add: BROKERAGE_PASSWORD = YourChosenPassword123!
   
4. Go to "Settings" → "Networking" → "Generate Domain"
   - Copy the URL — looks like: https://your-app-name.up.railway.app
   - This is your API_URL

---

## STEP 2 — Update offer_generator.html

Open offer_generator.html and find this line near the bottom:

```javascript
var API = 'REPLACE_WITH_RAILWAY_URL';
```

Replace with your Railway URL:
```javascript
var API = 'https://your-app-name.up.railway.app';
```

Save the file.

---

## STEP 3 — Deploy frontend to Netlify

1. Go to https://netlify.com
2. Drag the offer_generator.html file to the deploy area
   (or your whole Netlify site folder)
3. Done — the tool is live!

---

## How it works

- Agent opens the URL on any device
- Enters brokerage password (set in Railway env variable)
- Types offer terms in plain English
- AI extracts all fields
- Agent reviews and edits
- Clicks Download → Railway fills the TREC PDFs → PDF downloads to device

---

## Changing the password

Go to Railway dashboard → your project → Variables → edit BROKERAGE_PASSWORD
No redeploy needed — takes effect immediately.

---

## Forms generated per transaction

| Loan Type | Forms Included |
|-----------|---------------|
| Conventional | 20-18 + 40-11 |
| FHA | 20-18 + 40-11 |
| VA | 20-18 + 40-11 |
| Cash | 20-18 only |
| Any + HOA=yes | All above + 36-10 |

---

## Costs

- Railway free tier: $5/month credit (more than enough for your usage)
- Netlify free tier: unlimited static hosting
- Total: ~$0/month for typical brokerage usage
