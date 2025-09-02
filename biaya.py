import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------
# Konfigurasi Halaman
# -------------------------------
st.set_page_config(page_title="Analisis Penyusutan Aset", layout="wide")
st.title("📊 Dashboard Analisis Biaya Penyusutan Aset")

# -------------------------------
# Upload Dataset
# -------------------------------
uploaded = st.file_uploader("Unggah dataset (Excel .xlsx)", type=["xlsx"])

if uploaded:
    # Baca dataset
    df = pd.read_excel(uploaded)

    # -------------------------------
    # Data Cleaning
    # -------------------------------
    obj_cols = df.select_dtypes(include="object").columns

    # Hapus baris subtotal / total
    mask = df[obj_cols].apply(
        lambda x: x.str.contains("Subtotal|Total", case=False, na=False)
    ).any(axis=1)
    df = df[~mask]

    # Hapus baris kosong
    df = df.dropna(how="all")

    # Konversi Tahun_Perolehan ke integer (jika berupa datetime)
    if pd.api.types.is_datetime64_any_dtype(df["Tahun_Perolehan"]):
        df["Tahun_Perolehan"] = df["Tahun_Perolehan"].dt.year

    # Isi nilai kosong
    df[obj_cols] = df[obj_cols].fillna("-")
    num_cols = df.select_dtypes(include=["float64", "int64"]).columns
    df[num_cols] = df[num_cols].fillna(0)
    df.reset_index(drop=True, inplace=True)

    # -------------------------------
    # Preview Dataset
    # -------------------------------
    st.subheader("📑 Preview Dataset")
    st.dataframe(df.head())

    # -------------------------------
    # Ringkasan
    # -------------------------------
    st.subheader("📌 Ringkasan Total")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Nilai Perolehan", f"Rp {df['Nilai_Perolehan'].sum():,.0f}")
    col2.metric(
        "Total Biaya Penyusutan Bulan",
        f"Rp {df['Biaya_Penyusutan_Bulan'].sum():,.0f}",
    )
    col3.metric(
        "Total Akumulasi Penyusutan",
        f"Rp {df['Akumulasi_Penyusutan'].sum():,.0f}",
    )

    # -------------------------------
    # Visualisasi
    # -------------------------------
    st.subheader("📊 Visualisasi Data")

    # Top 10 Jenis Aktiva
    st.markdown("**Top 10 Jenis Aktiva Penyumbang Biaya Penyusutan (per bulan)**")
    biaya_per_jenis = (
        df.groupby("Jenis_Aktiva_Tetap")["Biaya_Penyusutan_Bulan"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    fig1, ax1 = plt.subplots()
    biaya_per_jenis.plot(kind="bar", ax=ax1, color="skyblue")
    ax1.set_ylabel("Biaya Penyusutan (Rp)")
    ax1.set_xlabel("Jenis Aktiva")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig1)

    # Top 10 Golongan Penyusutan
    st.markdown("**Top 10 Golongan Penyusutan**")
    biaya_per_gol = (
        df.groupby("Golongan_Penyusutan")["Biaya_Penyusutan_Bulan"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    fig2, ax2 = plt.subplots()
    biaya_per_gol.plot(kind="bar", ax=ax2, color="orange")
    ax2.set_ylabel("Biaya Penyusutan (Rp)")
    ax2.set_xlabel("Golongan Penyusutan")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig2)

    # Histogram Rasio Penyusutan
    st.markdown("**Distribusi Rasio Penyusutan**")
    if "Rasio_Penyusutan" not in df.columns:
        df["Rasio_Penyusutan"] = (
            df["Biaya_Penyusutan_Sampai_Bulan"] / df["Nilai_Buku_Bulan_Ini"]
        )
    rasio_positive = df[df["Rasio_Penyusutan"] > 0]["Rasio_Penyusutan"]
    rasio_filtered = rasio_positive[rasio_positive < 20]

    fig3, ax3 = plt.subplots()
    ax3.hist(rasio_filtered, bins=30, color="green", edgecolor="black")
    ax3.set_xlabel("Rasio Penyusutan (<20)")
    ax3.set_ylabel("Jumlah Aset")
    st.pyplot(fig3)

    # -------------------------------
    # Top Aset
    # -------------------------------
    st.subheader("🏆 Top Aset")

    st.markdown("**Top 10 Aset Berdasarkan Nilai Perolehan**")
    top10_perol = df.sort_values("Nilai_Perolehan", ascending=False).head(10)
    st.table(top10_perol[["Jenis_Aktiva_Tetap", "Nilai_Perolehan"]])

    st.markdown("**Top 10 Aset Berdasarkan Nilai Buku Bulan Ini**")
    top10_book = df.sort_values("Nilai_Buku_Bulan_Ini", ascending=False).head(10)
    st.table(top10_book[["Jenis_Aktiva_Tetap", "Nilai_Buku_Bulan_Ini"]])

    # -------------------------------
    # Pencarian Aset
    # -------------------------------
    st.subheader("🔎 Cari Aset berdasarkan Kata Kunci")
    keyword = st.text_input("Masukkan kata kunci (misal: meja, printer, AC, dll)")
    if keyword:
        mask = df["Jenis_Aktiva_Tetap"].str.contains(keyword, case=False, na=False)
        filtered = df[mask]
        st.write(f"Jumlah aset ditemukan: {len(filtered)}")
        st.write(
            f"Total nilai perolehan aset tersebut: Rp {filtered['Nilai_Perolehan'].sum():,.0f}"
        )
        st.dataframe(
            filtered[
                ["Jenis_Aktiva_Tetap", "Nilai_Perolehan", "Biaya_Penyusutan_Bulan"]
            ]
        )

else:
    st.info("⬅️ Silakan upload file Excel untuk mulai analisis.")
