# Gunakan Python 3.10 sebagai basis
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements dan install library
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode aplikasi
COPY . .

# PERBAIKAN: Hapus ".py" dari nama modul
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]