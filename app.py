import altair as alt
import base64
import html
import io
import os
from datetime import date

import pandas as pd
import streamlit as st
from supabase import create_client


def favicon():
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, 95, 95), radius=22, fill="#15803D")
        d.text((48, 50), "SG", font=ImageFont.load_default(size=44), fill="#FFFFFF", anchor="mm")
        return img
    except Exception:
        return "🌾"


st.set_page_config(page_title="SAWAL GROUP", page_icon=favicon(), layout="wide", initial_sidebar_state="expanded")

KOMODITAS = ["Kentang", "Cabai", "Kobis", "Jagung"]
KATEGORI = {"bibit": ("Bibit", "blue"), "pupuk": ("Pupuk", "ok"), "obat_tanaman": ("Pestisida", "amber"),
            "upah": ("Upah", "slate"), "listrik": ("Operasional", "violet"), "lainnya": ("Lainnya", "rose")}
PEMBELI = {"tengkulak": ("Tengkulak", "amber"), "mitra": ("Mitra", "blue"), "eceran": ("Eceran", "slate")}
STATUS = {"selesai": ("ok", "Selesai"), "berjalan": ("ok", "Berjalan"), "lunas": ("ok", "Lunas"),
          "sebagian": ("amber", "Cicilan"), "belum": ("rose", "Belum Lunas")}
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus",
         "September", "Oktober", "November", "Desember"]
HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
HALAMAN = {
    "Laporan": "Ringkasan keuangan dan kinerja tiap musim tanam.",
    "Musim Tanam": "Kelola data musim tanam dan aktivitas lahan.",
    "Biaya": "Catat dan pantau biaya operasional usaha tani.",
    "Penjualan": "Catat hasil panen yang terjual berdasarkan saluran penjualan.",
    "Pembayaran": "Pantau tagihan penjualan dan arus kas yang diterima.",
}
MENU = [("Laporan", ":material/monitoring:"), ("Musim Tanam", ":material/potted_plant:"),
        ("Biaya", ":material/receipt_long:"), ("Penjualan", ":material/shopping_basket:"),
        ("Pembayaran", ":material/account_balance_wallet:")]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
.stApp *:not([data-testid="stIconMaterial"]):not(svg):not(path){font-family:'Inter','Segoe UI',system-ui,sans-serif}
.stApp{background:var(--bg)}
[data-testid="stToolbarActions"],[data-testid="stMainMenu"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],#MainMenu,footer,
[data-testid="stAppDeployButton"],[class*="viewerBadge"],[class*="_profileContainer"]{display:none!important}
[data-testid="stHeader"]{background:transparent}
[data-testid="stExpandSidebarButton"]{display:flex!important}
.block-container{max-width:1240px;padding-top:1.4rem;padding-bottom:4rem}
.stApp h3{font-weight:600;font-size:1.05rem;margin:1.4rem 0 .6rem;color:var(--teks)}
.crumb{font-size:.88rem;color:var(--muted)}.crumb b{color:var(--teks);font-weight:600}.crumb span{display:block;font-size:.76rem;margin-top:2px}
.judul{font-size:1.65rem;font-weight:700;letter-spacing:-.02em;color:var(--teks);margin:14px 0 2px}
.sub{font-size:.92rem;color:var(--muted);margin-bottom:18px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-bottom:18px}
.stat{background:var(--card);border:1px solid var(--garis);border-radius:12px;padding:16px 18px;box-shadow:0 1px 2px rgba(15,23,42,.06)}
.stat .l{font-size:.8rem;color:var(--muted);font-weight:500}
.stat .v{margin-top:6px;font-size:1.5rem;font-weight:700;letter-spacing:-.01em;font-variant-numeric:tabular-nums;color:var(--teks)}
.stat .s{margin-top:4px;font-size:.78rem;color:var(--muted)}
.stat.hl{background:var(--pri);border-color:var(--pri)}.stat.hl .l,.stat.hl .s{color:rgba(255,255,255,.88)}.stat.hl .v{color:#fff}
.stat.ok .v{color:var(--ok-fg)}
.dot{display:inline-block;width:8px;height:8px;margin-right:8px;border-radius:50%;background:var(--pri);animation:denyut 1.6s infinite}
@keyframes denyut{0%{box-shadow:0 0 0 0 rgba(21,128,61,.5)}70%{box-shadow:0 0 0 7px rgba(21,128,61,0)}100%{box-shadow:0 0 0 0 rgba(21,128,61,0)}}
.pill{display:inline-block;padding:2px 10px;border-radius:999px;font-size:.74rem;font-weight:600;white-space:nowrap}
.pill.ok{background:var(--ok-bg);color:var(--ok-fg)}.pill.amber{background:var(--am-bg);color:var(--am-fg)}
.pill.blue{background:var(--bl-bg);color:var(--bl-fg)}.pill.rose{background:var(--ro-bg);color:var(--ro-fg)}
.pill.slate{background:var(--sl-bg);color:var(--sl-fg)}.pill.violet{background:var(--vi-bg);color:var(--vi-fg)}
.pos{color:var(--ok-fg);font-weight:600}.neg{color:var(--ro-fg);font-weight:600}
.mut{display:block;font-size:.74rem;color:var(--muted)}
[data-testid="stVerticalBlockBorderWrapper"]{background:var(--card);border:1px solid var(--garis)!important;border-radius:12px;box-shadow:0 1px 2px rgba(15,23,42,.05)}
.tabelbox{background:var(--card);border:1px solid var(--garis);border-radius:12px;overflow-x:auto;box-shadow:0 1px 2px rgba(15,23,42,.05)}
.tabel{width:100%;border-collapse:collapse;font-size:.88rem;color:var(--teks)}
.tabel th{background:var(--head);font-weight:600;font-size:.74rem;color:var(--muted);padding:10px 14px;text-align:left;white-space:nowrap}
.tabel td{padding:11px 14px;border-top:1px solid var(--garis);font-variant-numeric:tabular-nums}
.tabel .r,.th.r,.td.r{text-align:right}.tabel .c,.th.c,.td.c{text-align:center}
.tabel tbody tr:hover{background:var(--hover)}
.th{font-size:.74rem;font-weight:600;color:var(--muted)}.td{font-size:.88rem;color:var(--teks);font-variant-numeric:tabular-nums}
[class*="st-key-daftar_"] [data-testid="stVerticalBlock"]{gap:0}
[class*="st-key-daftar_"] [data-testid="stHorizontalBlock"]{padding:7px 8px;border-bottom:1px solid var(--garis);align-items:center}
[class*="st-key-daftar_"] [data-testid="stHorizontalBlock"]:hover{background:var(--hover)}
[class*="st-key-daftar_"] .stButton>button,[class*="st-key-daftar_"] [data-testid="stPopover"]>button{min-height:30px;padding:0 10px;font-size:.78rem;border-radius:8px}
.kosong{border:1px dashed var(--garis);border-radius:12px;padding:26px 16px;text-align:center;color:var(--teks);background:var(--card)}
.kosong b{display:block}.kosong span{display:block;margin-top:4px;font-size:.86rem;color:var(--muted)}
.bar{margin:10px 0}.bar .a{display:flex;justify-content:space-between;font-size:.84rem;color:var(--teks)}.bar .a span{color:var(--muted);font-variant-numeric:tabular-nums}
.bar .t{height:8px;border-radius:99px;background:var(--head);margin-top:5px;overflow:hidden}.bar .t i{display:block;height:100%;background:var(--pri);border-radius:99px}
.sub-total{background:var(--head);border-radius:10px;padding:12px 14px;margin:4px 0 12px;display:flex;justify-content:space-between;align-items:center;color:var(--teks)}
.sub-total span{font-size:.8rem;color:var(--muted)}.sub-total b{font-size:1.2rem;font-variant-numeric:tabular-nums}
[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="select"]>div{border-radius:8px!important}
[data-baseweb="input"]:focus-within{border-color:var(--pri)!important;box-shadow:0 0 0 3px rgba(21,128,61,.2)!important}
div.stButton>button,div.stFormSubmitButton>button,[data-testid="stPopover"]>button{min-height:38px;border-radius:8px;font-weight:600;transition:background .15s,box-shadow .15s}
[data-testid^="stBaseButton-primary"]{background:var(--pri)!important;color:#fff!important;border:0!important}
[data-testid^="stBaseButton-primary"]:hover{filter:brightness(.92)}
[data-testid^="stBaseButton-secondary"]{background:var(--card)!important;color:var(--teks)!important;border:1px solid var(--garis)!important}
[data-testid^="stBaseButton-secondary"]:hover{background:var(--hover)!important}
[class*="st-key-b_"] button{background:var(--ro-fg)!important;color:#fff!important;border:0!important}
[data-testid="stSidebar"]{background:var(--card)!important;border-right:1px solid var(--garis)}
.logo{display:flex;align-items:center;gap:11px;padding:4px 4px 18px}
.logo .mark{flex:none;width:42px;height:42px;border-radius:10px;overflow:hidden;display:flex;align-items:center;justify-content:center;background:var(--pri);color:#fff;font-weight:700;font-size:.95rem}
.logo .mark img{width:100%;height:100%;object-fit:cover}
.logo b{display:block;font-size:.98rem;font-weight:700;letter-spacing:.04em;color:var(--teks)}.logo span{display:block;font-size:.72rem;color:var(--muted)}
[data-testid="stSidebar"] .stButton>button{justify-content:flex-start!important;gap:10px;min-height:40px;border:0!important;background:transparent!important;color:var(--muted)!important;font-weight:500}
[data-testid="stSidebar"] .stButton>button>div{justify-content:flex-start!important;width:100%}
[data-testid="stSidebar"] .stButton>button p{text-align:left}
[data-testid="stSidebar"] .stButton>button:hover{background:var(--hover)!important;color:var(--teks)!important}
[data-testid="stSidebar"] .stButton>button[data-testid="stBaseButton-primary"]{background:var(--ok-bg)!important;color:var(--ok-fg)!important;font-weight:600}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:.3rem}
.profil{display:flex;align-items:center;gap:10px;padding:10px 4px 0;color:var(--teks);font-size:.84rem}
.profil .mark{width:34px;height:34px;border-radius:50%;overflow:hidden;display:flex;align-items:center;justify-content:center;background:var(--sl-bg);color:var(--sl-fg);font-weight:700;font-size:.8rem}
.profil .mark img{width:100%;height:100%;object-fit:cover}.profil span{display:block;font-size:.72rem;color:var(--muted)}
[class*="st-key-hal_"]{animation:fadeIn .35s ease both}
@keyframes fadeIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
div.stButton>button,div.stFormSubmitButton>button,[data-testid="stPopover"]>button{transition:transform .15s,box-shadow .15s,background .15s}
div.stButton>button:hover,div.stFormSubmitButton>button:hover,[data-testid="stPopover"]>button:hover{transform:translateY(-1px);box-shadow:0 4px 10px rgba(15,23,42,.14)}
div.stButton>button:active,div.stFormSubmitButton>button:active,[data-testid="stPopover"]>button:active{transform:scale(.95);box-shadow:none}
[data-testid="stSidebar"] .stButton>button:hover{transform:none;box-shadow:none}
@media (prefers-reduced-motion:reduce){[class*="st-key-hal_"]{animation:none}div.stButton>button:hover,div.stButton>button:active{transform:none}}
@media (max-width:640px){.judul{font-size:1.35rem}.stat .v{font-size:1.25rem}}
@media (prefers-reduced-motion:reduce){.dot{animation:none}}
</style>
""", unsafe_allow_html=True)

LIGHT = ("--bg:#F8FAFC;--card:#FFFFFF;--garis:#E2E8F0;--muted:#64748B;--head:#F1F5F9;--hover:#F1F5F9;--teks:#0F172A;"
         "--pri:#15803D;--ok-bg:#DCFCE7;--ok-fg:#166534;--am-bg:#FEF3C7;--am-fg:#B45309;--bl-bg:#DBEAFE;--bl-fg:#1D4ED8;"
         "--ro-bg:#FFE4E6;--ro-fg:#BE123C;--sl-bg:#E2E8F0;--sl-fg:#334155;--vi-bg:#EDE9FE;--vi-fg:#6D28D9")
DARK = ("--bg:#0B1220;--card:#111A2C;--garis:#1F2A3F;--muted:#94A3B8;--head:#16213A;--hover:#16213A;--teks:#E2E8F0;"
        "--pri:#16A34A;--ok-bg:#14532D;--ok-fg:#86EFAC;--am-bg:#451A03;--am-fg:#FCD34D;--bl-bg:#1E3A8A;--bl-fg:#93C5FD;"
        "--ro-bg:#4C0519;--ro-fg:#FDA4AF;--sl-bg:#1E293B;--sl-fg:#CBD5E1;--vi-bg:#2E1065;--vi-fg:#C4B5FD")


GELAP = (
    '.stApp{background-color:#0B1220!important;color:#E2E8F0!important}'
    '.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,.stApp li,.stApp span,'
    '.stApp [data-testid="stMarkdownContainer"],.stApp [data-testid="stCaptionContainer"]{color:#E2E8F0!important}'
    '.stApp .tile span,.stApp .stat .l,.stApp .stat .s,.stApp .mut,.stApp .th,.stApp .sub,.stApp .crumb,.stApp .logo span,'
    '.stApp .sub-total span,.stApp .bar .a span{color:#94A3B8!important}'
    '.stApp .stat.hl .l,.stApp .stat.hl .s,.stApp .stat.hl .v{color:#FFFFFF!important}'
    '.stApp [data-baseweb="input"],.stApp [data-baseweb="base-input"],.stApp [data-baseweb="select"]>div,'
    '.stApp textarea,.stApp input{background-color:#16213A!important;color:#E2E8F0!important;'
    'border-color:#334155!important;-webkit-text-fill-color:#E2E8F0!important}'
    '.stApp input::placeholder,.stApp textarea::placeholder{color:#94A3B8!important;opacity:1!important;'
    '-webkit-text-fill-color:#94A3B8!important}'
    '.stApp [data-baseweb="select"] *,.stApp [data-baseweb="input"] svg{color:#E2E8F0!important;fill:#CBD5E1!important}'
    '.stApp [data-baseweb="input"]:focus-within{border-color:#22C55E!important}'
    '[data-baseweb="popover"],[data-baseweb="popover"]>div,[data-baseweb="menu"],[data-baseweb="popover"] ul,'
    '[data-testid="stPopoverBody"]{background-color:#16213A!important;color:#E2E8F0!important}'
    '[data-baseweb="popover"] *{color:#E2E8F0!important}'
    '[data-baseweb="popover"] li:hover,[data-baseweb="menu"] li:hover{background-color:#1F2A3F!important}'
    '.stApp [data-testid^="stBaseButton-secondary"]{background:#111A2C!important;color:#E2E8F0!important;border-color:#334155!important}'
)
TERANG = (
    '.stApp{background-color:#F8FAFC!important;color:#0F172A!important}'
    '.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,.stApp li,'
    '.stApp [data-testid="stMarkdownContainer"],.stApp [data-testid="stCaptionContainer"]{color:#0F172A!important}'
    '.stApp [data-baseweb="input"],.stApp [data-baseweb="base-input"],.stApp [data-baseweb="select"]>div,'
    '.stApp textarea,.stApp input{background-color:#FFFFFF!important;color:#0F172A!important}'
)


def css_tampilan(mode):
    if mode == "Gelap":
        return f":root{{{DARK}}}" + GELAP
    if mode == "Terang":
        return f":root{{{LIGHT}}}" + TERANG
    # Otomatis: ikut perangkat (komponen bawaan Streamlit tetap terang, jadi mode gelap perangkat ditambal sama seperti Gelap)
    return f":root{{{LIGHT}}}@media (prefers-color-scheme:dark){{:root{{{DARK}}}{GELAP}}}"


st.session_state.setdefault("mode_tampilan", "Terang")
st.markdown(f"<style>{css_tampilan(st.session_state['mode_tampilan'])}</style>", unsafe_allow_html=True)


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


def tgl_id(s):
    try:
        y, m, d = str(s)[:10].split("-")
        return f"{int(d):02d} {BULAN[int(m) - 1]} {y}"
    except Exception:
        return str(s)


def bln_thn(s):
    try:
        y, m, _ = str(s)[:10].split("-")
        return f"{BULAN[int(m) - 1][:3]} {y}"
    except Exception:
        return str(s)


def rp(x):
    return "Rp {:,.0f}".format(x or 0).replace(",", ".")


def sel(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return html.escape(str(v)).replace("$", "&#36;")


# ---------- Halaman awal dan login ----------
@st.cache_data
def foto_latar():
    """Cari foto latar (nama file diawali 'latar') di folder aplikasi, perkecil, ubah ke base64."""
    from PIL import Image
    for nama in sorted(os.listdir(".")):
        if nama.lower().startswith("latar") and nama.lower().endswith((".jpg", ".jpeg", ".png")):
            img = Image.open(nama).convert("RGB")
            img.thumbnail((1600, 1600))
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=72)
            return base64.b64encode(buf.getvalue()).decode()
    return None


CSS_DEPAN = """
<style>
:root{--foto:FOTO_LATAR}
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="stExpandSidebarButton"]{display:none!important}
.lencana{width:112px;height:112px;margin:0 auto 22px;border-radius:50%;background:#15803D;border:6px solid rgba(255,255,255,.92);
 display:flex;align-items:center;justify-content:center;font-size:2rem;font-weight:700;letter-spacing:.04em;color:#fff;box-shadow:0 10px 30px rgba(0,0,0,.35)}
.latar-hijau{background-image:linear-gradient(rgba(10,45,22,.80),rgba(10,45,22,.90)),var(--foto);background-size:cover;background-position:center bottom}
CSS_TAHAP
</style>
"""
CSS_AWAL = """
.stApp{background-image:linear-gradient(rgba(10,45,22,.78),rgba(10,45,22,.90)),var(--foto);background-size:cover;background-position:center bottom;background-attachment:fixed}
.block-container{max-width:760px;padding-top:15vh}
.awal{text-align:center;animation:naik .6s ease both}
.awal .t1{font-size:2.8rem;font-weight:800;letter-spacing:.06em;color:#fff!important}
.awal .t2{font-size:1.2rem;margin:8px 0 14px;color:#E2F5E8!important}
.awal .t3{max-width:46ch;margin:0 auto 28px;color:#CFE9D8!important;line-height:1.6}
.stApp [class*="st-key-awal_masuk"] button{background:#fff!important;color:#15803D!important;border:0!important;border-radius:999px;font-weight:700;min-height:48px}
@keyframes naik{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@media (max-width:640px){.awal .t1{font-size:2rem}}
"""
CSS_LOGIN = """
.block-container{max-width:100%!important;padding:0!important}
[data-testid="stHorizontalBlock"]{gap:0!important}
.kiri{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:40px;color:#fff;
 animation:geser .55s ease both}
.kiri .t1{font-size:1.9rem;font-weight:800;letter-spacing:.05em;color:#fff!important}
.kiri .t2{margin-top:6px;color:#CFE9D8!important}
[class*="st-key-loginform"]{min-height:100vh;display:flex;flex-direction:column;justify-content:center;padding:0 13%;background:var(--card);animation:masukKanan .55s ease both}
.sambut{text-align:center;font-size:1.9rem;font-weight:800;color:var(--teks)}
.sambut-s{text-align:center;color:var(--muted);margin:4px 0 22px}
.hakcipta{text-align:center;color:var(--muted);font-size:.78rem;margin-top:18px}
@keyframes geser{from{transform:translateX(-24%);opacity:.35}to{transform:none;opacity:1}}
@keyframes masukKanan{from{opacity:0;transform:translateX(28px)}to{opacity:1;transform:none}}
@media (max-width:768px){.kiri{min-height:32vh;padding:28px}[class*="st-key-loginform"]{min-height:auto;padding:28px 8%}}
@media (prefers-reduced-motion:reduce){.awal,.kiri,[class*="st-key-loginform"]{animation:none}}
"""


def css_depan(tahap):
    foto = foto_latar()
    var = f"url(data:image/jpeg;base64,{foto})" if foto else "linear-gradient(#14532D,#14532D)"
    isi = (CSS_DEPAN.replace("FOTO_LATAR", var)
           .replace("CSS_TAHAP", CSS_AWAL if tahap == "awal" else CSS_LOGIN))
    st.markdown(isi, unsafe_allow_html=True)


if not st.session_state.get("masuk"):
    st.session_state.setdefault("tahap", "awal")
    css_depan(st.session_state["tahap"])
    if st.session_state["tahap"] == "awal":
        st.markdown('<div class="awal"><div class="lencana">SG</div><div class="t1">SAWAL GROUP</div>'
                    '<div class="t2">Sistem Catatan Keuangan Usaha Tani</div>'
                    '<div class="t3">Catat biaya, penjualan, dan pembayaran usaha tani dengan rapi, '
                    'agar laba dan sisa piutang selalu jelas.</div></div>', unsafe_allow_html=True)
        _, _tengah, _ = st.columns([1, 1, 1])
        with _tengah:
            if st.button("Masuk Sekarang", key="awal_masuk", type="primary", width="stretch"):
                st.session_state["tahap"] = "login"
                st.rerun()
    else:
        _kiri, _kanan = st.columns(2)
        with _kiri:
            st.markdown('<div class="kiri latar-hijau"><div class="lencana">SG</div><div class="t1">SAWAL GROUP</div>'
                        '<div class="t2">Usaha Tani · Catatan Keuangan</div></div>', unsafe_allow_html=True)
        with _kanan, st.container(key="loginform"):
            st.markdown('<div class="sambut">Selamat Datang</div>'
                        '<div class="sambut-s">Silakan masuk untuk mengakses sistem</div>', unsafe_allow_html=True)
            with st.form("form_login", border=False):
                _sandi = st.text_input("Kata sandi", type="password")
                _kirim = st.form_submit_button("MASUK SISTEM", type="primary", width="stretch")
            if _kirim:
                if _sandi == st.secrets["APP_PASSWORD"]:
                    st.session_state["masuk"] = True
                    st.rerun()
                else:
                    st.error("Kata sandi belum cocok. Coba ketik ulang dengan teliti.")
            if st.button("Kembali ke beranda", key="kembali", width="stretch"):
                st.session_state["tahap"] = "awal"
                st.rerun()
            st.markdown('<div class="hakcipta">© 2026 SAWAL GROUP. Seluruh hak dilindungi.</div>', unsafe_allow_html=True)
    st.stop()

if "pesan" in st.session_state:
    st.toast(st.session_state.pop("pesan"))
if "galat" in st.session_state:
    st.error(st.session_state.pop("galat"))


@st.cache_resource
def koneksi():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


db = koneksi()


def ambil(tabel, urut="id"):
    return db.table(tabel).select("*").order(urut, desc=True).execute().data


def simpan(tabel, data):
    try:
        db.table(tabel).insert(data).execute()
        st.session_state["pesan"] = "Data tersimpan."
        st.rerun()
    except Exception as e:
        st.error(f"Data belum tersimpan. Periksa isian lalu coba lagi. ({e})")


def hapus(tabel, i):
    db.table(tabel).delete().eq("id", i).execute()
    st.session_state["pesan"] = "Data sudah dihapus."
    st.rerun()


# ---------- Komponen tampilan ----------
def stat(label, nilai, sub="", kelas=""):
    s = f'<div class="s">{sub}</div>' if sub else ""
    return f'<div class="stat {kelas}"><div class="l">{label}</div><div class="v">{nilai}</div>{s}</div>'


def stats(items):
    st.markdown('<div class="stats">' + "".join(stat(*i) for i in items) + "</div>", unsafe_allow_html=True)


def kosong(judul="Belum ada data", ket="Tambahkan data pertama untuk mulai mencatat aktivitas usaha tani."):
    st.markdown(f'<div class="kosong"><b>{judul}</b><span>{ket}</span></div>', unsafe_allow_html=True)


def sel_html(b, k):
    v = b.get(k)
    if k == "status":
        kls, t = STATUS.get(v, ("slate", sel(v)))
        dot = '<i class="dot"></i>' if v == "berjalan" else ""
        return f'<span class="pill {kls}">{dot}{t}</span>'
    if k == "saluran":
        t, kls = PEMBELI.get(v, (sel(v), "slate"))
        return f'<span class="pill {kls}">{t}</span>'
    if k == "kategori":
        t, kls = KATEGORI.get(v, (sel(v), "slate"))
        return f'<span class="pill {kls}">{t}</span>'
    if k == "laba":
        return f'<span class="{"pos" if b.get("_laba", 0) >= 0 else "neg"}">{sel(v)}</span>'
    if isinstance(v, tuple):
        return f'{sel(v[0])}<small class="mut">{sel(v[1])}</small>'
    return sel(v)


def saring(baris):
    q = st.session_state.get("cari", "").strip().lower()
    if not q:
        return baris
    return [b for b in baris if any(q in str(v).lower() for v in b.values())]


def tabel(baris, kolom):
    """Tabel statis. kolom: (judul, kunci, rata)."""
    baris = saring(baris)
    if not baris:
        kosong()
        return
    th = "".join(f'<th class="{r}">{html.escape(j)}</th>' for j, _, r in kolom)
    tr = "".join("<tr>" + "".join(f'<td class="{r}">{sel_html(b, k)}</td>' for _, k, r in kolom) + "</tr>"
                 for b in baris)
    st.markdown(f'<div class="tabelbox"><table class="tabel"><thead><tr>{th}</tr></thead>'
                f'<tbody>{tr}</tbody></table></div>', unsafe_allow_html=True)


def daftar(nama, baris, kolom, aksi=()):
    """Daftar dengan tombol aksi tiap baris. kolom: (judul, kunci, rata, lebar). aksi: [(lebar, fungsi(b))]."""
    baris = saring(baris)
    with st.container(border=True, key="daftar_" + nama):
        if not baris:
            kosong()
            return
        lebar = [k[3] for k in kolom] + [a[0] for a in aksi]
        h = st.columns(lebar, vertical_alignment="center")
        for c, k in zip(h, kolom):
            c.markdown(f'<div class="th {k[2]}">{html.escape(k[0])}</div>', unsafe_allow_html=True)
        for b in baris:
            cs = st.columns(lebar, vertical_alignment="center")
            for c, k in zip(cs, kolom):
                c.markdown(f'<div class="td {k[2]}">{sel_html(b, k[1])}</div>', unsafe_allow_html=True)
            for c, a in zip(cs[len(kolom):], aksi):
                with c:
                    a[1](b)


def aksi_hapus(tabel_db, kunci, peringatan="Hapus data ini?"):
    def f(b):
        with st.popover("Hapus", width="stretch"):
            st.caption(peringatan)
            if st.button("Ya, hapus", key=f"b_{kunci}_{b['id']}", width="stretch"):
                hapus(tabel_db, b["id"])
    return f


# ---------- Grafik ----------
def grafik(df):
    d = df.copy()
    d["label"] = d["tanaman"] + " - " + d["tanggal_tanam"].map(bln_thn)
    d["label"] = d["label"] + d.groupby("label").cumcount().map(lambda n: "" if n == 0 else f" ({n + 1})")
    p = pd.concat([d[["label"]].assign(jenis="Pendapatan", juta=pd.to_numeric(d["total_penjualan"]) / 1e6),
                   d[["label"]].assign(jenis="Biaya", juta=pd.to_numeric(d["total_biaya"]) / 1e6)])
    return (alt.Chart(p).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(x=alt.X("label:N", title=None, axis=alt.Axis(labelAngle=0, labelLimit=110)), xOffset="jenis:N",
                    y=alt.Y("juta:Q", title="Juta rupiah"),
                    color=alt.Color("jenis:N", title=None, legend=alt.Legend(orient="top"),
                                    scale=alt.Scale(domain=["Pendapatan", "Biaya"], range=["#15803D", "#E11D48"])),
                    tooltip=[alt.Tooltip("label:N", title="Musim"), alt.Tooltip("jenis:N", title="Jenis"),
                             alt.Tooltip("juta:Q", title="Juta Rp", format=",.1f")])
            .properties(height=300))


def donat(df):
    d = df.assign(juta=pd.to_numeric(df["total_penjualan"]) / 1e6).groupby("tanaman", as_index=False)["juta"].sum()
    return (alt.Chart(d).mark_arc(innerRadius=62, outerRadius=105)
            .encode(theta="juta:Q",
                    color=alt.Color("tanaman:N", title=None, legend=alt.Legend(orient="bottom"),
                                    scale=alt.Scale(range=["#15803D", "#F59E0B", "#0EA5E9", "#94A3B8"])),
                    tooltip=[alt.Tooltip("tanaman:N", title="Komoditas"), alt.Tooltip("juta:Q", title="Juta Rp", format=",.1f")])
            .properties(height=300))


# ---------- Data ----------
with st.spinner("Memuat data..."):
    musim = ambil("musim_tanam")
    biaya_all = ambil("biaya")
    jual_all = ambil("penjualan")
    bayar_all = ambil("pembayaran")
nama_musim = {m["id"]: f'{m["tanaman"]} · {tgl_id(m["tanggal_tanam"])}' for m in musim}

# ---------- Sidebar ----------
st.session_state.setdefault("menu", "Laporan")
if st.session_state["menu"] not in dict(MENU):
    st.session_state["menu"] = "Laporan"
_ay = foto_ayah()
_mark = f'<img src="data:image/jpeg;base64,{_ay}" alt="">' if _ay else "SG"
st.sidebar.markdown(f'<div class="logo"><div class="mark">{_mark}</div><div><b>SAWAL GROUP</b>'
                    '<span>Usaha Tani · Catatan Keuangan</span></div></div>', unsafe_allow_html=True)
for nama, ikon in MENU:
    if st.sidebar.button(nama, icon=ikon, key="nav_" + nama.replace(" ", "_"), width="stretch",
                         type="primary" if st.session_state["menu"] == nama else "secondary"):
        st.session_state["menu"] = nama
        st.rerun()
halaman = st.session_state["menu"]
st.sidebar.divider()
st.sidebar.selectbox("Tampilan", ["Terang", "Gelap", "Otomatis"], key="mode_tampilan",
                     format_func=lambda x: {"Terang": "Terang", "Gelap": "Gelap", "Otomatis": "Otomatis (ikut perangkat)"}[x])
st.sidebar.markdown(f'<div class="profil"><div class="mark">{_mark if _ay else "P"}</div>'
                    '<div>Pencatat keuangan<span>Akun pengelola</span></div></div>', unsafe_allow_html=True)

# ---------- Header ----------
_t = date.today()
_k1, _k2, _k3 = st.columns([2.4, 2, 1.4], vertical_alignment="center")
_k1.markdown(f'<div class="crumb">Dashboard / <b>{halaman}</b><span>{HARI[_t.weekday()]}, {_t.day:02d} '
             f'{BULAN[_t.month - 1]} {_t.year}</span></div>', unsafe_allow_html=True)
_k2.text_input("Cari", key="cari", placeholder="Cari di halaman ini...", label_visibility="collapsed")
with _k3.popover("+ Catat Transaksi", type="primary", width="stretch"):
    for _n in ["Biaya", "Penjualan", "Pembayaran"]:
        if st.button(_n, key="cta_" + _n, width="stretch"):
            st.session_state["menu"] = _n
            st.rerun()
st.markdown(f'<div class="judul">{halaman}</div><div class="sub">{HALAMAN[halaman]}</div>', unsafe_allow_html=True)

with st.container(key="hal_" + halaman.replace(" ", "_")):
    # ---------- Laporan ----------
    if halaman == "Laporan":
        with st.spinner("Menghitung laporan..."):
            data = (db.table("laporan_musim_tanam").select("*").order("tanggal_tanam", desc=True).execute().data)
        if not data:
            kosong("Belum ada data laporan", "Mulai dari menu Musim Tanam, lalu catat biaya dan hasil panen.")
            st.stop()
        df = pd.DataFrame(data)
        for k in ["total_biaya", "total_penjualan", "total_diterima", "sisa_piutang", "laba_rugi"]:
            df[k] = pd.to_numeric(df[k])
        pend, biaya, laba, piutang = (df["total_penjualan"].sum(), df["total_biaya"].sum(),
                                      df["laba_rugi"].sum(), df["sisa_piutang"].sum())
        margin = laba / pend * 100 if pend else 0
        stats([("Total Pendapatan", rp(pend)), ("Total Biaya Operasional", rp(biaya)),
               ("Laba Bersih" if laba >= 0 else "Rugi Bersih", rp(laba), f"Margin {margin:.0f}%", "hl"),
               ("Sisa Piutang", rp(piutang), "Semua sudah lunas" if piutang == 0 else "Belum diterima",
                "ok" if piutang == 0 else "")])
        k1, k2 = st.columns([6, 4], gap="medium")
        with k1, st.container(border=True):
            st.subheader("Pendapatan dan biaya per musim tanam")
            st.altair_chart(grafik(df), width="stretch")
        with k2, st.container(border=True):
            st.subheader("Pendapatan per komoditas")
            st.altair_chart(donat(df), width="stretch")
        st.subheader("Rincian finansial per musim tanam")
        tabel([{"tanaman": r.tanaman, "tgl": tgl_id(r.tanggal_tanam), "biaya": rp(r.total_biaya),
                "jual": rp(r.total_penjualan), "piutang": rp(r.sisa_piutang), "laba": rp(r.laba_rugi),
                "_laba": r.laba_rugi, "margin": f"{r.laba_rugi / r.total_penjualan * 100:.0f}%" if r.total_penjualan else "-",
                "status": r.status} for r in df.itertuples()],
              [("Komoditas", "tanaman", "l"), ("Tanggal tanam", "tgl", "l"), ("Total biaya", "biaya", "r"),
               ("Total penjualan", "jual", "r"), ("Sisa piutang", "piutang", "r"), ("Laba bersih", "laba", "r"),
               ("Margin", "margin", "r"), ("Status", "status", "c")])

    # ---------- Musim Tanam ----------
    elif halaman == "Musim Tanam":
        n_jalan = sum(1 for m in musim if m["status"] == "berjalan")
        stats([("Total Musim", str(len(musim))),
               ("Sedang Berjalan", ('<i class="dot"></i>' if n_jalan else "") + str(n_jalan)),
               ("Sudah Panen", str(len(musim) - n_jalan)),
               ("Total Luas Lahan", f'{sum(m["luas_ha"] or 0 for m in musim):g} Ha')])
        kiri, kanan = st.columns([35, 65], gap="medium")
        with kiri, st.container(border=True):
            st.subheader("Tambah musim tanam")
            with st.form("form_musim", clear_on_submit=True, border=False):
                tanaman = st.selectbox("Komoditas", KOMODITAS)
                tgl = st.date_input("Tanggal tanam", value=date.today())
                luas = st.number_input("Luas lahan (hektar)", min_value=0.0, step=0.1)
                catatan = st.text_input("Catatan (opsional)")
                if st.form_submit_button("Simpan musim tanam", type="primary", width="stretch"):
                    simpan("musim_tanam", {"tanaman": tanaman, "tanggal_tanam": str(tgl),
                                           "luas_ha": luas or None, "catatan": catatan or None})

        def aksi_selesai(b):
            if b["status"] == "berjalan" and st.button("Selesai", key=f"sel_{b['id']}", width="stretch"):
                db.table("musim_tanam").update(
                    {"status": "selesai", "tanggal_panen": str(date.today())}).eq("id", b["id"]).execute()
                st.session_state["pesan"] = "Musim tanam ditandai selesai."
                st.rerun()

        with kanan:
            st.subheader("Daftar musim tanam")
            daftar("musim", [{"id": m["id"], "tanaman": m["tanaman"], "tgl": tgl_id(m["tanggal_tanam"]),
                              "luas": f'{m["luas_ha"]:g} Ha' if m["luas_ha"] else "-", "status": m["status"]}
                             for m in musim],
                   [("Komoditas", "tanaman", "l", 1.3), ("Mulai", "tgl", "l", 1.5), ("Luas", "luas", "r", 0.9),
                    ("Status", "status", "c", 1.2)],
                   [(1.0, aksi_selesai),
                    (0.9, aksi_hapus("musim_tanam", "ms", "Hapus musim tanam ini? Biaya dan penjualannya ikut terhapus."))])

    # ---------- Biaya ----------
    elif halaman == "Biaya":
        if not musim:
            st.warning("Buat musim tanam dulu di menu Musim Tanam.")
            st.stop()
        total = sum(b["jumlah"] for b in biaya_all)
        per = {k: 0 for k in KATEGORI}
        for b in biaya_all:
            per[b["kategori"]] = per.get(b["kategori"], 0) + b["jumlah"]
        besar = max(per, key=per.get) if total else None
        a, b2 = st.columns([55, 45], gap="medium")
        with a:
            stats([("Total Biaya", rp(total)), ("Rata-rata Biaya / Musim", rp(total / len(musim))),
                   ("Total Transaksi", str(len(biaya_all))),
                   ("Alokasi Terbesar", f"{KATEGORI[besar][0]} · {per[besar] / total * 100:.0f}%" if besar else "-")])
        with b2, st.container(border=True):
            st.subheader("Biaya per kategori")
            mx = max(per.values()) if total else 0
            st.markdown("".join(
                f'<div class="bar"><div class="a">{KATEGORI[k][0]}<span>{rp(v)}</span></div>'
                f'<div class="t"><i style="width:{(v / mx * 100) if mx else 0:.0f}%"></i></div></div>'
                for k, v in sorted(per.items(), key=lambda x: -x[1])), unsafe_allow_html=True)
        kiri, kanan = st.columns([35, 65], gap="medium")
        with kiri, st.container(border=True):
            st.subheader("Catat biaya operasional")
            with st.form("form_biaya", clear_on_submit=True, border=False):
                mid = st.selectbox("Musim tanam", list(nama_musim), format_func=nama_musim.get)
                tgl = st.date_input("Tanggal", value=date.today())
                kat = st.selectbox("Kategori", list(KATEGORI), format_func=lambda x: KATEGORI[x][0])
                ket = st.text_input("Keterangan (opsional)")
                jml = st.number_input("Jumlah (Rp)", min_value=0, step=1000, format="%d")
                if st.form_submit_button("Simpan biaya", type="primary", width="stretch"):
                    simpan("biaya", {"musim_tanam_id": mid, "tanggal": str(tgl), "kategori": kat,
                                     "keterangan": ket or None, "jumlah": jml})
        with kanan:
            st.subheader("Riwayat biaya")
            f1, f2 = st.columns(2)
            fm = f1.selectbox("Musim tanam", ["Semua"] + list(nama_musim), key="f_bm",
                              format_func=lambda x: x if x == "Semua" else nama_musim[x])
            fk = f2.selectbox("Kategori", ["Semua"] + list(KATEGORI), key="f_bk",
                              format_func=lambda x: x if x == "Semua" else KATEGORI[x][0])
            rows = [{"id": b["id"], "tgl": b["tanggal"], "musim": nama_musim.get(b["musim_tanam_id"], "-"),
                     "kategori": b["kategori"], "ket": b["keterangan"], "jumlah": rp(b["jumlah"])}
                    for b in biaya_all
                    if (fm == "Semua" or b["musim_tanam_id"] == fm) and (fk == "Semua" or b["kategori"] == fk)]
            daftar("biaya", rows[:30],
                   [("Tanggal", "tgl", "l", 1.1), ("Musim", "musim", "l", 1.7), ("Kategori", "kategori", "l", 1.1),
                    ("Keterangan", "ket", "l", 1.3), ("Jumlah", "jumlah", "r", 1.3)],
                   [(0.8, aksi_hapus("biaya", "bi"))])
            if len(rows) > 30:
                st.caption(f"Menampilkan 30 dari {len(rows)} catatan terbaru.")

    # ---------- Penjualan ----------
    elif halaman == "Penjualan":
        if not musim:
            st.warning("Buat musim tanam dulu di menu Musim Tanam.")
            st.stop()
        tot = sum(p["total"] for p in jual_all)
        per = {k: sum(p["total"] for p in jual_all if p["jenis_pembeli"] == k) for k in PEMBELI}
        kg = sum(p["jumlah_kg"] for p in jual_all)
        pc = lambda v: f"{v / tot * 100:.0f}% dari total" if tot else "0% dari total"
        stats([("Total Penjualan", rp(tot), f"Eceran {rp(per['eceran'])}" if per["eceran"] else ""),
               ("Saluran Tengkulak", rp(per["tengkulak"]), pc(per["tengkulak"])),
               ("Saluran Mitra", rp(per["mitra"]), pc(per["mitra"])),
               ("Volume Terjual", f"{kg:,.0f} kg".replace(",", "."), f"{kg / 1000:g} ton")])

        def simpan_jual():
            s = st.session_state
            tgl_tanam = next(m["tanggal_tanam"] for m in musim if m["id"] == s["j_musim"])
            if s["j_kg"] <= 0:
                s["galat"] = "Jumlah kg harus lebih dari 0."
                return
            if str(s["j_tgl"]) < tgl_tanam:
                s["galat"] = "Tanggal penjualan tidak boleh lebih awal dari tanggal tanam."
                return
            try:
                db.table("penjualan").insert({
                    "musim_tanam_id": s["j_musim"], "tanggal": str(s["j_tgl"]), "jenis_pembeli": s["j_jenis"],
                    "nama_pembeli": s["j_nama"] or None, "jumlah_kg": s["j_kg"], "harga_per_kg": s["j_harga"]}).execute()
            except Exception as e:
                s["galat"] = f"Data belum tersimpan. ({e})"
                return
            s["pesan"] = "Penjualan tersimpan."
            s["j_kg"], s["j_harga"], s["j_nama"] = 0.0, 0, ""

        kiri, kanan = st.columns([35, 65], gap="medium")
        with kiri, st.container(border=True):
            st.subheader("Catat penjualan")
            st.selectbox("Musim tanam", list(nama_musim), format_func=nama_musim.get, key="j_musim")
            st.date_input("Tanggal", value=date.today(), key="j_tgl")
            st.selectbox("Saluran penjualan", list(PEMBELI), format_func=lambda x: PEMBELI[x][0], key="j_jenis")
            st.text_input("Nama pembeli (opsional)", key="j_nama")
            st.number_input("Jumlah (kg)", min_value=0.0, step=10.0, key="j_kg")
            st.number_input("Harga per kg (Rp)", min_value=0, step=100, format="%d", key="j_harga")
            st.markdown(f'<div class="sub-total"><span>Subtotal</span><b>'
                        f'{rp(st.session_state.get("j_kg", 0) * st.session_state.get("j_harga", 0))}</b></div>',
                        unsafe_allow_html=True)
            st.button("Simpan penjualan", type="primary", width="stretch", on_click=simpan_jual)
        with kanan:
            st.subheader("Riwayat penjualan")
            rows = [{"id": p["id"], "tgl": (p["tanggal"], nama_musim.get(p["musim_tanam_id"], "-")),
                     "saluran": p["jenis_pembeli"], "nama": p["nama_pembeli"], "kg": f'{p["jumlah_kg"]:g} kg',
                     "harga": rp(p["harga_per_kg"]), "total": rp(p["total"])} for p in jual_all]
            daftar("jual", rows[:30],
                   [("Tanggal", "tgl", "l", 1.8), ("Saluran", "saluran", "l", 1.1), ("Pembeli", "nama", "l", 1.1),
                    ("Jumlah", "kg", "r", 1.0), ("Harga/kg", "harga", "r", 1.1), ("Subtotal", "total", "r", 1.3)],
                   [(0.8, aksi_hapus("penjualan", "pj", "Hapus penjualan ini? Pembayarannya ikut terhapus."))])
            if len(rows) > 30:
                st.caption(f"Menampilkan 30 dari {len(rows)} penjualan terbaru.")

    # ---------- Pembayaran ----------
    elif halaman == "Pembayaran":
        if not jual_all:
            st.warning("Catat penjualan dulu di menu Penjualan.")
            st.stop()
        dibayar = {}
        for y in bayar_all:
            dibayar[y["penjualan_id"]] = dibayar.get(y["penjualan_id"], 0) + y["jumlah"]
        total_jual, diterima = sum(p["total"] for p in jual_all), sum(dibayar.values())
        stats([("Total Kas Diterima", rp(diterima), "", "ok"), ("Total Nilai Penjualan", rp(total_jual)),
               ("Sisa Piutang", rp(total_jual - diterima), "Semua sudah lunas" if total_jual - diterima <= 0 else "Belum diterima",
                "ok" if total_jual - diterima <= 0 else "")])
        label = {p["id"]: f'{tgl_id(p["tanggal"])} · {p["nama_pembeli"] or PEMBELI[p["jenis_pembeli"]][0]} · {rp(p["total"])}'
                 for p in jual_all}

        @st.dialog("Catat Pembayaran")
        def dialog_bayar(p):
            sisa = p["total"] - dibayar.get(p["id"], 0)
            st.markdown(f'**{label[p["id"]]}**  \nSisa tagihan: **{rp(sisa)}**')
            tgl = st.date_input("Tanggal diterima", value=date.today())
            jml = st.number_input("Jumlah diterima (Rp)", min_value=0, value=max(int(sisa), 0), step=1000, format="%d")
            ket = st.text_input("Keterangan (opsional)")
            if st.button("Simpan pembayaran", type="primary", width="stretch"):
                if jml <= 0:
                    st.error("Jumlah harus lebih dari 0.")
                elif str(tgl) < p["tanggal"]:
                    st.error("Tanggal diterima tidak boleh lebih awal dari tanggal penjualan.")
                else:
                    simpan("pembayaran", {"penjualan_id": p["id"], "tanggal": str(tgl), "jumlah": jml,
                                          "keterangan": ket or None})

        def aksi_bayar(b):
            if st.button("Catat Pembayaran", key=f"cb_{b['id']}", width="stretch"):
                dialog_bayar(next(p for p in jual_all if p["id"] == b["id"]))

        def status(p):
            d = dibayar.get(p["id"], 0)
            return "lunas" if d >= p["total"] else ("sebagian" if d > 0 else "belum")

        st.subheader("Tagihan penjualan")
        daftar("tagihan", [{"id": p["id"], "tgl": (tgl_id(p["tanggal"]), nama_musim.get(p["musim_tanam_id"], "-")),
                            "saluran": p["jenis_pembeli"], "total": rp(p["total"]), "dibayar": rp(dibayar.get(p["id"], 0)),
                            "sisa": rp(max(p["total"] - dibayar.get(p["id"], 0), 0)), "status": status(p)}
                           for p in jual_all][:30],
               [("Penjualan", "tgl", "l", 1.8), ("Saluran", "saluran", "l", 1.0), ("Total", "total", "r", 1.2),
                ("Dibayar", "dibayar", "r", 1.2), ("Sisa", "sisa", "r", 1.2), ("Status", "status", "c", 1.1)],
               [(1.4, aksi_bayar)])
        st.subheader("Riwayat kas diterima")
        daftar("kas", [{"id": y["id"], "tgl": tgl_id(y["tanggal"]), "jual": label.get(y["penjualan_id"], "-"),
                        "jumlah": rp(y["jumlah"]), "ket": y["keterangan"]} for y in bayar_all][:30],
               [("Tanggal", "tgl", "l", 1.3), ("Penjualan", "jual", "l", 3.0), ("Jumlah", "jumlah", "r", 1.2),
                ("Keterangan", "ket", "l", 1.3)],
               [(0.8, aksi_hapus("pembayaran", "by"))])
