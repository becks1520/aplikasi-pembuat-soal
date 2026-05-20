import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import markdown
from htmldocx import HtmlToDocx
import re
import requests
import urllib.parse
import time

# =====================================================
# 1. KONFIGURASI HALAMAN
# =====================================================
st.set_page_config(
    page_title="SmartQuiz AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(145deg, #EEF2FF 0%, #F0FAFA 50%, #FAF5FF 100%);
    min-height: 100vh;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1E1B4B 0%, #312E81 100%);
    border-right: none;
}
[data-testid="stSidebar"] * { color: #E0E7FF !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: white !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder { color: rgba(255,255,255,0.5) !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }

/* Main Container */
[data-testid="block-container"] {
    background: rgba(255, 255, 255, 0.80);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-radius: 28px;
    padding: 2.5rem 3.5rem;
    box-shadow: 0 25px 50px rgba(79, 70, 229, 0.07), 0 8px 16px rgba(0,0,0,0.04);
    border: 1px solid rgba(255, 255, 255, 0.7);
    margin-top: 1.5rem;
    margin-bottom: 2rem;
}

/* Title */
.title-text {
    background: linear-gradient(135deg, #4338CA 0%, #7C3AED 50%, #EC4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 3.2rem;
    letter-spacing: -1.5px;
    line-height: 1.15;
}
.subtitle-badge {
    display: inline-block;
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    color: white !important;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 4px 14px;
    border-radius: 100px;
    margin-bottom: 0.75rem;
}

/* Section headers */
.section-header {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1E1B4B;
    padding: 0.4rem 0;
    border-left: 4px solid #4F46E5;
    padding-left: 0.8rem;
    margin-bottom: 1rem;
    margin-top: 0.5rem;
}

/* Input fields */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    border-radius: 12px !important;
    background-color: #FAFBFF !important;
    border: 1.5px solid #DDE3F5 !important;
    transition: all 0.25s ease;
}
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within {
    border-color: #4F46E5 !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
    background-color: #FFFFFF !important;
}

/* Number input */
div[data-testid="stNumberInput"] input {
    border-radius: 10px !important;
    text-align: center;
    font-weight: 700;
    font-size: 1.1rem;
}

/* Generate Button */
div[data-testid="stButton"] > button[kind="primary"],
.stButton > button {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    color: white !important;
    font-weight: 700;
    font-size: 1.05rem;
    border-radius: 14px;
    padding: 0.85rem 1.5rem;
    width: 100%;
    border: none;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.35);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    letter-spacing: 0.01em;
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.01);
    box-shadow: 0 12px 30px rgba(79, 70, 229, 0.45);
    color: white !important;
}
.stButton > button:active { transform: translateY(-1px); }

/* Download button */
.stDownloadButton > button {
    background: linear-gradient(135deg, #059669 0%, #0D9488 100%) !important;
    color: white !important;
    font-weight: 700;
    font-size: 1rem;
    border-radius: 12px;
    border: none !important;
    box-shadow: 0 4px 15px rgba(5, 150, 105, 0.3) !important;
    transition: all 0.3s ease !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(5, 150, 105, 0.4) !important;
}

/* Tabs */
[data-baseweb="tab-list"] {
    gap: 0.5rem;
    border-bottom: 2px solid #E8EDFF;
    padding-bottom: 0;
    margin-bottom: 1.5rem;
}
[data-baseweb="tab"] {
    font-weight: 600;
    font-size: 0.95rem;
    color: #6B7280;
    padding: 0.6rem 1rem;
    border-radius: 8px 8px 0 0;
    transition: all 0.2s ease;
}
[data-baseweb="tab"]:hover { color: #4F46E5; background: rgba(79,70,229,0.05); }
[data-baseweb="tab"][aria-selected="true"] { color: #4F46E5; }
[data-baseweb="tab-highlight"] {
    background: linear-gradient(90deg, #4F46E5, #7C3AED);
    height: 3px;
    border-radius: 3px 3px 0 0;
}

/* Info & Alert boxes */
.stAlert { border-radius: 12px !important; }
.stInfo { background: #EEF2FF !important; border-color: #4F46E5 !important; }
.stSuccess { border-radius: 12px !important; }

/* Divider */
hr { border-color: #E8EDFF !important; margin: 1.5rem 0 !important; }

/* Stats card */
.stat-card {
    background: linear-gradient(135deg, #EEF2FF 0%, #F5F3FF 100%);
    border: 1px solid #C7D2FE;
    border-radius: 14px;
    padding: 1rem 1.25rem;
    text-align: center;
}
.stat-number {
    font-size: 2rem;
    font-weight: 800;
    color: #4F46E5;
    line-height: 1;
}
.stat-label { font-size: 0.8rem; color: #6366F1; font-weight: 600; margin-top: 4px; }

/* Checkbox */
[data-testid="stCheckbox"] { gap: 0.5rem; }

/* Caption */
.stCaption { color: #9CA3AF !important; font-size: 0.8rem !important; }

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid #DDE3F5 !important;
    border-radius: 14px !important;
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    font-weight: 600;
    color: #4F46E5;
    padding: 0.8rem 1rem;
}

/* Responsive */
@media (max-width: 768px) {
    [data-testid="block-container"] { padding: 1.2rem 1rem; border-radius: 16px; margin-top: 0.25rem; }
    .title-text { font-size: 2rem; }
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# 2. HEADER
# =====================================================
st.markdown("""
<div style="text-align:center; margin-bottom:2.5rem;">
    <span class="subtitle-badge">100% Free · AI-Powered · Google Gemini</span>
    <h1 class="title-text">SmartQuiz AI ⚡</h1>
    <p style="color:#64748B; font-size:1.1rem; max-width:680px; margin:0.6rem auto 0; line-height:1.7;">
        Generator soal evaluasi otomatis berbasis AI — lengkap dengan kunci jawaban, 
        kisi-kisi, kartu soal, dan ekspor Word dalam satu klik.
    </p>
</div>
""", unsafe_allow_html=True)


# =====================================================
# 3. FUNGSI EXPORT KE WORD
# =====================================================
def export_to_docx(judul, info, hasil_ai):
    doc = Document()

    # Style dokumen
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    # Judul dokumen
    title_para = doc.add_heading(judul, level=0)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_para.runs[0]
    run.font.color.rgb = RGBColor(0x2D, 0x31, 0x9E)

    doc.add_paragraph()

    # Tabel info
    table = doc.add_table(rows=3, cols=2)
    table.style = 'Table Grid'
    cells_data = [
        ("Mata Pelajaran", info["mapel"]),
        ("Kelas", info["kelas"]),
        ("Topik / Tujuan Pembelajaran", info["topik"]),
    ]
    for i, (label, value) in enumerate(cells_data):
        row = table.rows[i]
        row.cells[0].text = label
        row.cells[1].text = value
        for cell in row.cells:
            for para in cell.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(10)
        row.cells[0].paragraphs[0].runs[0].font.bold = True

    doc.add_paragraph()

    # Konten utama: pisahkan teks biasa dan gambar
    parts = re.split(r'!\[.*?\]\((.*?)\)', hasil_ai)
    new_parser = HtmlToDocx()

    for i, part in enumerate(parts):
        if i % 2 == 0:
            if part.strip():
                clean_text = part.replace("```markdown", "").replace("```", "")
                html_text = markdown.markdown(
                    clean_text, extensions=['tables', 'nl2br', 'sane_lists']
                )
                new_parser.add_html_to_document(html_text, doc)
        else:
            url = part.strip()
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Accept': 'image/*,*/*;q=0.8'
                }
                response = requests.get(url, timeout=20, headers=headers, allow_redirects=True)
                if response.status_code == 200:
                    image_stream = BytesIO(response.content)
                    doc.add_picture(image_stream, width=Inches(4.0))
                else:
                    doc.add_paragraph(f"[Gambar tidak tersedia – kode error: {response.status_code}]")
            except Exception:
                doc.add_paragraph("[Gambar tidak dapat dimuat – periksa koneksi internet Anda.]")

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


# =====================================================
# 4. FUNGSI GENERATE AI
# =====================================================
PREFERRED_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

def get_best_model(api_key: str) -> str:
    """Pilih model Gemini terbaik yang tersedia."""
    try:
        genai.configure(api_key=api_key)
        available = {m.name.split("/")[-1] for m in genai.list_models()
                     if "generateContent" in m.supported_generation_methods}
        for preferred in PREFERRED_MODELS:
            if preferred in available:
                return preferred
        # Fallback: ambil model flash pertama yang ada
        for name in available:
            if "flash" in name:
                return name
        return "gemini-1.5-flash"
    except Exception:
        return "gemini-1.5-flash"


@st.cache_data(show_spinner=False, ttl=600)
def generate_with_gemini(prompt: str, api_key: str, model_name: str) -> str:
    genai.configure(api_key=api_key)
    generation_config = genai.GenerationConfig(
        temperature=0.85,
        top_p=0.95,
        max_output_tokens=8192,
    )
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    model = genai.GenerativeModel(
        model_name,
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    response = model.generate_content(prompt)
    return response.text


# =====================================================
# 5. SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
        <div style="font-size:2.8rem;">⚡</div>
        <div style="font-size:1.1rem; font-weight:800; color:white; letter-spacing:-0.5px;">SmartQuiz AI</div>
        <div style="font-size:0.7rem; color:#A5B4FC; margin-top:2px; letter-spacing:0.08em;">v2.0 · Powered by Google Gemini</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🔑 Autentikasi")
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="AIzaSy...",
        help="Dapatkan API Key gratis di https://aistudio.google.com/app/apikey"
    )

    if api_key:
        if len(api_key) < 30:
            st.error("⚠️ API Key tampaknya tidak valid.")
        else:
            st.success("✅ API Key terdeteksi")

    st.markdown("---")
    st.markdown("#### 🌐 Bahasa Output")
    bahasa_output = st.selectbox(
        "Pilih bahasa untuk soal yang dihasilkan",
        ["Bahasa Indonesia", "Bahasa Inggris", "Bahasa Melayu"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.82rem; color:#A5B4FC; line-height:1.9;">
        <div style="color:#C7D2FE; font-weight:700; margin-bottom:0.4rem;">✨ Fitur Unggulan</div>
        🚀 &nbsp;Generate super cepat<br>
        🖼️ &nbsp;Ilustrasi gambar otomatis<br>
        📊 &nbsp;Kisi-kisi & kartu soal<br>
        📄 &nbsp;Export ke Word (.docx)<br>
        🧠 &nbsp;Dukungan Taksonomi Bloom<br>
        📱 &nbsp;Responsif di HP & Tablet
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.75rem; color:#7C6EBA; text-align:center;">
        Dibuat dengan ❤️ untuk Pendidikan Indonesia<br>
        <a href="https://aistudio.google.com/app/apikey" target="_blank" 
           style="color:#A5B4FC; text-decoration:none;">→ Dapatkan API Key Gratis</a>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# 6. FORM INPUT UTAMA
# =====================================================
st.markdown('<div class="section-header">📋 Konfigurasi Evaluasi</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")
with col1:
    mapel = st.text_input("📚 Mata Pelajaran", placeholder="Contoh: Matematika, IPA, Bahasa Indonesia...")
    kelas = st.selectbox(
        "🎓 Kelas",
        [f"Kelas {i}" for i in range(1, 13)],
        index=9,
        help="Pilih jenjang kelas sesuai dengan peserta didik."
    )
    format_soal = st.selectbox(
        "📝 Format Soal",
        ["Pilihan Ganda", "Pilihan Jamak (>1 Jawaban)", "Benar Salah", "Uraian / Essay", "Menjodohkan"],
        help="Pilih jenis / format soal yang ingin dibuat."
    )
    # Opsi jumlah opsi: sembunyikan jika Uraian
    if format_soal not in ["Uraian / Essay"]:
        jml_opsi_label = "Jumlah Pernyataan" if format_soal == "Benar Salah" else (
            "Jumlah Pasangan" if format_soal == "Menjodohkan" else "Jumlah Opsi Jawaban"
        )
        jml_opsi = st.selectbox(
            f"🔢 {jml_opsi_label}",
            [3, 4, 5, 6],
            index=1,
            help="Jumlah pilihan/opsi untuk setiap soal."
        )
    else:
        jml_opsi = 0

with col2:
    topik = st.text_area(
        "🎯 Topik / Tujuan Pembelajaran",
        placeholder="Contoh: Peserta didik mampu memahami konsep fotosintesis pada tumbuhan hijau...",
        height=130
    )
    st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
    mode_bergambar = st.checkbox("🖼️ Sisipkan Ilustrasi Gambar Otomatis", value=False)
    if mode_bergambar:
        st.caption("💡 Gambar diambil otomatis dari internet. Bisa diganti atau dihapus di Word.")

    sertakan_rubrik = st.checkbox("📋 Sertakan Rubrik Penilaian (khusus Uraian)", value=False,
                                  disabled=(format_soal != "Uraian / Essay"))

st.markdown("---")

# Komposisi soal
st.markdown('<div class="section-header">📊 Komposisi Tingkat Kesulitan</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3, gap="medium")
with c1:
    jml_mudah = st.number_input("🟢 Mudah", min_value=0, max_value=50, value=3, step=1)
with c2:
    jml_sedang = st.number_input("🟡 Sedang", min_value=0, max_value=50, value=4, step=1)
with c3:
    jml_sulit = st.number_input("🔴 Sulit", min_value=0, max_value=50, value=3, step=1)

total_soal = jml_mudah + jml_sedang + jml_sulit

# Ringkasan statistik
st.markdown("<div style='margin: 1.2rem 0 0.5rem;'></div>", unsafe_allow_html=True)
s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_soal}</div><div class="stat-label">Total Soal</div></div>', unsafe_allow_html=True)
with s2:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{jml_mudah}</div><div class="stat-label">Mudah</div></div>', unsafe_allow_html=True)
with s3:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{jml_sedang}</div><div class="stat-label">Sedang</div></div>', unsafe_allow_html=True)
with s4:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{jml_sulit}</div><div class="stat-label">Sulit</div></div>', unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)

# Level kognitif
st.markdown('<div class="section-header">🧠 Level Kognitif (Taksonomi Bloom)</div>', unsafe_allow_html=True)
kognitif = st.multiselect(
    "Pilih satu atau lebih level Taksonomi Bloom",
    ["C1 – Mengingat (Remember)", "C2 – Memahami (Understand)", "C3 – Menerapkan (Apply)",
     "C4 – Menganalisis (Analyze)", "C5 – Mengevaluasi (Evaluate)", "C6 – Mencipta (Create)"],
    default=["C2 – Memahami (Understand)", "C3 – Menerapkan (Apply)"],
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)


# =====================================================
# 7. MEMBANGUN PROMPT
# =====================================================
def build_format_instruksi(format_soal, jml_opsi):
    if format_soal == "Benar Salah":
        return (
            f"Format BENAR/SALAH.\n"
            f"Setiap nomor soal berisi {jml_opsi} PERNYATAAN TERPISAH.\n\n"
            f"Aturan penulisan (WAJIB DIIKUTI):\n"
            f"- Tulis 1 nomor soal utama di baris pertama.\n"
            f"- Buat baris baru untuk setiap pernyataan, berlabel a., b., c., dst.\n"
            f"- DILARANG menggabungkan pernyataan dalam satu paragraf.\n"
            f"- Di akhir setiap soal tulis: 'Tentukan apakah pernyataan di atas BENAR atau SALAH.'\n\n"
            f"Contoh:\n1. Perhatikan pernyataan berikut:\na. Jantung berfungsi memompa darah.\nb. Lambung adalah organ pernapasan.\nTentukan apakah setiap pernyataan di atas BENAR atau SALAH."
        )
    elif format_soal == "Uraian / Essay":
        return (
            "Format URAIAN (Essay).\n"
            "Berikan pertanyaan terbuka yang mendorong peserta didik berpikir kritis.\n"
            "Tulis teks soal dengan rapi, TANPA opsi jawaban.\n"
            "Setiap soal harus jelas, spesifik, dan terukur."
        )
    elif format_soal == "Pilihan Jamak (>1 Jawaban)":
        return (
            f"Format PILIHAN JAMAK (lebih dari 1 jawaban bisa benar).\n"
            f"Setiap soal WAJIB memiliki {jml_opsi} opsi jawaban.\n\n"
            f"Aturan penulisan:\n"
            f"- Tambahkan petunjuk: '(Pilih semua jawaban yang benar)' setelah teks soal.\n"
            f"- Buat baris baru untuk setiap opsi, berlabel A., B., C., dst.\n"
            f"- DILARANG menggabungkan opsi dalam satu paragraf."
        )
    elif format_soal == "Menjodohkan":
        return (
            f"Format MENJODOHKAN.\n"
            f"Setiap nomor soal WAJIB memiliki {jml_opsi} pasangan.\n\n"
            f"Aturan penulisan:\n"
            f"- Buat dua kolom: Kolom A (daftar istilah/pernyataan) dan Kolom B (daftar jawaban).\n"
            f"- Kolom A berlabel 1., 2., 3., dst. (berurutan).\n"
            f"- Kolom B berlabel a., b., c., dst. (diacak, tidak sejajar dengan A).\n"
            f"- Instruksikan peserta didik untuk mencocokkan setiap item di Kolom A dengan Kolom B.\n"
            f"- Buat jumlah item di Kolom B lebih banyak 1-2 dari Kolom A sebagai pengecoh."
        )
    else:  # Pilihan Ganda
        return (
            f"Format PILIHAN GANDA (hanya 1 jawaban benar).\n"
            f"Setiap soal WAJIB memiliki {jml_opsi} opsi jawaban.\n\n"
            f"Aturan penulisan:\n"
            f"- Buat baris baru untuk setiap opsi, berlabel A., B., C., dst.\n"
            f"- DILARANG menggabungkan opsi dalam satu paragraf.\n"
            f"- Buat pengecoh (distraktor) yang masuk akal dan mendekati jawaban benar."
        )


def build_prompt(mapel, kelas, topik, kognitif, format_soal, jml_opsi,
                 jml_mudah, jml_sedang, jml_sulit, total_soal,
                 mode_bergambar, sertakan_rubrik, bahasa_output):
    instruksi_format = build_format_instruksi(format_soal, jml_opsi)

    instruksi_gambar = (
        """4. ATURAN GAMBAR (WAJIB): Sisipkan 1 gambar di SETIAP soal.
           Gunakan format: {{GAMBAR: kata kunci}}
           Kata kunci: 1-2 kata benda bahasa Inggris yang umum dan spesifik.
           Contoh: {{GAMBAR: human heart}} atau {{GAMBAR: plant cell}}"""
        if mode_bergambar
        else "4. JANGAN menyisipkan gambar apapun."
    )

    instruksi_rubrik = (
        "\n\nDi dalam [BAGIAN_KUNCI], sertakan RUBRIK PENILAIAN untuk setiap soal uraian dengan skor per aspek."
        if sertakan_rubrik and "Uraian" in format_soal
        else ""
    )

    instruksi_bahasa = {
        "Bahasa Indonesia": "Tulis seluruh soal, kunci jawaban, kisi-kisi, dan kartu soal dalam Bahasa Indonesia yang baik dan benar.",
        "Bahasa Inggris": "Write all questions, answer keys, grid, and question cards in proper English.",
        "Bahasa Melayu": "Tulis semua soal, kunci jawaban, kisi-kisi, dan kad soal dalam Bahasa Melayu yang betul.",
    }.get(bahasa_output, "")

    kognitif_str = ", ".join(kognitif) if kognitif else "C2 – Memahami, C3 – Menerapkan"

    return f"""
Anda adalah Guru Ahli Kurikulum Merdeka yang berpengalaman.

{instruksi_bahasa}

Buatkan {total_soal} soal evaluasi berkualitas tinggi dengan detail berikut:
- Mata Pelajaran : {mapel}
- Kelas          : {kelas}
- Topik / TP     : {topik}
- Level Kognitif : {kognitif_str}
- Distribusi     : Mudah ({jml_mudah}), Sedang ({jml_sedang}), Sulit ({jml_sulit})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ATURAN LAYOUT (WAJIB DIIKUTI 100%):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. DILARANG KERAS menggunakan Heading Markdown (simbol #, ##, ###).
   Gunakan cetak tebal (**teks**) untuk sub-judul saja.

2. DILARANG KERAS menggunakan format LaTeX atau simbol dolar ($).
   Tulis rumus dalam teks biasa: x^2, sqrt(x), 1/2, dsb.

3. {instruksi_format}

{instruksi_gambar}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT WAJIB (ikuti urutan persis ini):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[BAGIAN_SOAL]
(Tulis semua soal evaluasi di sini sesuai aturan di atas){instruksi_rubrik}

[BAGIAN_KUNCI]
(Buat tabel Kunci Jawaban dan Pembahasan singkat untuk setiap nomor.
 Format tabel: | No | Jawaban | Pembahasan Singkat |)

[BAGIAN_KISI]
WAJIB buat dalam format Tabel Markdown persis seperti ini:
| No | Indikator Soal | Level Kognitif | Tingkat Kesulitan |
|---|---|---|---|
(Isi baris tabel untuk semua nomor soal)

[BAGIAN_KARTU]
Tuliskan ulang SETIAP SOAL dalam format Kartu Soal Kurikulum Merdeka.
Gunakan struktur berikut untuk setiap nomor:

---
**KARTU SOAL NOMOR [X]**
* **Tujuan Pembelajaran:** {topik}
* **Materi Pokok:** [isi]
* **Indikator Soal:** [isi – sesuaikan dengan tabel kisi-kisi]
* **Level Kognitif:** [isi]
* **Tingkat Kesulitan:** [Mudah / Sedang / Sulit]

**Rumusan Soal:**
[Tuliskan teks soal lengkap beserta opsi jawaban secara berurutan]
"""


# =====================================================
# 8. TOMBOL GENERATE & LOGIKA UTAMA
# =====================================================
generate_clicked = st.button("🚀 Generate Evaluasi Sekarang", use_container_width=True, type="primary")

if generate_clicked:
    # Validasi
    errors = []
    if not api_key:
        errors.append("⚠️ Masukkan **Google Gemini API Key** di sidebar kiri.")
    if not mapel.strip():
        errors.append("⚠️ Kolom **Mata Pelajaran** tidak boleh kosong.")
    if not topik.strip():
        errors.append("⚠️ Kolom **Topik / Tujuan Pembelajaran** tidak boleh kosong.")
    if total_soal == 0:
        errors.append("⚠️ Total soal tidak boleh **0**. Isi minimal 1 soal.")
    if total_soal > 50:
        errors.append("⚠️ Total soal maksimal **50** untuk menjaga kualitas output.")
    if not kognitif:
        errors.append("⚠️ Pilih minimal **1 level kognitif** Taksonomi Bloom.")

    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    prompt = build_prompt(
        mapel, kelas, topik, kognitif, format_soal, jml_opsi,
        jml_mudah, jml_sedang, jml_sulit, total_soal,
        mode_bergambar, sertakan_rubrik, bahasa_output
    )

    try:
        with st.spinner(f"⏳ Mendeteksi model Gemini terbaik yang tersedia..."):
            model_name = get_best_model(api_key)

        progress_bar = st.progress(0, text="🤖 Menginisialisasi AI...")
        time.sleep(0.3)
        progress_bar.progress(15, text=f"✅ Model: **{model_name}** dipilih. Mulai generate soal...")

        with st.spinner(f"📝 AI sedang menyusun {total_soal} soal, kunci, kisi-kisi & kartu soal..."):
            hasil = generate_with_gemini(prompt, api_key, model_name)

        progress_bar.progress(70, text="✨ Soal berhasil di-generate! Memproses hasil...")
        time.sleep(0.3)

        # Bersihkan heading markdown
        hasil_clean = re.sub(r'^#+\s+(.*)$', r'**\1**', hasil, flags=re.MULTILINE)

        # Proses gambar
        if mode_bergambar:
            def ubah_ke_url(match):
                kata_kunci = match.group(1).strip()
                kata_kunci_aman = urllib.parse.quote(kata_kunci.replace(" ", ","))
                return f"\n\n![Ilustrasi {kata_kunci}](https://loremflickr.com/600/350/{kata_kunci_aman}/all)\n\n"
            hasil_clean = re.sub(
                r'\{\{GAMBAR:\s*(.*?)\}\}', ubah_ke_url, hasil_clean, flags=re.IGNORECASE
            )

        # Pisahkan 4 bagian
        bagian_pattern = r'\[BAGIAN_SOAL\]|\[BAGIAN_KUNCI\]|\[BAGIAN_KISI\]|\[BAGIAN_KARTU\]'
        parts = re.split(bagian_pattern, hasil_clean)

        # Filter bagian kosong di awal
        parts = [p for p in parts if p.strip()]

        soal_teks  = parts[0].strip() if len(parts) > 0 else hasil_clean
        kunci_teks = parts[1].strip() if len(parts) > 1 else "*Kunci jawaban tidak berhasil dipisahkan.*"
        kisi_teks  = parts[2].strip() if len(parts) > 2 else "*Kisi-kisi tidak berhasil dipisahkan.*"
        kartu_teks = parts[3].strip() if len(parts) > 3 else "*Kartu soal tidak berhasil dipisahkan.*"

        progress_bar.progress(90, text="📄 Menyiapkan tampilan dan file Word...")
        time.sleep(0.3)

        # Siapkan DOCX
        info_doc = {"mapel": mapel, "kelas": kelas, "topik": topik}
        formatted_content = (
            f"{soal_teks}\n\n"
            f"## Kunci Jawaban & Pembahasan\n{kunci_teks}\n\n"
            f"## Kisi-Kisi Soal\n{kisi_teks}\n\n"
            f"## Kumpulan Kartu Soal\n{kartu_teks}"
        )
        doc_buffer = export_to_docx(
            f"SOAL EVALUASI: {mapel.upper()} – {kelas}", info_doc, formatted_content
        )

        progress_bar.progress(100, text="🎉 Selesai! Semua dokumen siap.")
        time.sleep(0.5)
        progress_bar.empty()

        st.success(f"✨ Berhasil! **{total_soal} soal** beserta kunci, kisi-kisi, dan kartu soal telah di-generate menggunakan model **{model_name}**.")

        # ── Tab Tampilan ──
        st.markdown("<br>", unsafe_allow_html=True)
        tab1, tab2, tab3, tab4 = st.tabs([
            "📄 Soal Evaluasi", "🔑 Kunci & Pembahasan", "📊 Kisi-Kisi", "📇 Kartu Soal"
        ])
        with tab1: st.markdown(soal_teks)
        with tab2: st.markdown(kunci_teks)
        with tab3: st.markdown(kisi_teks)
        with tab4: st.markdown(kartu_teks)

        st.markdown("---")

        # ── Tombol Download ──
        dl_col1, dl_col2 = st.columns([2, 1])
        with dl_col1:
            st.download_button(
                label="⬇️ Download Lengkap – Microsoft Word (.docx)",
                data=doc_buffer.getvalue(),
                file_name=f"Evaluasi_{mapel.replace(' ','_')}_{kelas.replace(' ','_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        with dl_col2:
            st.info(f"📁 Format: `.docx` · {len(doc_buffer.getvalue()) // 1024} KB")

        # ── Tips ──
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("💡 Tips: Merapikan Rumus Matematika di Microsoft Word"):
            st.info("""
**Cara mengubah rumus teks biasa menjadi format Equation rapi di Word:**

1. **Salin** teks rumus dari hasil AI (misal: `x^2 - 4ac = 0`)
2. **Tempel** ke dokumen Microsoft Word
3. **Blok / sorot** teks rumus tersebut
4. Tekan **`Alt + =`** pada keyboard
5. Klik tab **Design** → **Convert** → **Convert to Professional**

➡️ Rumus langsung berubah menjadi format Equation matematika yang profesional!
            """)

        with st.expander("ℹ️ Tentang Gambar Ilustrasi"):
            st.info("""
Gambar diambil secara otomatis dari layanan **LoremFlickr** berdasarkan kata kunci yang ditentukan AI.

- **Di web:** Gambar terlihat langsung di halaman ini.
- **Di Word:** Gambar diunduh dan disematkan saat tombol Download diklik.
- Jika gambar kurang relevan, Anda bisa **mengganti atau menghapus** gambar tersebut di Microsoft Word dengan mudah.
            """)

    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper() or "invalid" in error_msg.lower():
            st.error("🔐 **API Key tidak valid.** Pastikan API Key Gemini Anda benar dan aktif.")
        elif "quota" in error_msg.lower() or "429" in error_msg:
            st.error("⏳ **Kuota API habis atau terlalu banyak permintaan.** Tunggu beberapa menit lalu coba lagi.")
        elif "timeout" in error_msg.lower():
            st.error("⌛ **Koneksi timeout.** Coba generate ulang dengan jumlah soal yang lebih sedikit.")
        else:
            st.error(f"❌ **Terjadi kesalahan:** {error_msg}")
        st.info("💡 Jika masalah berlanjut, coba kurangi jumlah soal atau periksa koneksi internet Anda.")
