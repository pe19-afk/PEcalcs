import streamlit as st

st.set_page_config(page_title="Steel Beam Flexure", page_icon="📐")

st.title("Steel Beam Flexural Capacity (LRFD)")
st.caption("Assumes a compact, fully braced section: φMn = 0.9 · Fy · Zx")

col1, col2 = st.columns(2)
Fy = col1.number_input("Yield strength Fy (ksi)", value=50.0, min_value=0.0)
Zx = col2.number_input("Plastic modulus Zx (in³)", value=100.0, min_value=0.0)

Mp = Fy * Zx                # kip-in
phiMn = 0.9 * Mp / 12       # kip-ft

st.subheader("Results")
st.write(f"**Mp** = {Mp:,.1f} kip-in")
st.write(f"**φMn** = {phiMn:,.1f} kip-ft")
st.info("Reminder: check compactness (AISC Table B4.1b) and lateral bracing (Lp, Lb) — "
        "this simplified form does not cover LTB.")
