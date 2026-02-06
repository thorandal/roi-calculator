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
    claimed = st.number_input("Total Claimed", min_value=0.0, value=1402.71, format="%.2f")
with col2:
    available = st.number_input("Available", min_value=0.0, value=101.59, format="%.2f")
with col3:
    claimable = st.number_input("Claimable", min_value=0.0, value=7.15, format="%.2f")

st.subheader("Kontraktsfestet (SMC)")
locked = st.number_input("Locked Auto Renew", min_value=0.0, value=94.43, format="%.2f")
remaining = st.number_input("Remaining Earning", min_value=0.0, value=7162.45, format="%.2f")