import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from tempfile import NamedTemporaryFile

st.set_page_config(page_title="Bandırma HKİ Dashboard", layout="wide", page_icon="🌍")

# 🧠 HKİ İkon Fonksiyonu
def get_hki_icon(hki_value):
    if hki_value <= 50:
        return "🟢 😊 (İyi)"
    elif hki_value <= 100:
        return "🟡 😐 (Orta)"
    elif hki_value <= 150:
        return "🟠 😷 (Hassas Gruplar)"
    elif hki_value <= 200:
        return "🔴 🤒 (Sağlıksız)"
    elif hki_value <= 300:
        return "🟣 😫 (Kötü)"
    else:
        return "⚫ ☠️ (Tehlikeli)"

# 📄 Veri Yükleme
@st.cache_data
def load_data():
    df = pd.read_excel("Bandirma_AQ.xlsx")
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["year"] = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.month
    df["day"] = df["datetime"].dt.date
    df["hour"] = df["datetime"].dt.hour
    return df

df = load_data()

# 🎛️ Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/tr/thumb/4/49/Bandırma_Onyedi_Eylül_Üniversitesi_logosu.png/600px-Bandırma_Onyedi_Eylül_Üniversitesi_logosu.png", width=150)
    st.title("🌍 Bandırma HKİ Paneli")
    st.markdown("---")
    selected_date = st.date_input("🗓️ Tarih Seç", df["datetime"].min().date())
    period = st.selectbox("📊 Dönem", ["Günlük", "Aylık", "Yıllık"])
    if period in ["Aylık", "Yıllık"]:
        selected_year = st.selectbox("📅 Yıl", sorted(df["year"].unique()))
    else:
        selected_year = None
    if period == "Aylık":
        selected_month = st.selectbox("📆 Ay", sorted(df["month"].unique()))
    else:
        selected_month = None

    st.markdown("---")
    user_name = st.text_input("👤 Adınız Soyadınız", value="Fatih KARABAŞ")
    generate = st.button("📄 PDF Raporu Oluştur")
    st.markdown("---")
    st.info(f"Toplam Gözlem: {df.shape[0]} | Veri Aralığı: {df['datetime'].min().date()} - {df['datetime'].max().date()}")

# 🎯 Seçilen Gün Verisi
st.title("📊 Hava Kalitesi İndeksi (HKİ) Analizi")
st.markdown(f"**Seçilen Tarih:** {selected_date}")

selected_row = df[df["datetime"].dt.date == selected_date]
if not selected_row.empty:
    row = selected_row.iloc[0]
    st.markdown(f"""
    - **HKİ:** {row['hki']} {get_hki_icon(row['hki'])}
    - **Kategori:** {row['hki_kategori']}
    - **Renk:** {row['hki_renk']}
    - **Açıklama:** {row['hki_aciklama']}
    - **Kirletici:** {row['hki_kaynak']}
    """)
else:
    st.warning("Seçilen tarihe ait veri bulunamadı.")

# 📌 Döneme Göre Filtreleme
if period == "Günlük":
    period_df = df[df["datetime"].dt.date == selected_date]
elif period == "Aylık" and selected_month and selected_year:
    period_df = df[(df["month"] == selected_month) & (df["year"] == selected_year)]
elif period == "Yıllık" and selected_year:
    period_df = df[df["year"] == selected_year]
else:
    period_df = df.copy()

# 📈 Trend Grafiği
fig = px.line(
    period_df,
    x="datetime",
    y=["pm10", "so2", "no2", "o3"],
    labels={"value": "Konsantrasyon (µg/m³)", "datetime": "Tarih"},
    title=f"{period} Hava Kalitesi Trendleri"
)
fig.update_layout(legend_title_text="Kirletici")
st.plotly_chart(fig, use_container_width=True)

# 📄 PDF Oluşturma Fonksiyonu
def generate_pdf(row, best_row, worst_row, plot_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.image('./fonts/bandirma_uni_logo.png', x=10, y=8, w=30)
    pdf.set_font('DejaVu', 'B', 16)
    pdf.cell(0, 10, "Bandırma Hava Kalitesi Raporu", ln=True, align="C")
    pdf.set_font("DejaVu", "", 10)
    pdf.cell(0, 10, f"Oluşturulma Tarihi: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="R")
    pdf.ln(5)
    pdf.set_font("DejaVu", "", 12)
    pdf.multi_cell(0, 10, f"""
    Tarih: {row['datetime'].date()}
    HKİ: {row['hki']} - {get_hki_icon(row['hki'])}
    Kategori: {row['hki_kategori']}
    Renk: {row['hki_renk']}
    Açıklama: {row['hki_aciklama']}
    Kirletici: {row['hki_kaynak']}

    En İyi HKİ: {best_row['hki']} - {best_row['datetime']} {get_hki_icon(best_row['hki'])}
    En Kötü HKİ: {worst_row['hki']} - {worst_row['datetime']} {get_hki_icon(worst_row['hki'])}
    """)
    pdf.image(plot_path, x=10, y=None, w=180)
    pdf.set_font("DejaVu", "I", 10)
    pdf.cell(0, 10, f"Raporu hazırlayan: {user_name}", ln=True, align="R")
    return pdf.output(dest="S").encode("latin-1")

# 🖨️ PDF Oluştur
if generate:
    if not selected_row.empty and not period_df.empty:
        best_row = period_df.loc[period_df["hki"].idxmin()]
        worst_row = period_df.loc[period_df["hki"].idxmax()]
        fig2, ax = plt.subplots(figsize=(10, 4))
        ax.plot(period_df["datetime"], period_df["hki"], label="HKİ", color="tab:blue")
        ax.set_title(f"{period} HKİ Değişimi")
        ax.set_xlabel("Tarih")
        ax.set_ylabel("HKİ")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True)
        plt.tight_layout()
        with NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            plt.savefig(tmpfile.name)
            image_path = tmpfile.name
        pdf_content = generate_pdf(row, best_row, worst_row, image_path)
        st.download_button("📄 PDF Raporunu İndir", data=BytesIO(pdf_content), file_name="hava_kalitesi_raporu.pdf", mime="application/pdf")
    else:
        st.warning("PDF oluşturmak için yeterli veri bulunamadı.")

# 📊 En İyi ve Kötü HKİ Değerleri
st.header(f"📌 {period} için En İyi ve En Kötü HKİ Verileri")
if not period_df.empty:
    best_row = period_df.loc[period_df["hki"].idxmin()]
    worst_row = period_df.loc[period_df["hki"].idxmax()]
    st.subheader("✅ En İyi HKİ")
    st.markdown(f"""
    - 🕓 **Zaman:** {best_row['datetime']}
    - **HKİ:** {best_row['hki']} {get_hki_icon(best_row['hki'])}
    - **Kategori:** {best_row['hki_kategori']}
    - **Açıklama:** {best_row['hki_aciklama']}
    """)
    st.subheader("❌ En Kötü HKİ")
    st.markdown(f"""
    - 🕓 **Zaman:** {worst_row['datetime']}
    - **HKİ:** {worst_row['hki']} {get_hki_icon(worst_row['hki'])}
    - **Kategori:** {worst_row['hki_kategori']}
    - **Açıklama:** {worst_row['hki_aciklama']}
    """)
else:
    st.warning(f"{period} dönemine ait analiz yapılamadı.")