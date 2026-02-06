import streamlit as st
from datetime import date

st.set_page_config(page_title="ROI-kalkulator (3 varianter)", layout="centered")

st.title("ROI-kalkulator – 3 varianter")
st.caption("Realisert ROI · Produksjons-ROI · Kontrakts-ROI (SMC)")

# ---------- DATOER ----------
st.header("🗓️ Startdato og varighet")

DEFAULT_START = date(2025, 4, 7)
startdato = st.date_input("Startdato (når du startet)", value=DEFAULT_START)

i_dag = date.today()
dager = (i_dag - startdato).days

if dager < 0:
    st.error("Startdato kan ikke være i fremtiden. Velg en dato før i dag.")
    st.stop()

mnd = dager / 30.437 if dager > 0 else 0

colA, colB, colC = st.columns(3)
with colA:
    st.metric("Dager siden start", f"{dager}")
with colB:
    st.metric("Ca. måneder", f"{mnd:.1f}")
with colC:
    st.metric("Startdato", startdato.strftime("%d.%m.%Y"))

st.divider()
# ---------- INPUT ----------
st.header("1️⃣ Legg inn tall (USD)")

total_spent = st.number_input(
    "Total Spent (Fiat & Crypto) – investert kapital",
    min_value=0.0, value=2695.58, format="%.2f"
)

total_earned = st.number_input(
    "Total Earned – historisk produsert verdi",
    min_value=0.0, value=9598.85, format="%.2f"
)

st.subheader("Realisert verdi (cash)")
col1, col2, col3 = st.columns(3)

with col1:
    claimed = st.number_input(
        "Total Claimed",
        min_value=0.0,
        value=1402.71,
        format="%.2f"
    )

with col2:
    available = st.number_input(
        "Available",
        min_value=0.0,
        value=101.59,
        format="%.2f"
    )

with col3:
    claimable = st.number_input(
        "Claimable",
        min_value=0.0,
        value=7.15,
        format="%.2f"
    )
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

# ---------- OUTPUT ----------
st.divider()
st.header("2️⃣ Resultater")

def show_block(title, value_basis, net, roi):
    st.subheader(title)
    st.write(f"Verdi-grunnlag: **${value_basis:,.2f}**")
    st.write(f"Netto (verdi − spent): **${net:,.2f}**")
    st.write(f"ROI: **{roi:.2f}%**" if roi is not None else "ROI: **N/A**")

    d = per_day(net)
    mo = per_month(net)

    colx, coly = st.columns(2)
    with colx:
        st.write("**Netto per dag:**")
        st.write(f"${d:,.2f}" if d is not None else "N/A")
    with coly:
        st.write("**Netto per måned (ca.):**")
        st.write(f"${mo:,.2f}" if mo is not None else "N/A")

show_block("✅ Realisert ROI (Cash)", realized_value, realized_net, realized_roi)
show_block("📈 Produksjons-ROI (Historical)", total_earned, production_net, production_roi)
show_block("📜 Kontrakts-ROI (SMC – tidsvariabel)", contracted_value, contracted_net, contracted_roi)

st.caption(
    "⚠️ Kontrakts-ROI er basert på kontraktsfestet verdi (Locked Auto Renew + Remaining Earning). "
    "Dette er ikke kontantverdi per i dag."
)
col1, col2, col3 = st.columns(3)
with col1:
    claimed = st.number_input("Total Claimed", min_value=0.0, value=1402.71, format="%.2f")
with col2:
    available = st.number_input("Available", min_value=0.0, value=101.59, format="%.2f")
with col3:
    claimable = st.number_input("Claimable", min_value=0.0, value=7.15, format="%.2f")

st.subheader("Kontraktsfestet (SMC)")
locked = st.number_input("Locked Auto Renew", min_value=0.0, value=94.43, format="%.2f")
remaining = st.number_input("Remaining Earning", min_value=0.0, value=7162.45, format="%.2f")
