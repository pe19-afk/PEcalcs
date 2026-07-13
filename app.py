import math
import streamlit as st

# ----------------------------------------------------------------------
# Sabo-style engineering calculators — learning template
# NOTE: These are for learning/checking only, not a stamped calculation.
# Always verify against the governing code and your own judgment.
# ----------------------------------------------------------------------

st.set_page_config(page_title="Engineering Calculators", page_icon="📐")

st.sidebar.title("📐 Calculators")
choice = st.sidebar.radio(
    "Pick a calculator",
    ["Section Properties", "Steel Beam Flexure (LRFD)", "Wind Velocity Pressure (ASCE 7)"],
)


def section_properties():
    st.title("Rectangular Section Properties")
    col1, col2 = st.columns(2)
    b = col1.number_input("Width b (in)", value=12.0, min_value=0.0)
    h = col2.number_input("Height h (in)", value=24.0, min_value=0.0)

    if b > 0 and h > 0:
        A = b * h
        Ix = b * h**3 / 12
        Iy = h * b**3 / 12
        Sx = Ix / (h / 2)
        Sy = Iy / (b / 2)
        rx = math.sqrt(Ix / A)
        ry = math.sqrt(Iy / A)

        st.subheader("Results")
        st.write(f"**Area A** = {A:,.2f} in²")
        st.write(f"**Ix** = {Ix:,.1f} in⁴   |   **Sx** = {Sx:,.1f} in³   |   **rx** = {rx:.2f} in")
        st.write(f"**Iy** = {Iy:,.1f} in⁴   |   **Sy** = {Sy:,.1f} in³   |   **ry** = {ry:.2f} in")


def steel_flexure():
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


def wind_pressure():
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


if choice == "Section Properties":
    section_properties()
elif choice == "Steel Beam Flexure (LRFD)":
    steel_flexure()
else:
    wind_pressure()

st.sidebar.markdown("---")
st.sidebar.caption("Learning template — verify all results against the governing code.")
