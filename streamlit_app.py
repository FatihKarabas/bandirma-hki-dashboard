import streamlit as st import pandas as pd import plotly.express as px from fpdf import FPDF from io import BytesIO import matplotlib.pyplot as plt import matplotlib.dates as mdates from tempfile import NamedTemporaryFile

Sayfa Yapılandırması

st.set_page_config(page_title="Bandırma HKİ Dashboard", layout="wide", page_icon="🌍")

Veri Yükleme

@st.cache_data def load_data(): df = pd.read_excel('Bandirma_AQ.xlsx') df['datetime'] = pd.to_datetime(df['datetime']) df['year'] = df['datetime'].dt.year df['month'] = df['datetime'].dt.month df['day'] = df['datetime'].dt.date df['hour'] = df['datetime'].dt.hour return df

df = load_data()

Sidebar Yapısı

with st.sidebar: st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Logo_Band%C4%B1rma.png/600px-Logo_Band%C4%B1rma.png", width=120) st.title("🌍 Bandırma HKİ (Hava Kalitesi İndeksi) ")

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

Ana Sayfa

st.title("📊 Hava Kalitesi İndeksi (HKİ) Analizi") st.markdown(f"Seçilen Tarih: {selected_date}")

Seçilen tarih için filtreleme

selected_row = df[df['datetime'].dt.date == selected_date]

if not selected_row.empty: row = selected_row.iloc[0] st.markdown(f""" - Kategori: {row['hki_kategori']} - Renk: {row['hki_renk']} - Açıklama: {row['hki_aciklama']} - Belirleyici Kirletici: {row['hki_kaynak']} """) else: st.warning("Seçilen tarihte veri bulunamadı.")

Döneme göre filtreleme

if period == "Günlük": period_df = df[df['datetime'].dt.date == selected_date] elif period == "Aylık": period_df = df[(df['month'] == selected_month) & (df['year'] == selected_year)] elif period == "Yıllık": period_df = df[df['year'] == selected_year] else: period_df = df.copy()

Grafik - Hava Kalitesi

fig = px.line( period_df, x='datetime', y=['pm10', 'so2', 'no2', 'o3'], labels={'value': 'Konsantrasyon (µg/m³)', 'datetime': 'Tarih'}, title=f"{period} Hava Kalitesi Trendleri" ) fig.update_layout(legend_title_text='Kirletici Türü') st.plotly_chart(fig, use_container_width=True)

PDF Raporu Oluşturma Fonksiyonu

def generate_pdf(row, best_row, worst_row, plot_path): pdf = FPDF() pdf.add_page() pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True) pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True) pdf.set_font('DejaVu', 'B', 16) pdf.cell(0, 10, 'Bandırma Hava Kalitesi Raporu', ln=True, align='C') pdf.ln(10) pdf.set_font('DejaVu', '', 12) pdf.multi_cell(0, 10, f""" Tarih: {row['datetime'].date()} HKİ: {row['hki']} Kategori: {row['hki_kategori']} Renk: {row['hki_renk']} Açıklama: {row['hki_aciklama']} Belirleyici Kirletici: {row['hki_kaynak']}

En İyi HKİ (Seçilen Dönem): {best_row['hki']} - {best_row['datetime']}
En Kötü HKİ (Seçilen Dönem): {worst_row['hki']} - {worst_row['datetime']}
""")
pdf.image(plot_path, x=10, y=None, w=180)
return pdf.output(dest='S').encode('latin-1')

Matplotlib ile grafik oluşturup geçici olarak kaydet

best_row, worst_row = None, None if not period_df.empty: best_row = period_df.loc[period_df['hki'].idxmin()] worst_row = period_df.loc[period_df['hki'].idxmax()]

fig2, ax = plt.subplots(figsize=(10, 4))
ax.plot(period_df['datetime'], period_df['hki'], label='HKİ', color='tab:blue')
ax.set_title(f"{period} HKİ Değişimi")
ax.set_xlabel("Tarih")
ax.set_ylabel("HKİ")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.tick_params(axis='x', rotation=45)
ax.grid(True)
plt.tight_layout()

with NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
    plt.savefig(tmpfile.name)
    image_path = tmpfile.name

if generate and not selected_row.empty:
    pdf_content = generate_pdf(row, best_row, worst_row, image_path)
    st.download_button(label="📄 PDF Raporunu İndir", data=BytesIO(pdf_content), file_name="hava_kalitesi_raporu.pdf", mime="application/pdf")

Sorgular

st.header(f"📈 {period} İçin En İyi ve En Kötü HKİ Analizi")

if not period_df.empty: st.subheader("✅ En İyi HKİ Verisi") st.markdown(f""" - Tarih/Saat: {best_row['datetime']} - HKİ: {best_row['hki']} - Kategori: {best_row['hki_kategori']} - Renk: {best_row['hki_renk']} - Kirletici: {best_row['hki_kaynak']} - Açıklama: {best_row['hki_aciklama']} """)

st.subheader("❌ En Kötü HKİ Verisi")
st.markdown(f"""
- **Tarih/Saat:** {worst_row['datetime']}
- **HKİ:** {worst_row['hki']}
- **Kategori:** {worst_row['hki_kategori']}
- **Renk:** {worst_row['hki_renk']}
- **Kirletici:** {worst_row['hki_kaynak']}
- **Açıklama:** {worst_row['hki_aciklama']}
""")

else: st.warning(f"{period} için veri bulunamadı.")

