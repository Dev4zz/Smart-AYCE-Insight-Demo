# 🍱 Smart-AYCE Optimizer

**Smart-AYCE Optimizer** adalah sistem *Pipeline Machine Learning End-to-End* untuk menganalisis ulasan pelanggan restoran *All-You-Can-Eat* (AYCE) di Google Maps. Sistem ini memadukan model **Fast-SVM (LinearSVC)** lokal untuk klasifikasi sentimen dan *Dual-AI Fallback* (**Groq Llama 3.1 & Google Gemini 3.5 Flash**) untuk merumuskan rekomendasi perbaikan kualitas layanan secara otomatis.

---

## 🛠️ Prasyarat Sistem
Sebelum mengeksekusi proyek ini, pastikan komputer Anda telah menginstal:
1. **[Git](https://git-scm.com/downloads)** (Untuk mengunduh repositori).
2. **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (Wajib dibuka dan dalam status *Running* sebelum mulai).
3. **[Node.js](https://nodejs.org/)** (Untuk menjalankan antarmuka web).

---

## 🚀 Panduan Instalasi (Step-by-Step)

### Langkah 1: Persiapan API Key
Sistem ini membutuhkan otorisasi eksternal. Siapkan 3 API Key berikut:
* **`APIFY_TOKEN`**: Untuk agen *scraper* ulasan Google Maps.
* **`GROQ_API_KEY`**: Untuk LLM utama (Llama 3.1).
* **`GEMINI_API_KEY`**: Untuk LLM cadangan otomatis jika server Groq penuh.

### Langkah 2: Eksekusi Otomatis (Cukup 1x Copy-Paste)
Salin blok kode di bawah ini ke Notepad terlebih dahulu, lalu **ganti tulisan `"ISI_KEY_ASLI_KAMU"`** dengan API Key milik Anda. 

Setelah itu, *copy* dan *paste* seluruh kode tersebut ke dalam **Command Prompt (CMD)** lalu tekan **Enter**. Sistem akan otomatis mengunduh proyek, membangun kontainer AI, dan menyalakan *website* secara berurutan.

```cmd
git clone https://github.com/Dev4zz/Smart-AYCE-Insight-Demo.git
cd Smart-AYCE-Insight-Demo\Backend
docker build -t smart-ayce-backend .
docker run -d -p 8000:8000 --name smart-ayce-api -e GROQ_API_KEY="ISI_KEY_ASLI_KAMU" -e GEMINI_API_KEY="ISI_KEY_ASLI_KAMU" -e APIFY_TOKEN="ISI_KEY_ASLI_KAMU" smart-ayce-backend
cd ..\Frontend
npm install
npm run dev
