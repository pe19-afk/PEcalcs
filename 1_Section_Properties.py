import math
import streamlit as st

st.set_page_config(page_title="Section Properties", page_icon="📐")

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
