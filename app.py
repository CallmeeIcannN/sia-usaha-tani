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

def favicon():
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, 95, 95), radius=22, fill="#2D6A3E")
        d.text((48, 50), "SG", font=ImageFont.load_default(size=44), fill="#FFFFFF", anchor="mm")
        return img
    except Exception:
        return "🌾"


st.set_page_config(page_title="SAWAL GROUP", page_icon=favicon(), layout="wide")

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
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
:root{--foto:linear-gradient(#2A5A34,#2A5A34);--e1:0 1px 2px rgba(0,0,0,.14),0 1px 3px 1px rgba(0,0,0,.08)}
.stApp *:not([data-testid="stIconMaterial"]):not(svg):not(path){font-family:'Roboto','Segoe UI',system-ui,sans-serif}
.stApp{background:var(--bg)}
[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1100px;padding-top:1.6rem;padding-bottom:4rem;animation:naik .4s ease both}
@keyframes naik{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.stApp h3{font-weight:500;font-size:1.35rem;margin-top:2rem}
.appbar{display:flex;overflow:hidden;min-height:190px;margin-bottom:28px;border-radius:28px;background:var(--pri-c);color:var(--on-pri-c);box-shadow:var(--e1)}
.appbar .isi{flex:1 1 auto;padding:28px 32px;display:flex;flex-direction:column;justify-content:center}
.appbar .tag{align-self:flex-start;font-size:.8rem;font-weight:500;padding:4px 12px;border-radius:8px;background:var(--ter-c);color:var(--on-ter-c)}
.appbar .judul{margin:12px 0 6px;font-size:2rem;font-weight:500;line-height:1.2;text-wrap:balance}
.appbar .desk{font-size:1rem;opacity:.85;max-width:50ch}
.appbar .kutip{margin-top:12px;font-size:.85rem;font-style:italic;opacity:.7;max-width:56ch}
.appbar .foto{flex:0 0 34%;background:var(--foto);background-size:cover;background-position:center bottom;border-radius:45% 0 0 45%/50% 0 0 50%}
.metrikwrap,.tiles{display:flex;flex-wrap:wrap;gap:12px}.metrikwrap{margin:4px 0 8px}
.metrik{flex:1.7 1 300px;background:var(--pri-c);color:var(--on-pri-c);border-radius:28px;padding:24px 28px;box-shadow:var(--e1)}
.metrik.rugi{background:var(--err-c);color:var(--on-err-c)}.metrik.oranye{background:var(--ter-c);color:var(--on-ter-c)}
.metrik .lbl{font-size:.9rem;font-weight:500;opacity:.8}
.metrik .angka{font-size:3rem;font-weight:700;letter-spacing:-.02em;line-height:1.15;margin-top:4px}
.tile{flex:1 1 150px;background:var(--card);border-radius:20px;padding:18px 20px;box-shadow:var(--e1)}
.tile span{display:block;font-size:.8rem;color:var(--muted)}
.tile b{display:block;margin-top:4px;font-size:1.2rem;font-weight:700;color:var(--teks)}
.lini{list-style:none;margin:0 0 0 6px;padding:0 0 0 14px;border-left:2px solid var(--garis)}
.lini li{position:relative;padding:0 0 18px 16px;color:var(--teks)}
.lini li::before{content:"";position:absolute;left:-23px;top:5px;width:12px;height:12px;border-radius:50%;background:var(--pri);border:2px solid var(--bg)}
.lini small{display:block;color:var(--muted);margin-top:2px}
.buku{margin-top:1.1rem;background:var(--card);border:1px solid var(--garis);border-radius:14px;padding:4px 20px 12px}
.buku .kepala{padding:14px 0 8px;font-size:.82rem;font-weight:500;color:var(--muted);border-bottom:1px solid var(--garis)}
.rk{width:100%;border-collapse:collapse;color:var(--teks);font-size:.93rem}
.rk td{padding:9px 0;border-bottom:1px dotted var(--garis)}.rk tr:last-child td{border-bottom:0}
.rk .r{text-align:right;font-weight:500;font-variant-numeric:tabular-nums}
.rk .th td{font-size:.78rem;color:var(--muted);font-weight:500}
.tabelbox{background:var(--card);border-radius:16px;overflow-x:auto;box-shadow:var(--e1)}
.tabel{width:100%;border-collapse:collapse;font-size:.92rem;color:var(--teks)}
.tabel th{background:var(--head);font-weight:500;font-size:.8rem;color:var(--muted);padding:12px 16px;text-align:left;white-space:nowrap}
.tabel td{padding:12px 16px;border-top:1px solid var(--garis)}
.tabel .r{text-align:right;font-variant-numeric:tabular-nums}.tabel .c{text-align:center}
.tabel tbody tr{transition:background .15s}.tabel tbody tr:hover{background:var(--hover)}
.badge{display:inline-block;padding:3px 10px;border-radius:8px;font-size:.78rem;font-weight:500;white-space:nowrap}
.badge.ok{background:rgba(62,142,65,.2);color:var(--ok)}.badge.jalan{background:rgba(217,154,27,.22);color:var(--warn)}
.badge.belum{background:rgba(186,26,26,.14);color:var(--bad)}
.kosong{background:var(--card);border:1px dashed var(--garis);border-radius:16px;padding:28px 16px;text-align:center;color:var(--teks)}
.kosong .ik{font-size:1.8rem}.kosong b{display:block;margin-top:6px}
.kosong span{display:block;margin-top:4px;font-size:.88rem;color:var(--muted)}
[data-testid="stForm"]{background:var(--card);border:0;border-radius:24px;padding:22px;box-shadow:var(--e1)}
[data-testid="stExpander"] details{background:var(--card);border:0!important;border-radius:16px;box-shadow:var(--e1)}
[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="select"]>div{border-radius:8px!important}
[data-baseweb="input"]:focus-within{border-color:var(--pri)!important;box-shadow:0 0 0 1px var(--pri)!important}
[data-testid="stNumberInputStepUp"],[data-testid="stNumberInputStepDown"]{background:transparent!important}
[data-testid="stNumberInputStepUp"]:hover,[data-testid="stNumberInputStepDown"]:hover{background:var(--hover)!important}
div.stButton>button,div.stFormSubmitButton>button{min-height:40px;padding:0 24px;border-radius:20px;font-weight:500;transition:box-shadow .15s,filter .15s}
div.stButton>button:hover,div.stFormSubmitButton>button:hover{box-shadow:var(--e1);filter:brightness(1.06)}
[data-testid^="stBaseButton-primary"]{background:var(--pri)!important;color:var(--on-pri)!important;border:0!important}
[data-testid^="stBaseButton-secondary"]{background:var(--sek-c)!important;color:var(--on-sek-c)!important;border:0!important}
[class*="st-key-b_"] button{background:var(--bad)!important;color:var(--bg)!important;border:0!important}
[class*="st-key-b_"] button:disabled{opacity:.4}
[data-testid="stSidebar"]{background:var(--card)!important;border-radius:0 28px 28px 0}
.logo{display:flex;align-items:center;gap:12px;padding:6px 6px 20px}
.logo .mark{flex:none;width:54px;height:54px;border-radius:50%;overflow:hidden;display:flex;align-items:center;justify-content:center;
 background:var(--pri);color:var(--on-pri);font-weight:700;font-size:1.1rem;letter-spacing:.04em;box-shadow:var(--e1)}
.logo .mark img{width:100%;height:100%;object-fit:cover}
.logo .nama b{display:block;font-size:1.1rem;font-weight:700;letter-spacing:.06em;color:var(--teks)}
.logo .nama span{display:block;margin-top:2px;font-size:.78rem;line-height:1.3;color:var(--muted)}
[data-testid="stSidebar"] .stButton>button{justify-content:flex-start;gap:10px;min-height:48px;border-radius:28px;background:transparent!important;color:var(--teks)!important}
[data-testid="stSidebar"] .stButton>button:hover{background:var(--hover)!important;box-shadow:none;filter:none}
[data-testid="stSidebar"] .stButton>button[data-testid="stBaseButton-primary"]{background:var(--sek-c)!important;color:var(--on-sek-c)!important;font-weight:700}
[data-testid="stSidebar"] .stButton>button>div{justify-content:flex-start!important;width:100%}
[data-testid="stSidebar"] .stButton>button p{text-align:left}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:.4rem}
@media (max-width:640px){.appbar{flex-direction:column-reverse;min-height:0}.appbar .foto{flex:0 0 110px;border-radius:0 0 45% 45%/0 0 60% 60%}
 .appbar .isi{padding:22px}.appbar .judul{font-size:1.6rem}.metrik .angka{font-size:2.2rem}.tabel th,.tabel td{padding:10px 12px}}
@media (prefers-reduced-motion:reduce){.block-container{animation:none}div.stButton>button,div.stFormSubmitButton>button,.tabel tbody tr{transition:none}}
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


@st.cache_data
def foto_ayah():
    """Cari foto profil (nama file diawali 'ayah') di folder aplikasi, potong persegi, ubah ke base64."""
    from PIL import Image, ImageOps
    for nama in sorted(os.listdir(".")):
        if nama.lower().startswith("ayah") and nama.lower().endswith((".jpg", ".jpeg", ".png")):
            img = ImageOps.exif_transpose(Image.open(nama)).convert("RGB")
            img = ImageOps.fit(img, (160, 160), method=Image.LANCZOS, centering=(0.5, 0.35))
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=82)
            return base64.b64encode(buf.getvalue()).decode()
    return None


LIGHT = ("--bg:#F6FBF1;--card:#EAF0E4;--garis:#C1C9BC;--muted:#414941;--head:#DDE5D6;--hover:rgba(45,106,62,.08);"
         "--teks:#181D17;--ok:#1B5E20;--warn:#6B4F00;--bad:#BA1A1A;--pri:#2D6A3E;--on-pri:#FFFFFF;--pri-c:#BDEDC3;"
         "--on-pri-c:#00210D;--sek-c:#D6E8D2;--on-sek-c:#111F13;--ter-c:#FFDF9B;--on-ter-c:#251A00;--err-c:#FFDAD6;--on-err-c:#410002")
DARK = ("--bg:#101512;--card:#1A211C;--garis:#414941;--muted:#C1C9BC;--head:#232B25;--hover:rgba(160,214,167,.10);"
        "--teks:#E0E4DA;--ok:#8FD99A;--warn:#F0C463;--bad:#FFB4AB;--pri:#8FD99A;--on-pri:#00391A;--pri-c:#1B5030;"
        "--on-pri-c:#B8F0BF;--sek-c:#3A4B3C;--on-sek-c:#D6E8D2;--ter-c:#5A4300;--on-ter-c:#FFDF9B;--err-c:#93000A;--on-err-c:#FFDAD6")
TEMA = {
    "Terang": dict(vars=LIGHT, bg="#F6FBF1", teks="#181D17", input="#FFFFFF"),
    "Gelap": dict(vars=DARK, bg="#101512", teks="#E0E4DA", input="#232B25"),
}


def css_tampilan(mode, foto):
    css = f":root{{--foto:url(data:image/jpeg;base64,{foto})}}" if foto else ""
    if mode not in TEMA:  # Otomatis: ikut pengaturan perangkat
        return css + f":root{{{LIGHT}}}@media (prefers-color-scheme:dark){{:root{{{DARK}}}}}"
    t = TEMA[mode]
    return css + f":root{{{t['vars']}}}" + (
        f'.stApp{{background-color:{t["bg"]}!important;color:{t["teks"]}!important}}'
        f'.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,.stApp li,'
        f'.stApp [data-testid="stMarkdownContainer"],.stApp [data-testid="stCaptionContainer"]'
        f'{{color:{t["teks"]}!important}}'
        f'.stApp [data-baseweb="input"],.stApp [data-baseweb="base-input"],.stApp [data-baseweb="select"]>div,'
        f'.stApp textarea,.stApp input{{background-color:{t["input"]}!important;color:{t["teks"]}!important}}'
    )


_css = css_tampilan(st.session_state.get("mode_tampilan", "Otomatis"), foto_latar())
st.markdown(f"<style>{_css}</style>", unsafe_allow_html=True)

st.session_state.setdefault("kutipan", random.choice(KUTIPAN))

HERO = {
    "Laporan": ("Laporan", "Pantau kondisi keuangan usaha tani", "Biaya, penjualan, dan laba dalam satu tampilan.", "kuning"),
    "Musim Tanam": ("Musim Tanam", "Kelola musim tanam di lahanmu", "Kelola data musim tanam dan aktivitas lahan.", "hijau"),
    "Biaya": ("Biaya", "Catat setiap pengeluaran", "Agar kondisi usaha tani tetap terkontrol.", "oranye"),
    "Penjualan": ("Penjualan", "Hasil usaha tani", "Catat hasil panen yang terjual dan pantau pendapatan.", "kuning"),
    "Pembayaran": ("Pembayaran", "Arus pembayaran", "Pantau uang yang sudah diterima dan sisa piutang.", "sage"),
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


def hero(tag, judul, desk="", aksen=""):
    st.markdown(
        f'<div class="appbar"><div class="isi"><span class="tag">{tag}</span>'
        f'<div class="judul">{judul}</div><div class="desk">{desk}</div>'
        f'<div class="kutip">“{st.session_state["kutipan"]}”</div></div><div class="foto"></div></div>',
        unsafe_allow_html=True,
    )


def tiles(items):
    return "".join(f'<div class="tile"><span>{k}</span><b>{v}</b></div>' for k, v in items)


def pendukung(items):
    return f'<div class="tiles">{tiles(items)}</div>'


def fokus(label, nilai, items, kelas=""):
    st.markdown(f'<div class="metrikwrap"><div class="metrik {kelas}"><div class="lbl">{label}</div>'
                f'<div class="angka">{nilai}</div></div>{tiles(items)}</div>', unsafe_allow_html=True)


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
    hero("SAWAL GROUP", "Catatan keuangan usaha tani", "Masuk untuk membuka catatan usaha tani.")
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
MENU = [("Laporan", ":material/monitoring:"), ("Musim Tanam", ":material/potted_plant:"),
        ("Biaya", ":material/receipt_long:"), ("Penjualan", ":material/shopping_basket:"),
        ("Pembayaran", ":material/account_balance_wallet:")]
st.session_state.setdefault("menu", "Laporan")
if st.session_state["menu"] not in dict(MENU):
    st.session_state["menu"] = "Laporan"
_ay = foto_ayah()
_mark = f'<img src="data:image/jpeg;base64,{_ay}" alt="">' if _ay else "SG"
st.sidebar.markdown(
    f'<div class="logo"><div class="mark">{_mark}</div><div class="nama"><b>SAWAL GROUP</b>'
    '<span>Usaha tani · catatan keuangan</span></div></div>', unsafe_allow_html=True)
for nama, ikon in MENU:
    if st.sidebar.button(nama, icon=ikon, key="nav_" + nama.replace(" ", "_"), width="stretch",
                         type="primary" if st.session_state["menu"] == nama else "secondary"):
        st.session_state["menu"] = nama
        st.rerun()
halaman = st.session_state["menu"]
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
        per = {}
        for m in musim:
            d = per.setdefault(m["tanaman"], [0, 0.0])
            d[0] += 1
            d[1] += m["luas_ha"] or 0
        komoditas = "".join(f'<tr><td>{sel(k)}</td><td class="r">{v[0]}</td><td class="r">{v[1]:g} ha</td></tr>'
                            for k, v in per.items())
        st.markdown(
            '<div class="buku"><div class="kepala">Ringkasan musim tanam</div><table class="rk">'
            f'<tr><td>Total musim tanam</td><td class="r">{len(musim)}</td></tr>'
            f'<tr><td>Sedang berjalan</td><td class="r">{n_jalan}</td></tr>'
            f'<tr><td>Sudah selesai</td><td class="r">{len(musim) - n_jalan}</td></tr>'
            f'<tr><td>Total luas dicatat</td><td class="r">{total_luas:g} ha</td></tr></table>'
            '<div class="kepala">Per komoditas</div><table class="rk">'
            '<tr class="th"><td>Komoditas</td><td class="r">Musim</td><td class="r">Luas</td></tr>'
            f'{komoditas}</table></div>',
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
