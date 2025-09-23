#  AI-Powered Artisan Marketplace

An AI-driven digital marketplace platform designed to empower local artisans to bring their craft online with professional product presentation, marketing storytelling, and data-driven sales insights.

Built using Google Cloud Platform (Vertex AI Gemini, Vertex AI Imagen, Cloud Speech-to-Text, Firestore, Cloud Storage, Identity Platform, Cloud Run) and FastAPI + Flutter Web.


## Features

* *Secure Login* – Artisans authenticate via *Identity Platform*.
* *Product Creation* – Add product details with a simple form.
* *AI Description Enhancement* – *Gemini* refines product title, description, and SEO tags.
* *Image Cleaning & Backgrounding* – *Vertex AI Imagen* removes backgrounds and generates studio-quality product photos.
* *Speech-to-Pitch* – Record artisan’s story → *Speech-to-Text + Gemini* produces transcription, summary, and polished marketing pitch.
* *AI Insights Dashboard* – Firestore order data analyzed by *Gemini* for:

  * Pricing optimization
  * Seasonal promotions
  * SEO recommendations
  * Inventory alerts
  * Product bundling ideas
* *Orders & Stats* – Artisans can track orders, revenue, and sales trends in real time.



##  Architecture


[Frontend: Flutter Web]  -->  [Backend: FastAPI on Cloud Run]
         |                               |
   Identity Platform (Auth)        Firestore (DB)
                                   Cloud Storage (Images)
                                   Vertex AI Gemini (Text/Insights)
                                   Vertex AI Imagen (Image Cleanup)
                                   Speech-to-Text




##  Project Structure


artisan-marketplace/
│
├── backend/
│   ├── main.py                # FastAPI backend (Cloud Run ready)
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Example env vars
│
├── frontend/
│   ├── lib/                   # Flutter app code
│   ├── pubspec.yaml           # Flutter dependencies
│   └── web/                   # Flutter web build output
│
└── README.md




## ⚙ Setup & Deployment

### 1. Clone repo

bash
git clone https://github.com/AryanKanungo/artisan-marketplace.git
cd artisan-marketplace


### 2. Backend (FastAPI on Cloud Run)

*Dependencies*

bash	
cd backend
pip install -r requirements.txt


*Run locally*

bash
uvicorn main:app --reload --port 8000


*Deploy*

bash
gcloud run deploy artisans-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars=PROJECT_ID=emerald-pipe-472704-m5,LOCATION=us-central1,BUCKET_NAME=emerald-pipe-472704-m5-artisan-media

*Libraries*

pip install google-cloud-firestore \
            google-cloud-storage \
            google-cloud-aiplatform \
            google-cloud-speech \
            google-cloud-run
pip install firebase-admin



### 3. Frontend (Flutter Web + Firebase Hosting)

bash
cd frontend
flutter build web
firebase init hosting
firebase deploy




##  Environment Variables (.env)

Create a .env file inside backend/ with:


GOOGLE_APPLICATION_CREDENTIALS=gcp-credentials.json
PROJECT_ID=emerald-pipe-472704-m5
LOCATION=us-central1
BUCKET_NAME=emerald-pipe-472704-m5-artisan-media



##  Estimated Costs (India)
| Service           | Pilot Cost (₹) |
| ----------------- | -------------- |
| Identity Platform | ₹0             |
| Firestore         | ₹1,500         |
| Cloud Storage     | ₹200           |
| Vertex AI Gemini  | ₹2,000         |
| Vertex AI Imagen  | ₹9,000         |
| Speech-to-Text    | ₹100           |
| Cloud Run         | ₹300           |
| **Total**         | \~₹13,100      |




##  USP

Unlike generic marketplaces, our platform is custom-built for artisans, turning raw product images + simple descriptions + voice stories into professional e-commerce listings with AI-generated content, polished visuals, and real-time sales coaching.



##  Screens / Wireframes

* Landing page with Artisan login/signup
* Dashboard with revenue/orders/AI insights
* Add product with “Enhance with AI”
* Image upload & cleanup (before/after)
* Speech-to-Pitch generation screen
* Orders table + Stats dashboard



##  Team

[Ananya Baweja / Leader]
[Aryan Kanungo]
[Soha Chand]
[Kartik Agrawal]
[Atharv Dixit]
