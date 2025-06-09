import streamlit as st import pandas as pd import plotly.express as px from fpdf import FPDF from io import BytesIO

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

Grafik - Hava Kalitesi

df_filtered = df[(df['datetime'].dt.month == selected_month) & (df['datetime'].dt.year == selected_year)] fig = px.line(df_filtered, x='datetime', y=['pm10', 'so2', 'no2', 'o3'], labels={'value': 'Konsantrasyon (µg/m³)', 'datetime': 'Tarih'}, title="Aylık Hava Kalitesi Trendleri") fig.update_layout(legend_title_text='Kirletici Türü') st.plotly_chart(fig, use_container_width=True)

PDF Raporu Oluşturma Fonksiyonu

def generate_pdf(row): pdf = FPDF() pdf.add_page() pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True) pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True) pdf.set_font('DejaVu', 'B', 16) pdf.cell(0, 10, 'Bandırma Hava Kalitesi Raporu', ln=True, align='C') pdf.ln(10) pdf.set_font('DejaVu', '', 12) pdf.multi_cell(0, 10, f""" Tarih: {row['datetime'].date()} HKİ: {row['hki']} Kategori: {row['hki_kategori']} Renk: {row['hki_renk']} Açıklama: {row['hki_aciklama']} Belirleyici Kirletici: {row['hki_kaynak']} """) return pdf.output(dest='S').encode('latin-1')

if generate and not selected_row.empty: pdf_content = generate_pdf(row) st.download_button(label="PDF Raporunu 🔥 İndir", data=BytesIO(pdf_content), file_name="hava_kalitesi_raporu.pdf", mime="application/pdf")

Sorgular

st.header("🔍 Seçilen Zamanlara Göre HKİ Sorguları")

1. Seçilen gün ve saat

st.subheader("1️⃣ Seçilen Gün ve Saat Bilgisi") if not selected_row.empty: row = selected_row.iloc[0] st.write(f"🕒 Saat: {row['datetime'].hour}:00") st.markdown(f""" - HKİ Değeri: {row['hki']} - Kategori: {row['hki_kategori']} - Renk: {row['hki_renk']} - Belirleyici Kirletici: {row['hki_kaynak']} - Açıklama: {row['hki_aciklama']} """) else: st.warning("Seçilen saatlik veriye ulaşılamadı.")

2. Yıllık analiz

year_df = df[df['year'] == selected_year] if not year_df.empty: st.subheader("2️⃣ Seçilen Yıl İçin HKİ Özeti") best_year_row = year_df.loc[year_df['hki'].idxmin()] worst_year_row = year_df.loc[year_df['hki'].idxmax()]

st.markdown("**2.a En İyi Gün (Yıl İçinde)**")
st.markdown(f"""
- **Tarih:** {best_year_row['datetime']}
- **HKİ:** {best_year_row['hki']}
- **Kategori:** {best_year_row['hki_kategori']}
- **Renk:** {best_year_row['hki_renk']}
- **Kirletici:** {best_year_row['hki_kaynak']}
- **Açıklama:** {best_year_row['hki_aciklama']}
""")

st.markdown("**2.b En Kötü Gün (Yıl İçinde)**")
st.markdown(f"""
- **Tarih:** {worst_year_row['datetime']}
- **HKİ:** {worst_year_row['hki']}
- **Kategori:** {worst_year_row['hki_kategori']}
- **Renk:** {worst_year_row['hki_renk']}
- **Kirletici:** {worst_year_row['hki_kaynak']}
- **Açıklama:** {worst_year_row['hki_aciklama']}
""")

else: st.warning("Seçilen yıl için veri bulunamadı.")

3. Aylık analiz

month_df = df[(df['month'] == selected_month) & (df['year'] == selected_year)] if not month_df.empty: st.subheader("3️⃣ Seçilen Ay İçin HKİ Özeti") best_month_row = month_df.loc[month_df['hki'].idxmin()] worst_month_row = month_df.loc[month_df['hki'].idxmax()]

st.markdown("**3.a En İyi Gün (Ay İçinde)**")
st.markdown(f"""
- **Tarih:** {best_month_row['datetime']}
- **HKİ:** {best_month_row['hki']}
- **Kategori:** {best_month_row['hki_kategori']}
- **Renk:** {best_month_row['hki_renk']}
- **Kirletici:** {best_month_row['hki_kaynak']}
- **Açıklama:** {best_month_row['hki_aciklama']}
""")

st.markdown("**3.b En Kötü Gün (Ay İçinde)**")
st.markdown(f"""
- **Tarih:** {worst_month_row['datetime']}
- **HKİ:** {worst_month_row['hki']}
- **Kategori:** {worst_month_row['hki_kategori']}
- **Renk:** {worst_month_row['hki_renk']}
- **Kirletici:** {worst_month_row['hki_kaynak']}
- **Açıklama:** {worst_month_row['hki_aciklama']}
""")

else: st.warning("Seçilen ay için veri bulunamadı.")

4. Günlük analiz

day_df = df[df['datetime'].dt.date == selected_date] if not day_df.empty: st.subheader("4️⃣ Seçilen Gün İçin HKİ Özeti") best_day_row = day_df.loc[day_df['hki'].idxmin()] worst_day_row = day_df.loc[day_df['hki'].idxmax()]

st.markdown("**4.a Gün İçindeki En İyi Saat**")
st.markdown(f"""
- **Saat:** {best_day_row['datetime'].hour}:00
- **HKİ:** {best_day_row['hki']}
- **Kategori:** {best_day_row['hki_kategori']}
- **Renk:** {best_day_row['hki_renk']}
- **Kirletici:** {best_day_row['hki_kaynak']}
- **Açıklama:** {best_day_row['hki_aciklama']}
""")

st.markdown("**4.b Gün İçindeki En Kötü Saat**")
st.markdown(f"""
- **Saat:** {worst_day_row['datetime'].hour}:00
- **HKİ:** {worst_day_row['hki']}
- **Kategori:** {worst_day_row['hki_kategori']}
- **Renk:** {worst_day_row['hki_renk']}
- **Kirletici:** {worst_day_row['hki_kaynak']}
- **Açıklama:** {worst_day_row['hki_aciklama']}
""")

else: st.warning("Seçilen gün için saatlik veri bulunamadı.")

