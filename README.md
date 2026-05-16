[README.md](https://github.com/user-attachments/files/27840390/README.md)
# 🔬 Analisis Saringan Web App
**Developer: KAKUKA 2026 — Toro-Praba**

## Cara Menjalankan

### 1. Install dependensi
```bash
pip install flask reportlab
```

### 2. Jalankan server
```bash
python app.py
```

### 3. Buka browser
```
http://localhost:5050
```

---

## Struktur File
```
├── app.py              ← Server Flask + logika PDF
└── templates/
    └── index.html      ← Tampilan web form
```

## Fitur
- ✅ Form lengkap sesuai dokumen asli (11 seksi)
- ✅ Kalkulasi otomatis: Ww, kadar air, % tertahan, kumulatif, % lolos, Cu, Cc
- ✅ Auto-hitung Wi dari berat saringan kosong & berat saringan+tanah
- ✅ Cetak PDF profesional dengan nama developer KAKUKA 2026 Toro-Praba
- ✅ Reset form
- ✅ Validasi data

## Persyaratan
- Python 3.8+
- Flask
- ReportLab
