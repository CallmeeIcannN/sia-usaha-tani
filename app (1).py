import random
import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client

st.set_page_config(page_title="SIA Usaha Tani", page_icon="🌱", layout="wide")

KUTIPAN = [
    "Dari tanganmu di lahan, jutaan piring di Indonesia terisi. Terima kasih sudah bertani.",
    "Setiap musim tanam adalah doa yang ditanam di tanah. Catat dengan rapi, panen dengan tenang.",
    "Petani tidak hanya menanam, petani merawat masa depan bangsa.",
    "Hujan dan kemarau tidak bisa dipilih, tapi catatan yang rapi membuat kita tetap tegak.",
    "Pangan bangsa ini berdiri di atas kerja keras para petaninya.",
    "Sedikit demi sedikit dicatat, lama-lama usaha tani terlihat jelas arahnya.",
]
IKON = {"Kentang": "🥔", "Cabai": "🌶️", "Kobis": "🥬", "Jagung": "🌽"}

st.markdown("""
<style>
.hero{background:#1F4D2B;color:#F1F7E4;padding:26px 30px;border-radius:14px;margin-bottom:18px;
 background-image:repeating-linear-gradient(100deg,transparent 0 22px,rgba(255,255,255,.05) 22px 24px);}
.hero .judul{font-size:2rem;font-weight:700;margin-bottom:6px;color:#F1F7E4}
.hero .kutip{font-size:1.05rem;line-height:1.55;max-width:62ch;color:#DDEBC3}
.kartu{background:#F4F8EC;border:1px solid #D5E2BD;border-left:6px solid #5E9B3A;border-radius:10px;
 padding:12px 16px;color:#25351B;margin-bottom:8px}
.kartu.rugi{border-left-color:#C0392B}.kartu.piutang{border-left-color:#D99A1B}
.kartu span{display:block;font-size:.88rem;opacity:.8}.kartu b{font-size:1.35rem}
div.stButton>button,div.stFormSubmitButton>button{transition:transform .15s ease,box-shadow .15s ease}
div.stButton>button:hover,div.stFormSubmitButton>button:hover{transform:translateY(-2px);box-shadow:0 4px 10px rgba(0,0,0,.2)}
@media (prefers-reduced-motion:reduce){div.stButton>button,div.stFormSubmitButton>button{transition:none}}
</style>
""", unsafe_allow_html=True)

st.session_state.setdefault("kutipan", random.choice(KUTIPAN))


def hero(judul):
    st.markdown(
        f'<div class="hero"><div class="judul">{judul}</div>'
        f'<div class="kutip">“{st.session_state["kutipan"]}”</div></div>',
        unsafe_allow_html=True,
    )


def kartu(judul, nilai, kelas=""):
    st.markdown(f'<div class="kartu {kelas}"><span>{judul}</span><b>{nilai}</b></div>',
                unsafe_allow_html=True)


# ---------- Login ----------
if not st.session_state.get("masuk"):
    hero("🌱 SIA Usaha Tani")
    sandi = st.text_input("Kata sandi", type="password")
    if st.button("Masuk"):
        if sandi == st.secrets["APP_PASSWORD"]:
            st.session_state["masuk"] = True
            st.rerun()
        else:
            st.error("Kata sandi belum cocok. Coba ketik ulang dengan teliti.")
    st.stop()

if "pesan" in st.session_state:
    st.toast(st.session_state.pop("pesan"))


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
        st.session_state["pesan"] = "Data tersimpan ✅ Terima kasih sudah mencatat."
        st.rerun()
    except Exception as e:
        st.error(f"Data belum tersimpan. Periksa isian lalu coba lagi. ({e})")


def hapus_ui(tabel, pilihan, catatan=""):
    if not pilihan:
        return
    with st.expander("🗑️ Hapus data"):
        if catatan:
            st.caption(catatan)
        pid = st.selectbox("Pilih data", list(pilihan), format_func=pilihan.get, key="h_" + tabel)
        yakin = st.checkbox("Saya yakin ingin menghapus data ini", key="y_" + tabel)
        if st.button("Hapus data", disabled=not yakin, key="b_" + tabel):
            db.table(tabel).delete().eq("id", pid).execute()
            st.session_state["pesan"] = "Data sudah dihapus 🗑️"
            st.rerun()


with st.spinner("Memuat data..."):
    musim = ambil("musim_tanam")
nama_musim = {m["id"]: f'{IKON.get(m["tanaman"], "🌱")} {m["tanaman"]} ({m["tanggal_tanam"]})' for m in musim}

st.sidebar.title("🌱 SIA Usaha Tani")
menu = st.sidebar.radio("Menu", ["📊 Laporan", "🌱 Musim Tanam", "💸 Biaya", "🧺 Penjualan", "💰 Pembayaran"])
halaman = menu.split(" ", 1)[1]
st.sidebar.caption("Terima kasih, petani Indonesia 🇮🇩")

hero(menu)

# ---------- Laporan ----------
if halaman == "Laporan":
    with st.spinner("Menghitung laporan..."):
        data = (db.table("laporan_musim_tanam").select("*")
                .order("tanggal_tanam", desc=True).execute().data)
    if not data:
        st.info("Belum ada data. Mulai dari menu Musim Tanam, lalu catat biaya dan hasil panen.")
        st.stop()
    df = pd.DataFrame(data)
    k = st.columns(4)
    with k[0]:
        kartu("Total biaya", rp(df["total_biaya"].sum()))
    with k[1]:
        kartu("Total penjualan", rp(df["total_penjualan"].sum()))
    with k[2]:
        kartu("Sisa piutang", rp(df["sisa_piutang"].sum()), "piutang")
    with k[3]:
        laba = df["laba_rugi"].sum()
        kartu("Laba bersih" if laba >= 0 else "Rugi bersih", rp(laba), "" if laba >= 0 else "rugi")

    grafik = df.assign(label=df["tanaman"] + " " + df["tanggal_tanam"].astype(str))
    grafik = grafik.set_index("label")[["total_biaya", "total_penjualan"]]
    grafik.columns = ["Biaya", "Penjualan"]
    st.subheader("Biaya dan penjualan tiap musim")
    st.bar_chart(grafik)

    st.subheader("Rincian per musim tanam")
    for i, r in df.iterrows():
        status = "✅ selesai" if r["status"] == "selesai" else "🌿 berjalan"
        with st.expander(f'{IKON.get(r["tanaman"], "🌱")} {r["tanaman"]} ({r["tanggal_tanam"]}) · {status}',
                         expanded=(i == 0)):
            c = st.columns(4)
            with c[0]:
                kartu("Biaya", rp(r["total_biaya"]))
            with c[1]:
                kartu("Penjualan", rp(r["total_penjualan"]))
            with c[2]:
                kartu("Sisa piutang", rp(r["sisa_piutang"]), "piutang")
            with c[3]:
                ok = r["laba_rugi"] >= 0
                kartu("Laba" if ok else "Rugi", rp(r["laba_rugi"]), "" if ok else "rugi")

# ---------- Musim Tanam ----------
elif halaman == "Musim Tanam":
    with st.form("form_musim", clear_on_submit=True):
        tanaman = st.selectbox("Tanaman", list(IKON))
        tgl = st.date_input("Tanggal tanam", value=date.today())
        luas = st.number_input("Luas lahan (hektar)", min_value=0.0, step=0.1)
        catatan = st.text_input("Catatan (opsional)")
        if st.form_submit_button("Simpan musim tanam"):
            simpan("musim_tanam", {"tanaman": tanaman, "tanggal_tanam": str(tgl),
                                   "luas_ha": luas or None, "catatan": catatan or None})
    berjalan = {m["id"]: nama_musim[m["id"]] for m in musim if m["status"] == "berjalan"}
    if berjalan:
        st.subheader("Tandai panen selesai")
        pilih = st.selectbox("Musim tanam", list(berjalan), format_func=berjalan.get)
        if st.button("Tandai selesai"):
            db.table("musim_tanam").update(
                {"status": "selesai", "tanggal_panen": str(date.today())}).eq("id", pilih).execute()
            st.session_state["pesan"] = "Selamat panen! 🌾"
            st.rerun()
    if musim:
        st.subheader("Daftar musim tanam")
        st.dataframe(pd.DataFrame(musim)[["tanaman", "tanggal_tanam", "luas_ha", "status", "catatan"]],
                     use_container_width=True, hide_index=True)
    hapus_ui("musim_tanam", nama_musim, "Menghapus musim tanam juga menghapus biaya dan penjualannya.")

# ---------- Biaya ----------
elif halaman == "Biaya":
    if not musim:
        st.warning("Buat musim tanam dulu di menu Musim Tanam.")
        st.stop()
    with st.form("form_biaya", clear_on_submit=True):
        mid = st.selectbox("Musim tanam", list(nama_musim), format_func=nama_musim.get)
        tgl = st.date_input("Tanggal", value=date.today())
        kat = st.selectbox("Kategori", ["bibit", "pupuk", "obat_tanaman", "upah", "listrik", "lainnya"])
        ket = st.text_input("Keterangan (opsional)")
        jml = st.number_input("Jumlah (Rp)", min_value=0, step=1000)
        if st.form_submit_button("Simpan biaya"):
            simpan("biaya", {"musim_tanam_id": mid, "tanggal": str(tgl), "kategori": kat,
                             "keterangan": ket or None, "jumlah": jml})
    data = ambil("biaya")[:20]
    if data:
        df = pd.DataFrame(data)
        df["musim"] = df["musim_tanam_id"].map(nama_musim)
        pilihan = {b["id"]: f'{b["tanggal"]} · {b["kategori"]} · {rp(b["jumlah"])}' for b in data}
        df["jumlah"] = df["jumlah"].map(rp)
        st.subheader("20 catatan terakhir")
        st.dataframe(df[["tanggal", "musim", "kategori", "keterangan", "jumlah"]],
                     use_container_width=True, hide_index=True)
        hapus_ui("biaya", pilihan)

# ---------- Penjualan ----------
elif halaman == "Penjualan":
    if not musim:
        st.warning("Buat musim tanam dulu di menu Musim Tanam.")
        st.stop()
    with st.form("form_jual", clear_on_submit=True):
        mid = st.selectbox("Musim tanam", list(nama_musim), format_func=nama_musim.get)
        tgl = st.date_input("Tanggal", value=date.today())
        jenis = st.selectbox("Jenis pembeli", ["tengkulak", "mitra"])
        nama = st.text_input("Nama pembeli (opsional)")
        kg = st.number_input("Jumlah (kg)", min_value=0.0, step=10.0)
        harga = st.number_input("Harga per kg (Rp)", min_value=0, step=100)
        if st.form_submit_button("Simpan penjualan"):
            if kg <= 0:
                st.error("Jumlah kg harus lebih dari 0.")
            else:
                simpan("penjualan", {"musim_tanam_id": mid, "tanggal": str(tgl), "jenis_pembeli": jenis,
                                     "nama_pembeli": nama or None, "jumlah_kg": kg, "harga_per_kg": harga})
    data = ambil("penjualan")[:20]
    if data:
        df = pd.DataFrame(data)
        df["musim"] = df["musim_tanam_id"].map(nama_musim)
        pilihan = {p["id"]: f'{p["tanggal"]} · {p["nama_pembeli"] or p["jenis_pembeli"]} · {rp(p["total"])}'
                   for p in data}
        df["total"] = df["total"].map(rp)
        st.subheader("20 penjualan terakhir")
        st.dataframe(df[["tanggal", "musim", "jenis_pembeli", "nama_pembeli", "jumlah_kg",
                         "harga_per_kg", "total"]], use_container_width=True, hide_index=True)
        hapus_ui("penjualan", pilihan, "Menghapus penjualan juga menghapus pembayarannya.")

# ---------- Pembayaran ----------
elif halaman == "Pembayaran":
    jual = ambil("penjualan")
    if not jual:
        st.warning("Catat penjualan dulu di menu Penjualan.")
        st.stop()
    label = {p["id"]: f'{p["tanggal"]} · {nama_musim.get(p["musim_tanam_id"])} · '
                      f'{p["nama_pembeli"] or p["jenis_pembeli"]} · {rp(p["total"])}' for p in jual}
    with st.form("form_bayar", clear_on_submit=True):
        pid = st.selectbox("Penjualan", list(label), format_func=label.get)
        tgl = st.date_input("Tanggal diterima", value=date.today())
        jml = st.number_input("Jumlah diterima (Rp)", min_value=0, step=1000)
        ket = st.text_input("Keterangan (opsional)")
        if st.form_submit_button("Simpan pembayaran"):
            if jml <= 0:
                st.error("Jumlah harus lebih dari 0.")
            else:
                simpan("pembayaran", {"penjualan_id": pid, "tanggal": str(tgl),
                                      "jumlah": jml, "keterangan": ket or None})
    data = ambil("pembayaran")[:20]
    if data:
        df = pd.DataFrame(data)
        df["penjualan"] = df["penjualan_id"].map(label)
        pilihan = {y["id"]: f'{y["tanggal"]} · {rp(y["jumlah"])}' for y in data}
        df["jumlah"] = df["jumlah"].map(rp)
        st.subheader("20 pembayaran terakhir")
        st.dataframe(df[["tanggal", "penjualan", "jumlah", "keterangan"]],
                     use_container_width=True, hide_index=True)
        hapus_ui("pembayaran", pilihan)
