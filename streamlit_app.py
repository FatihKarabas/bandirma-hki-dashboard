import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from io import BytesIO

# Sayfa Yapılandırması
st.set_page_config(page_title="Bandırma HKİ Dashboard", layout="wide", page_icon="🌍")

# Veri Yükleme
@st.cache_data
def load_data():
    df = pd.read_excel('Bandirma_AQ.xlsx')
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

df = load_data()

# Sidebar Yapısı
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Logo_Band%C4%B1rma.png/600px-Logo_Band%C4%B1rma.png", width=120)
    st.title("🌍 Bandırma HKİ (Hava Kalitesi İndeksi) ")

    st.markdown("Hava Kalitesi Bilgilendirme Platformu")
    st.markdown("---")

    st.subheader("🗓️ Tarih Seçimi")
    selected_date = st.date_input("Tarih", df['datetime'].min().date())

    st.subheader("🗓️ Dönem Seçimi")
    period = st.selectbox("Dönem", ["Günlük", "Aylık", "Yıllık"])
    selected_month = st.selectbox("Ay", sorted(df['month'].unique()))
    selected_year = st.selectbox("Yıl", sorted(df['year'].unique()))

    st.markdown("---")

    st.subheader("📄 Rapor Al")
    generate = st.button("📅 PDF Raporu Oluştur")

    st.markdown("---")
    st.subheader("🔢 Veri Özeti")
    st.markdown(f"**Toplam Gözlem:** {df.shape[0]}")
    st.markdown(f"**Veri Aralığı:** {df['datetime'].min().date()} - {df['datetime'].max().date()}")

    st.info("Bu uygulama 2021-2024 yılları arasında Bandırma bölgesi hava kalitesi verilerini analiz etmektedir.")

# Ana Sayfa
st.title("📊 Hava Kalitesi İndeksi (HKİ) Analizi")
st.markdown(f"**Seçilen Tarih:** {selected_date}")

# Seçilen tarih için filtreleme
selected_row = df[df['datetime'].dt.date == selected_date]

if not selected_row.empty:
    row = selected_row.iloc[0]
    st.markdown(f"""
    - **Kategori:** {row['hki_kategori']}
    - **Renk:** {row['hki_renk']}
    - **Açıklama:** {row['hki_aciklama']}
    - **Belirleyici Kirletici:** {row['hki_kaynak']}
    """)
else:
    st.warning("Seçilen tarihte veri bulunamadı.")

# Grafik - Hava Kalitesi
fig = px.line(df[df['datetime'].dt.month == selected_month], x='datetime', y=['pm10', 'so2', 'no2', 'o3'],
              labels={'value': 'Konsantrasyon (µg/m³)', 'datetime': 'Tarih'}, title="Aylık Hava Kalitesi Trendleri")
fig.update_layout(legend_title_text='Kirletici Türü')
st.plotly_chart(fig, use_container_width=True)

# PDF Raporu Oluşturma Fonksiyonu
def generate_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
    pdf.set_font('DejaVu', 'B', 16)
    pdf.cell(0, 10, 'Bandırma Hava Kalitesi Raporu', ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('DejaVu', '', 12)
    pdf.multi_cell(0, 10, f"""
    Tarih: {row['datetime'].date()}
    Kategori: {row['hki_kategori']}
    Renk: {row['hki_renk']}
    Açıklama: {row['hki_aciklama']}
    Belirleyici Kirletici: {row['hki_kaynak']}
    """)
    return pdf.output(dest='S').encode('latin-1')

if generate and not selected_row.empty:
    pdf_content = generate_pdf(row)
    st.download_button(label="PDF Raporunu 🔥 İndir", data=BytesIO(pdf_content), file_name="hava_kalitesi_raporu.pdf", mime="application/pdf")
