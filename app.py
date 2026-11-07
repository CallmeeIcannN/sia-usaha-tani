import base64
import html
import io
import os
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
DESK = {
    "Laporan": "Ringkasan biaya, penjualan, piutang, dan laba tiap musim tanam.",
    "Musim Tanam": "Kelola data musim tanam dan aktivitas lahan.",
    "Biaya": "Catat dan pantau biaya operasional usaha tani.",
    "Penjualan": "Catat hasil penjualan hasil pertanian.",
    "Pembayaran": "Kelola transaksi pembayaran usaha tani.",
}
IKON = {"Kentang": "🥔", "Cabai": "🌶️", "Kobis": "🥬", "Jagung": "🌽"}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
.stApp,input,textarea,button,select{font-family:'Plus Jakarta Sans',system-ui,sans-serif}
[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1080px;padding-top:2.2rem;padding-bottom:4rem}
.stApp h3{font-weight:700;font-size:1.2rem;margin-top:1.6rem}
.hero{background:#1F4D2B;color:#F1F7E4;padding:24px 28px;border-radius:14px;margin-bottom:22px;
 background-image:repeating-linear-gradient(100deg,transparent 0 22px,rgba(255,255,255,.05) 22px 24px)}
.hero .judul{font-size:1.9rem;font-weight:800;line-height:1.2;color:#F1F7E4}
.hero .desk{margin-top:6px;font-size:1rem;color:#DDEBC3}
.hero .kutip{margin-top:12px;padding-left:12px;border-left:3px solid #8DBF4A;font-size:.88rem;
 font-style:italic;line-height:1.5;color:#C5DBA3;max-width:64ch}
.kartu{background:var(--card);border:1px solid var(--garis);border-left:5px solid #5E9B3A;border-radius:12px;
 padding:14px 16px;color:var(--teks);margin-bottom:8px;backdrop-filter:blur(4px)}
.kartu.rugi{border-left-color:#C0392B}.kartu.piutang{border-left-color:#D99A1B}
.kartu span{display:block;font-size:.82rem;color:var(--muted)}
.kartu b{display:block;margin-top:2px;font-size:1.65rem;font-weight:800;letter-spacing:-.01em}
.tabelbox{background:var(--card);border:1px solid var(--garis);border-radius:14px;overflow-x:auto;backdrop-filter:blur(4px)}
.tabel{width:100%;border-collapse:collapse;font-size:.92rem;color:var(--teks)}
.tabel th{background:var(--head);font-weight:700;font-size:.8rem;color:var(--muted);padding:11px 16px;text-align:left;white-space:nowrap}
.tabel td{padding:12px 16px;border-top:1px solid var(--garis)}
.tabel .r{text-align:right;font-variant-numeric:tabular-nums}.tabel .c{text-align:center}
.tabel tbody tr:hover{background:var(--hover)}
.badge{display:inline-block;padding:2px 10px;border-radius:999px;font-size:.78rem;font-weight:600}
.badge.ok{background:rgba(62,142,65,.18);color:var(--ok)}.badge.jalan{background:rgba(217,154,27,.2);color:var(--warn)}
.kosong{background:var(--card);border:1px dashed var(--garis);border-radius:14px;padding:28px 16px;text-align:center;color:var(--teks)}
.kosong .ik{font-size:1.8rem}.kosong b{display:block;margin-top:6px}
.kosong span{display:block;margin-top:4px;font-size:.88rem;color:var(--muted)}
[data-testid="stForm"]{background:var(--card);border:1px solid var(--garis);border-radius:14px;padding:20px;
 box-shadow:0 1px 3px rgba(0,0,0,.08);backdrop-filter:blur(4px)}
[data-testid="stExpander"] details{background:var(--card);border:1px solid var(--garis)!important;border-radius:14px}
[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="select"]>div{border-radius:10px!important}
[data-baseweb="input"]:focus-within{border-color:#5E9B3A!important;box-shadow:0 0 0 3px rgba(94,155,58,.25)!important}
[data-testid="stNumberInputStepUp"],[data-testid="stNumberInputStepDown"]{background:transparent!important}
[data-testid="stNumberInputStepUp"]:hover,[data-testid="stNumberInputStepDown"]:hover{background:rgba(94,155,58,.18)!important}
div.stButton>button,div.stFormSubmitButton>button{min-height:42px;border-radius:10px;font-weight:600;transition:background .15s,transform .15s}
[data-testid^="stBaseButton-primary"]{background:#2F6B3A!important;color:#fff!important;border:0!important}
[data-testid^="stBaseButton-primary"]:hover{background:#265A30!important;transform:translateY(-1px)}
[data-testid^="stBaseButton-secondary"]{background:rgba(94,155,58,.14)!important;border:1px solid rgba(94,155,58,.45)!important}
[class*="st-key-b_"] button{background:#B83A2E!important;color:#fff!important;border:0!important}
[class*="st-key-b_"] button:disabled{opacity:.45}
[data-testid="stSidebar"] [role="radiogroup"]{gap:4px}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:10px 12px;border-radius:10px;border-left:3px solid transparent;width:100%;transition:background .15s}
[data-testid="stSidebar"] [role="radiogroup"] label>div:first-child{display:none}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:var(--hover)}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:rgba(94,155,58,.22);border-left-color:#5E9B3A;font-weight:700}
@media (max-width:640px){.hero{padding:18px}.hero .judul{font-size:1.45rem}.kartu b{font-size:1.35rem}.tabel th,.tabel td{padding:10px 12px}}
@media (prefers-reduced-motion:reduce){div.stButton>button,div.stFormSubmitButton>button{transition:none}}
</style>
""", unsafe_allow_html=True)



@st.cache_data
def foto_latar():
    """Cari foto latar (nama file diawali 'latar') di folder aplikasi, perkecil, ubah ke base64."""
    from PIL import Image
    for nama in sorted(os.listdir(".")):
        if nama.lower().startswith("latar") and nama.lower().endswith((".jpg", ".jpeg", ".png")):
            img = Image.open(nama).convert("RGB")
            img.thumbnail((1600, 1600))
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=70)
            return base64.b64encode(buf.getvalue()).decode()
    return None


LIGHT = ("--card:rgba(255,255,255,.88);--garis:rgba(31,77,43,.16);--muted:#5A6B52;--head:rgba(31,77,43,.07);"
         "--hover:rgba(94,155,58,.10);--teks:#1B2A16;--ok:#2E7D32;--warn:#8A5A00")
DARK = ("--card:rgba(18,32,20,.84);--garis:rgba(255,255,255,.14);--muted:#A9BC9B;--head:rgba(255,255,255,.07);"
        "--hover:rgba(141,191,74,.12);--teks:#EAF2DD;--ok:#8FD18F;--warn:#F0C463")
TEMA = {
    "Terang": dict(vars=LIGHT, bg="#FFFFFF", teks="#1B2A16", side="#E7F0DA", input="#FFFFFF",
                   garis="#C9D8B4", overlay="rgba(255,255,255,.78)"),
    "Gelap": dict(vars=DARK, bg="#0E180E", teks="#EAF2DD", side="#16241A", input="#1F3023",
                  garis="#35503A", overlay="rgba(14,24,14,.70)"),
}


def css_tampilan(mode, foto):
    css = f":root{{--foto:url(data:image/jpeg;base64,{foto})}}" if foto else ""

    def latar(ov):
        if not foto:
            return ""
        return (f".stApp{{background-image:linear-gradient({ov},{ov}),var(--foto);"
                "background-size:cover;background-position:center bottom;background-attachment:fixed}")

    if mode not in TEMA:  # Otomatis: ikut pengaturan perangkat
        css += f":root{{{LIGHT}}}@media (prefers-color-scheme:dark){{:root{{{DARK}}}}}"
        css += latar("rgba(255,255,255,.78)")
        if foto:
            css += "@media (prefers-color-scheme:dark){" + latar("rgba(14,24,14,.70)") + "}"
        return css
    t = TEMA[mode]
    css += f":root{{{t['vars']}}}" + latar(t["overlay"])
    css += (
        f'.stApp{{background-color:{t["bg"]}!important;color:{t["teks"]}!important}}'
        f'[data-testid="stSidebar"]{{background:{t["side"]}!important}}'
        f'.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,.stApp li,'
        f'.stApp [data-testid="stMarkdownContainer"],.stApp [data-testid="stCaptionContainer"]'
        f'{{color:{t["teks"]}!important}}'
        f'[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="select"]>div,textarea,input'
        f'{{background-color:{t["input"]}!important;color:{t["teks"]}!important}}'
        f'[data-testid="stExpander"]{{border-color:{t["garis"]}!important}}'
    )
    return css


_css = css_tampilan(st.session_state.get("mode_tampilan", "Otomatis"), foto_latar())
if _css:
    st.markdown(f"<style>{_css}</style>", unsafe_allow_html=True)

st.session_state.setdefault("kutipan", random.choice(KUTIPAN))


def hero(judul, desk=""):
    d = f'<div class="desk">{desk}</div>' if desk else ""
    st.markdown(
        f'<div class="hero"><div class="judul">{judul}</div>{d}'
        f'<div class="kutip">“{st.session_state["kutipan"]}”</div></div>',
        unsafe_allow_html=True,
    )


def kosong(judul="Belum ada data transaksi",
           ket="Tambahkan transaksi pertama untuk mulai mencatat aktivitas usaha tani."):
    st.markdown(f'<div class="kosong"><div class="ik">📋</div><b>{judul}</b><span>{ket}</span></div>',
                unsafe_allow_html=True)


def sel(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return html.escape(str(v)).replace("$", "&#36;")


def tabel(baris, kolom):
    """kolom: daftar (judul, kunci, rata) dengan rata l/r/c. Isi sel di-escape agar aman."""
    if not baris:
        kosong()
        return
    th = "".join(f'<th class="{r}">{html.escape(j)}</th>' for j, _, r in kolom)
    tr = ""
    for b in baris:
        td = ""
        for _, k, r in kolom:
            v = b.get(k)
            if k == "status":
                ok = v == "selesai"
                isi = f'<span class="badge {"ok" if ok else "jalan"}">● {"Selesai" if ok else "Berjalan"}</span>'
            else:
                isi = sel(v)
            td += f'<td class="{r}">{isi}</td>'
        tr += f"<tr>{td}</tr>"
    st.markdown(f'<div class="tabelbox"><table class="tabel"><thead><tr>{th}</tr></thead>'
                f'<tbody>{tr}</tbody></table></div>', unsafe_allow_html=True)


def kartu(judul, nilai, kelas=""):
    st.markdown(f'<div class="kartu {kelas}"><span>{judul}</span><b>{nilai}</b></div>',
                unsafe_allow_html=True)


# ---------- Login ----------
if not st.session_state.get("masuk"):
    hero("🌱 SIA Usaha Tani", "Aplikasi pencatatan akuntansi sederhana untuk usaha tani.")
    sandi = st.text_input("Kata sandi", type="password")
    if st.button("Masuk", type="primary"):
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
menu = st.sidebar.radio("Menu", ["📊 Laporan", "🌱 Musim Tanam", "💰 Biaya", "🧺 Penjualan", "💳 Pembayaran"])
halaman = menu.split(" ", 1)[1]
st.sidebar.divider()
st.sidebar.selectbox(
    "Tampilan", ["Otomatis", "Terang", "Gelap"], key="mode_tampilan",
    format_func=lambda x: {"Otomatis": "🖥️ Otomatis (ikut perangkat)", "Terang": "☀️ Terang", "Gelap": "🌙 Gelap"}[x],
)
st.sidebar.caption("Terima kasih, petani Indonesia 🇮🇩")

hero(menu, DESK[halaman])

# ---------- Laporan ----------
if halaman == "Laporan":
    with st.spinner("Menghitung laporan..."):
        data = (db.table("laporan_musim_tanam").select("*")
                .order("tanggal_tanam", desc=True).execute().data)
    if not data:
        kosong("Belum ada data laporan", "Mulai dari menu Musim Tanam, lalu catat biaya dan hasil panen.")
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
    st.bar_chart(grafik, color=["#D9822B", "#3E8E41"])

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
        if st.form_submit_button("Simpan musim tanam", type="primary"):
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
    st.subheader("Daftar musim tanam")
    tabel([{**m, "tanaman": f'{IKON.get(m["tanaman"], "🌱")} {m["tanaman"]}',
            "luas_ha": f'{m["luas_ha"]:g} ha' if m["luas_ha"] else "-"} for m in musim],
          [("Tanaman", "tanaman", "l"), ("Tanggal tanam", "tanggal_tanam", "l"), ("Luas", "luas_ha", "r"),
           ("Status", "status", "c"), ("Catatan", "catatan", "l")])
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
        if st.form_submit_button("Simpan biaya", type="primary"):
            simpan("biaya", {"musim_tanam_id": mid, "tanggal": str(tgl), "kategori": kat,
                             "keterangan": ket or None, "jumlah": jml})
    data = ambil("biaya")[:20]
    if not data:
        kosong()
    else:
        df = pd.DataFrame(data)
        df["musim"] = df["musim_tanam_id"].map(nama_musim)
        pilihan = {b["id"]: f'{b["tanggal"]} · {b["kategori"]} · {rp(b["jumlah"])}' for b in data}
        df["jumlah"] = df["jumlah"].map(rp)
        st.subheader("Riwayat biaya")
        st.caption(f"Menampilkan {len(data)} data terbaru")
        tabel(df.to_dict("records"), [("Tanggal", "tanggal", "l"), ("Musim tanam", "musim", "l"),
              ("Kategori", "kategori", "l"), ("Keterangan", "keterangan", "l"), ("Jumlah", "jumlah", "r")])
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
        if st.form_submit_button("Simpan penjualan", type="primary"):
            if kg <= 0:
                st.error("Jumlah kg harus lebih dari 0.")
            elif str(tgl) < next(m["tanggal_tanam"] for m in musim if m["id"] == mid):
                st.error("Tanggal penjualan tidak boleh lebih awal dari tanggal tanam.")
            else:
                simpan("penjualan", {"musim_tanam_id": mid, "tanggal": str(tgl), "jenis_pembeli": jenis,
                                     "nama_pembeli": nama or None, "jumlah_kg": kg, "harga_per_kg": harga})
    data = ambil("penjualan")[:20]
    if not data:
        kosong()
    else:
        df = pd.DataFrame(data)
        df["musim"] = df["musim_tanam_id"].map(nama_musim)
        pilihan = {p["id"]: f'{p["tanggal"]} · {p["nama_pembeli"] or p["jenis_pembeli"]} · {rp(p["total"])}'
                   for p in data}
        df["total"] = df["total"].map(rp)
        st.subheader("Riwayat penjualan")
        st.caption(f"Menampilkan {len(data)} data terbaru")
        df = df.assign(jumlah_kg=df["jumlah_kg"].map(lambda x: f"{x:g} kg"),
                       harga_per_kg=df["harga_per_kg"].map(rp))
        tabel(df.to_dict("records"), [("Tanggal", "tanggal", "l"), ("Musim tanam", "musim", "l"),
              ("Pembeli", "jenis_pembeli", "l"), ("Nama", "nama_pembeli", "l"),
              ("Jumlah", "jumlah_kg", "r"), ("Harga/kg", "harga_per_kg", "r"), ("Total", "total", "r")])
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
        if st.form_submit_button("Simpan pembayaran", type="primary"):
            if jml <= 0:
                st.error("Jumlah harus lebih dari 0.")
            elif str(tgl) < next(p["tanggal"] for p in jual if p["id"] == pid):
                st.error("Tanggal diterima tidak boleh lebih awal dari tanggal penjualan.")
            else:
                simpan("pembayaran", {"penjualan_id": pid, "tanggal": str(tgl),
                                      "jumlah": jml, "keterangan": ket or None})
    data = ambil("pembayaran")[:20]
    if not data:
        kosong()
    else:
        df = pd.DataFrame(data)
        df["penjualan"] = df["penjualan_id"].map(label)
        pilihan = {y["id"]: f'{y["tanggal"]} · {rp(y["jumlah"])}' for y in data}
        df["jumlah"] = df["jumlah"].map(rp)
        st.subheader("Riwayat pembayaran")
        st.caption(f"Menampilkan {len(data)} data terbaru")
        tabel(df.to_dict("records"), [("Tanggal", "tanggal", "l"), ("Penjualan", "penjualan", "l"),
              ("Jumlah", "jumlah", "r"), ("Keterangan", "keterangan", "l")])
        hapus_ui("pembayaran", pilihan)
