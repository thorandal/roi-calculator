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