import streamlit as st

st.set_page_config(page_title="PEcalcs", page_icon="📐")

st.title("📐 PEcalcs")
st.write("A collection of structural engineering calculators.")

st.markdown(
    """
    **Pick a calculator from the sidebar** on the left:

    - **Section Properties** — area, moment of inertia, section modulus, radius of gyration
    - **Steel Beam Flexure (LRFD)** — φMn for a compact, fully braced section
    - **Wind Velocity Pressure (ASCE 7)** — qz from basic wind speed and coefficients

    ---
    *Learning template — verify every result against the governing code and your own
    engineering judgment before using it on real work.*
    """
)
