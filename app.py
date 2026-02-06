import streamlit as st
from datetime import date

st.set_page_config(page_title="ROI-kalkulator", layout="centered")

# --- subtle styling ---
st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
.small {opacity: 0.75; font-size: 0.95rem;}
.card {
  padding: 1rem 1.1rem;
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 16px;
  background: rgba(255,255,255,0.03);
}
.big {font-size: 1.8rem; font-weight: 800; line-height: 1.1;}
.kpi {font-size: 1.1rem; font-weight: 700;}
hr {margin: 1.2rem 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("## ROI-kalkulator")
st.markdown(
    '<div class="small">Realisert ROI · Produksjons-ROI · Kontrakts-ROI (SMC)</div>',
    unsafe_allow_html=True
)
st.divider()

# ---------- DATOER ----------
st.subheader("🗓️ Startdato og varighet")

DEFAULT_START = date(2025, 4, 7)
startdato = st.date_input("Startdato (når du startet)", value=DEFAULT_START)

i_dag = date.today()
dager = (i_dag - startdato).days

if dager < 0:
    st.error("Startdato kan ikke være i fremtiden. Velg en dato før i dag.")
    st.stop()

# En “måned” for snittberegning: 30,437 dager (365,25/12)
mnd = dager / 30.437 if dager > 0 else 0

# ---------- INPUT ----------
st.subheader("1️⃣ Tall (USD)")

col1, col2 = st.columns(2)
with col1:
    total_spent = st.number_input(
        "Total Spent (Fiat & Crypto)",
        min_value=0.0, value=2695.58, format="%.2f"
    )
with col2:
    total_earned = st.number_input(
        "Total Earned (historisk produsert)",
        min_value=0.0, value=9598.85, format="%.2f"
    )

tab_cash, tab_contract = st.tabs(["💵 Cash (realisert)", "📜 Kontrakt (SMC)"])

with tab_cash:
    st.markdown("**Realisert verdi (cash)**")
    c1, c2, c3 = st.columns(3)
    with c1:
        claimed = st.number_input("Total Claimed", min_value=0.0, value=1402.71, format="%.2f")
    with c2:
        available = st.number_input("Available", min_value=0.0, value=101.59, format="%.2f")
    with c3:
        claimable = st.number_input("Claimable", min_value=0.0, value=7.15, format="%.2f")

with tab_contract:
    st.markdown("**Kontraktsfestet (SMC)**")
    c1, c2 = st.columns(2)
    with c1:
        locked = st.number_input("Locked Auto Renew", min_value=0.0, value=94.43, format="%.2f")
    with c2:
        remaining = st.number_input("Remaining Earning", min_value=0.0, value=7162.45, format="%.2f")

# ---------- CALCULATIONS ----------
def roi_percent(net: float, spent: float):
    if spent == 0:
        return None
    return (net / spent) * 100

def per_day(amount: float):
    if dager == 0:
        return None
    return amount / dager

def per_month(amount: float):
    if mnd == 0:
        return None
    return amount / mnd

realized_value = claimed + available + claimable
realized_net = realized_value - total_spent
realized_roi = roi_percent(realized_net, total_spent)

production_net = total_earned - total_spent
production_roi = roi_percent(production_net, total_spent)

contracted_value = locked + remaining
contracted_net = contracted_value - total_spent
contracted_roi = roi_percent(contracted_net, total_spent)

st.divider()

# ---------- OUTPUT ----------
st.subheader("2️⃣ Resultater")

# Hero row (top KPIs)
k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(
        '<div class="card"><div class="small">Realisert ROI</div>'
        f'<div class="big">{(realized_roi if realized_roi is not None else 0):.1f}%</div>'
        f'<div class="small">Netto: ${realized_net:,.2f}</div></div>',
        unsafe_allow_html=True
    )
with k2:
    st.markdown(
        '<div class="card"><div class="small">Produksjons-ROI</div>'
        f'<div class="big">{(production_roi if production_roi is not None else 0):.1f}%</div>'
        f'<div class="small">Netto: ${production_net:,.2f}</div></div>',
        unsafe_allow_html=True
    )
with k3:
    st.markdown(
        '<div class="card"><div class="small">Kontrakts-ROI</div>'
        f'<div class="big">{(contracted_roi if contracted_roi is not None else 0):.1f}%</div>'
        f'<div class="small">Netto: ${contracted_net:,.2f}</div></div>',
        unsafe_allow_html=True
    )

st.markdown("---")

def result_card(title, value_basis, net, roi):
    d = per_day(net)
    mo = per_month(net)

    roi_txt = f"{roi:.2f}%" if roi is not None else "N/A"
    d_txt = f"${d:,.2f}" if d is not None else "N/A"
    mo_txt = f"${mo:,.2f}" if mo is not None else "N/A"

    st.markdown(
        f"""
        <div class="card">
          <div class="kpi">{title}</div>
          <div class="small">Verdi-grunnlag: ${value_basis:,.2f}</div>
          <div class="small">Netto: ${net:,.2f} · ROI: {roi_txt}</div>
          <hr/>
          <div class="small">Netto per dag: <b>{d_txt}</b> · Netto per måned (ca.): <b>{mo_txt}</b></div>
        </div>
        """,
        unsafe_allow_html=True
    )

result_card("✅ Realisert (Cash)", realized_value, realized_net, realized_roi)
st.write("")
result_card("📈 Produksjon (Historical)", total_earned, production_net, production_roi)
st.write("")
result_card("📜 Kontrakt (SMC – tidsvariabel)", contracted_value, contracted_net, contracted_roi)

st.caption(
    "⚠️ Kontrakts-ROI er basert på kontraktsfestet verdi (Locked Auto Renew + Remaining Earning) "
    "og er ikke kontantverdi per i dag."
)

colA, colB, colC = st.columns(3)
with colA:
    st.metric("Dager", f"{dager}")
with colB:
    st.metric("Måneder (ca.)", f"{mnd:.1f}")
with colC:
    st.metric("Startdato", startdato.strftime("%d.%m.%Y"))

st.divider()
