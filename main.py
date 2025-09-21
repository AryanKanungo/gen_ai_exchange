import os
import traceback
import base64
import json
import datetime as dt
from collections import Counter
from typing import Annotated, List, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel, Field

from google.auth.transport import requests as ga_requests
from google.oauth2 import id_token as ga_id_token

from google.cloud import firestore, storage, speech, aiplatform
from vertexai import init as vertex_init
from vertexai.generative_models import GenerativeModel
from vertexai.preview.vision_models import Image as VtxImage
from vertexai.preview.vision_models import ImageGenerationModel

load_dotenv()

print("PROJECT_ID:", os.getenv("PROJECT_ID"))
print("CREDENTIALS:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
print("BUCKET_NAME:", os.getenv("BUCKET_NAME"))

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "us-central1")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
BUCKET_NAME = os.getenv("BUCKET_NAME")

if not PROJECT_ID or not GOOGLE_APPLICATION_CREDENTIALS:
    raise RuntimeError("Missing PROJECT_ID or GOOGLE_APPLICATION_CREDENTIALS in .env")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

db = firestore.Client(project=PROJECT_ID)

storage_client = storage.Client(project=PROJECT_ID)
bucket = storage_client.bucket(BUCKET_NAME)
if not bucket.exists():
    raise RuntimeError(
        f"GCS bucket '{BUCKET_NAME}' not found. Create it in Console or set the correct BUCKET_NAME."
    )

aiplatform.init(project=PROJECT_ID, location=LOCATION)
vertex_init(project=PROJECT_ID, location=LOCATION)
GEMINI_PRO = GenerativeModel("gemini-2.0-flash")

speech_client = speech.SpeechClient()

app = FastAPI(title="Artisans Marketplace API (Google Cloud only)", version="3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_identity_token(authorization: Annotated[str | None, Header()] = None) -> dict:
    """
    Verifies a Google Identity Platform ID token.
    Clients must authenticate via Identity Platform (client SDK / REST) and send:
      Authorization: Bearer <ID_TOKEN>
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        token = authorization.split(" ")[1]
    except Exception:
        raise HTTPException(status_code=401, detail="Malformed Authorization header")

    try:
        req = ga_requests.Request()

        claims = ga_id_token.verify_oauth2_token(token, req, audience=PROJECT_ID)

        iss_ok = claims.get("iss") in (
            f"https://securetoken.google.com/{PROJECT_ID}",
            "https://accounts.google.com",
            "accounts.google.com",
        )
        if not iss_ok:
            raise ValueError(f"Invalid issuer: {claims.get('iss')}")

        uid = claims.get("user_id") or claims.get("sub")
        if not uid:
            raise ValueError("Token missing user identifier")
        claims["uid"] = uid
        return claims
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

DEMO_UID = "demo-user"  #auth disabled 


# class ProductCreate(BaseModel):
#     name: str
#     description: str
#     price: float = Field(ge=0)
#     category: Optional[str] = None
#     tags: List[str] = Field(default_factory=list)
#     made_to_order: bool = False
#     inventory: Optional[int] = Field(default=None, ge=0)

class DescriptionIn(BaseModel):
    description: str
    title: Optional[str] = None
    language: Optional[str] = "en"
    category: Optional[str] = None


# @app.get("/", include_in_schema=False)
# def root():
#     return RedirectResponse(url="/docs")

# @app.get("/health")
# def health():
#     return JSONResponse({"status": "ok", "project": PROJECT_ID, "location": LOCATION})

# #AUTH REMOVED
# @app.post("/products")
# def create_product(product: ProductCreate):
#     try:
#         user_id = DEMO_UID  # was: current_user["uid"]
#         product_data = {
#             "name": product.name,
#             "description": product.description,
#             "price": product.price,
#             "category": product.category,
#             "tags": [t.lower() for t in product.tags],
#             "owner_id": user_id,
#             "created_at": firestore.SERVER_TIMESTAMP,
#             "active": True,
#             "made_to_order": product.made_to_order,
#             "inventory": None if product.made_to_order else (product.inventory if product.inventory is not None else 999999),
#         }
#         ref = db.collection("products").add(product_data)[1]
#         return {"message": "Product created", "product_id": ref.id}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# #AUTH REMOVED
# @app.get("/products/mine")
# def get_my_products():
#     try:
#         uid = DEMO_UID  # was: current_user["uid"]
#         products = []
#         for doc in db.collection("products").where("owner_id", "==", uid).stream():
#             p = doc.to_dict(); p["id"] = doc.id
#             products.append(p)
#         return {"data": products}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/products")
# def get_products():
#     try:
#         products = []
#         for doc in db.collection("products").where("active", "==", True).stream():
#             p = doc.to_dict(); p["id"] = doc.id
#             products.append(p)
#         return {"data": products}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

#AUTH REMOVED
@app.post("/upload/image")
def upload_image(file: UploadFile = File(...)):
    try:
        uid = DEMO_UID  # was: current_user["uid"]
        object_name = f"{uid}/{dt.datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{file.filename}"
        blob = bucket.blob(object_name)
        blob.upload_from_file(file.file, content_type=file.content_type)
        # For demo: make public. In prod, use Signed URLs instead.
        blob.make_public()
        return {"message": "Image uploaded", "url": blob.public_url, "gcs_path": f"gs://{BUCKET_NAME}/{object_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {e}")

def _daterange(n_days=30):
    today = dt.date.today()
    start = today - dt.timedelta(days=n_days)
    return start, today

#AUTH REMOVED
@app.get("/stats/overview")
def stats_overview(days: int = 30):
    """
    Reads 'orders' collection. Each order should include:
      items: [{product_id, qty, price_at_purchase}], owner_split: {artisan_uid: amount}, created_at
    """
    try:
        artisan_id = DEMO_UID  # was: current_user["uid"]
        start_date, _ = _daterange(days)
        start_ts = dt.datetime.combine(start_date, dt.time.min)

        q = db.collection("orders").where("created_at", ">=", start_ts)
        orders = [dict(doc.to_dict(), id=doc.id) for doc in q.stream()]
        orders = [o for o in orders if artisan_id in (o.get("owner_split") or {})]

        total_orders = len(orders)
        revenue = sum(o.get("owner_split", {}).get(artisan_id, 0.0) for o in orders)

        items_count = 0
        product_counter = Counter()
        for o in orders:
            for it in o.get("items", []):
                product_counter[it["product_id"]] += it["qty"]
                items_count += it["qty"]

        aov = (revenue / total_orders) if total_orders else 0.0
        top_products = [{"product_id": pid, "qty": qty} for pid, qty in product_counter.most_common(5)]

        products = []
        for doc in db.collection("products").where("owner_id", "==", artisan_id).stream():
            p = doc.to_dict(); p["id"] = doc.id
            products.append(p)

        return {
            "days": days,
            "summary": {
                "total_orders": total_orders,
                "revenue": round(revenue, 2),
                "items_sold": items_count,
                "average_order_value": round(aov, 2),
                "top_products": top_products
            },
            "catalog_size": len(products),
            "products": products
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats failed: {e}")

#AUTH REMOVED
@app.get("/ai/analysis")
def analysis_dashboard(days: int = 30):
    try:
        stats = stats_overview(days=days)
        prompt = {
            "task": "Marketplace coaching for Indian artisan",
            "context": {
                "stats": stats["summary"],
                "catalog_size": stats["catalog_size"],
                "products": stats["products"],
                "time_window_days": stats["days"]
            },
            "instructions": [
                "Return STRICT JSON with keys: 'pricing', 'bundles', 'seo', 'photos', 'seasonality', 'inventory', 'promotions', 'discounts', 'new_product_ideas'.",
                "Each key should be a list of recommendations; include rationale and expected impact.",
                "Consider Indian festivals (Diwali, Rakhi, Eid, wedding season) and payday patterns."
            ]
        }
        resp = GEMINI_PRO.generate_content(
            [json.dumps(prompt)],
            generation_config={"response_mime_type": "application/json"}
        )
        try:
            ai_json = json.loads(resp.text)
        except Exception:
            ai_json = {"raw": resp.text}
        return {"stats": stats, "ai": ai_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

#AUTH REMOVED
@app.post("/ai/enhance-description")
def enhance_description(body: DescriptionIn):
    try:
        prompt = {
            "task": "Enhance an artisan product listing for ecommerce in India",
            "inputs": body.dict(),
            "instructions": [
                "Return STRICT JSON with keys: title, short_description, long_description, bullet_points[], seo_tags[], alt_text.",
                "Tone: warm, authentic, concise; avoid hype.",
                "Include craft technique, materials, care instructions if present.",
                "Optimize title for search (<=70 chars) including craft terms (Banarasi, Ajrakh, Dhokra, etc.).",
                "Use Indian English if language='en'."
            ]
        }
        resp = GEMINI_PRO.generate_content(
            [json.dumps(prompt)],
            generation_config={"response_mime_type": "application/json"}
        )
        try:
            return json.loads(resp.text)
        except Exception:
            return {"raw": resp.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {e}")

# AUTH REMOVED
@app.post("/ai/speech-to-pitch")
def speech_to_pitch(file: UploadFile = File(...)):
    try:
        audio_bytes = file.file.read()

        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            language_code="en-IN",  # adjust or expose as query param
            enable_automatic_punctuation=True,
            model="latest_long"
        )
        stt_resp = speech_client.recognize(config=config, audio=audio)
        transcript = " ".join([r.alternatives[0].transcript for r in stt_resp.results]) if stt_resp.results else ""

        sys = (
            "You are helping an Indian artisan craft a business pitch. "
            "Given a transcript, return strict JSON with keys: "
            "transcription, summary, pitch_title, pitch_story, key_points[]."
        )
        resp = GEMINI_PRO.generate_content(
            [sys, f"TRANSCRIPT:\n{transcript}\n\nNow produce the JSON."],
            generation_config={"response_mime_type": "application/json"}
        )
        try:
            out = json.loads(resp.text)
        except Exception:
            out = {"transcription": transcript, "raw": resp.text}
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech-to-pitch failed: {e}")

#AUTH REMOVED
# @app.post("/ai/clean-image")
# def clean_image(file: UploadFile = File(...)):
#     """
#     Background removal + studio background using Vertex AI Imagen.
#     Returns 2 base64 images:
#       - transparent_png_base64: subject cutout
#       - studio_background_base64: subject on clean gradient
#     """
#     try:
#         image_bytes = file.file.read()
#         base = VtxImage(image_bytes=image_bytes)
#         model = ImageGenerationModel.from_pretrained("imagegeneration@005")

#         cutout = model.edit_image(
#             base_image=base,
#             prompt="Remove the entire background; keep only the product with clean edges. Output PNG with transparent background.",
#             guidance_scale=18
#         )

#         studio = model.edit_image(
#             base_image=cutout,
#             prompt="Place the product on a professional ecommerce background: soft light grey to white gradient, even lighting, subtle ground shadow. Preserve true colors.",
#             guidance_scale=18
#         )

#         def to_b64(img_or_list):
#             img0 = img_or_list[0] if isinstance(img_or_list, list) else img_or_list
#             raw = getattr(img0, "_image_bytes", None) or img0.to_bytes()
#             return base64.b64encode(raw).decode("utf-8")

#         return {
#             "transparent_png_base64": to_b64(cutout),
#             "studio_background_base64": to_b64(studio),
#             "mime": "image/png"
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Image cleaning failed: {e}")

# @app.post("/ai/clean-image")
# def clean_image(file: UploadFile = File(...)):
#     """
#     Background removal + studio background using Vertex AI Imagen.
#     Returns 2 base64 images:
#       - transparent_png_base64: subject cutout
#       - studio_background_base64: subject on clean gradient
#     """
#     try:
#         # ✅ Step 1: Check input file
#         image_bytes = file.file.read()
#         print(f"[DEBUG] Received file: {file.filename}, size: {len(image_bytes)} bytes")

#         # ✅ Step 2: Initialize base image
#         base = VtxImage(image_bytes=image_bytes)
#         print("[DEBUG] Base image created ✅")

#         # ✅ Step 3: Load model
#         try:
#             model = ImageGenerationModel.from_pretrained("imagegeneration@002")
#             print("[DEBUG] Model loaded ✅")
#         except Exception as e:
#             print("[ERROR] Model load failed:", e)
#             traceback.print_exc()
#             raise

#         # ✅ Step 4: Generate cutout
#         try:
#             cutout = model.edit_image(
#                 base_image=base,
#                 prompt="Remove the entire background; keep only the product with clean edges. Output PNG with transparent background.",
#                 guidance_scale=18
#             )
#             print("[DEBUG] Cutout generated ✅")
#         except Exception as e:
#             print("[ERROR] Cutout generation failed:", e)
#             traceback.print_exc()
#             raise

#         # ✅ Step 5: Generate studio background
#         try:
#             studio = model.edit_image(
#                 base_image=cutout,
#                 prompt="Place the product on a professional ecommerce background: soft light grey to white gradient, even lighting, subtle ground shadow. Preserve true colors.",
#                 guidance_scale=18
#             )
#             print("[DEBUG] Studio background generated ✅")
#         except Exception as e:
#             print("[ERROR] Studio generation failed:", e)
#             traceback.print_exc()
#             raise

#         # ✅ Step 6: Safe base64 converter
#         def to_b64(img_or_list):
#             try:
#                 img0 = img_or_list[0] if isinstance(img_or_list, list) else img_or_list
#                 raw = getattr(img0, "_image_bytes", None) or img0.to_bytes()
#                 print(f"[DEBUG] Encoded image, size: {len(raw)} bytes")
#                 return base64.b64encode(raw).decode("utf-8")
#             except Exception as e:
#                 print("[ERROR] Base64 conversion failed:", e)
#                 traceback.print_exc()
#                 raise

#         result = {
#             "transparent_png_base64": to_b64(cutout),
#             "studio_background_base64": to_b64(studio),
#             "mime": "image/png"
#         }
#         print("[DEBUG] Returning response ✅")
#         return result

#     except Exception as e:
#         print("[FATAL ERROR] Image cleaning failed:", e)
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Image cleaning failed: {e}")
@app.post("/ai/clean-image")
def clean_image(file: UploadFile = File(...)):
    """
    Background removal + studio background using Vertex AI Imagen.
    Returns 2 base64 images:
      - transparent_png_base64: subject cutout
      - studio_background_base64: subject on clean gradient
    """
    try:
        # ✅ Step 1: Read input
        image_bytes = file.file.read()
        print(f"[DEBUG] Received file: {file.filename}, size: {len(image_bytes)} bytes")

        base = VtxImage(image_bytes=image_bytes)
        print("[DEBUG] Base image created ✅")

        # ✅ Step 2: Load model
        model = ImageGenerationModel.from_pretrained("imagegeneration@002")
        print("[DEBUG] Model loaded ✅")

        # ✅ Step 3: Generate cutout (background removed)
        cutout_resp = model.edit_image(
            base_image=base,
            prompt="Remove the entire background; keep only the product with clean edges. Output PNG with transparent background.",
            guidance_scale=18,
        )
        print("[DEBUG] Cutout generated ✅")

        # Extract image bytes properly
        cutout_img = cutout_resp[0] if isinstance(cutout_resp, list) else cutout_resp
        cutout_bytes = cutout_img.images[0]._image_bytes  # ✅ FIXED

        # ✅ Step 4: Re-wrap cutout as VtxImage for second edit
        cutout_base = VtxImage(image_bytes=cutout_bytes)

        # ✅ Step 5: Generate studio background
        studio_resp = model.edit_image(
            base_image=cutout_base,
            prompt = "Create a professional, high-end ecommerce product photo. Keep the product exactly as it is: preserve its true shape, proportions, textures, and exact colors. Do not add, remove, or modify any product details. Place it on a seamless, premium studio background with a smooth gradient from soft light gray (#f5f5f5) to pure white. Lighting should be bright, diffused, and evenly balanced, with no harsh reflections or color shifts. Add a very subtle, natural ground shadow directly under the product for depth. The final image should look like a luxury catalog photo: crisp, high resolution, minimalistic, with sharp focus and no noise, blemishes, or artifacts. Do not generate anything outside of the product itself and the clean background.",

            guidance_scale=18,
        )
        print("[DEBUG] Studio background generated ✅")

        studio_img = studio_resp[0] if isinstance(studio_resp, list) else studio_resp
        studio_bytes = studio_img.images[0]._image_bytes  # ✅ FIXED

        # ✅ Step 6: Return base64
        return {
            "transparent_png_base64": base64.b64encode(cutout_bytes).decode("utf-8"),
            "studio_background_base64": base64.b64encode(studio_bytes).decode("utf-8"),
            "mime": "image/png",
        }

    except Exception as e:
        print("[FATAL ERROR] Image cleaning failed:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Image cleaning failed: {e}")
