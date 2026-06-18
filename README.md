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

### Langkah 1: Dapatkan API Key
Sistem ini membutuhkan otorisasi untuk menarik data ulasan dan menjalankan AI. Silakan dapatkan API Key Anda melalui tautan resmi berikut:
* **`APIFY_TOKEN`**: [Apify Console](https://console.apify.com/) *(Untuk agen scraper ulasan Google Maps)*
* **`GROQ_API_KEY`**: [Groq Cloud Console](https://console.groq.com/keys) *(Untuk LLM utama - Llama 3.1)*
* **`GEMINI_API_KEY`**: [Google AI Studio](https://aistudio.google.com/api-keys) *(Untuk LLM cadangan otomatis)*

### Langkah 2: Eksekusi Otomatis (Cukup 1x Copy-Paste)
Salin blok kode di bawah ini ke Notepad terlebih dahulu, lalu **ganti tulisan `"ISI_KEY_ASLI_KAMU"`** dengan API Key milik Anda. 

> **📝 NOTE PENTING:** 
> **Jangan langsung *paste* kode di bawah ini ke CMD!** 
> 1. *Copy* kode di bawah ini dan *paste* ke aplikasi **Notepad** (atau *text editor* lainnya) terlebih dahulu.
> 2. Ganti teks `"ISI_KEY_ASLI_KAMU"` dengan ketiga API Key yang sudah Anda dapatkan pada Langkah 1.
> 3. Jika sudah diubah, *copy* ulang seluruh baris tersebut dari Notepad.
> 4. Buka **Command Prompt (CMD)**, *paste* kodenya, lalu tekan **Enter**.

```cmd
git clone https://github.com/Dev4zz/Smart-AYCE-Insight-Demo.git
cd Smart-AYCE-Insight-Demo\Backend
docker build -t smart-ayce-backend .
docker run -d -p 8000:8000 --name smart-ayce-api -e GROQ_API_KEY="ISI_KEY_ASLI_KAMU" -e GEMINI_API_KEY="ISI_KEY_ASLI_KAMU" -e APIFY_TOKEN="ISI_KEY_ASLI_KAMU" smart-ayce-backend
cd ..\Frontend
npm install
npm run dev
