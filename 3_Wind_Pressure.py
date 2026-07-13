import streamlit as st

st.set_page_config(page_title="Wind Velocity Pressure", page_icon="📐")

st.title("Wind Velocity Pressure — qz (ASCE 7)")
st.caption("qz = 0.00256 · Kz · Kzt · Kd · Ke · V²   (V in mph, qz in psf)")

col1, col2 = st.columns(2)
V = col1.number_input("Basic wind speed V (mph)", value=115.0, min_value=0.0)
Kz = col2.number_input("Velocity pressure coeff. Kz", value=0.85, min_value=0.0)
Kzt = col1.number_input("Topographic factor Kzt", value=1.0, min_value=0.0)
Kd = col2.number_input("Directionality factor Kd", value=0.85, min_value=0.0)
Ke = col1.number_input("Ground elevation factor Ke", value=1.0, min_value=0.0)

qz = 0.00256 * Kz * Kzt * Kd * Ke * V**2

st.subheader("Results")
st.write(f"**qz** = {qz:,.2f} psf")
