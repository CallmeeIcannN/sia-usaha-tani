import altair as alt
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
:root{--foto:linear-gradient(#2A5A34,#2A5A34)}
.stApp,input,textarea,button,select{font-family:'Plus Jakarta Sans',system-ui,sans-serif}
.stApp{background:var(--bg)}
[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1100px;padding-top:1.6rem;padding-bottom:4rem;animation:naik .45s ease both}
@keyframes naik{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.stApp h3{font-weight:800;font-size:1.25rem;margin-top:1.8rem}
.hero2{position:relative;overflow:hidden;display:flex;align-items:center;min-height:220px;padding:30px 40px;margin-bottom:28px;
 border-radius:26px 26px 100px 26px;color:#F5F0E1;
 background:linear-gradient(100deg,rgba(24,62,34,.96) 0 44%,rgba(24,62,34,.55) 100%),var(--foto);background-size:cover;background-position:center bottom}
.hero2::after{content:"";position:absolute;right:-50px;bottom:-70px;width:220px;height:220px;background:var(--aksen,#F2C14E);border-radius:58% 42% 51% 49%/46% 55% 45% 54%;opacity:.9}
.hero2::before{content:"";position:absolute;right:-140px;bottom:-190px;width:480px;height:480px;border-radius:50%;background:repeating-radial-gradient(circle,transparent 0 30px,rgba(245,240,225,.11) 30px 32px)}
.hero2 .isi{position:relative;z-index:2;max-width:640px}
.hero2 .tag{display:inline-block;font-weight:700;font-size:.85rem;background:rgba(245,240,225,.16);padding:4px 12px;border-radius:999px}
.hero2 .judul{text-wrap:balance;margin:14px 0 8px;font-size:2.15rem;font-weight:800;line-height:1.12;letter-spacing:-.02em;color:#F5F0E1}
.hero2 .desk{font-size:1rem;color:#E6EFD2;max-width:46ch}
.hero2 .kutip{margin-top:16px;padding-left:12px;border-left:3px solid var(--aksen,#F2C14E);font-size:.85rem;font-style:italic;color:#CFE0AE;max-width:56ch}
.hero2 .tunas{position:absolute;right:46px;bottom:24px;width:78px;z-index:2}
.hero2.kuning{--aksen:#F2C14E}.hero2.hijau{--aksen:#8DBF4A}.hero2.oranye{--aksen:#E08A3C}.hero2.sage{--aksen:#9CCB9A}
.fokus{margin:4px 0 10px;animation:naik .6s ease both}
.fokus .lbl{font-weight:600;color:var(--muted);font-size:.95rem}
.fokus .angka{display:inline;font-size:3.4rem;font-weight:800;letter-spacing:-.03em;line-height:1.2;color:var(--teks);
 background:linear-gradient(transparent 64%,var(--hl,rgba(242,193,78,.6)) 64%)}
.fokus.rugi .angka{color:var(--bad)}.fokus.oranye{--hl:rgba(224,138,60,.5)}.fokus.hijau{--hl:rgba(141,191,74,.5)}
.pendukung{display:flex;gap:34px;flex-wrap:wrap;margin-top:16px;padding-top:14px;border-top:1px solid var(--garis)}
.pendukung span{display:block;font-size:.8rem;color:var(--muted)}.pendukung b{font-size:1.1rem;font-weight:700;color:var(--teks)}
.lini{list-style:none;margin:0 0 0 6px;padding:0 0 0 14px;border-left:2px solid var(--garis)}
.lini li{position:relative;padding:0 0 18px 16px;color:var(--teks)}
.lini li::before{content:"";position:absolute;left:-23px;top:5px;width:12px;height:12px;border-radius:50%;background:#5E9B3A;border:2px solid var(--bg)}
.lini small{display:block;color:var(--muted);margin-top:2px}
.panel{position:relative;overflow:hidden;border-radius:22px 22px 22px 80px;padding:26px 28px 90px;background:#1F4D2B;color:#F5F0E1;margin-top:1.1rem}
.panel small{color:#CFE0AE}.panel .besar{font-size:2.9rem;font-weight:800;line-height:1.1}
.panel .baris{display:flex;justify-content:space-between;padding:9px 0;border-top:1px solid rgba(245,240,225,.18)}
.panel .tunas{position:absolute;right:22px;bottom:12px;width:84px;opacity:.95}
.tabelbox{background:var(--card);border:1px solid var(--garis);border-radius:16px;overflow-x:auto}
.tabel{width:100%;border-collapse:collapse;font-size:.92rem;color:var(--teks)}
.tabel th{background:var(--head);font-weight:700;font-size:.8rem;color:var(--muted);padding:11px 16px;text-align:left;white-space:nowrap}
.tabel td{padding:12px 16px;border-top:1px solid var(--garis)}
.tabel .r{text-align:right;font-variant-numeric:tabular-nums}.tabel .c{text-align:center}
.tabel tbody tr{transition:background .15s}.tabel tbody tr:hover{background:var(--hover)}
.badge{display:inline-block;padding:2px 10px;border-radius:999px;font-size:.78rem;font-weight:600;white-space:nowrap}
.badge.ok{background:rgba(62,142,65,.18);color:var(--ok)}.badge.jalan{background:rgba(217,154,27,.2);color:var(--warn)}
.badge.belum{background:rgba(192,57,43,.16);color:var(--bad)}
.kosong{background:var(--card);border:1px dashed var(--garis);border-radius:16px;padding:28px 16px;text-align:center;color:var(--teks)}
.kosong .ik{font-size:1.8rem}.kosong b{display:block;margin-top:6px}
.kosong span{display:block;margin-top:4px;font-size:.88rem;color:var(--muted)}
[data-testid="stForm"]{background:var(--card);border:1px solid var(--garis);border-radius:18px;padding:20px}
[data-testid="stExpander"] details{background:var(--card);border:1px solid var(--garis)!important;border-radius:14px}
[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="select"]>div{border-radius:10px!important}
[data-baseweb="input"]:focus-within{border-color:#5E9B3A!important;box-shadow:0 0 0 3px rgba(94,155,58,.25)!important}
[data-testid="stNumberInputStepUp"],[data-testid="stNumberInputStepDown"]{background:transparent!important}
[data-testid="stNumberInputStepUp"]:hover,[data-testid="stNumberInputStepDown"]:hover{background:rgba(94,155,58,.18)!important}
div.stButton>button,div.stFormSubmitButton>button{min-height:42px;border-radius:12px;font-weight:600;transition:background .15s,transform .15s}
[data-testid^="stBaseButton-primary"]{background:#2F6B3A!important;color:#fff!important;border:0!important}
[data-testid^="stBaseButton-primary"]:hover{background:#265A30!important;transform:translateY(-1px)}
[data-testid^="stBaseButton-secondary"]{background:rgba(94,155,58,.14)!important;border:1px solid rgba(94,155,58,.45)!important}
[class*="st-key-b_"] button{background:#B83A2E!important;color:#fff!important;border:0!important}
[class*="st-key-b_"] button:disabled{opacity:.45}
[data-testid="stSidebar"]{background:#1F4D2B!important;border-radius:0 28px 28px 0}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] small{color:#E4EDCF!important}
.logo{padding:6px 6px 18px}.logo .ik{font-size:1.9rem}.logo b{display:block;font-size:1.25rem;font-weight:800;color:#F5F0E1}
.logo span{font-size:.8rem;color:#B9D18D}
[data-testid="stSidebar"] .stButton>button{justify-content:flex-start;padding:10px 14px;background:transparent!important;border:0!important;color:#DDEBC3!important}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(255,255,255,.09)!important;transform:translateX(4px)}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]{background:#F2C14E!important;color:#1F4D2B!important;font-weight:800}
[data-testid="stSidebar"] [data-baseweb="select"]>div{background:#F5F0E1!important}
[data-testid="stSidebar"] [data-baseweb="select"] *{color:#1E2A19!important}
@media (max-width:640px){.hero2{padding:24px 22px 70px;min-height:0;border-radius:22px 22px 64px 22px}.hero2 .judul{font-size:1.65rem}
 .hero2 .tunas{width:58px;right:20px;bottom:14px}.hero2::after{width:150px;height:150px;right:-40px;bottom:-50px}.hero2::before{display:none}.fokus .angka{font-size:2.3rem}.pendukung{gap:20px}
 .tabel th,.tabel td{padding:10px 12px}}
@media (prefers-reduced-motion:reduce){.block-container,.fokus{animation:none}div.stButton>button,div.stFormSubmitButton>button,.tabel tbody tr{transition:none}}
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


LIGHT = ("--bg:#F5F0E1;--card:rgba(255,255,255,.72);--garis:rgba(31,77,43,.14);--muted:#5E6B55;--head:rgba(31,77,43,.07);"
         "--hover:rgba(94,155,58,.10);--teks:#1E2A19;--ok:#2E7D32;--warn:#8A5A00;--bad:#B03A2E")
DARK = ("--bg:#0E170F;--card:rgba(255,255,255,.06);--garis:rgba(255,255,255,.14);--muted:#A9BC9B;--head:rgba(255,255,255,.07);"
        "--hover:rgba(141,191,74,.12);--teks:#ECF2E0;--ok:#8FD18F;--warn:#F0C463;--bad:#F29A8F")
TEMA = {
    "Terang": dict(vars=LIGHT, bg="#F5F0E1", teks="#1E2A19", input="#FFFFFF", garis="#C9D8B4"),
    "Gelap": dict(vars=DARK, bg="#0E170F", teks="#ECF2E0", input="#1F3023", garis="#35503A"),
}


def css_tampilan(mode, foto):
    css = ":root{--foto:linear-gradient(#2A5A34,#2A5A34)}" if not foto else (
        f":root{{--foto:url(data:image/jpeg;base64,{foto})}}")
    if mode not in TEMA:  # Otomatis: ikut pengaturan perangkat
        return css + f":root{{{LIGHT}}}@media (prefers-color-scheme:dark){{:root{{{DARK}}}}}"
    t = TEMA[mode]
    return css + f":root{{{t['vars']}}}" + (
        f'.stApp{{background-color:{t["bg"]}!important;color:{t["teks"]}!important}}'
        f'.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,.stApp li,'
        f'.stApp [data-testid="stMarkdownContainer"],.stApp [data-testid="stCaptionContainer"]'
        f'{{color:{t["teks"]}!important}}'
        f'.stApp [data-testid="stMain"] [data-baseweb="input"],.stApp [data-testid="stMain"] [data-baseweb="base-input"],'
        f'.stApp [data-testid="stMain"] [data-baseweb="select"]>div,.stApp [data-testid="stMain"] textarea,'
        f'.stApp [data-testid="stMain"] input{{background-color:{t["input"]}!important;color:{t["teks"]}!important}}'
        f'[data-testid="stExpander"]{{border-color:{t["garis"]}!important}}'
        '.stApp .hero2,.stApp .hero2 .judul,.stApp .hero2 .tag{color:#F5F0E1!important}.stApp .hero2 .desk{color:#E6EFD2!important}'
        '.stApp .hero2 .kutip{color:#CFE0AE!important}.stApp .panel,.stApp .panel small{color:#F5F0E1!important}'
        '[data-testid="stSidebar"] p,[data-testid="stSidebar"] label{color:#E4EDCF!important}'
    )


_css = css_tampilan(st.session_state.get("mode_tampilan", "Otomatis"), foto_latar())
st.markdown(f"<style>{_css}</style>", unsafe_allow_html=True)

st.session_state.setdefault("kutipan", random.choice(KUTIPAN))

TUNAS = ('<svg class="tunas" viewBox="0 0 120 140" aria-hidden="true"><path d="M60 138V58" stroke="#F5F0E1" '
         'stroke-width="5" stroke-linecap="round" fill="none"/><path d="M60 80C60 52 38 38 14 40c0 28 20 44 46 40z" '
         'fill="#8DBF4A"/><path d="M60 64C60 38 80 22 106 24c0 26-20 42-46 40z" fill="#C5E27A"/></svg>')
HERO = {
    "Laporan": ("📊 Laporan", "Pantau kondisi keuangan usaha tani", "Biaya, penjualan, dan laba dalam satu tampilan.", "kuning"),
    "Musim Tanam": ("🌱 Musim Tanam", "Kelola musim tanam di lahanmu", "Kelola data musim tanam dan aktivitas lahan.", "hijau"),
    "Biaya": ("💰 Biaya", "Catat setiap pengeluaran", "Agar kondisi usaha tani tetap terkontrol.", "oranye"),
    "Penjualan": ("🧺 Penjualan", "Hasil usaha tani", "Catat hasil panen yang terjual dan pantau pendapatan.", "kuning"),
    "Pembayaran": ("💳 Pembayaran", "Arus pembayaran", "Pantau uang yang sudah diterima dan sisa piutang.", "sage"),
}
STATUS = {"selesai": ("ok", "Selesai"), "berjalan": ("jalan", "Berjalan"), "lunas": ("ok", "Lunas"),
          "sebagian": ("jalan", "Sebagian"), "belum": ("belum", "Belum dibayar")}
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus",
         "September", "Oktober", "November", "Desember"]


def tgl_id(s):
    try:
        y, m, d = str(s)[:10].split("-")
        return f"{int(d):02d} {BULAN[int(m) - 1]} {y}"
    except Exception:
        return str(s)


def hero(tag, judul, desk="", aksen="kuning"):
    st.markdown(
        f'<div class="hero2 {aksen}"><div class="isi"><span class="tag">{tag}</span>'
        f'<div class="judul">{judul}</div><div class="desk">{desk}</div>'
        f'<div class="kutip">“{st.session_state["kutipan"]}”</div></div>{TUNAS}</div>',
        unsafe_allow_html=True,
    )


def pendukung(items):
    return '<div class="pendukung">' + "".join(f"<div><span>{k}</span><b>{v}</b></div>" for k, v in items) + "</div>"


def fokus(label, nilai, items, kelas=""):
    st.markdown(f'<div class="fokus {kelas}"><div class="lbl">{label}</div><div class="angka">{nilai}</div>'
                f'{pendukung(items)}</div>', unsafe_allow_html=True)


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
                kls, teks = STATUS.get(v, ("jalan", sel(v)))
                isi = f'<span class="badge {kls}">● {teks}</span>'
            else:
                isi = sel(v)
            td += f'<td class="{r}">{isi}</td>'
        tr += f"<tr>{td}</tr>"
    st.markdown(f'<div class="tabelbox"><table class="tabel"><thead><tr>{th}</tr></thead>'
                f'<tbody>{tr}</tbody></table></div>', unsafe_allow_html=True)


def grafik(df):
    d = df.assign(label=df["tanaman"] + " " + df["tanggal_tanam"].astype(str))
    d = pd.concat([
        d[["label"]].assign(jenis="Biaya", juta=pd.to_numeric(d["total_biaya"]) / 1e6),
        d[["label"]].assign(jenis="Penjualan", juta=pd.to_numeric(d["total_penjualan"]) / 1e6),
    ])
    return (alt.Chart(d).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
            .encode(x=alt.X("label:N", title=None, axis=alt.Axis(labelAngle=0, labelLimit=90)),
                    xOffset="jenis:N", y=alt.Y("juta:Q", title="Juta rupiah"),
                    color=alt.Color("jenis:N", title=None, legend=alt.Legend(orient="top"),
                                    scale=alt.Scale(domain=["Biaya", "Penjualan"], range=["#D9822B", "#3E8E41"])),
                    tooltip=[alt.Tooltip("label:N", title="Musim"), alt.Tooltip("jenis:N", title="Jenis"),
                             alt.Tooltip("juta:Q", title="Juta Rp", format=",.1f")])
            .properties(height=300))


# ---------- Login ----------
if not st.session_state.get("masuk"):
    hero("🌱 SIA Usaha Tani", "Pencatatan akuntansi usaha tani", "Masuk untuk membuka catatan usaha tani.", "kuning")
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

# ---------- Navigasi ----------
MENU = ["📊 Laporan", "🌱 Musim Tanam", "💰 Biaya", "🧺 Penjualan", "💳 Pembayaran"]
st.session_state.setdefault("menu", MENU[0])
st.sidebar.markdown(
    '<div class="logo"><div class="ik">🌱</div><b>SIA Usaha Tani</b>'
    '<span>Pencatatan akuntansi usaha tani</span></div>', unsafe_allow_html=True)
for m in MENU:
    if st.sidebar.button(m, key="nav_" + m.split(" ", 1)[1].replace(" ", "_"), width="stretch",
                         type="primary" if st.session_state["menu"] == m else "secondary"):
        st.session_state["menu"] = m
        st.rerun()
menu = st.session_state["menu"]
halaman = menu.split(" ", 1)[1]
st.sidebar.divider()
st.sidebar.selectbox(
    "Tampilan", ["Otomatis", "Terang", "Gelap"], key="mode_tampilan",
    format_func=lambda x: {"Otomatis": "🖥️ Otomatis (ikut perangkat)", "Terang": "☀️ Terang", "Gelap": "🌙 Gelap"}[x],
)
st.sidebar.caption("Terima kasih, petani Indonesia 🇮🇩")

hero(*HERO[halaman])

# ---------- Laporan ----------
if halaman == "Laporan":
    with st.spinner("Menghitung laporan..."):
        data = (db.table("laporan_musim_tanam").select("*")
                .order("tanggal_tanam", desc=True).execute().data)
    if not data:
        kosong("Belum ada data laporan", "Mulai dari menu Musim Tanam, lalu catat biaya dan hasil panen.")
        st.stop()
    df = pd.DataFrame(data)
    for k in ["total_biaya", "total_penjualan", "total_diterima", "sisa_piutang", "laba_rugi"]:
        df[k] = pd.to_numeric(df[k])
    laba = df["laba_rugi"].sum()
    fokus("Laba bersih" if laba >= 0 else "Rugi bersih", rp(laba),
          [("Pendapatan", rp(df["total_penjualan"].sum())), ("Biaya", rp(df["total_biaya"].sum())),
           ("Sisa piutang", rp(df["sisa_piutang"].sum()))], "" if laba >= 0 else "rugi")
    kiri, kanan = st.columns([1, 1.3], gap="large")
    with kiri:
        st.subheader("Aktivitas musim tanam")
        st.markdown('<ul class="lini">' + "".join(
            f'<li><b>{IKON.get(r.tanaman, "🌱")} {sel(r.tanaman)}</b>'
            f'<small>{tgl_id(r.tanggal_tanam)} · {"Selesai" if r.status == "selesai" else "Berjalan"}</small></li>'
            for r in df.itertuples()) + "</ul>", unsafe_allow_html=True)
    with kanan:
        st.subheader("Biaya dan penjualan")
        st.altair_chart(grafik(df), width="stretch")
    st.subheader("Rincian per musim tanam")
    for i, r in df.iterrows():
        status = "✅ selesai" if r["status"] == "selesai" else "🌿 berjalan"
        with st.expander(f'{IKON.get(r["tanaman"], "🌱")} {r["tanaman"]} ({tgl_id(r["tanggal_tanam"])}) · {status}',
                         expanded=(i == 0)):
            ok = r["laba_rugi"] >= 0
            st.markdown(pendukung([("Biaya", rp(r["total_biaya"])), ("Penjualan", rp(r["total_penjualan"])),
                                   ("Sisa piutang", rp(r["sisa_piutang"])),
                                   ("Laba" if ok else "Rugi", rp(r["laba_rugi"]))]), unsafe_allow_html=True)

# ---------- Musim Tanam ----------
elif halaman == "Musim Tanam":
    kiri, kanan = st.columns([1.15, 1], gap="large")
    with kiri:
        st.subheader("Tambah musim tanam")
        with st.form("form_musim", clear_on_submit=True):
            tanaman = st.selectbox("Tanaman", list(IKON))
            tgl = st.date_input("Tanggal tanam", value=date.today())
            luas = st.number_input("Luas lahan (hektar)", min_value=0.0, step=0.1)
            catatan = st.text_input("Catatan (opsional)")
            if st.form_submit_button("Simpan musim tanam", type="primary"):
                simpan("musim_tanam", {"tanaman": tanaman, "tanggal_tanam": str(tgl),
                                       "luas_ha": luas or None, "catatan": catatan or None})
    with kanan:
        n_jalan = sum(1 for m in musim if m["status"] == "berjalan")
        total_luas = sum(m["luas_ha"] or 0 for m in musim)
        st.markdown(
            f'<div class="panel"><small>Total musim tanam</small><div class="besar">{len(musim)}</div>'
            f'<div class="baris"><span>Sedang berjalan</span><b>{n_jalan}</b></div>'
            f'<div class="baris"><span>Sudah selesai</span><b>{len(musim) - n_jalan}</b></div>'
            f'<div class="baris"><span>Total luas dicatat</span><b>{total_luas:g} ha</b></div>{TUNAS}</div>',
            unsafe_allow_html=True)
    st.subheader("Daftar musim tanam")
    tabel([{**m, "tanaman": f'{IKON.get(m["tanaman"], "🌱")} {m["tanaman"]}',
            "tanggal_tanam": tgl_id(m["tanggal_tanam"]),
            "luas_ha": f'{m["luas_ha"]:g} ha' if m["luas_ha"] else "-"} for m in musim],
          [("Tanaman", "tanaman", "l"), ("Tanggal tanam", "tanggal_tanam", "l"), ("Luas", "luas_ha", "r"),
           ("Status", "status", "c"), ("Catatan", "catatan", "l")])
    berjalan = {m["id"]: nama_musim[m["id"]] for m in musim if m["status"] == "berjalan"}
    if berjalan:
        st.subheader("Tandai panen selesai")
        pilih = st.selectbox("Musim tanam", list(berjalan), format_func=berjalan.get)
        if st.button("Tandai selesai"):
            db.table("musim_tanam").update(
                {"status": "selesai", "tanggal_panen": str(date.today())}).eq("id", pilih).execute()
            st.session_state["pesan"] = "Selamat panen! 🌾"
            st.rerun()
    hapus_ui("musim_tanam", nama_musim, "Menghapus musim tanam juga menghapus biaya dan penjualannya.")

# ---------- Biaya ----------
elif halaman == "Biaya":
    if not musim:
        st.warning("Buat musim tanam dulu di menu Musim Tanam.")
        st.stop()
    semua = ambil("biaya")
    fokus("Total biaya", rp(sum(b["jumlah"] for b in semua)),
          [("Jumlah catatan", str(len(semua))), ("Musim tanam", str(len(musim)))], "oranye")
    st.subheader("Catat biaya")
    with st.form("form_biaya", clear_on_submit=True):
        mid = st.selectbox("Musim tanam", list(nama_musim), format_func=nama_musim.get)
        tgl = st.date_input("Tanggal", value=date.today())
        kat = st.selectbox("Kategori", ["bibit", "pupuk", "obat_tanaman", "upah", "listrik", "lainnya"])
        ket = st.text_input("Keterangan (opsional)")
        jml = st.number_input("Jumlah (Rp)", min_value=0, step=1000)
        if st.form_submit_button("Simpan biaya", type="primary"):
            simpan("biaya", {"musim_tanam_id": mid, "tanggal": str(tgl), "kategori": kat,
                             "keterangan": ket or None, "jumlah": jml})
    data = semua[:20]
    st.subheader("Riwayat biaya")
    if not data:
        kosong()
    else:
        st.caption(f"Menampilkan {len(data)} data terbaru")
        df = pd.DataFrame(data)
        df["musim"] = df["musim_tanam_id"].map(nama_musim)
        pilihan = {b["id"]: f'{b["tanggal"]} · {b["kategori"]} · {rp(b["jumlah"])}' for b in data}
        df["jumlah"] = df["jumlah"].map(rp)
        tabel(df.to_dict("records"), [("Tanggal", "tanggal", "l"), ("Musim tanam", "musim", "l"),
              ("Kategori", "kategori", "l"), ("Keterangan", "keterangan", "l"), ("Jumlah", "jumlah", "r")])
        hapus_ui("biaya", pilihan)

# ---------- Penjualan ----------
elif halaman == "Penjualan":
    if not musim:
        st.warning("Buat musim tanam dulu di menu Musim Tanam.")
        st.stop()
    semua = ambil("penjualan")
    per = lambda j: sum(p["total"] for p in semua if p["jenis_pembeli"] == j)
    fokus("Total penjualan", rp(sum(p["total"] for p in semua)),
          [("Ke tengkulak", rp(per("tengkulak"))), ("Ke mitra", rp(per("mitra"))),
           ("Total hasil terjual", f'{sum(p["jumlah_kg"] for p in semua):g} kg')], "hijau")
    st.subheader("Catat penjualan")
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
    data = semua[:20]
    st.subheader("Riwayat penjualan")
    if not data:
        kosong()
    else:
        st.caption(f"Menampilkan {len(data)} data terbaru")
        df = pd.DataFrame(data)
        df["musim"] = df["musim_tanam_id"].map(nama_musim)
        pilihan = {p["id"]: f'{p["tanggal"]} · {p["nama_pembeli"] or p["jenis_pembeli"]} · {rp(p["total"])}'
                   for p in data}
        df["total"] = df["total"].map(rp)
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
    bayar = ambil("pembayaran")
    dibayar = {}
    for y in bayar:
        dibayar[y["penjualan_id"]] = dibayar.get(y["penjualan_id"], 0) + y["jumlah"]
    total_jual = sum(p["total"] for p in jual)
    diterima = sum(dibayar.values())
    fokus("Pembayaran diterima", rp(diterima),
          [("Total penjualan", rp(total_jual)), ("Sisa piutang", rp(total_jual - diterima))], "hijau")
    label = {p["id"]: f'{p["tanggal"]} · {nama_musim.get(p["musim_tanam_id"])} · '
                      f'{p["nama_pembeli"] or p["jenis_pembeli"]} · {rp(p["total"])}' for p in jual}
    st.subheader("Status tiap penjualan")
    tabel([{"tanggal": p["tanggal"], "pembeli": p["nama_pembeli"] or p["jenis_pembeli"], "total": rp(p["total"]),
            "dibayar": rp(dibayar.get(p["id"], 0)),
            "status": "lunas" if dibayar.get(p["id"], 0) >= p["total"]
            else ("sebagian" if dibayar.get(p["id"], 0) > 0 else "belum")} for p in jual[:20]],
          [("Tanggal", "tanggal", "l"), ("Pembeli", "pembeli", "l"), ("Total", "total", "r"),
           ("Sudah dibayar", "dibayar", "r"), ("Status", "status", "c")])
    st.subheader("Catat pembayaran")
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
    data = bayar[:20]
    st.subheader("Riwayat pembayaran")
    if not data:
        kosong()
    else:
        st.caption(f"Menampilkan {len(data)} data terbaru")
        df = pd.DataFrame(data)
        df["penjualan"] = df["penjualan_id"].map(label)
        pilihan = {y["id"]: f'{y["tanggal"]} · {rp(y["jumlah"])}' for y in data}
        df["jumlah"] = df["jumlah"].map(rp)
        tabel(df.to_dict("records"), [("Tanggal", "tanggal", "l"), ("Penjualan", "penjualan", "l"),
              ("Jumlah", "jumlah", "r"), ("Keterangan", "keterangan", "l")])
        hapus_ui("pembayaran", pilihan)
