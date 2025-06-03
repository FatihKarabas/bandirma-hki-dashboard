import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64

# Sayfa Ayarı
st.set_page_config(page_title="Bandırma HKİ Dashboard", layout="wide")

# Veri Yükleme
@st.cache_data
def load_data():
    df = pd.read_excel('Bandirma_AQ.xlsx')
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

df = load_data()

# PDF Fonksiyonları
def generate_pdf(row, en_iyi, en_kotu):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
    
    pdf.set_font('DejaVu', 'B', 16)
    pdf.cell(0, 10, 'Bandırma Hava Kalitesi Raporu', ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font('DejaVu', '', 12)
    pdf.cell(0, 10, f"Tarih: {row['datetime']}", ln=True)
    pdf.cell(0, 10, f"Kategori: {row['hki_kategori']}", ln=True)
    pdf.cell(0, 10, f"Açıklama: {row['hki_aciklama']}", ln=True)
    pdf.cell(0, 10, f"Belirleyici Kirletici: {row['hki_kaynak']}", ln=True)
    pdf.ln(10)

    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, 'Seçilen Dönemde En İyi Değer', ln=True)
    pdf.set_font('DejaVu', '', 12)
    pdf.multi_cell(0, 10, f"- Tarih: {en_iyi['datetime']}\n- Değer: {en_iyi['hki_genel']}\n- Kategori: {en_iyi['hki_kategori']}\n- Açıklama: {en_iyi['hki_aciklama']}\n- Belirleyici Kirletici: {en_iyi['hki_kaynak']}")

    pdf.ln(10)
    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, 'Seçilen Dönemde En Kötü Değer', ln=True)
    pdf.set_font('DejaVu', '', 12)
    pdf.multi_cell(0, 10, f"- Tarih: {en_kotu['datetime']}\n- Değer: {en_kotu['hki_genel']}\n- Kategori: {en_kotu['hki_kategori']}\n- Açıklama: {en_kotu['hki_aciklama']}\n- Belirleyici Kirletici: {en_kotu['hki_kaynak']}")

    return pdf.output(dest='S').encode('latin1', 'replace')

def get_pdf_download_link(pdf_content):
    b64 = base64.b64encode(pdf_content).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="hava_kalitesi_raporu.pdf">📄 PDF İndir</a>'
    return href

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔎 Seçim Paneli")
    st.markdown("---")
    st.subheader("📅 Tarih Seçimi")
    selected_date = st.date_input(
        "Tarih Seçiniz", 
        min_value=df['datetime'].min().date(), 
        max_value=df['datetime'].max().date()
    )

    st.markdown("---")
    st.subheader("📆 Dönem Seçimi")
    selected_year = st.selectbox("Yıl Seçiniz", sorted(df['datetime'].dt.year.unique()))
    selected_month = st.selectbox("Ay Seçiniz", sorted(df[df['datetime'].dt.year == selected_year]['datetime'].dt.month.unique()))

    st.markdown("---")
    st.subheader("📄 PDF Rapor")
    generate_button = st.button("📥 Raporu İndir")

# --- Veri Seçimi ---
row = df[df['datetime'].dt.date == selected_date].iloc[0]
filtered = df[(df['datetime'].dt.year == selected_year) & (df['datetime'].dt.month == selected_month)]

en_iyi = filtered.loc[filtered['hki_genel'].idxmin()]
en_kotu = filtered.loc[filtered['hki_genel'].idxmax()]

# --- SAYFA ÜSTÜ ---
st.markdown("<h1 style='text-align: center; font-size:30px;'>Bandırma Hava Kalitesi İndeksi (HKİ) Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- BİLGİ KARTLARI ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div style="background-color:{row['hki_renk']};padding:20px;border-radius:10px;">
        <h3 style="text-align:left;">❤️ <span style="color:white;">{row['hki_kategori']}</span></h3>
        <ul style="text-align:left; font-size:16px;">
            <li><b>Tarih:</b> {row['datetime'].strftime('%Y-%m-%d %H:%M')}</li>
            <li><b>Açıklama:</b> {row['hki_aciklama']}</li>
            <li><b>Belirleyici Kirletici:</b> {row['hki_kaynak']}</li>
        </ul>
        </div>
        """, unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="background-color:{en_iyi['hki_renk']};padding:20px;border-radius:10px;">
        <h3 style="text-align:center;">✅ En İyi Gün</h3>
        <ul style="text-align:left; font-size:16px;">
            <li><b>Tarih:</b> {en_iyi['datetime'].strftime('%Y-%m-%d %H:%M')}</li>
            <li><b>Değer:</b> {en_iyi['hki_genel']}</li>
            <li><b>Kategori:</b> {en_iyi['hki_kategori']}</li>
            <li><b>Açıklama:</b> {en_iyi['hki_aciklama']}</li>
            <li><b>Kirletici:</b> {en_iyi['hki_kaynak']}</li>
        </ul>
        </div>
        """, unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div style="background-color:{en_kotu['hki_renk']};padding:20px;border-radius:10px;">
        <h3 style="text-align:center;">❌ En Kötü Gün</h3>
        <ul style="text-align:left; font-size:16px;">
            <li><b>Tarih:</b> {en_kotu['datetime'].strftime('%Y-%m-%d %H:%M')}</li>
            <li><b>Değer:</b> {en_kotu['hki_genel']}</li>
            <li><b>Kategori:</b> {en_kotu['hki_kategori']}</li>
            <li><b>Açıklama:</b> {en_kotu['hki_aciklama']}</li>
            <li><b>Kirletici:</b> {en_kotu['hki_kaynak']}</li>
        </ul>
        </div>
        """, unsafe_allow_html=True
    )

# --- GRAFİK ---
st.markdown("### 📈 Seçilen Gün Kirletici Trendleri")
daily_data = df[df['datetime'].dt.date == selected_date]
fig = px.line(
    daily_data, 
    x='datetime', 
    y=['pm10', 'so2', 'no2', 'o3'],
    labels={'value': 'Değer', 'datetime': 'Saat'},
)
fig.update_layout(
    height=300, 
    margin=dict(l=20, r=20, t=30, b=20),
    legend_title_text='Kirleticiler'
)
st.plotly_chart(fig, use_container_width=True)

# --- PDF İNDİRME ---
if generate_button:
    pdf_content = generate_pdf(row, en_iyi, en_kotu)
    st.markdown(get_pdf_download_link(pdf_content), unsafe_allow_html=True)
