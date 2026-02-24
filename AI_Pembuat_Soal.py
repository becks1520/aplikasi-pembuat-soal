import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Inches
from io import BytesIO
import markdown
from htmldocx import HtmlToDocx
import re
import requests
import urllib.parse

# =====================================
# 1. KONFIGURASI HALAMAN & TEMA MODERN
# =====================================
st.set_page_config(page_title="AI Quiz Gen", page_icon="⚡", layout="wide")

# CSS Super Modern (Glassmorphism & Gradient)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Plus Jakarta Sans', sans-serif !important; 
    }
    
    /* Background Latar Belakang - Gradasi Lembut */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
    }
    
    [data-testid="stHeader"] { background: transparent; }
    
    /* Kotak Utama - Efek Kaca (Glassmorphism) */
    [data-testid="block-container"] {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 32px; 
        padding: 3rem 4rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08); 
        border: 1px solid rgba(255, 255, 255, 0.5);
        margin-top: 2rem; margin-bottom: 3rem;
    }
    
    /* Teks Judul dengan Warna Gradasi Menyala */
    .title-text {
        background: linear-gradient(135deg, #4F46E5 0%, #EC4899 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 3.5rem; letter-spacing: -1.5px;
        margin-bottom: 0px; padding-bottom: 0px;
    }
    
    /* Kotak Inputan (Kolom Ketik) Lebih Elegan */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="textarea"] > div {
        border-radius: 16px !important; 
        border: 1px solid #CBD5E1 !important;
        background-color: rgba(255, 255, 255, 0.9) !important; 
        transition: all 0.3s ease;
    }
    
    /* Efek Saat Kotak Input Diklik */
    div[data-baseweb="input"] > div:focus-within, div[data-baseweb="select"] > div:focus-within, div[data-baseweb="textarea"] > div:focus-within {
        border-color: #4F46E5 !important; 
        box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.15) !important;
        background-color: #FFFFFF !important;
    }
    
    /* Tombol Utama - Efek 3D dan Glow */
    .stButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: #FFFFFF; font-weight: 700; font-size: 1.15rem;
        border-radius: 16px; padding: 0.8rem 2rem; border: none;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
        width: 100%; letter-spacing: 0.5px;
    }
    
    /* Efek Hover Saat Tombol Disentuh Kursor */
    .stButton > button:hover {
        background: linear-gradient(135deg, #4338CA 0%, #6D28D9 100%);
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 25px rgba(79, 70, 229, 0.6); 
        color: white;
    }
    
    /* Modifikasi Tab Soal, Kunci, Kisi-kisi */
    [data-baseweb="tab-list"] { gap: 2rem; border-bottom: 2px solid #E2E8F0; }
    [data-baseweb="tab"] { font-weight: 600; color: #64748B; padding-bottom: 1rem; transition: color 0.2s;}
    [data-baseweb="tab"]:hover { color: #4F46E5; }
    [data-baseweb="tab"][aria-selected="true"] { color: #4F46E5; }
    [data-baseweb="tab-highlight"] { background-color: #4F46E5; height: 3px; border-radius: 3px 3px 0 0; }
    hr { border-top: 1px solid #E2E8F0; margin: 2rem 0; }
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
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
                }
                
                response = requests.get(url, timeout=20, headers=headers, allow_redirects=True)
                
                if response.status_code == 200:
                    image_stream = BytesIO(response.content)
                    doc.add_picture(image_stream, width=Inches(4.0))
                else:
                    doc.add_paragraph(f"[Gambar gagal didownload. Error Code: {response.status_code}]")
            except Exception as e:
                doc.add_paragraph(f"[Gambar gagal dimuat: Koneksi Terputus / Server Lambat]")

    bio = BytesIO()
    doc.save(bio)
    return bio

# =====================================
# 3. ANTARMUKA PENGGUNA (UI)
# =====================================
st.markdown("""
<style>
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.premium-header {
    text-align: center;
    margin-bottom: 3rem;
    animation: fadeUp 0.9s ease-out;
}

.premium-badge {
    display: inline-block;
    margin-bottom: 1rem;
    padding: 0.35rem 1rem;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: #4F46E5;
    background: rgba(79, 70, 229, 0.12);
    border-radius: 999px;
}

.premium-subtitle {
    max-width: 760px;
    margin: 0.8rem auto 0;
    font-size: 1.15rem;
    color: #64748B;
    line-height: 1.7;
}
</style>

<div class="premium-header">
    <div class="premium-badge">AI-POWERED QUIZ SYSTEM</div>
    <h1 class="title-text">⚡ SmartQuiz AI</h1>
    <div class="premium-subtitle">
        Generator soal otomatis berbasis AI dengan desain modern,
        cepat, dan akurat.
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2>⚙️ Settings</h2>", unsafe_allow_html=True)
    api_key_input = st.text_input("Gemini API Key", type="password", placeholder="Paste API Key di sini...")
    st.markdown("---")
    st.caption("Powered by **Google Gemini** & **LoremFlickr**.")

st.markdown("<h3>📋 Konfigurasi Evaluasi</h3>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    mapel = st.text_input("Mata Pelajaran", value="Matematika")
    col_fase, col_kelas = st.columns(2)
    with col_fase:
        fase = st.selectbox("Fase", ["Fase A", "Fase B", "Fase C", "Fase D", "Fase E", "Fase F"], index=4)
    with col_kelas:
        kelas = st.selectbox("Kelas", [f"Kelas {i}" for i in range(1,13)], index=9)
        
    col_format, col_opsi = st.columns([2, 1])
    with col_format:
        format_soal = st.selectbox("Format Soal", ["Pilihan Ganda", "Pilihan Jamak", "Benar Salah", "Uraian"])
    with col_opsi:
        jml_opsi = st.selectbox("Opsi", [0, 1, 2, 3, 4, 5], index=5)

with col2:
    topik = st.text_area("Topik / Tujuan Pembelajaran", value="Struktur Tubuh Manusia", height=115)
    st.markdown("<br>", unsafe_allow_html=True)
    mode_bergambar = st.checkbox("🖼️ Sisipkan Ilustrasi (Auto-generate)", value=True)
    
    st.caption("💡 *Catatan: Gambar diambil secara otomatis dari internet. Jika gambarnya kurang pas dengan soal, Anda bisa menghapus atau menggantinya sendiri nanti di Microsoft Word.*")

st.markdown("---")
col3, col4 = st.columns(2)
with col3:
    st.markdown("<h3>📊 Tingkat Kesulitan</h3>", unsafe_allow_html=True)
    c_m, c_s, c_sl = st.columns(3)
    with c_m: jml_mudah = st.number_input("Mudah", min_value=0, max_value=50, value=3)
    with c_s: jml_sedang = st.number_input("Sedang", min_value=0, max_value=50, value=5)
    with c_sl: jml_sulit = st.number_input("Sulit", min_value=0, max_value=50, value=2)

with col4:
    st.markdown("<h3>🧠 Level Kognitif</h3>", unsafe_allow_html=True)
    kognitif = st.multiselect(
        "Pilih taksonomi Bloom", 
        ["C1 (Mengingat)", "C2 (Memahami)", "C3 (Menerapkan)", "C4 (Menganalisis)", "C5 (Mengevaluasi)", "C6 (Mencipta)"],
        default=["C2 (Memahami)", "C3 (Menerapkan)"], label_visibility="collapsed"
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
            if 'generateContent' in m.supported_generation_methods and 'flash' in m.name:
                model_terpilih = m.name
                break
        
        if model_terpilih is None:
            st.error("Gagal: API Key tidak valid atau tidak memiliki akses ke model.")
            st.stop()
            
        model = genai.GenerativeModel(model_terpilih)
        
        instruksi_format = ""
        if format_soal == "Benar Salah":
            instruksi_format = "Format: BENAR/SALAH. Berikan pernyataan, lalu WAJIB berikan HANYA DUA opsi: '- Benar' dan '- Salah'."
        elif format_soal == "Uraian":
            instruksi_format = "Format: URAIAN (Essay). Berikan pertanyaan terbuka. JANGAN berikan opsi jawaban."
        elif format_soal == "Pilihan Jamak":
            instruksi_format = f"Format: PILIHAN JAMAK (Bisa >1 jawaban benar). Berikan {jml_opsi} opsi jawaban."
        else:
            instruksi_format = f"Format: PILIHAN GANDA (1 jawaban benar). Berikan {jml_opsi} opsi jawaban."

        instruksi_gambar = ""
        if mode_bergambar:
            instruksi_gambar = """
            3. ATURAN GAMBAR (SANGAT PENTING): Anda WAJIB menyisipkan 1 gambar di SETIAP soal!
               Gunakan format Kurung Kurawal Ganda persis seperti ini: {{GAMBAR: kata kunci}}
               Ganti kata kunci dengan 1 atau 2 kata benda bahasa Inggris yang sangat umum.
               Contoh Benar: {{GAMBAR: human anatomy}} atau {{GAMBAR: animal cell}}
            """
        else:
            instruksi_gambar = "3. JANGAN menyisipkan gambar apapun ke dalam soal."

        prompt = f"""
        Anda adalah Guru Ahli. Buatkan {total_soal} soal evaluasi.
        DATA: Mapel {mapel} | Kelas {kelas} | Topik: {topik}.
        Fokus Level Kognitif: {', '.join(kognitif)}.
        
        KUOTA TINGKAT KESULITAN:
        - Buat {jml_mudah} soal dengan tingkat MUDAH.
        - Buat {jml_sedang} soal dengan tingkat SEDANG.
        - Buat {jml_sulit} soal dengan tingkat SULIT.
        Total harus pas {total_soal} soal.
        
        ATURAN LAYOUT (WAJIB DIIKUTI 100%):
        1. DILARANG KERAS menggunakan format Heading/Judul Markdown (simbol #, ##, ###) di bagian manapun! Tuliskan nomor soal dengan teks biasa. Gunakan cetak tebal (**teks**) saja jika ingin membuat sub-judul.
        
        2. {instruksi_format}
           Jika ada opsi jawaban, WAJIB ditulis menurun ke bawah diawali tanda strip (-) agar menjadi Bullet Point.
        
        {instruksi_gambar}
           
        4. ATURAN TABEL KUNCI & KISI-KISI: 
           - WAJIB gunakan format tabel Markdown (menggunakan tanda garis vertikal |).
           - DILARANG menggunakan Enter di dalam sel tabel! Gunakan tag <br> jika butuh baris baru.
        
        OUTPUT WAJIB MENGGUNAKAN PEMISAH INI:
        [BAGIAN_SOAL]
        (Isi daftar soal di sini)
        
        [BAGIAN_KUNCI]
        | No | Jawaban | Pembahasan |
        |---|---|---|
        (Lanjutkan tabel kunci)
        
        [BAGIAN_KISI]
        | No | Indikator | Level Kognitif | Tingkat Kesulitan |
        |---|---|---|---|
        (Lanjutkan tabel kisi-kisi)
        """

        with st.spinner(f"⏳ Processing... Menyusun {total_soal} soal dengan AI..."):
            response = model.generate_content(prompt)
            hasil = response.text
            
            hasil_clean = hasil.replace(" A. ", "\n- A. ").replace(" B. ", "\n- B. ").replace(" C. ", "\n- C. ").replace(" D. ", "\n- D. ").replace(" E. ", "\n- E. ")
            hasil_clean = hasil_clean.replace(" Benar\n", "\n- Benar\n").replace(" Salah\n", "\n- Salah\n")
            
            hasil_clean = re.sub(r'^#+\s+(.*)$', r'**\1**', hasil_clean, flags=re.MULTILINE)
            
            def ubah_ke_url(match):
                kata_kunci = match.group(1).strip()
                kata_kunci_aman = urllib.parse.quote(kata_kunci.replace(" ", ","))
                return f"\n\n![Ilustrasi](https://loremflickr.com/500/300/{kata_kunci_aman}/all)\n\n"
            
            hasil_clean = re.sub(r'\{\{GAMBAR:\s*(.*?)\}\}', ubah_ke_url, hasil_clean, flags=re.IGNORECASE)
            
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
            
            with st.spinner("📦 Compiling document... Menyiapkan file Word."):
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