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

# =====================================================
# 1. KONFIGURASI HALAMAN & TEMA RESPONSIVE MODERN
# =====================================================
st.set_page_config(page_title="SmartQuiz AI", page_icon="⚡", layout="wide")

st.markdown("""
<style>
/* Import Font Premium */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { 
    font-family: 'Plus Jakarta Sans', sans-serif !important; 
}

/* Background Aplikasi - Gradien Halus */
[data-testid="stAppViewContainer"] { 
    background: linear-gradient(135deg, #F0F4F8 0%, #D9E2EC 100%); 
}

/* Container Utama (Glassmorphism / Efek Kaca) */
[data-testid="block-container"] {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 3rem 4rem;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.6);
    margin-top: 2rem;
    margin-bottom: 2rem;
}

/* Teks Judul Gradient */
.title-text {
    background: linear-gradient(135deg, #4338CA 0%, #EC4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 3.5rem;
    letter-spacing: -1px;
    line-height: 1.2;
}

/* Modifikasi Input, Select Box, Text Area */
div[data-baseweb="input"] > div, 
div[data-baseweb="select"] > div, 
div[data-baseweb="textarea"] > div {
    border-radius: 12px !important;
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
    transition: all 0.3s ease;
}

/* Efek saat Input diklik (Fokus) */
div[data-baseweb="input"] > div:focus-within, 
div[data-baseweb="select"] > div:focus-within, 
div[data-baseweb="textarea"] > div:focus-within {
    border-color: #4F46E5 !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2) !important;
}

/* Tombol Generate Premium */
.stButton > button {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    color: white;
    font-weight: 700;
    font-size: 1.1rem;
    border-radius: 14px;
    padding: 0.8rem;
    width: 100%;
    border: none;
    box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Efek Hover Tombol */
.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(79, 70, 229, 0.45);
    color: white;
}

/* Desain Tab Navigation */
[data-baseweb="tab-list"] { gap: 1.5rem; border-bottom: 2px solid #E2E8F0; margin-bottom: 1rem;}
[data-baseweb="tab"] { font-weight: 600; font-size: 1.05rem; color: #64748B; padding-bottom: 0.8rem; transition: color 0.3s ease;}
[data-baseweb="tab"]:hover { color: #4F46E5; }
[data-baseweb="tab"][aria-selected="true"] { color: #4F46E5; }
[data-baseweb="tab-highlight"] { background-color: #4F46E5; height: 3px; border-radius: 3px 3px 0 0; }

/* ======== CSS RESPONSIVE UNTUK LAYAR HP & TABLET ======== */
@media (max-width: 768px) {
    [data-testid="block-container"] {
        padding: 1.5rem 1.2rem; /* Memperkecil padding di HP agar layar tidak penuh border */
        border-radius: 16px;
        margin-top: 0.5rem;
    }
    .title-text {
        font-size: 2.2rem; /* Mengecilkan teks judul di HP */
    }
    h3 {
        font-size: 1.3rem; /* Mengecilkan teks sub-judul */
    }
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 2. HEADER
# =====================================================
st.markdown("""
<div style="text-align:center; margin-bottom:2rem;">
    <div style="font-size:0.8rem; font-weight:700; color:#4F46E5; letter-spacing:0.1em; text-transform:uppercase;">
        100% Free AI-Powered System
    </div>
    <h1 class="title-text"> SmartQuiz AI</h1>
    <p style="color:#64748B; font-size:1.15rem; max-width: 1200px; margin: 0.5rem auto;">
        Generator soal otomatis berbasis AI dengan desain modern, cepat, dan akurat.
    </p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# 3. FUNGSI EXPORT KE WORD (DENGAN GAMBAR)
# =====================================================
def export_to_docx(judul, info, hasil_ai):
    doc = Document()
    header = doc.add_heading(judul, 0)
    header.alignment = 1

    table = doc.add_table(rows=3, cols=2)
    table.style = 'Table Grid'
    table.rows[0].cells[0].text = "Mata Pelajaran"
    table.rows[0].cells[1].text = info["mapel"]
    table.rows[1].cells[0].text = "Kelas"
    table.rows[1].cells[1].text = info["kelas"]
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

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# =====================================================
# 4. SIDEBAR (HANYA GEMINI - 100% GRATIS)
# =====================================================
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; justify-content: center; margin-bottom: 10px;">
            <img src="https://i.ibb.co.com/4gdKY9Zj/Desain-tanpa-judul-2.png", width="80">
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.header("⚙️ Autentikasi Sistem")
    api_key = st.text_input("🔑 Google Gemini API Key", type="password", placeholder="Mulai dengan 'AIzaSy...'")
    st.markdown("---")
    st.markdown("✨ **Fitur Unggulan:**")
    st.markdown("- 🚀 Generasi Super Cepat\n- 📱 Responsif di HP & Tablet\n- 🖼️ Dukungan Gambar Otomatis\n- 📄 Export format Word (.docx)")

# =====================================================
# 5. FUNGSI GENERATE AI TERBARU
# =====================================================
def generate_with_gemini(prompt, api_key):
    genai.configure(api_key=api_key)
    
    model_name = "gemini-1.5-flash"
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods and 'flash' in m.name:
            model_name = m.name
            break
            
    model = genai.GenerativeModel(model_name)
    return model.generate_content(prompt).text

# =====================================================
# 6. FORM INPUT 
# =====================================================
st.markdown("### 📋 Konfigurasi Evaluasi")

col1, col2 = st.columns(2)
with col1:
    mapel = st.text_input("📚 Mata Pelajaran", "Isi Mata Pelajaran")
    kelas = st.selectbox("🎓 Kelas", [f"Kelas {i}" for i in range(1,13)], index=9)
    format_soal = st.selectbox(
        "📝 Format Soal",
        ["Pilihan Ganda", "Pilihan Jamak", "Benar Salah", "Uraian"]
    )
    jml_opsi = st.selectbox("🔢 Jumlah Opsi/Pernyataan", [0,1,2,3,4,5], index=0)

with col2:
    topik = st.text_area("🎯 Topik / Tujuan Pembelajaran", "isi materi pelajaran", height=115)
    
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    mode_bergambar = st.checkbox("🖼️ Sisipkan Ilustrasi Gambar (Auto-generate)", value=True)
    st.caption("💡 Catatan: Gambar diambil secara otomatis dari internet. Jika gambarnya kurang pas dengan soal, Anda bisa menghapus atau menggantinya sendiri nanti di Microsoft Word.")

st.markdown("---")

st.markdown("### 📊 Detail Komposisi Soal")
c1, c2, c3 = st.columns(3)
with c1: jml_mudah = st.number_input("🙂‍ Mudah", 0, 50, 0)
with c2: jml_sedang = st.number_input("☹️ Sedang", 0, 50, 0)
with c3: jml_sulit = st.number_input("😱 Sulit", 0, 50, 0)

total_soal = jml_mudah + jml_sedang + jml_sulit

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
kognitif = st.multiselect(
    "📌 Level Kognitif (Taksonomi Bloom)",
    ["C1 (Mengingat)", "C2 (Memahami)", "C3 (Menerapkan)", "C4 (Menganalisis)", "C5 (Mengevaluasi)", "C6 (Mencipta)"],
    default=["C2 (Memahami)", "C3 (Menerapkan)"]
)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# 7. LOGIKA GENERASI SOAL & GAMBAR
# =====================================================
instruksi_format = ""
if format_soal == "Benar Salah":
    instruksi_format = (
        f"Format BENAR/SALAH.\n"
        f"SETIAP SATU NOMOR soal berisi {jml_opsi} PERNYATAAN.\n\n"
        f"Aturan penulisan (WAJIB DIIKUTI 100%):\n"
        f"- Tulis 1 nomor soal utama di baris pertama.\n"
        f"- WAJIB BUAT BARIS BARU (ENTER) ke bawah untuk menulis setiap pernyataan.\n"
        f"- Buat {jml_opsi} pernyataan berlabel a., b., c., dst secara MENURUN KE BAWAH.\n"
        f"- DILARANG KERAS menggabungkan pernyataan a, b, c dalam satu paragraf!\n\n"
        f"Contoh format yang WAJIB DITIRU:\n"
        f"1. Perhatikan pernyataan berikut:\n"
        f"a. Jantung berfungsi memompa darah.\n"
        f"b. Lambung adalah organ pernapasan.\n"
        f"Tentukan apakah setiap pernyataan di atas BENAR atau SALAH."
    )
elif format_soal == "Uraian":
    instruksi_format = "Format URAIAN (Essay). Berikan pertanyaan terbuka tanpa opsi jawaban. Tuliskan teks soal dengan rapi."
elif format_soal == "Pilihan Jamak":
    instruksi_format = (
        f"Format PILIHAN JAMAK (Bisa >1 jawaban benar).\n"
        f"Setiap soal WAJIB memiliki {jml_opsi} opsi jawaban.\n\n"
        f"Aturan penulisan (WAJIB DIIKUTI 100%):\n"
        f"Setelah penulisan soal tambahkan keterangan penulisan jawaban lebih dari 1 (WAJIB DIIKUTI 100%):\n"
        f"- WAJIB BUAT BARIS BARU (ENTER) ke bawah untuk menulis setiap opsi jawaban.\n"
        f"- Buat opsi berlabel A., B., C., dst secara MENURUN KE BAWAH.\n"
        f"- TIDAK BOLEH menggabungkan opsi A, B, C dalam satu paragraf yang sama!\n"
    )
else:
    instruksi_format = (
        f"Format PILIHAN GANDA (1 jawaban benar).\n"
        f"Setiap soal WAJIB memiliki {jml_opsi} opsi jawaban.\n\n"
        f"Aturan penulisan (WAJIB DIIKUTI 100%):\n"
        f"- WAJIB BUAT BARIS BARU (ENTER) ke bawah untuk menulis setiap opsi jawaban.\n"
        f"- Buat opsi berlabel A., B., C., dst secara MENURUN KE BAWAH.\n"
        f"- TIDAK BOLEH menggabungkan opsi A, B, C dalam satu paragraf yang sama!\n"
    )

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

if st.button("🚀 Generate Evaluasi Sekarang", use_container_width=True):
    if not api_key:
        st.error("⚠️ Masukkan API Key Google Gemini di menu sidebar kiri.")
        st.stop()
    if total_soal == 0:
        st.warning("⚠️ Total soal tidak boleh 0.")
        st.stop()

    prompt = f"""
    Anda adalah Guru Ahli.

    Buatkan {total_soal} soal evaluasi.
    Mapel: {mapel}
    Kelas: {kelas}
    Topik: {topik}
    Level Kognitif: {', '.join(kognitif)}

    Distribusi Kesulitan:
    - Mudah: {jml_mudah}
    - Sedang: {jml_sedang}
    - Sulit: {jml_sulit}

    ATURAN LAYOUT (WAJIB DIIKUTI 100%):
    1. DILARANG KERAS menggunakan format Heading/Judul Markdown (simbol #, ##, ###) di bagian manapun! Tuliskan nomor soal dengan teks biasa. Gunakan cetak tebal (**teks**) saja jika ingin membuat sub-judul.
    
    2. {instruksi_format}
    
    {instruksi_gambar}

    Di akhir, sertakan:
    [BAGIAN_KUNCI] 
    (Buat tabel Kunci Jawaban dan Pembahasan di sini)
    
    [BAGIAN_KISI] 
    WAJIB buat dalam format Tabel Markdown dengan struktur persis seperti ini:
    | No | Indikator Soal | Level Kognitif | Tingkat Kesulitan |
    |---|---|---|---|
    (Isi tabel kisi-kisi di sini)
    """

    try:
        with st.spinner("⏳ Memproses data... AI sedang menyusun soal untuk Anda."):
            hasil = generate_with_gemini(prompt, api_key)

        st.success("✨ Selesai! Evaluasi berhasil di-generate.")

        # Mencegah Teks Raksasa
        hasil_clean = re.sub(r'^#+\s+(.*)$', r'**\1**', hasil, flags=re.MULTILINE)
        
        # --- SISTEM GAMBAR LOREMFLICKR ---
        def ubah_ke_url(match):
            kata_kunci = match.group(1).strip()
            kata_kunci_aman = urllib.parse.quote(kata_kunci.replace(" ", ","))
            return f"\n\n![Ilustrasi](https://loremflickr.com/500/300/{kata_kunci_aman}/all)\n\n"
        
        if mode_bergambar:
            hasil_clean = re.sub(r'\{\{GAMBAR:\s*(.*?)\}\}', ubah_ke_url, hasil_clean, flags=re.IGNORECASE)

        # Memisahkan hasil teks AI menjadi 3 bagian
        parts = re.split(r'\[BAGIAN_KUNCI\]|\[BAGIAN_KISI\]', hasil_clean)
        soal_teks = parts[0].strip()
        kunci_teks = parts[1].strip() if len(parts) > 1 else "Kunci jawaban gagal dibuat."
        kisi_teks = parts[2].strip() if len(parts) > 2 else "Kisi-kisi gagal dibuat."

        # Menampilkan di Tab
        st.markdown("<br>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["📄 Soal Evaluasi", "🔑 Kunci Jawaban", "📊 Kisi-kisi"])

        with tab1:
            st.markdown(soal_teks)
        with tab2:
            st.markdown(kunci_teks)
        with tab3:
            st.markdown(kisi_teks)
            
        st.markdown("---")
        
        # Logika Tombol Download Word
        with st.spinner("📦 Menyiapkan file Microsoft Word (.docx)..."):
            info_doc = {"mapel": mapel, "kelas": kelas, "topik": topik}
            
            # Gabungkan kembali untuk diexport
            formatted_content = f"{soal_teks}\n\n## Kunci Jawaban\n{kunci_teks}\n\n## Kisi-kisi\n{kisi_teks}"
            
            doc_buffer = export_to_docx(f"KUMPULAN SOAL: {mapel} ({kelas})", info_doc, formatted_content)
            
            st.download_button(
                label="⬇️ Download MS Word (.docx)",
                data=doc_buffer.getvalue(),
                file_name=f"Soal_{mapel}_{kelas}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

    except Exception as e:

        st.error(f"Terjadi kesalahan: Pastikan API Key Gemini Anda valid. (Error Detail: {e})")
