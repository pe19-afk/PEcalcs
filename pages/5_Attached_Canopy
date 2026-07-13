import streamlit as st

st.set_page_config(page_title="Attached Canopy", page_icon="📐")

st.title("Attached Canopy — Wind Pressure")
st.caption("ASCE 7-22 §30.9, Fig 30.9.1A · attached canopies on buildings with h ≤ 60 ft")

# ---------------------------------------------------------------
# Kz per ASCE 7-22 Table 26.10-1 (published values, Exposures B/C/D)
# z < 15 ft uses the 15-ft value per table footnote.
# ---------------------------------------------------------------
KZ_TABLE = {
    "z": [15, 20, 25, 30, 40, 50, 60],
    "B": [0.57, 0.62, 0.66, 0.70, 0.76, 0.81, 0.85],
    "C": [0.85, 0.90, 0.94, 0.98, 1.04, 1.09, 1.13],
    "D": [1.03, 1.08, 1.12, 1.16, 1.22, 1.27, 1.31],
}


def interp_kz(z: float, exposure: str) -> float:
    zs = KZ_TABLE["z"]
    ks = KZ_TABLE[exposure]
    if z <= zs[0]:
        return ks[0]
    if z >= zs[-1]:
        return ks[-1]
    for i in range(len(zs) - 1):
        if zs[i] <= z <= zs[i + 1]:
            t = (z - zs[i]) / (zs[i + 1] - zs[i])
            return ks[i] + t * (ks[i + 1] - ks[i])
    return ks[-1]


# ---------------------------- Inputs ----------------------------
st.subheader("Wind parameters")
col1, col2 = st.columns(2)
V = col1.number_input("Basic wind speed V (mph)", value=160.0, min_value=0.0, step=1.0)
exposure = col2.selectbox("Exposure category", ["B", "C", "D"], index=2)
z = col1.number_input("Mean roof height h (ft)", value=50.0, min_value=0.0, step=1.0,
                      help="Kz is interpolated from ASCE 7-22 Table 26.10-1 at this height. "
                           "Heights below 15 ft use the 15-ft value. Limited to h ≤ 60 ft per §30.9.")
Kd = col2.number_input("Directionality factor Kd", value=0.85, min_value=0.0, step=0.01)
Kzt = col1.number_input("Topographic factor Kzt", value=1.0, min_value=0.0, step=0.01)
Ke = col2.number_input("Ground elevation factor Ke", value=1.0, min_value=0.0, step=0.01)

if z > 60:
    st.warning("h exceeds 60 ft — §30.9 (Fig 30.9.1A) applies to buildings with h ≤ 60 ft. "
               "Kz shown is capped at the 60-ft table value.")

Kz = interp_kz(z, exposure)

st.subheader("Pressure coefficients (from Fig 30.9.1A)")
st.caption("Read GCp from Fig 30.9.1A for your effective wind area and clearance ratio, "
           "then enter the values here.")
col3, col4 = st.columns(2)
ewa = col3.number_input("Effective wind area (ft²)", value=20.0, min_value=0.0, step=1.0,
                        help="For reference/record — use it to read GCp off the figure.")
gcp_upper = col4.number_input("GCp — upper surface (−)", value=-1.10, step=0.05)
gcp_lower = col3.number_input("GCp — lower surface (−)", value=-0.75, step=0.05)
gcp_pos = col4.number_input("GCp — positive (+)", value=0.75, step=0.05)

# --------------------------- Calculation ---------------------------
# ASCE 7-22 Eq 26.10-1: qh = 0.00256 * Kz * Kzt * Kd * Ke * V^2   (psf, V in mph)
qh = 0.00256 * Kz * Kzt * Kd * Ke * V**2

# Design pressure: p = qh * (GCp)
p_upper = qh * gcp_upper
p_lower = qh * gcp_lower
p_pos = qh * gcp_pos

# ---------------------------- Results ----------------------------
st.subheader("Results")
st.write(f"**Kz** = {Kz:.3f}  (interpolated, Exposure {exposure} at z = {z:g} ft)")
st.write(f"**qh** = 0.00256 · Kz · Kzt · Kd · Ke · V² = **{qh:,.2f} psf**")

st.markdown("**Design pressures, p = qh · (GCp):**")
rc1, rc2, rc3 = st.columns(3)
rc1.metric("p — upper (−)", f"{p_upper:,.2f} psf")
rc2.metric("p — lower (−)", f"{p_lower:,.2f} psf")
rc3.metric("p — positive (+)", f"{p_pos:,.2f} psf")

st.info("Kd is applied once, inside qh, per ASCE 7-22 Eq 26.10-1. "
        "Confirm GCp zone, clearance ratio, and load cases from Fig 30.9.1A, and apply "
        "governing load combinations. LRFD pressures shown; multiply by 0.6 for ASD.")
