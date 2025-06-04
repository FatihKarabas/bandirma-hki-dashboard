import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import matplotlib.pyplot as plt
import tempfile
import os

# Sayfa Ayarı
st.set_page_config(page_title="Bandırma HKİ Dashboard", layout="wide")

# Veri Yükleme
@st.cache_data
def load_data():
    df = pd.read_excel('Bandirma_AQ.xlsx')
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

df = load_data()

# PDF Fonksiyonu (grafikli)
def generate_pdf(row, en_iyi, en_kotu, daily_data, year_max, month_max):
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

    # En İyi ve En Kötü Gün
    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, 'Dönemin En İyi Değeri', ln=True)
    pdf.set_font('DejaVu', '', 12)
    pdf.multi_cell(0, 10, f"- Tarih: {en_iyi['datetime']}\n- Değer: {en_iyi['hki_genel']}\n- Kategori: {en_iyi['hki_kategori']}\n- Açıklama: {en_iyi['hki_aciklama']}\n- Belirleyici Kirletici: {en_iyi['hki_kaynak']}")
    
    pdf.ln(5)
    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, 'Dönemin En Kötü Değeri', ln=True)
    pdf.set_font('DejaVu', '', 12)
    pdf.multi_cell(0, 10, f"- Tarih: {en_kotu['datetime']}\n- Değer: {en_kotu['hki_genel']}\n- Kategori: {en_kotu['hki_kategori']}\n- Açıklama: {en_kotu['hki_aciklama']}\n- Belirleyici Kirletici: {en_kotu['hki_kaynak']}")
    pdf.ln(5)

    # Bu yılın ve bu ayın en kötü günü
    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, 'Bu Yılın En Kötü Değeri', ln=True)
    pdf.set_font('DejaVu', '', 12)
    pdf.multi_cell(0, 10, f"- Tarih: {year_max['datetime']}\n- Değer: {year_max['hki_genel']}\n- Kategori: {year_max['hki_kategori']}\n- Açıklama: {year_max['hki_aciklama']}\n- Belirleyici Kirletici: {year_max['hki_kaynak']}")

    pdf.ln(5)
    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, 'Bu Ayın En Kötü Değeri', ln=True)
    pdf.set_font('DejaVu', '', 12)
    pdf.multi_cell(0, 10, f"- Tarih: {month_max['datetime']}\n- Değer: {month_max['hki_genel']}\n- Kategori: {month_max['hki_kategori']}\n- Açıklama: {month_max['hki_aciklama']}\n- Belirleyici Kirletici: {month_max['hki_kaynak']}")
    pdf.ln(10)

    # Grafik
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(daily_data['datetime'], daily_data['pm10'], label='PM10')
    ax.plot(daily_data['datetime'], daily_data['so2'], label='SO2')
    ax.plot(daily_data['datetime'], daily_data['no2'], label='NO2')
    ax.plot(daily_data['datetime'], daily_data['o3'], label='O3')
    ax.set_xlabel('Saat')
    ax.set_ylabel('Değer')
    ax.set_title('Günlük Kirletici Değerleri')
    ax.legend()

    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
        plt.savefig(tmpfile.name, bbox_inches='tight')
        plt.close(fig)
        image_path = tmpfile.name

    pdf.image(image_path, x=10, y=None, w=190)
    os.remove(image_path)

    return pdf.output(dest='S').encode('latin1', 'replace')

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
    generate_button = st.button("📥 PDF Raporu İndir")

# --- VERİLER ---
row = df[df['datetime'].dt.date == selected_date].iloc[0]
filtered = df[(df['datetime'].dt.year == selected_year) & (df['datetime'].dt.month == selected_month)]

en_iyi = filtered.loc[filtered['hki_genel'].idxmin()]
en_kotu = filtered.loc[filtered['hki_genel'].idxmax()]

year_filtered = df[df['datetime'].dt.year == selected_year]
month_filtered = df[(df['datetime'].dt.year == selected_year) & (df['datetime'].dt.month == selected_month)]

year_max = year_filtered.loc[year_filtered['hki_genel'].idxmax()]
month_max = month_filtered.loc[month_filtered['hki_genel'].idxmax()]

# --- SAYFA BAŞLIĞI ---
st.markdown("<h1 style='text-align: center; font-size:30px;'>Bandırma Hava Kalitesi İndeksi (HKİ) Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- BİLGİ KARTLARI ---
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        f"""
        <div style="background-color:{row['hki_renk']};padding:15px;border-radius:10px;">
        <h4 style="text-align:center;">📅 Seçilen Gün</h4>
        <p><b>Tarih:</b> {row['datetime'].strftime('%Y-%m-%d')}</p>
        <p><b>Kategori:</b> {row['hki_kategori']}</p>
        <p><b>Kirletici:</b> {row['hki_kaynak']}</p>
        </div>
        """, unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="background-color:{en_kotu['hki_renk']};padding:15px;border-radius:10px;">
        <h4 style="text-align:center;">⚡ Dönemin En Kötüsü</h4>
        <p><b>Tarih:</b> {en_kotu['datetime'].strftime('%Y-%m-%d')}</p>
        <p><b>Kategori:</b> {en_kotu['hki_kategori']}</p>
        <p><b>Kirletici:</b> {en_kotu['hki_kaynak']}</p>
        </div>
        """, unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div style="background-color:{year_max['hki_renk']};padding:15px;border-radius:10px;">
        <h4 style="text-align:center;">🗓️ Bu Yılın En Kötüsü</h4>
        <p><b>Tarih:</b> {year_max['datetime'].strftime('%Y-%m-%d')}</p>
        <p><b>Kategori:</b> {year_max['hki_kategori']}</p>
        <p><b>Kirletici:</b> {year_max['hki_kaynak']}</p>
        </div>
        """, unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div style="background-color:{month_max['hki_renk']};padding:15px;border-radius:10px;">
        <h4 style="text-align:center;">📆 Bu Ayın En Kötüsü</h4>
        <p><b>Tarih:</b> {month_max['datetime'].strftime('%Y-%m-%d')}</p>
        <p><b>Kategori:</b> {month_max['hki_kategori']}</p>
        <p><b>Kirletici:</b> {month_max['hki_kaynak']}</p>
        </div>
        """, unsafe_allow_html=True
    )

# --- GRAFİKLER ---
st
