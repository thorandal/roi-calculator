import io
from datetime import date

import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


# =========================
# Page config
# =========================
st.set_page_config(page_title="ROI-kalkulator", layout="wide")


# =========================
# Helpers
# =========================
def safe_roi_percent(net: float, spent: float):
    if spent == 0:
        return None
    return (net / spent) * 100.0


def safe_div(n: float, d: float):
    if d == 0:
        return None
    return n / d


def fmt_money(x: float):
    return f"${x:,.2f}"


def fmt_pct(x):
    return "N/A" if x is None else f"{x:.2f}%"


def build_png_report(title: str, rows: list[tuple[str, str]], footer: str):
    """
    Creates a simple PNG report (text-based) using PIL.
    rows: list of (label, value) lines.
    """
    # Canvas setup
    padding = 40
    line_h = 42
    width = 1200
    height = padding * 2 + line_h * (len(rows) + 4)

    img = Image.new("RGB", (width, height), color=(18, 18, 18))
    draw = ImageDraw.Draw(img)

    # Font (fallback if default font is used)
    try:
        font_title = ImageFont.truetype("DejaVuSans.ttf", 42)
        font = ImageFont.truetype("DejaVuSans.ttf", 28)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 22)
    except Exception:
        font_title = ImageFont.load_default()
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    y = padding
    draw.text((padding, y), title, font=font_title, fill=(240, 240, 240))
    y += line_h * 1.4

    # Divider
    draw.line((padding, y, width - padding, y), fill=(80, 80, 80), width=2)
    y += line_h * 0.8

    for label, value in rows:
        draw.text((padding, y), label, font=font, fill=(200, 200, 200))
        draw.text((width // 2, y), value, font=font, fill=(240, 240, 240))
        y += line_h

    y += line_h * 0.5
    draw.line((padding, y, width - padding, y), fill=(80, 80, 80), width=2)
    y += line_h * 0.6
    draw.text((padding, y), footer, font=font_small, fill=(160, 160, 160))

    out = io.BytesIO()
    img.save(out, format="PNG")
    out.seek(0)
    return out


# =========================
# Sidebar controls
# =========================
with st.sidebar:
    st.markdown("## ⚙️ Innstillinger")

    theme = st.radio("Tema", ["Dark", "Light"], index=0, horizontal=True)

    st.markdown("---")
    st.markdown("### 🗓️ Tidsperiode")
    DEFAULT_START = date(2025, 4, 7)
    startdato = st.date_input("Startdato (når du startet)", value=DEFAULT_START)

    st.markdown("---")
    st.markdown("### 💵 Basis (USD)")
    total_spent = st.number_input(
        "Total Spent (Fiat & Crypto)",
        min_value=0.0,
        value=2695.58,
        format="%.2f",
    )
    total_earned = st.number_input(
        "Total Earned (historisk produsert)",
        min_value=0.0,
        value=9598.85,
        format="%.2f",
    )

    st.markdown("---")
    st.markdown("### 💳 Realisert (Cash)")
    claimed = st.number_input("Total Claimed", min_value=0.0, value=1402.71, format="%.2f")
    available = st.number_input("Available", min_value=0.0, value=101.59, format="%.2f")
    claimable = st.number_input("Claimable", min_value=0.0, value=7.15, format="%.2f")

    st.markdown("---")
    st.markdown("### 📜 Kontrakt (SMC)")
    locked = st.number_input("Locked Auto Renew", min_value=0.0, value=94.43, format="%.2f")
    remaining = st.number_input("Remaining Earning", min_value=0.0, value=7162.45, format="%.2f")

    st.markdown("---")
    st.markdown("### 🧹 Reset")
    if st.button("Reset til standardverdier"):
        # Streamlit-safe reset
        for k in list(st.session_state.keys()):
            if k not in ["_is_running_with_streamlit"]:
                del st.session_state[k]
        st.rerun()


# =========================
# Theme CSS (simple + safe)
# =========================
if theme == "Dark":
    css = """
    <style>
    .card {
      padding: 16px 18px;
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 18px;
      background: rgba(255,255,255,0.04);
    }
    .muted {opacity: 0.75;}
    .big {font-size: 34px; font-weight: 900; line-height: 1.1;}
    .kpi {font-size: 16px; font-weight: 700;}
    </style>
    """
else:
    css = """
    <style>
    .card {
      padding: 16px 18px;
      border: 1px solid rgba(0,0,0,0.10);
      border-radius: 18px;
      background: rgba(0,0,0,0.02);
    }
    .muted {opacity: 0.75;}
    .big {font-size: 34px; font-weight: 900; line-height: 1.1;}
    .kpi {font-size: 16px; font-weight: 700;}
    </style>
    """
st.markdown(css, unsafe_allow_html=True)


# =========================
# Dates & derived time
# =========================
st.markdown("## ROI-kalkulator")
st.markdown('<div class="muted">Realisert ROI · Produksjons-ROI · Kontrakts-ROI (SMC)</div>', unsafe_allow_html=True)

i_dag = date.today()
dager = (i_dag - startdato).days
if dager < 0:
    st.error("Startdato kan ikke være i fremtiden. Velg en dato før i dag.")
    st.stop()

mnd = dager / 30.437 if dager > 0 else 0

top1, top2, top3 = st.columns(3)
top1.metric("Dager siden start", f"{dager}")
top2.metric("Måneder (ca.)", f"{mnd:.1f}")
top3.metric("Startdato", startdato.strftime("%d.%m.%Y"))

st.divider()


# =========================
# Calculations
# =========================
realized_value = claimed + available + claimable
realized_net = realized_value - total_spent
realized_roi = safe_roi_percent(realized_net, total_spent)

production_net = total_earned - total_spent
production_roi = safe_roi_percent(production_net, total_spent)

contracted_value = locked + remaining
contracted_net = contracted_value - total_spent
contracted_roi = safe_roi_percent(contracted_net, total_spent)

# Rates
realized_per_day = safe_div(realized_net, dager)
production_per_day = safe_div(production_net, dager)
contracted_per_day = safe_div(contracted_net, dager)

realized_per_month = safe_div(realized_net, mnd)
production_per_month = safe_div(production_net, mnd)
contracted_per_month = safe_div(contracted_net, mnd)


# =========================
# UI blocks
# =========================
def hero_card(title: str, roi, net: float):
    roi_show = "N/A" if roi is None else f"{roi:.1f}%"
    return f"""
    <div class="card">
      <div class="muted">{title}</div>
      <div class="big">{roi_show}</div>
      <div class="muted">Netto: {fmt_money(net)}</div>
    </div>
    """


def detail_card(title: str, value_basis: float, net: float, roi, per_day, per_month):
    return f"""
    <div class="card">
      <div class="kpi">{title}</div>
      <div class="muted">Verdi-grunnlag: {fmt_money(value_basis)}</div>
      <div class="muted">Netto: {fmt_money(net)} · ROI: {fmt_pct(roi)}</div>
      <hr/>
      <div class="muted">Netto per dag: <b>{'N/A' if per_day is None else fmt_money(per_day)}</b>
      · Netto per måned (ca.): <b>{'N/A' if per_month is None else fmt_money(per_month)}</b></div>
    </div>
    """


st.subheader("📊 Resultater (dashboard)")

h1, h2, h3 = st.columns(3)
with h1:
    st.markdown(hero_card("Realisert ROI", realized_roi, realized_net), unsafe_allow_html=True)
with h2:
    st.markdown(hero_card("Produksjons-ROI", production_roi, production_net), unsafe_allow_html=True)
with h3:
    st.markdown(hero_card("Kontrakts-ROI", contracted_roi, contracted_net), unsafe_allow_html=True)

st.markdown("### Detaljer")
d1, d2, d3 = st.columns(3)
with d1:
    st.markdown(detail_card("✅ Realisert (Cash)", realized_value, realized_net, realized_roi, realized_per_day, realized_per_month), unsafe_allow_html=True)
with d2:
    st.markdown(detail_card("📈 Produksjon (Historical)", total_earned, production_net, production_roi, production_per_day, production_per_month), unsafe_allow_html=True)
with d3:
    st.markdown(detail_card("📜 Kontrakt (SMC – tidsvariabel)", contracted_value, contracted_net, contracted_roi, contracted_per_day, contracted_per_month), unsafe_allow_html=True)

st.caption(
    "⚠️ Kontrakts-ROI er basert på kontraktsfestet verdi (Locked Auto Renew + Remaining Earning) og er ikke kontantverdi per i dag."
)

st.divider()


# =========================
# Exports (CSV + PNG)
# =========================
st.subheader("📦 Eksport")

rows = [
    ("Startdato", startdato.strftime("%Y-%m-%d")),
    ("Dager", str(dager)),
    ("Måneder (ca.)", f"{mnd:.2f}"),
    ("Total Spent", f"{total_spent:.2f}"),
    ("Total Earned", f"{total_earned:.2f}"),
    ("Realisert verdi", f"{realized_value:.2f}"),
    ("Realisert netto", f"{realized_net:.2f}"),
    ("Realisert ROI", "" if realized_roi is None else f"{realized_roi:.4f}"),
    ("Produksjon netto", f"{production_net:.2f}"),
    ("Produksjon ROI", "" if production_roi is None else f"{production_roi:.4f}"),
    ("Kontrakt verdi", f"{contracted_value:.2f}"),
    ("Kontrakt netto", f"{contracted_net:.2f}"),
    ("Kontrakt ROI", "" if contracted_roi is None else f"{contracted_roi:.4f}"),
]

df = pd.DataFrame(rows, columns=["felt", "verdi"])

c1, c2 = st.columns(2)

with c1:
    st.download_button(
        "⬇️ Last ned CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="roi_calculator_export.csv",
        mime="text/csv",
        use_container_width=True
    )

with c2:
    png_rows = [
        ("Startdato", startdato.strftime("%d.%m.%Y")),
        ("Dager / Måneder", f"{dager} / {mnd:.1f}"),
        ("Realisert ROI / Netto", f"{fmt_pct(realized_roi)} / {fmt_money(realized_net)}"),
        ("Produksjon ROI / Netto", f"{fmt_pct(production_roi)} / {fmt_money(production_net)}"),
        ("Kontrakt ROI / Netto", f"{fmt_pct(contracted_roi)} / {fmt_money(contracted_net)}"),
    ]
    png_footer = "Kontrakts-ROI er basert på kontraktsfestet verdi (ikke kontantverdi i dag)."
    png = build_png_report("ROI-kalkulator – rapport", png_rows, png_footer)

    st.download_button(
        "🖼️ Last ned PNG-rapport",
        data=png,
        file_name="roi_calculator_report.png",
        mime="image/png",
        use_container_width=True
    )
