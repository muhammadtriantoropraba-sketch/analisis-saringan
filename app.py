from flask import Flask, render_template, request, send_file, jsonify
import io
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph,
                                 Spacer, HRFlowable, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import Flowable
import math

app = Flask(__name__)

SIEVE_DATA = [
    {"no": 1,  "nomor": '3"',      "ukuran": "75,0"},
    {"no": 2,  "nomor": '2"',      "ukuran": "50,0"},
    {"no": 3,  "nomor": '1 1/2"',  "ukuran": "37,5"},
    {"no": 4,  "nomor": '1"',      "ukuran": "25,0"},
    {"no": 5,  "nomor": '3/4"',    "ukuran": "19,0"},
    {"no": 6,  "nomor": '1/2"',    "ukuran": "12,5"},
    {"no": 7,  "nomor": '3/8"',    "ukuran": "9,5"},
    {"no": 8,  "nomor": "No. 4",   "ukuran": "4,75"},
    {"no": 9,  "nomor": "No. 10",  "ukuran": "2,00"},
    {"no": 10, "nomor": "No. 20",  "ukuran": "0,850"},
    {"no": 11, "nomor": "No. 40",  "ukuran": "0,425"},
    {"no": 12, "nomor": "No. 60",  "ukuran": "0,250"},
    {"no": 13, "nomor": "No. 100", "ukuran": "0,150"},
    {"no": 14, "nomor": "No. 200", "ukuran": "0,075"},
    {"no": 15, "nomor": "Pan",     "ukuran": "< 0,075"},
]

@app.route("/")
def index():
    return render_template("index.html", sieve_data=SIEVE_DATA)

@app.route("/cetak_pdf", methods=["POST"])
def cetak_pdf():
    data = request.get_json()
    pdf_buffer = generate_pdf(data)
    pdf_buffer.seek(0)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nama = data.get("identitas", {}).get("nama_praktikan", "sampel").replace(" ", "_")
    filename = f"analisis_saringan_{nama}_{timestamp}.pdf"
    return send_file(pdf_buffer, mimetype="application/pdf",
                     as_attachment=True, download_name=filename)

def safe_float(val, default=0.0):
    try:
        return float(str(val).replace(",", ".").strip())
    except:
        return default

def generate_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=20*mm,
        title="Analisis Saringan - KAKUKA 2026",
        author="KAKUKA 2026 Toro-Praba"
    )

    # ── Colours ────────────────────────────────────────────────────────────────
    C_PRIMARY   = colors.HexColor("#1a3a5c")   # dark navy
    C_SECONDARY = colors.HexColor("#2e6da4")   # medium blue
    C_ACCENT    = colors.HexColor("#e8f0fa")   # very light blue bg
    C_HEADER    = colors.HexColor("#d0e4f7")   # table header bg
    C_ALT       = colors.HexColor("#f5f9ff")   # alternating row
    C_WHITE     = colors.white
    C_BORDER    = colors.HexColor("#9ab8d8")   # border colour
    C_GOLD      = colors.HexColor("#c8a415")   # accent gold
    C_TEXT      = colors.HexColor("#1a1a2e")   # body text

    # ── Styles ─────────────────────────────────────────────────────────────────
    styles = getSampleStyleSheet()
    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    sTitle  = S("sTitle",  fontSize=16, leading=20, alignment=TA_CENTER,
                fontName="Helvetica-Bold", textColor=C_PRIMARY, spaceAfter=2)
    sSub    = S("sSub",    fontSize=10, leading=13, alignment=TA_CENTER,
                fontName="Helvetica", textColor=C_SECONDARY, spaceAfter=1)
    sSmall  = S("sSmall",  fontSize=7.5, leading=10, alignment=TA_CENTER,
                fontName="Helvetica-Oblique", textColor=colors.HexColor("#555555"))
    sSec    = S("sSec",    fontSize=9.5, leading=12, fontName="Helvetica-Bold",
                textColor=C_WHITE, spaceBefore=6, spaceAfter=2)
    sCell   = S("sCell",  fontSize=8, leading=10, fontName="Helvetica",
                textColor=C_TEXT)
    sCellB  = S("sCellB", fontSize=8, leading=10, fontName="Helvetica-Bold",
                textColor=C_TEXT)
    sCellC  = S("sCellC", fontSize=8, leading=10, fontName="Helvetica",
                textColor=C_TEXT, alignment=TA_CENTER)
    sNote   = S("sNote",  fontSize=7.5, leading=10, fontName="Helvetica-Oblique",
                textColor=colors.HexColor("#444444"), spaceBefore=2)
    sDev    = S("sDev",   fontSize=7, leading=9, fontName="Helvetica",
                textColor=colors.HexColor("#888888"), alignment=TA_CENTER)

    story = []
    W = A4[0] - 30*mm   # usable width

    # ═══════════════════════════════════════════════════════════════════════════
    # HEADER BANNER
    # ═══════════════════════════════════════════════════════════════════════════
    banner_data = [[
        Paragraph("LEMBAR PENDATAAN PRAKTIKUM", S("bT", fontSize=13, leading=16,
                   alignment=TA_CENTER, fontName="Helvetica-Bold", textColor=C_WHITE)),
        Paragraph("ANALISIS UJI SARINGAN / SIEVE ANALYSIS", S("bS", fontSize=10, leading=13,
                   alignment=TA_CENTER, fontName="Helvetica", textColor=colors.HexColor("#cde2f7"))),
        Paragraph("Digunakan untuk mencatat data lapangan/laboratorium dan<br/>perhitungan distribusi ukuran butiran tanah.", S("bD", fontSize=7.5, leading=10,
                   alignment=TA_CENTER, fontName="Helvetica-Oblique", textColor=colors.HexColor("#b8d4ee"))),
    ]]
    banner_style = TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), C_PRIMARY),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("LINEBELOW",     (0,-1),(-1,-1), 3, C_GOLD),
    ])
    banner = Table([[r] for r in banner_data[0]], colWidths=[W])
    banner.setStyle(banner_style)
    story.append(banner)
    story.append(Spacer(1, 4*mm))

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION HELPER
    # ═══════════════════════════════════════════════════════════════════════════
    def section_header(title):
        t = Table([[Paragraph(title, sSec)]], colWidths=[W])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), C_PRIMARY),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 5),
            ("LEFTPADDING",   (0,0),(-1,-1), 8),
            ("RIGHTPADDING",  (0,0),(-1,-1), 8),
            ("LINEBELOW",     (0,0),(-1,-1), 1.5, C_GOLD),
        ]))
        return t

    def std_table(rows, col_widths, header_rows=1, alt_start=1):
        t = Table(rows, colWidths=col_widths, repeatRows=header_rows)
        cmds = [
            ("FONTNAME",      (0,0), (-1,-1), "Helvetica"),
            ("FONTSIZE",      (0,0), (-1,-1), 8),
            ("LEADING",       (0,0), (-1,-1), 10),
            ("TOPPADDING",    (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("LEFTPADDING",   (0,0), (-1,-1), 5),
            ("RIGHTPADDING",  (0,0), (-1,-1), 5),
            ("GRID",          (0,0), (-1,-1), 0.4, C_BORDER),
            ("BACKGROUND",    (0,0), (-1,header_rows-1), C_HEADER),
            ("FONTNAME",      (0,0), (-1,header_rows-1), "Helvetica-Bold"),
            ("ALIGN",         (0,0), (-1,header_rows-1), "CENTER"),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ]
        for i in range(alt_start, len(rows), 2):
            cmds.append(("BACKGROUND", (0,i), (-1,i), C_ALT))
        t.setStyle(TableStyle(cmds))
        return t

    def v(path, default=""):
        """Safely get nested dict value."""
        parts = path.split(".")
        cur = data
        for p in parts:
            if isinstance(cur, dict):
                cur = cur.get(p, default)
            else:
                return default
        return cur if cur not in (None, "") else default

    # ═══════════════════════════════════════════════════════════════════════════
    # 1. IDENTITAS PRAKTIKUM
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(section_header("1. IDENTITAS PRAKTIKUM"))
    ident = data.get("identitas", {})
    irows = [
        [Paragraph("Nama Praktikan", sCellB), Paragraph(ident.get("nama_praktikan",""), sCell),
         Paragraph("Kelompok / Kelas", sCellB), Paragraph(ident.get("kelompok_kelas",""), sCell)],
        [Paragraph("Asisten / Dosen", sCellB), Paragraph(ident.get("asisten_dosen",""), sCell),
         Paragraph("Tanggal Uji", sCellB), Paragraph(ident.get("tanggal_uji",""), sCell)],
        [Paragraph("Lokasi Pengambilan Sampel", sCellB), Paragraph(ident.get("lokasi",""), sCell),
         Paragraph("Cuaca / Kondisi Lokasi", sCellB), Paragraph(ident.get("cuaca",""), sCell)],
        [Paragraph("Kode Sampel", sCellB), Paragraph(ident.get("kode_sampel",""), sCell),
         Paragraph("Titik / Bor / STA", sCellB), Paragraph(ident.get("titik_bor",""), sCell)],
        [Paragraph("Kedalaman Sampel", sCellB), Paragraph(ident.get("kedalaman",""), sCell),
         Paragraph("Jenis Sampel", sCellB), Paragraph(ident.get("jenis_sampel",""), sCell)],
        [Paragraph("Metode Pengeringan", sCellB), Paragraph(ident.get("metode_pengeringan",""), sCell),
         Paragraph("Kondisi Sampel", sCellB), Paragraph(ident.get("kondisi_sampel",""), sCell)],
    ]
    cw = [W*0.22, W*0.28, W*0.22, W*0.28]
    it = Table(irows, colWidths=cw)
    it.setStyle(TableStyle([
        ("FONTNAME",      (0,0),(-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0),(-1,-1), 8),
        ("LEADING",       (0,0),(-1,-1), 10),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ("RIGHTPADDING",  (0,0),(-1,-1), 5),
        ("GRID",          (0,0),(-1,-1), 0.4, C_BORDER),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("BACKGROUND",    (0,0),(0,-1), C_ACCENT),
        ("BACKGROUND",    (2,0),(2,-1), C_ACCENT),
    ]))
    story.append(it)
    story.append(Spacer(1, 3*mm))

    # ═══════════════════════════════════════════════════════════════════════════
    # 2. CHECKLIST PERALATAN
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(section_header("2. CHECKLIST PERALATAN DAN BAHAN"))
    peralatan_list = [
        "Satu set saringan standar", "Pan dan tutup saringan", "Timbangan digital",
        "Oven pengering", "Kuas pembersih saringan", "Shaker/alat penggetar saringan",
        "Cawan/wadah sampel", "Tanah sampel kering", "Label sampel dan alat tulis"
    ]
    peralatan_data = data.get("peralatan", [{}]*9)
    ph = [Paragraph(t, sCellB) for t in ["No.", "Peralatan / Bahan", "Kondisi", "Jumlah", "Catatan"]]
    prows = [ph]
    for i, nama in enumerate(peralatan_list):
        pd_i = peralatan_data[i] if i < len(peralatan_data) else {}
        prows.append([
            Paragraph(str(i+1), sCellC),
            Paragraph(nama, sCell),
            Paragraph(pd_i.get("kondisi",""), sCellC),
            Paragraph(pd_i.get("jumlah",""), sCellC),
            Paragraph(pd_i.get("catatan",""), sCell),
        ])
    pt = std_table(prows, [W*0.06, W*0.38, W*0.16, W*0.12, W*0.28])
    story.append(pt)
    story.append(Spacer(1, 3*mm))

    # ═══════════════════════════════════════════════════════════════════════════
    # 3. DATA AWAL SAMPEL
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(section_header("3. DATA AWAL SAMPEL"))
    da = data.get("data_awal", {})
    dah = [Paragraph(t, sCellB) for t in ["No.", "Parameter", "Simbol", "Satuan", "Nilai"]]
    darows = [dah,
        [Paragraph("1",sCellC), Paragraph("Berat wadah kosong",sCell),
         Paragraph("Wc",sCellC), Paragraph("gram",sCellC), Paragraph(da.get("wc",""),sCellC)],
        [Paragraph("2",sCellC), Paragraph("Berat wadah + tanah basah",sCell),
         Paragraph("Wc+w",sCellC), Paragraph("gram",sCellC), Paragraph(da.get("wcw",""),sCellC)],
        [Paragraph("3",sCellC), Paragraph("Berat tanah basah  (Ww = Wc+w − Wc)",sCell),
         Paragraph("Ww",sCellC), Paragraph("gram",sCellC), Paragraph(da.get("ww",""),sCellC)],
        [Paragraph("4",sCellC), Paragraph("Berat wadah + tanah kering",sCell),
         Paragraph("Wc+d",sCellC), Paragraph("gram",sCellC), Paragraph(da.get("wcd",""),sCellC)],
        [Paragraph("5",sCellC), Paragraph("Berat tanah kering total sebelum disaring",sCell),
         Paragraph("Wd",sCellC), Paragraph("gram",sCellC), Paragraph(da.get("wd",""),sCellC)],
        [Paragraph("6",sCellC), Paragraph("Berat tanah kering untuk analisis saringan",sCell),
         Paragraph("Wtotal",sCellC), Paragraph("gram",sCellC), Paragraph(da.get("wtotal",""),sCellC)],
        [Paragraph("7",sCellC), Paragraph("Kadar air awal  w = (Ww − Wd)/Wd × 100%",sCell),
         Paragraph("w",sCellC), Paragraph("%",sCellC), Paragraph(da.get("kadar_air",""),sCellC)],
    ]
    dat = std_table(darows, [W*0.06, W*0.46, W*0.13, W*0.13, W*0.22])
    story.append(dat)
    story.append(Paragraph(
        "Catatan: gunakan satuan gram secara konsisten. Pastikan Wtotal sama dengan jumlah berat "
        "tertahan pada seluruh saringan + pan, dengan selisih massa sekecil mungkin.", sNote))
    story.append(Spacer(1, 3*mm))

    # ═══════════════════════════════════════════════════════════════════════════
    # 5. TABEL DATA UTAMA
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(section_header("5. TABEL DATA UTAMA ANALISIS SARINGAN"))
    sieve_rows_data = data.get("saringan", [{}]*15)
    wtotal = safe_float(da.get("wtotal", 0))

    # Compute cumulative
    def to_num(s):
        return safe_float(s)

    computed = []
    cum = 0.0
    for i, sd in enumerate(SIEVE_DATA):
        rd = sieve_rows_data[i] if i < len(sieve_rows_data) else {}
        wi = to_num(rd.get("berat_tertahan",""))
        pct = (wi / wtotal * 100) if wtotal > 0 else 0
        cum += pct
        lolos = max(0, 100 - cum)
        computed.append({
            "berat_saringan_kosong": rd.get("berat_saringan_kosong",""),
            "berat_saringan_tanah": rd.get("berat_saringan_tanah",""),
            "berat_tertahan": rd.get("berat_tertahan",""),
            "pct_tertahan": f"{pct:.2f}" if pct else "",
            "pct_kum": f"{cum:.2f}" if pct or cum else "",
            "pct_lolos": f"{lolos:.2f}" if wtotal > 0 else "",
            "keterangan": rd.get("keterangan",""),
        })

    mh = [Paragraph(t, sCellB) for t in [
        "No.", "Nomor\nSaringan", "Ukuran\n(mm)",
        "Berat Saringan\nKosong (g)", "Berat Saringan\n+ Tanah (g)",
        "Berat\nTertahan Wi(g)", "% Tertahan", "% Tertahan\nKumulatif", "% Lolos", "Keterangan"
    ]]
    mrows = [mh]
    for i, sd in enumerate(SIEVE_DATA):
        c = computed[i]
        mrows.append([
            Paragraph(str(sd["no"]),   sCellC),
            Paragraph(sd["nomor"],     sCellC),
            Paragraph(sd["ukuran"],    sCellC),
            Paragraph(c["berat_saringan_kosong"], sCellC),
            Paragraph(c["berat_saringan_tanah"],  sCellC),
            Paragraph(c["berat_tertahan"],         sCellC),
            Paragraph(c["pct_tertahan"],           sCellC),
            Paragraph(c["pct_kum"],               sCellC),
            Paragraph(c["pct_lolos"],             sCellC),
            Paragraph(c["keterangan"],             sCell),
        ])
    # Total row
    total_wi = sum(to_num(sieve_rows_data[i].get("berat_tertahan","") if i < len(sieve_rows_data) else "") for i in range(15))
    mrows.append([
        Paragraph("",sCellC), Paragraph("TOTAL",sCellB),
        Paragraph("",sCellC),
        Paragraph("",sCellC), Paragraph("",sCellC),
        Paragraph(f"{total_wi:.2f}" if total_wi else "", sCellC),
        Paragraph("100%", sCellB), Paragraph("",sCellC), Paragraph("",sCellC), Paragraph("",sCellC)
    ])
    cws = [W*0.04, W*0.08, W*0.08, W*0.10, W*0.10, W*0.10, W*0.08, W*0.10, W*0.08, W*0.24]
    mt = std_table(mrows, cws)
    # Style total row
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0, len(mrows)-1), (-1, len(mrows)-1), C_HEADER),
        ("FONTNAME",   (0, len(mrows)-1), (-1, len(mrows)-1), "Helvetica-Bold"),
    ]))
    story.append(mt)
    story.append(Paragraph(
        "Rumus: % tertahan = Wi/Wtotal × 100%;  % tertahan kumulatif = jumlah % tertahan dari "
        "saringan teratas;  % lolos = 100% − % tertahan kumulatif.", sNote))
    story.append(Spacer(1, 3*mm))

    # ═══════════════════════════════════════════════════════════════════════════
    # 6. KONTROL KEHILANGAN MASSA
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(section_header("6. KONTROL KEHILANGAN MASSA"))
    selisih = wtotal - total_wi if wtotal > 0 else 0
    pct_hilang = (selisih / wtotal * 100) if wtotal > 0 else 0
    kh = [Paragraph(t, sCellB) for t in ["Parameter", "Simbol / Rumus", "Satuan", "Nilai", "Keterangan"]]
    khrows = [kh,
        [Paragraph("Berat tanah kering awal",sCell), Paragraph("Wtotal",sCellC),
         Paragraph("g",sCellC), Paragraph(f"{wtotal:.2f}" if wtotal else "",sCellC), Paragraph("",sCell)],
        [Paragraph("Jumlah berat tertahan seluruh saringan + pan",sCell), Paragraph("ΣWi",sCellC),
         Paragraph("g",sCellC), Paragraph(f"{total_wi:.2f}" if total_wi else "",sCellC), Paragraph("",sCell)],
        [Paragraph("Selisih massa",sCell), Paragraph("Wtotal − ΣWi",sCellC),
         Paragraph("g",sCellC), Paragraph(f"{selisih:.2f}" if wtotal else "",sCellC), Paragraph("",sCell)],
        [Paragraph("Persentase kehilangan massa",sCell),
         Paragraph("(Wtotal − ΣWi)/Wtotal × 100%",sCellC),
         Paragraph("%",sCellC), Paragraph(f"{pct_hilang:.2f}" if wtotal else "",sCellC),
         Paragraph("Semakin kecil semakin baik",sCell)],
    ]
    kht = std_table(khrows, [W*0.36, W*0.28, W*0.08, W*0.12, W*0.16])
    story.append(kht)
    story.append(Spacer(1, 3*mm))

    # ═══════════════════════════════════════════════════════════════════════════
    # 7. REKAP FRAKSI TANAH
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(section_header("7. REKAP FRAKSI TANAH"))
    fraksi = data.get("fraksi", {})
    fh = [Paragraph(t, sCellB) for t in ["Fraksi Tanah", "Batas Umum", "Rumus dari Data Saringan", "Persentase (%)", "Keterangan"]]
    frows = [fh,
        [Paragraph("Kerikil / Gravel",sCell), Paragraph("> 4,75 mm",sCellC),
         Paragraph("Tertahan kumulatif pada No. 4",sCell),
         Paragraph(fraksi.get("kerikil",""),sCellC), Paragraph(fraksi.get("ket_kerikil",""),sCell)],
        [Paragraph("Pasir / Sand",sCell), Paragraph("4,75 mm − 0,075 mm",sCellC),
         Paragraph("% lolos No. 4 − % lolos No. 200",sCell),
         Paragraph(fraksi.get("pasir",""),sCellC), Paragraph(fraksi.get("ket_pasir",""),sCell)],
        [Paragraph("Lanau + Lempung / Fines",sCell), Paragraph("< 0,075 mm",sCellC),
         Paragraph("% lolos No. 200",sCell),
         Paragraph(fraksi.get("lanau",""),sCellC), Paragraph(fraksi.get("ket_lanau",""),sCell)],
    ]
    ft = std_table(frows, [W*0.20, W*0.18, W*0.30, W*0.14, W*0.18])
    story.append(ft)
    story.append(Spacer(1, 3*mm))

    # ═══════════════════════════════════════════════════════════════════════════
    # 8. DATA GRAFIK DISTRIBUSI
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(section_header("8. DATA GRAFIK DISTRIBUSI UKURAN BUTIRAN"))
    grafik = data.get("grafik", {})
    gh = [Paragraph(t, sCellB) for t in ["Parameter", "Definisi / Rumus", "Satuan", "Nilai"]]
    grows = [gh,
        [Paragraph("D10",sCellC), Paragraph("Diameter pada 10% lolos",sCell), Paragraph("mm",sCellC), Paragraph(grafik.get("d10",""),sCellC)],
        [Paragraph("D30",sCellC), Paragraph("Diameter pada 30% lolos",sCell), Paragraph("mm",sCellC), Paragraph(grafik.get("d30",""),sCellC)],
        [Paragraph("D50",sCellC), Paragraph("Diameter pada 50% lolos",sCell), Paragraph("mm",sCellC), Paragraph(grafik.get("d50",""),sCellC)],
        [Paragraph("D60",sCellC), Paragraph("Diameter pada 60% lolos",sCell), Paragraph("mm",sCellC), Paragraph(grafik.get("d60",""),sCellC)],
        [Paragraph("Cu",sCellC), Paragraph("D60 / D10",sCell), Paragraph("—",sCellC), Paragraph(grafik.get("cu",""),sCellC)],
        [Paragraph("Cc",sCellC), Paragraph("(D30)² / (D10 × D60)",sCell), Paragraph("—",sCellC), Paragraph(grafik.get("cc",""),sCellC)],
    ]
    gt = std_table(grows, [W*0.12, W*0.48, W*0.12, W*0.28])
    story.append(gt)
    story.append(Spacer(1, 3*mm))

    # ═══════════════════════════════════════════════════════════════════════════
    # 9. KLASIFIKASI DAN KESIMPULAN
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(section_header("9. KLASIFIKASI DAN KESIMPULAN SEMENTARA"))
    kes = data.get("kesimpulan", {})
    krows = [
        [Paragraph("Jenis tanah dominan", sCellB), Paragraph(kes.get("jenis_tanah",""), sCell)],
        [Paragraph("Persentase lolos No. 200", sCellB), Paragraph(kes.get("lolos_no200",""), sCell)],
        [Paragraph("Gradasi tanah", sCellB), Paragraph(kes.get("gradasi",""), sCell)],
        [Paragraph("Klasifikasi awal USCS/AASHTO", sCellB), Paragraph(kes.get("klasifikasi",""), sCell)],
        [Paragraph("Keterangan visual tanah", sCellB), Paragraph(kes.get("keterangan_visual",""), sCell)],
        [Paragraph("Catatan khusus saat pengujian", sCellB), Paragraph(kes.get("catatan_khusus",""), sCell)],
    ]
    kt = Table(krows, colWidths=[W*0.30, W*0.70])
    kt.setStyle(TableStyle([
        ("FONTNAME",      (0,0),(-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0),(-1,-1), 8),
        ("LEADING",       (0,0),(-1,-1), 11),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ("RIGHTPADDING",  (0,0),(-1,-1), 5),
        ("GRID",          (0,0),(-1,-1), 0.4, C_BORDER),
        ("BACKGROUND",    (0,0),(0,-1), C_ACCENT),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        *[("BACKGROUND",  (0,i),(-1,i), C_ALT) for i in range(0, len(krows), 2)],
    ]))
    story.append(kt)
    story.append(Paragraph(
        "Pengingat: pasir well graded bila Cu ≥ 6 dan 1 ≤ Cc ≤ 3; kerikil well graded bila "
        "Cu ≥ 4 dan 1 ≤ Cc ≤ 3. Sesuaikan dengan instruksi modul praktikum.", sNote))
    story.append(Spacer(1, 3*mm))

    # ═══════════════════════════════════════════════════════════════════════════
    # 10. CATATAN PENGAMATAN
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(section_header("10. CATATAN PENGAMATAN"))
    catatan = data.get("catatan_pengamatan", "")
    ct = Table([[Paragraph(catatan if catatan else " ", sCell)]], colWidths=[W])
    ct.setStyle(TableStyle([
        ("BOX",           (0,0),(-1,-1), 0.5, C_BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 50),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ("BACKGROUND",    (0,0),(-1,-1), C_ALT),
    ]))
    story.append(ct)
    story.append(Spacer(1, 3*mm))

    # ═══════════════════════════════════════════════════════════════════════════
    # 11. VALIDASI DATA
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(section_header("11. VALIDASI DATA"))
    val = data.get("validasi", [{}]*3)
    vh = [Paragraph(t, sCellB) for t in ["Praktikan", "Asisten / Dosen", "Tanggal Pemeriksaan"]]
    vrows = [vh]
    for i in range(3):
        vi = val[i] if i < len(val) else {}
        vrows.append([
            Paragraph(vi.get("praktikan",""), sCell),
            Paragraph(vi.get("asisten",""), sCell),
            Paragraph(vi.get("tanggal",""), sCellC),
        ])
    vt = std_table(vrows, [W/3, W/3, W/3])
    story.append(vt)
    story.append(Spacer(1, 4*mm))

    # ── Footer info ────────────────────────────────────────────────────────────
    nama_kelompok = ident.get("kelompok_kelas","____________________")
    tanggal_cetak = datetime.now().strftime("%d/%m/%Y")
    footer_text = (f"Nama Kelompok: {nama_kelompok}    |    "
                   f"Tanggal Cetak: {tanggal_cetak}    |    Halaman: 1")
    story.append(HRFlowable(width=W, thickness=1, color=C_SECONDARY))
    story.append(Spacer(1, 2*mm))

    ft_row = Table([[
        Paragraph(footer_text, S("ft", fontSize=7.5, fontName="Helvetica", textColor=C_SECONDARY)),
        Paragraph("KAKUKA 2026 | Toro-Praba", S("ftR", fontSize=7.5, fontName="Helvetica-Bold",
                   textColor=C_PRIMARY, alignment=TA_RIGHT)),
    ]], colWidths=[W*0.6, W*0.4])
    ft_row.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0)]))
    story.append(ft_row)
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "© 2026 KAKUKA — Developer: Toro-Praba  |  Sistem Pendataan Praktikum Analisis Saringan",
        sDev))

    doc.build(story)
    return buffer


if __name__ == "__main__":
    app.run(debug=True, port=5050)
