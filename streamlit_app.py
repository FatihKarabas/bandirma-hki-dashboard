import streamlit as st import pandas as pd

st.set_page_config(page_title="Bandırma HKİ Dashboard", layout="wide", page_icon="🌍")

def get_hki_icon(hki_value): if hki_value <= 50: return "🟢 😊 (İyi)" elif hki_value <= 100: return "🟡 😐 (Orta)" elif hki_value <= 150: return "🟠 😷 (Hassas Gruplar)" elif hki_value <= 200: return "🔴 🤒 (Sağlıksız)" elif hki_value <= 300: return "🟣 😫 (Kötü)" else: return "⚫ ☠️ (Tehlikeli)"

@st.cache_data def load_data(): df = pd.read_excel("Bandirma_AQ.xlsx") df["datetime"] = pd.to_datetime(df["datetime"]) df["year"] = df["datetime"].dt.year df["month"] = df["datetime"].dt.month df["day"] = df["datetime"].dt.date df["hour"] = df["datetime"].dt.hour return df

df = load_data()

with st.sidebar: st.image("https://upload.wikimedia.org/wikipedia/tr/thumb/4/49/Bandırma_Onyedi_Eylül_Üniversitesi_logosu.png/600px-Bandırma_Onyedi_Eylül_Üniversitesi_logosu.png", width=150) st.title("🌍 Bandırma HKİ Paneli") st.markdown("---") selected_date = st.date_input("🗓️ Tarih Seç", df["datetime"].min().date()) period = st.selectbox("📊 Dönem", ["Günlük", "Aylık", "Yıllık"]) if period in ["Aylık", "Yıllık"]: selected_year = st.selectbox("📅 Yıl", sorted(df["year"].unique())) else: selected_year = None if period == "Aylık": selected_month = st.selectbox("📆 Ay", sorted(df["month"].unique())) else: selected_month = None st.markdown("---") st.info(f"Toplam Gözlem: {df.shape[0]} | Veri Aralığı: {df['datetime'].min().date()} - {df['datetime'].max().date()}")

st.title("📊 Hava Kalitesi İndeksi (HKİ) Analizi") st.markdown(f"Seçilen Tarih: {selected_date}")

selected_row = df[df["datetime"].dt.date == selected_date] if not selected_row.empty: row = selected_row.iloc[0] st.markdown(f""" - HKİ: {row['hki']} {get_hki_icon(row['hki'])} - Kategori: {row['hki_kategori']} - Renk: {row['hki_renk']} - Açıklama: {row['hki_aciklama']} - Belirleyici Kirletici: {row['hki_kaynak']} """) else: st.warning("Seçilen tarihe ait veri bulunamadı.")

if period == "Günlük": period_df = df[df["datetime"].dt.date == selected_date] elif period == "Aylık" and selected_month and selected_year: period_df = df[(df["month"] == selected_month) & (df["year"] == selected_year)] elif period == "Yıllık" and selected_year: period_df = df[df["year"] == selected_year] else: period_df = df.copy()

st.header(f"📌 {period} için En İyi ve En Kötü HKİ Verileri") if not period_df.empty: best_row = period_df.loc[period_df["hki"].idxmin()] worst_row = period_df.loc[period_df["hki"].idxmax()] st.subheader("✅ En İyi HKİ") st.markdown(f""" - 🕓 Zaman: {best_row['datetime']} - HKİ: {best_row['hki']} {get_hki_icon(best_row['hki'])} - Kategori: {best_row['hki_kategori']} - Açıklama: {best_row['hki_aciklama']} """) st.subheader("❌ En Kötü HKİ") st.markdown(f""" - 🕓 Zaman: {worst_row['datetime']} - HKİ: {worst_row['hki']} {get_hki_icon(worst_row['hki'])} - Kategori: {worst_row['hki_kategori']} - Açıklama: {worst_row['hki_aciklama']} """) else: st.warning(f"{period} dönemine ait analiz yapılamadı.")

🔮 Gelecek Yıl (2025) HKİ Tahmini

st.header("🔮 2025 HKİ Tahmini") future_dates = pd.date_range(start="2025-01-01", end="2025-12-31", freq="D") df["month_day"] = df["datetime"].dt.strftime("%m-%d") avg_hki_by_day = df.groupby("month_day")["hki"].mean().reset_index()

future_df = pd.DataFrame() future_df["date"] = future_dates future_df["month_day"] = future_df["date"].dt.strftime("%m-%d") future_df = future_df.merge(avg_hki_by_day, on="month_day", how="left") future_df.rename(columns={"hki": "tahmini_hki"}, inplace=True)

future_date = st.date_input("📅 Gelecek Tahmin Tarihi", pd.to_datetime("2025-01-01")) if future_date.year == 2025: result = future_df[future_df["date"] == future_date] if not result.empty: tahmini_hki = result.iloc[0]["tahmini_hki"] st.markdown(f"📅 Tarih: {future_date} \n🔮 Tahmini HKİ: {round(tahmini_hki, 2)} {get_hki_icon(tahmini_hki)}") else: st.warning("Bu tarihe ait tahmin verisi bulunamadı.")

