import math
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


def gcp_canopy(A, gcp10, gcpU, A_U=100.0):
    """Log-linear GCp interpolation vs effective wind area (ft^2)."""
    if A <= 10.0:
        return gcp10
    if A >= A_U:
        return gcpU
    frac = (math.log10(A) - 1.0) / (math.log10(A_U) - 1.0)
    return gcp10 + (gcpU - gcp10) * frac


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

# ------------------- GCp from effective wind area -------------------
st.subheader("GCp — interpolated from effective wind area")
A_eff = st.number_input("Effective wind area (ft²)", value=20.0, min_value=0.0, step=1.0,
                        help="GCp is constant for A ≤ 10 ft², log-interpolated between "
                             "10 and 100 ft², and constant for A ≥ 100 ft².")

with st.expander("Curve endpoints from Fig 30.9.1A (set once per figure)", expanded=False):
    st.caption("Enter GCp at A ≤ 10 ft² and at A ≥ 100 ft² for each surface, read from "
               "Fig 30.9.1A for your clearance ratio.")
    e1, e2 = st.columns(2)
    u10 = e1.number_input("Upper (−): GCp @ ≤10 ft²", value=-1.10, step=0.05)
    uU = e2.number_input("Upper (−): GCp @ ≥100 ft²", value=-0.75, step=0.05)
    l10 = e1.number_input("Lower (−): GCp @ ≤10 ft²", value=-0.75, step=0.05)
    lU = e2.number_input("Lower (−): GCp @ ≥100 ft²", value=-0.75, step=0.05)
    p10 = e1.number_input("Positive (+): GCp @ ≤10 ft²", value=0.75, step=0.05)
    pU = e2.number_input("Positive (+): GCp @ ≥100 ft²", value=0.75, step=0.05)

gcp_upper = gcp_canopy(A_eff, u10, uU)
gcp_lower = gcp_canopy(A_eff, l10, lU)
gcp_pos = gcp_canopy(A_eff, p10, pU)

gc1, gc2, gc3 = st.columns(3)
gc1.metric("GCp upper (−)", f"{gcp_upper:.3f}")
gc2.metric("GCp lower (−)", f"{gcp_lower:.3f}")
gc3.metric("GCp positive (+)", f"{gcp_pos:.3f}")

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
        "Confirm GCp curve endpoints, zone, clearance ratio, and load cases from "
        "Fig 30.9.1A, and apply governing load combinations. LRFD pressures shown; "
        "multiply by 0.6 for ASD.")
