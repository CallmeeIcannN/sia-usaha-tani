import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client

st.set_page_config(page_title="SIA Usaha Tani", page_icon="🌱", layout="wide")

# ---------- Login sederhana ----------
if not st.session_state.get("masuk"):
    st.title("🌱 SIA Usaha Tani")
    sandi = st.text_input("Kata sandi", type="password")
    if st.button("Masuk"):
        if sandi == st.secrets["APP_PASSWORD"]:
            st.session_state["masuk"] = True
            st.rerun()
        else:
            st.error("Kata sandi salah.")
    st.stop()

# ---------- Koneksi database ----------
@st.cache_resource
def koneksi():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

db = koneksi()


def rp(x):
    return "Rp {:,.0f}".format(x or 0).replace(",", ".")


def ambil(tabel, urut="id"):
    return db.table(tabel).select("*").order(urut, desc=True).execute().data


def simpan(tabel, data):
    try:
        db.table(tabel).insert(data).execute()
        st.success("Data berhasil disimpan.")
        st.rerun()
    except Exception as e:
        st.error(f"Gagal menyimpan: {e}")


musim = ambil("musim_tanam")
nama_musim = {m["id"]: f'{m["tanaman"]} ({m["tanggal_tanam"]})' for m in musim}

st.sidebar.title("🌱 SIA Usaha Tani")
menu = st.sidebar.radio(
    "Menu", ["Laporan", "Musim Tanam", "Biaya", "Penjualan", "Pembayaran"]
)

# ---------- Laporan ----------
if menu == "Laporan":
    st.header("Laporan per Musim Tanam")
    data = (
        db.table("laporan_musim_tanam")
        .select("*")
        .order("tanggal_tanam", desc=True)
        .execute()
        .data
    )
    if not data:
        st.info("Belum ada data. Mulai dari menu Musim Tanam.")
    else:
        df = pd.DataFrame(data)
        k = st.columns(4)
        k[0].metric("Total biaya", rp(df["total_biaya"].sum()))
        k[1].metric("Total penjualan", rp(df["total_penjualan"].sum()))
        k[2].metric("Sisa piutang", rp(df["sisa_piutang"].sum()))
        k[3].metric("Laba / rugi", rp(df["laba_rugi"].sum()))
        tampil = df[
            ["tanaman", "tanggal_tanam", "status", "total_biaya",
             "total_penjualan", "total_diterima", "sisa_piutang", "laba_rugi"]
        ].copy()
        for kolom in ["total_biaya", "total_penjualan", "total_diterima",
                      "sisa_piutang", "laba_rugi"]:
            tampil[kolom] = tampil[kolom].map(rp)
        tampil.columns = ["Tanaman", "Tanggal tanam", "Status", "Biaya",
                          "Penjualan", "Sudah diterima", "Sisa piutang", "Laba/Rugi"]
        st.dataframe(tampil, use_container_width=True, hide_index=True)

# ---------- Musim Tanam ----------
elif menu == "Musim Tanam":
    st.header("Musim Tanam")
    with st.form("form_musim", clear_on_submit=True):
        tanaman = st.selectbox("Tanaman", ["Kentang", "Cabai", "Kobis", "Jagung"])
        tgl = st.date_input("Tanggal tanam", value=date.today())
        luas = st.number_input("Luas lahan (hektar)", min_value=0.0, step=0.1)
        catatan = st.text_input("Catatan (opsional)")
        if st.form_submit_button("Simpan"):
            simpan("musim_tanam", {
                "tanaman": tanaman, "tanggal_tanam": str(tgl),
                "luas_ha": luas or None, "catatan": catatan or None,
            })
    berjalan = {m["id"]: nama_musim[m["id"]] for m in musim if m["status"] == "berjalan"}
    if berjalan:
        st.subheader("Tandai musim tanam selesai")
        pilih = st.selectbox("Musim tanam", list(berjalan), format_func=berjalan.get)
        if st.button("Tandai selesai"):
            db.table("musim_tanam").update(
                {"status": "selesai", "tanggal_panen": str(date.today())}
            ).eq("id", pilih).execute()
            st.rerun()
    if musim:
        st.subheader("Daftar musim tanam")
        st.dataframe(
            pd.DataFrame(musim)[["tanaman", "tanggal_tanam", "luas_ha", "status", "catatan"]],
            use_container_width=True, hide_index=True,
        )

# ---------- Biaya ----------
elif menu == "Biaya":
    st.header("Catat Biaya")
    if not musim:
        st.warning("Buat musim tanam dulu.")
        st.stop()
    with st.form("form_biaya", clear_on_submit=True):
        mid = st.selectbox("Musim tanam", list(nama_musim), format_func=nama_musim.get)
        tgl = st.date_input("Tanggal", value=date.today())
        kat = st.selectbox(
            "Kategori", ["bibit", "pupuk", "obat_tanaman", "upah", "listrik", "lainnya"]
        )
        ket = st.text_input("Keterangan (opsional)")
        jml = st.number_input("Jumlah (Rp)", min_value=0, step=1000)
        if st.form_submit_button("Simpan"):
            simpan("biaya", {
                "musim_tanam_id": mid, "tanggal": str(tgl), "kategori": kat,
                "keterangan": ket or None, "jumlah": jml,
            })
    data = ambil("biaya")[:20]
    if data:
        df = pd.DataFrame(data)
        df["musim"] = df["musim_tanam_id"].map(nama_musim)
        df["jumlah"] = df["jumlah"].map(rp)
        st.subheader("20 catatan terakhir")
        st.dataframe(df[["tanggal", "musim", "kategori", "keterangan", "jumlah"]],
                     use_container_width=True, hide_index=True)

# ---------- Penjualan ----------
elif menu == "Penjualan":
    st.header("Catat Penjualan Hasil Panen")
    if not musim:
        st.warning("Buat musim tanam dulu.")
        st.stop()
    with st.form("form_jual", clear_on_submit=True):
        mid = st.selectbox("Musim tanam", list(nama_musim), format_func=nama_musim.get)
        tgl = st.date_input("Tanggal", value=date.today())
        jenis = st.selectbox("Jenis pembeli", ["tengkulak", "mitra"])
        nama = st.text_input("Nama pembeli (opsional)")
        kg = st.number_input("Jumlah (kg)", min_value=0.0, step=10.0)
        harga = st.number_input("Harga per kg (Rp)", min_value=0, step=100)
        if st.form_submit_button("Simpan"):
            if kg <= 0:
                st.error("Jumlah kg harus lebih dari 0.")
            else:
                simpan("penjualan", {
                    "musim_tanam_id": mid, "tanggal": str(tgl), "jenis_pembeli": jenis,
                    "nama_pembeli": nama or None, "jumlah_kg": kg, "harga_per_kg": harga,
                })
    data = ambil("penjualan")[:20]
    if data:
        df = pd.DataFrame(data)
        df["musim"] = df["musim_tanam_id"].map(nama_musim)
        df["total"] = df["total"].map(rp)
        st.subheader("20 penjualan terakhir")
        st.dataframe(
            df[["tanggal", "musim", "jenis_pembeli", "nama_pembeli",
                "jumlah_kg", "harga_per_kg", "total"]],
            use_container_width=True, hide_index=True,
        )

# ---------- Pembayaran ----------
elif menu == "Pembayaran":
    st.header("Catat Pembayaran dari Pembeli")
    jual = ambil("penjualan")
    if not jual:
        st.warning("Catat penjualan dulu.")
        st.stop()
    label = {
        p["id"]: f'{p["tanggal"]} - {nama_musim.get(p["musim_tanam_id"])} - '
                 f'{p["nama_pembeli"] or p["jenis_pembeli"]} - {rp(p["total"])}'
        for p in jual
    }
    with st.form("form_bayar", clear_on_submit=True):
        pid = st.selectbox("Penjualan", list(label), format_func=label.get)
        tgl = st.date_input("Tanggal diterima", value=date.today())
        jml = st.number_input("Jumlah diterima (Rp)", min_value=0, step=1000)
        ket = st.text_input("Keterangan (opsional)")
        if st.form_submit_button("Simpan"):
            if jml <= 0:
                st.error("Jumlah harus lebih dari 0.")
            else:
                simpan("pembayaran", {
                    "penjualan_id": pid, "tanggal": str(tgl),
                    "jumlah": jml, "keterangan": ket or None,
                })
    data = ambil("pembayaran")[:20]
    if data:
        df = pd.DataFrame(data)
        df["penjualan"] = df["penjualan_id"].map(label)
        df["jumlah"] = df["jumlah"].map(rp)
        st.subheader("20 pembayaran terakhir")
        st.dataframe(df[["tanggal", "penjualan", "jumlah", "keterangan"]],
                     use_container_width=True, hide_index=True)
