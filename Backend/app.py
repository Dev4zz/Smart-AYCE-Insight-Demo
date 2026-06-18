import os
import json
import requests
import joblib
import re
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from apify_client import ApifyClient
from google import genai

# --- 1. KONFIGURASI API ---
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 

if not GROQ_API_KEY:
    print("⚠️ WARNING: GROQ_API_KEY belum di-set!")
if not GEMINI_API_KEY:
    print("⚠️ WARNING: GEMINI_API_KEY belum di-set!")
if not APIFY_TOKEN:
    print("⚠️ WARNING: APIFY_TOKEN belum di-set!")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
apify_client = ApifyClient(APIFY_TOKEN)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. MUAT MODEL SVM (LOKAL) ---
print("Memuat model SVM dan TF-IDF Vectorizer...")
try:
    model_svm = joblib.load('model_sentimen_smart_ayce.pkl')
    vectorizer = joblib.load('vectorizer_smart_ayce.pkl')
    print("✅ Model SVM berhasil dimuat!")
except Exception as e:
    print(f"❌ ERROR: Gagal memuat model SVM: {e}")

# --- ASPECT KEYWORD MAP (Smart Aspect Mapping) ---
ASPECT_KEYWORDS = {
    "Kualitas Makanan": ["enak", "lezat", "makanan", "rasa", "menu", "segar", "matang", "mentah", "asin", "hambar", "bumbu", "daging", "seafood", "sushi", "dessert"],
    "Pelayanan": ["pelayan", "staf", "staff", "karyawan", "ramah", "jutek", "cepat", "responsif", "waitress", "waiter", "server"],
    "Kebersihan": ["bersih", "kotor", "higien", "AC", "toilet", "tempat", "meja", "lantai", "nyaman", "jorok", "bau"],
    "Harga": ["mahal", "murah", "harga", "worth", "ekonomis", "sebanding", "value", "bayar", "biaya", "promo"],
    "Variasi Menu": ["variasi", "pilihan", "beragam", "banyak menu", "macam", "jenis", "lengkap", "terbatas", "sedikit"],
    "Waktu Tunggu": ["antri", "antre", "lama", "tunggu", "queue", "booking", "reservasi", "penuh", "ramai"],
}

# --- FUNGSI PEMBERSIH TEKS (Untuk SVM) ---
def bersihkan_teks(teks):
    teks = str(teks).lower() 
    teks = re.sub(r'http\S+', '', teks) 
    teks = re.sub(r'[^a-z\s]', '', teks) 
    teks = re.sub(r'\s+', ' ', teks).strip() 
    return teks

# --- 3. FUNGSI ANALISIS SENTIMEN (FAST-SVM) ---
def analyze_sentiment(ulasan_list):
    aspek_list = ["Kualitas Makanan", "Pelayanan", "Kebersihan", "Harga", "Variasi Menu", "Waktu Tunggu"]
    raw_scores = {k: {"pos": 0, "neu": 0, "neg": 0} for k in aspek_list}
    
    for teks in ulasan_list[:100]:
        try:
            teks_bersih = bersihkan_teks(teks)
            if not teks_bersih:
                continue
                            
            teks_vektor = vectorizer.transform([teks_bersih])
            sentiment = model_svm.predict(teks_vektor)[0]
            
            teks_lower = teks.lower()
            matched_aspects = [
                asp for asp, keywords in ASPECT_KEYWORDS.items()
                if any(kw in teks_lower for kw in keywords)
            ]
            if not matched_aspects:
                matched_aspects = aspek_list
                
            for asp in matched_aspects:
                raw_scores[asp][sentiment] += 1
                
        except Exception as e:
            print(f"Sentiment Error: {e}")
            
    return raw_scores

# --- 4. FUNGSI REKOMENDASI DENGAN FALLBACK ---
def get_advanced_insights(ulasan_list):
    gabungan_ulasan = " | ".join(ulasan_list[:50])
    
    prompt = f"""
    Kamu adalah Konsultan Operasional Restoran. Tugasmu adalah membaca ulasan pelanggan berikut dan memberikan saran perbaikan kepada PEMILIK / MANAJEMEN restoran.
    
    Ulasan Pelanggan:
    {gabungan_ulasan}
    
    ATURAN MUTLAK:
    1. Bagian "rekomendasi" HARUS ditujukan kepada MANAJEMEN restoran. 
    2. DILARANG KERAS memberikan rekomendasi bergaya promosi untuk pelanggan.
    3. Batasi maksimal 30 kata kunci per kategori, dan maksimal 5 rekomendasi aksi.
    
    Kamu WAJIB mengembalikan respon HANYA dalam format JSON murni ini:
    {{
      "kata_kunci_positif": ["kata1", "kata2"],
      "kata_kunci_negatif": ["kata1", "kata2"],
      "rekomendasi": [
        {{"judul": "Tindakan Manajerial", "deskripsi": "Deskripsi tindakan untuk staf/manajemen", "prioritas": "High/Medium/Low"}}
      ]
    }}
    """
    
    #PERCOBAAN 1: MENGGUNAKAN GROQ (Llama 3.1)
    try:
        print("Mencoba Groq API...")
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.1-8b-instant", 
            "messages": [
                {"role": "system", "content": "You are a strict restaurant business consultant advising the management. Always output valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}, 
            "temperature": 0.4,
            "max_tokens": 2048
        }
        
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            t = data["choices"][0]["message"]["content"]
            return json.loads(t)
        else:
            print(f"Groq Gagal ({response.status_code}). Beralih ke Gemini...")
            raise Exception("Groq Timeout/Error")
            
    except Exception as e:
        #PERCOBAAN 2 (FALLBACK): MENGGUNAKAN GEMINI (Google GenAI SDK)
        print(f"Groq Error ({e}), Menjalankan Fallback Gemini via SDK...")
        if not GEMINI_API_KEY:
            return fallback_response()
            
        try:
            # Menggunakan format baru dari Google GenAI SDK
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            gemini_response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=f"System: You are a strict restaurant business consultant advising the management. Always output valid JSON.\n\nUser: {prompt}"
            )
            
            # Bersihkan teks kalau seandainya AI membalas pakai format markdown (```json ... ```)
            bersih = gemini_response.text.strip()
            if bersih.startswith("```json"):
                bersih = bersih[7:-3].strip()
            elif bersih.startswith("```"):
                bersih = bersih[3:-3].strip()
                
            return json.loads(bersih)
                
        except Exception as gemini_e:
            print(f"Gemini Error: {gemini_e}")
            return fallback_response()

def fallback_response():
    return {
        "kata_kunci_positif": ["Sistem Antre"], 
        "kata_kunci_negatif": ["Server Sibuk"], 
        "rekomendasi": [{"judul": "Sistem Sedang Sibuk", "deskripsi": "AI Rekomendasi sedang mengalami antrean (Groq & Gemini down). Silakan evaluasi data sentimen di atas secara manual sementara waktu.", "prioritas": "Low"}]
    }

# --- 5. ENDPOINT ---
@app.post("/analyze")
async def analyze_realtime(request: Request):
    try:
        body = await request.json()
        target_url = body.get("url")
        
        run = apify_client.actor("compass/google-maps-reviews-scraper").call(
            run_input={"startUrls": [{"url": target_url}], "maxReviews": 150, "language": "id"}
        )
        
        ulasan_lengkap = []
        ulasan_teks_saja = []
        for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
            if item.get("text"):
                ulasan_teks_saja.append(item["text"])
                ulasan_lengkap.append({
                    "nama": item.get("name", "Anonim"),
                    "rating": item.get("stars", 5),
                    "teks": item["text"]
                })
        if not ulasan_teks_saja:
            return {"status": "error", "message": "Ulasan tidak ditemukan."}

        raw_scores = analyze_sentiment(ulasan_teks_saja)
        insights_data = get_advanced_insights(ulasan_teks_saja) 
        
        sentiment_results = []
        tp = tn = tneu = 0
        for name, counts in raw_scores.items():
            total = counts["pos"] + counts["neu"] + counts["neg"]
            tp += counts["pos"]; tn += counts["neg"]; tneu += counts["neu"]
            
            p = round((counts["pos"]/total)*100) if total > 0 else 0
            n = round((counts["neg"]/total)*100) if total > 0 else 0
            neu = 100 - p - n if total > 0 else 100
            sentiment_results.append({"name": name, "positive": p, "neutral": neu, "negative": n})

        grand = tp + tn + tneu
        if grand == 0:
            over_p, over_neu, over_n = 0, 100, 0
        else:
            over_p = round((tp/grand)*100, 1); over_n = round((tn/grand)*100, 1)
            over_neu = round(100 - over_p - over_n, 1)

        return {
            "status": "success",
            "analysis": {
                "overall_sentiment": {"positive": over_p, "neutral": over_neu, "negative": over_n},
                "sentiment_score": sentiment_results,
                "kata_kunci": {
                    "positif": insights_data.get("kata_kunci_positif", []),
                    "negatif": insights_data.get("kata_kunci_negatif", [])
                },
                "contoh_review": ulasan_lengkap[:6], 
                "rekomendasi_list": insights_data.get("rekomendasi", [])
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}