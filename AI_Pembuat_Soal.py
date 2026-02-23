import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Inches
from io import BytesIO
import markdown
from htmldocx import HtmlToDocx
import re
import requests

# =====================================
# 1. KONFIGURASI HALAMAN & TEMA (MODERN MINIMALIST)
# =====================================
st.set_page_config(page_title="AI Quiz Gen", page_icon="⚡", layout="wide")

# Injeksi CSS Custom untuk tampilan Startup Kekinian
st.markdown("""
<style>
    /* Import Font Modern 'Plus Jakarta Sans' */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Background Aplikasi: Pola Titik-titik (Dotted) elegan */
    [data-testid="stAppViewContainer"] {
        background-color: #FAFAFA;
        background-image: radial-gradient(#E5E7EB 1px, transparent 1px);
        background-size: 24px 24px;
    }
    
    /* Sembunyikan Header bawaan Streamlit */
    [data-testid="stHeader"] {
        background: transparent;
    }

    /* Kotak Utama (Sleek Card) */
    [data-testid="block-container"] {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 3rem 4rem;
        box-shadow: 0 4px 40px rgba(0, 0, 0, 0.04);
        border: 1px solid #F1F5F9;
        margin-top: 2rem;
        margin-bottom: 3rem;
    }

    /* Styling Judul Aplikasi (Gradient Text Minimalist) */
    .title-text {
        background: linear-gradient(135deg, #0F172A 0%, #4338CA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.2rem;
        letter-spacing: -1.5px;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }

    /* Mempercantik Input Form (Sleek Border) */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div {
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #F8FAFC !important;
        transition: all 0.2s ease;
    }
    
    div[data-baseweb="input"] > div:focus-within, 
    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="textarea"] > div:focus-within {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15) !important;
        background-color: #FFFFFF !important;
    }

    /* Tombol Utama (Sleek Dark Mode style) */
    .stButton > button {
        background: #0F172A;
        color: #F8FAFC;
        font-weight: 600;
        font-size: 1.1rem;
        border-radius: 14px;
        padding: 0.6rem 2rem;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        background: #1E293B;
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        color: white;
    }

    /* Styling Tab (Modern Underline) */
    [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 2px solid #F1F5F9;
    }
    [data-baseweb="tab"] {
        font-weight: 600;
        color: #64748B;
        padding-bottom: 1rem;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        color: #4338CA;
    }
    [data-baseweb="tab-highlight"] {
        background-color: #4338CA;
        height: 3px;
        border-top-left-radius: 3px;
        border-top-right-radius: 3px;
    }

    hr {
        border-top: 1px solid #E2E8F0;
        margin: 2rem 0;
    }
    
    /* Styling Checkbox */
    [data-testid="stCheckbox"] label span {
        font-weight: 500;
        color: #334155;
    }
</style>
""", unsafe_allow_html=True)

# =====================================
# 2. FUNGSI EXPORT WORD
# =====================================
def create_docx(hasil_ai, info):
    doc = Document()
    header = doc.add_heading(f"KUMPULAN SOAL: {info['mapel']}", 0)
    header.alignment = 1

    table = doc.add_table(rows=3, cols=2)
    table.style = 'Table Grid'
    table.rows[0].cells[0].text = "Mata Pelajaran"
    table.rows[0].cells[1].text = info["mapel"]
    table.rows[1].cells[0].text = "Kelas / Fase"
    table.rows[1].cells[1].text = f"{info['kelas']} / {info['fase']}"
    table.rows[2].cells[0].text = "Topik"
    table.rows[2].cells[1].text = info["topik"]

    doc.add_paragraph('\n')
    
    parts = re.split(r'!\[.*?\]\((.*?)\)', hasil_ai)
    new_parser = HtmlToDocx()
    
    for i, part in enumerate(parts):
        if i % 2 == 0:
            if part.strip():
                clean_text = part.replace("```markdown", "").replace("```", "")
                html_text = markdown.markdown(clean_text, extensions=['tables', 'nl2br', 'sane_lists'])
                new_parser.add_html_to_document(html_text, doc)
        else:
            url = part.strip()
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    image_stream = BytesIO(response.content)
                    doc.add_picture(image_stream, width=Inches(4.5))
            except Exception as e:
                doc.add_paragraph(f"[Gambar ilustrasi gagal diunduh]")

    bio = BytesIO()
    doc.save(bio)
    return bio

# =====================================
# 3. ANTARMUKA PENGGUNA (UI)
# =====================================
st.markdown('<h1 class="title-text">⚡ AI Quiz Gen.</h1>', unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 1.15rem; font-weight: 400; margin-bottom: 2.5rem; letter-spacing: -0.3px;'>Sistem pembuat soal otomatis berbasis kecerdasan buatan.</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 style='color: #0F172A; font-weight: 700; letter-spacing: -0.5px;'>⚙️ Settings</h2>", unsafe_allow_html=True)
    api_key_input = st.text_input("Gemini API Key", type="password", placeholder="Paste API Key di sini...")
    st.markdown("---")
    st.caption("Powered by **Google Gemini Flash** & **Pollinations AI**.")

# Layout Card Form
st.markdown("<h3 style='font-size: 1.3rem; font-weight: 700; color: #1E293B; margin-bottom: 1rem;'>📋 Konfigurasi Evaluasi</h3>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    mapel = st.text_input("Mata Pelajaran", value="Matematika")
    col_fase, col_kelas = st.columns(2)
    with col_fase:
        fase = st.selectbox("Fase", ["Fase A", "Fase B", "Fase C", "Fase D", "Fase E", "Fase F"], index=4)
    with col_kelas:
        kelas = st.selectbox("Kelas", ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4", "Kelas 5", "Kelas 6", "Kelas 7", "Kelas 8", "Kelas 9", "Kelas 10", "Kelas 11", "Kelas 12"], index=9)
        
    col_format, col_opsi = st.columns([2, 1])
    with col_format:
        format_soal = st.selectbox("Format Soal", ["Pilihan Ganda", "Pilihan Jamak", "Benar Salah", "Uraian"])
    with col_opsi:
        jml_opsi = st.selectbox("Opsi", [0, 1, 2, 3, 4, 5], index=5)

with col2:
    topik = st.text_area("Topik / Tujuan Pembelajaran", value="Persamaan Kuadrat (Rumus ABC)", height=115)
    st.markdown("<br>", unsafe_allow_html=True)
    mode_bergambar = st.checkbox("🖼️ Sisipkan Ilustrasi AI (Auto-generate)", value=False)

st.markdown("---")
col3, col4 = st.columns(2)
with col3:
    st.markdown("<h3 style='font-size: 1.1rem; font-weight: 600; color: #334155;'>📊 Tingkat Kesulitan</h3>", unsafe_allow_html=True)
    c_m, c_s, c_sl = st.columns(3)
    with c_m:
        jml_mudah = st.number_input("Mudah", min_value=0, max_value=50, value=3)
    with c_s:
        jml_sedang = st.number_input("Sedang", min_value=0, max_value=50, value=5)
    with c_sl:
        jml_sulit = st.number_input("Sulit", min_value=0, max_value=50, value=2)

with col4:
    st.markdown("<h3 style='font-size: 1.1rem; font-weight: 600; color: #334155;'>🧠 Level Kognitif</h3>", unsafe_allow_html=True)
    kognitif = st.multiselect(
        "Pilih taksonomi Bloom", 
        ["C1 (Mengingat)", "C2 (Memahami)", "C3 (Menerapkan)", "C4 (Menganalisis)", "C5 (Mengevaluasi)", "C6 (Mencipta)"],
        default=["C2 (Memahami)", "C3 (Menerapkan)"],
        label_visibility="collapsed"
    )

# =====================================
# 4. LOGIKA GENERASI & PROMPT
# =====================================
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🚀 Generate Evaluasi Sekarang"):
    total_soal = jml_mudah + jml_sedang + jml_sulit
    
    if not api_key_input:
        st.error("⚠️ Autentikasi Gagal: Masukkan API Key di sidebar.")
        st.stop()
        
    if total_soal == 0:
        st.warning("⚠️ Parameter tidak valid: Total soal tidak boleh 0.")
        st.stop()

    try:
        genai.configure(api_key=api_key_input)
        
        model_terpilih = None
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_terpilih = m.name
                if 'flash' in m.name: break
        
        if model_terpilih is None:
            st.error("Gagal: API Key tidak valid atau tidak memiliki akses.")
            st.stop()
            
        model = genai.GenerativeModel(model_terpilih)
        
        prompt = f"""
        Anda adalah Guru Ahli. Buatkan {total_soal} soal evaluasi.
        DATA: Mapel {mapel} | Kelas {kelas} | Topik: {topik} | {jml_opsi} Opsi Jawaban.
        
        ATURAN LAYOUT (WAJIB DIIKUTI 100%):
        1. Tuliskan setiap opsi jawaban MENURUN KE BAWAH dengan diawali tanda strip (-) agar menjadi Bullet Point.
        
        2. ATURAN MATEMATIKA (SANGAT PENTING): 
           - JANGAN PERNAH menggunakan format LaTeX (simbol $ atau $$). Word tidak bisa membacanya!
           - Gunakan teks biasa dan simbol Unicode standar.
           - Contoh Benar: x² - 5x + 6 = 0, √(16), 1/2, ±
           - Contoh Salah: $x^2 - 5x + 6 = 0$, $\\sqrt{{16}}$
           
        3. Jika Mode Bergambar AKTIF: Tambahkan gambar di antara soal dan opsi.
           Gunakan URL ini: ![Ilustrasi](https://image.pollinations.ai/prompt/[kata_kunci]?width=500&height=300)
           Ganti [kata_kunci] dengan bahasa Inggris. DILARANG ADA SPASI (Ganti spasi dengan garis bawah _).
           
        4. ATURAN TABEL KUNCI & KISI-KISI: 
           - WAJIB gunakan format tabel Markdown (menggunakan tanda garis vertikal |).
           - DILARANG KERAS menggunakan Enter (baris baru) di dalam sel tabel pembahasan!
           - Jika butuh baris baru untuk memisahkan langkah pengerjaan, gunakan tag <br>.
           - Contoh penulisan tabel yang benar: | 1 | A | x² = 4 <br> x = 2 |
        
        OUTPUT WAJIB MARKDOWN DENGAN PEMISAH:
        [BAGIAN_SOAL]
        (Isi soal di sini)
        
        [BAGIAN_KUNCI]
        | No | Jawaban | Pembahasan |
        |---|---|---|
        (Lanjutkan isi tabel kunci di sini)
        
        [BAGIAN_KISI]
        | No | Indikator | Level Kognitif | Tingkat Kesulitan |
        |---|---|---|---|
        (Lanjutkan isi tabel kisi-kisi di sini)
        """

        with st.spinner(f"⏳ Processing... AI sedang menyusun materi evaluasi."):
            response = model.generate_content(prompt)
            hasil = response.text
            
            hasil_clean = hasil.replace(" A. ", "\n- A. ").replace(" B. ", "\n- B. ").replace(" C. ", "\n- C. ").replace(" D. ", "\n- D. ").replace(" E. ", "\n- E. ")
            hasil_clean = re.sub(r'(!\[.*?\]\()(.*?)(\))', lambda m: m.group(1) + m.group(2).replace(" ", "_") + m.group(3), hasil_clean)
            
            parts = re.split(r'\[BAGIAN_SOAL\]|\[BAGIAN_KUNCI\]|\[BAGIAN_KISI\]', hasil_clean)
            soal_text = parts[1].strip() if len(parts) > 1 else hasil_clean
            kunci_text = parts[2].strip() if len(parts) > 2 else "Kunci tidak tergenerasi."
            kisi_text = parts[3].strip() if len(parts) > 3 else "Kisi-kisi tidak tergenerasi."

            st.success("✨ Evaluasi berhasil di-generate!")
            
            tab1, tab2, tab3 = st.tabs(["📄 Soal Evaluasi", "🔑 Kunci Jawaban", "✅ Kisi-kisi"])
            with tab1: st.markdown(soal_text)
            with tab2: st.markdown(kunci_text)
            with tab3: st.markdown(kisi_text)
                
            st.markdown("---")
            formatted_content = hasil_clean.replace('[BAGIAN_SOAL]', 'SOAL').replace('[BAGIAN_KUNCI]', 'KUNCI').replace('[BAGIAN_KISI]', 'KISI-KISI')
            
            with st.spinner("📦 Compiling document... Mendownload aset visual ke Word."):
                doc_file = create_docx(formatted_content, {
                    "mapel": mapel, "kelas": kelas, "fase": fase, "topik": topik
                })
                
                st.download_button(
                    label="⬇️ Download MS Word (.docx)",
                    data=doc_file.getvalue(),
                    file_name=f"Soal_{mapel}_{kelas}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"System Error: {e}")