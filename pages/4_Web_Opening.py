"""
Steel Beam Web Opening Calculator — AISC Design Guide 2, Ch. 4 (LRFD)
Unreinforced web openings. Units: kips, in, ksi. phi = 0.90.

Section properties: AISC Shapes Database v15.0 (w_shapes.csv).
Method reproduces the source spreadsheet cell-for-cell.
NOT INDEPENDENTLY CHECKED — verify all results before use in design.
"""

import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Web Opening Calculator — AISC DG2",
    page_icon="🏗️",
    layout="wide",
)

PHI = 0.90


@st.cache_data
def load_shapes() -> pd.DataFrame:
    here = Path(__file__).parent
    for p in (here / "w_shapes.csv", here.parent / "w_shapes.csv"):
        if p.exists():
            return pd.read_csv(p)
    st.error("w_shapes.csv not found — place it in the repo root.")
    st.stop()


# ----------------------------------------------------------------------------
# Core calculation — mirrors the spreadsheet formulas exactly
# ----------------------------------------------------------------------------
def calc(Fy, Mu_kft, Vu, circular, h0_in, a0_in, e, tee_deeper,
         d, tw, bf, tf, Zx, S=None):
    r = {}

    # Geometry (spreadsheet rows 24-32)
    h0s = 0.9 * h0_in if circular else h0_in          # h0 for shear
    a0 = 0.45 * h0_in if circular else a0_in          # effective length
    dAs = h0_in * tw                                  # web area removed
    st_ = (d - h0s) / 2 + e                           # deeper tee
    sb = (d - h0s) / 2 - e                            # shallower tee
    nut = a0 / st_
    nub = a0 / sb
    Mp = Fy * Zx                                      # k-in
    Vp = Fy * tw * d / math.sqrt(3)                   # kips

    r.update(h0s=h0s, a0=a0, dAs=dAs, st=st_, sb=sb, nut=nut, nub=nub,
             Mp=Mp, Vp=Vp)

    # Proportioning & stability (Sec. 3.7, Table 4.5)
    flg_a, flg_l = bf / (2 * tf), 65 / math.sqrt(Fy)
    web_a, web_l = (d - 2 * tf) / tw, 520 / math.sqrt(Fy)
    stocky = web_a <= 420 / math.sqrt(Fy)
    ar_l = 3.0 if stocky else 2.2
    p0 = a0 / h0_in + 6 * h0_in / d
    nu_comp = nut if tee_deeper else nub

    ok = lambda cond: "OK" if cond else "NG"
    prop = [
        ("Flange bf/(2·tf)",       flg_a,   "≤", flg_l, ok(flg_a <= flg_l),      "Local buckling · Eq 3-22"),
        ("Web (d−2tf)/tw",         web_a,   "≤", web_l, ok(web_a <= web_l),      "Web buckling · Eq 3-25"),
        ("a0/h0",                  a0/h0s,  "≤", ar_l,  ok(a0/h0s <= ar_l),      f"{'Stocky' if stocky else 'Non-stocky'} web limit"),
        ("h0/d",                   h0_in/d, "≤", 0.70,  ok(h0_in/d <= 0.70),     "Opening depth · §3.7b1"),
        ("p0 = a0/h0 + 6h0/d",     p0,      "≤", 5.60,  ok(p0 <= 5.60),          "Opening parameter · Eq 3-24"),
        ("st/d",                   st_/d,   "≥", 0.15,  ok(st_/d >= 0.15),       "Min tee depth · §3.7b1"),
        ("sb/d",                   sb/d,    "≥", 0.15,  ok(sb/d >= 0.15),        "Min tee depth · §3.7b1"),
        ("νt = a0/st",             nut,     "≤", 12.0,  ok(nut <= 12),           "Tee aspect ratio"),
        ("νb = a0/sb",             nub,     "≤", 12.0,  ok(nub <= 12),           "Tee aspect ratio"),
    ]
    tee_buck = "OK" if nu_comp <= 4 else "CHECK"
    r.update(stocky=stocky, prop=prop, tee_buck=tee_buck, nu_comp=nu_comp)

    # Maximum moment capacity (Eq 3-6)
    red = dAs * (h0_in / 4 + e) / Zx
    phiMm = PHI * Mp * (1 - red)                      # k-in
    Mu_kin = Mu_kft * 12
    m_ratio = Mu_kin / phiMm
    r.update(red=red, phiMm=phiMm, Mu_kin=Mu_kin, m_ratio=m_ratio)

    # Maximum shear capacity (Eqs 3-12, 3-13; mu = 0, unreinforced)
    Vpt = Fy * tw * st_ / math.sqrt(3)
    avt = min(1.0, math.sqrt(6) / (nut + math.sqrt(3)))
    Vmt = Vpt * avt
    Vpb = Fy * tw * sb / math.sqrt(3)
    avb = min(1.0, math.sqrt(6) / (nub + math.sqrt(3)))
    Vmb = Vpb * avb
    sum_Vm = Vmt + Vmb
    Vm_cap = (2 / 3 if stocky else 0.45) * Vp
    Vm = min(sum_Vm, Vm_cap)
    phiVm = PHI * Vm
    v_ratio = Vu / phiVm
    r.update(Vpt=Vpt, avt=avt, Vmt=Vmt, Vpb=Vpb, avb=avb, Vmb=Vmb,
             sum_Vm=sum_Vm, Vm_cap=Vm_cap, Vm=Vm, phiVm=phiVm, v_ratio=v_ratio)

    # Moment–shear interaction (Eq 3-3)
    R = (m_ratio ** 3 + v_ratio ** 3) ** (1 / 3)
    r["R"] = R

    # Detailing (Sec. 3.7b)
    r_min = max(2 * tw, 0.625)
    q = Vu / (PHI * Vp)
    s_term = q / (1 - q) if q < 1 else math.inf
    S_req = (max(1.5 * h0_in, h0_in * s_term) if circular
             else max(h0_in, a0_in * s_term))
    s_status = "n/a" if S is None else ("OK" if S >= S_req else "NG")
    r.update(r_min=r_min, S_req=S_req, s_status=s_status)

    # Overall
    any_ng = (any(p[4] == "NG" for p in prop) or m_ratio > 1
              or v_ratio > 1 or R > 1 or s_status == "NG")
    r["overall"] = "NG" if any_ng else ("COND" if tee_buck == "CHECK" else "OK")
    return r


# ----------------------------------------------------------------------------
# Scaled elevation drawing
# ----------------------------------------------------------------------------
def elevation_figure(d, tf, h0, a0, e, circular, st_, sb):
    fig, ax = plt.subplots(figsize=(8, 3.2))
    L = 3.2 * max(a0, h0)
    steel, web, ink, blue = "#C9CEC4", "#EDEFE9", "#20261F", "#1D4FB8"

    ax.add_patch(plt.Rectangle((0, 0), L, d, fc=web, ec=ink, lw=1.2))
    ax.add_patch(plt.Rectangle((0, d - tf), L, tf, fc=steel, ec=ink, lw=1.2))
    ax.add_patch(plt.Rectangle((0, 0), L, tf, fc=steel, ec=ink, lw=1.2))

    cy = d / 2 - e  # deeper tee on top
    if circular:
        ax.add_patch(plt.Circle((L / 2, cy), h0 / 2, fc="white", ec=blue, lw=1.8))
    else:
        ax.add_patch(plt.Rectangle((L / 2 - a0 / 2, cy - h0 / 2), a0, h0,
                                   fc="white", ec=blue, lw=1.8,
                                   joinstyle="round"))
    ax.axhline(d / 2, color="#6E7568", lw=0.8, ls=(0, (8, 3, 2, 3)))

    kw = dict(fontsize=8, family="monospace", color="#444")
    ax.annotate(f'd = {d:.2f}"', (-0.06 * L, d / 2), ha="right", va="center", **kw)
    lbl = "D0" if circular else "h0"
    ax.annotate(f'{lbl} = {h0:.2f}"', (L / 2 + (a0 if not circular else h0) / 2 + 0.03 * L, cy),
                ha="left", va="center", **kw)
    if not circular:
        ax.annotate(f'a0 = {a0:.2f}"', (L / 2, cy - h0 / 2 - 0.05 * d),
                    ha="center", va="top", **kw)
    if abs(e) > 0.01:
        ax.annotate(f'e = {abs(e):.2f}"', (L / 2 - a0 / 2 - 0.03 * L, (d / 2 + cy) / 2),
                    ha="right", va="center", color=blue, fontsize=8, family="monospace")
    ax.annotate(f'st = {st_:.2f}"', (0.02 * L, d - st_ / 2), va="center", **kw)
    ax.annotate(f'sb = {sb:.2f}"', (0.02 * L, sb / 2), va="center", **kw)

    ax.set_xlim(-0.22 * L, 1.12 * L)
    ax.set_ylim(-0.14 * d, 1.08 * d)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------------
# UI helpers
# ----------------------------------------------------------------------------
def status_df(df: pd.DataFrame):
    def color(v):
        m = {"OK": "color:#1B7A44;font-weight:600",
             "NG": "color:#B3261E;font-weight:700",
             "CHECK": "color:#8A5A00;font-weight:600",
             "n/a": "color:#6E7568"}
        return m.get(v, "")
    return df.style.map(color, subset=["Status"]).format(precision=3)


# ----------------------------------------------------------------------------
# Inputs — main page
# ----------------------------------------------------------------------------
shapes = load_shapes()

st.title("Steel Beam — Unreinforced Web Opening")
st.caption("AISC Design Guide 2, Ch. 4 · LRFD · φ = 0.90 · Units: kips, in, ksi")

col_a, col_b, col_c = st.columns(3, gap="large")

with col_a:
    st.subheader("1 · Member")
    shape = st.selectbox("W-shape (AISC v15.0)", shapes["Shape"],
                         index=int(shapes.index[shapes.Shape == "W24X55"][0]))
    row = shapes.loc[shapes.Shape == shape].iloc[0]
    with st.expander("Section properties (editable)", expanded=False):
        A  = st.number_input("A — area (in²)",             value=float(row.A),  format="%.3f")
        d  = st.number_input("d — depth (in)",             value=float(row.d),  format="%.3f")
        tw = st.number_input("tw — web thickness (in)",    value=float(row.tw), format="%.3f")
        bf = st.number_input("bf — flange width (in)",     value=float(row.bf), format="%.3f")
        tf = st.number_input("tf — flange thickness (in)", value=float(row.tf), format="%.3f")
        Zx = st.number_input("Zx — plastic modulus (in³)", value=float(row.Zx), format="%.1f")
    Fy = st.number_input("Fy — yield stress (ksi)", value=36.0, min_value=1.0)

with col_b:
    st.subheader("2 · Loads")
    Mu = st.number_input("Mu — factored moment at opening ℄ (k-ft)", value=290.6)
    Vu = st.number_input("Vu — factored shear at opening ℄ (kips)", value=21.5)
    tee = st.radio("Tee in compression (§3.7a3)",
                   ["Deeper tee", "Shallower tee"], horizontal=True)

with col_c:
    st.subheader("3 · Opening")
    opening = st.radio("Opening shape", ["Rectangular", "Circular"], horizontal=True)
    circular = opening == "Circular"
    if circular:
        h0 = st.number_input("D0 — opening diameter (in)", value=10.0, min_value=0.01)
        a0 = 0.45 * h0
        st.caption("§3.7b4: h0 = D0 (bending), 0.9·D0 (shear), a0 = 0.45·D0")
    else:
        h0 = st.number_input("h0 — opening depth (in)", value=10.0, min_value=0.01)
        a0 = st.number_input("a0 — opening length (in)", value=20.0, min_value=0.01)
    e = abs(st.number_input("e — eccentricity from mid-depth (in)", value=2.0))
    S_txt = st.text_input("S — clear spacing to adjacent opening (in)",
                          value="", placeholder="blank if single opening")
    S = float(S_txt) if S_txt.strip() else None

st.divider()

# ----------------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------------
r = calc(Fy, Mu, Vu, circular, h0, a0, e, tee == "Deeper tee",
         d, tw, bf, tf, Zx, S)

st.markdown(f"#### Result — {shape}, Fy = {Fy:g} ksi")
banner = {
    "OK":   (st.success, "**OK — opening acceptable.** No reinforcement required."),
    "COND": (st.warning, "**Conditional.** Verify compression-tee buckling per §3.7a3 (ν > 4)."),
    "NG":   (st.error,   "**No good.** Revise opening size/location or reinforce (DG2 Table 4.2)."),
}
fn, msg = banner[r["overall"]]
fn(msg)

c1, c2, c3 = st.columns(3)
c1.metric("Moment  Mu / φMm", f"{r['m_ratio']:.3f}",
          delta="OK" if r['m_ratio'] <= 1 else "NG",
          delta_color="normal" if r['m_ratio'] <= 1 else "inverse")
c2.metric("Shear  Vu / φVm", f"{r['v_ratio']:.3f}",
          delta="OK" if r['v_ratio'] <= 1 else "NG",
          delta_color="normal" if r['v_ratio'] <= 1 else "inverse")
c3.metric("Interaction R (Eq 3-3)", f"{r['R']:.3f}",
          delta="OK" if r['R'] <= 1 else "NG",
          delta_color="normal" if r['R'] <= 1 else "inverse")

st.pyplot(elevation_figure(d, tf, h0, a0, e, circular, r["st"], r["sb"]),
          width="stretch")

# --- Section 3: proportioning
st.subheader("Proportioning & stability — §3.7, Table 4.5")
prop_df = pd.DataFrame(r["prop"],
                       columns=["Check", "Actual", "", "Limit", "Status", "Reference"])
extra = pd.DataFrame([
    ["Tee compression buckling", r["nu_comp"], "≤", 4.0, r["tee_buck"],
     "Not required (ν ≤ 4) · §3.7a3" if r["tee_buck"] == "OK"
     else "Investigate compression tee as axially loaded column · §3.7a3"],
    ["Lateral buckling", float("nan"), "", float("nan"), "n/a",
     "§3.7a4 — brace compression flange"],
], columns=prop_df.columns)
st.dataframe(status_df(pd.concat([prop_df, extra], ignore_index=True)),
             width="stretch", hide_index=True)

col_m, col_v = st.columns(2)

with col_m:
    st.subheader("Moment capacity — Eq 3-6")
    st.dataframe(pd.DataFrame({
        "Item": ["Mp = Fy·Zx", "Reduction ΔAs·(h0/4+e)/Zx", "φMm", "Mu", "Mu/φMm"],
        "Value": [f"{r['Mp']:.0f} k-in", f"{r['red']:.4f}",
                  f"{r['phiMm']:.0f} k-in  ({r['phiMm']/12:.1f} k-ft)",
                  f"{r['Mu_kin']:.0f} k-in  ({Mu:g} k-ft)", f"{r['m_ratio']:.3f}"],
    }), width="stretch", hide_index=True)

with col_v:
    st.subheader("Shear capacity — Eqs 3-12, 3-13")
    st.dataframe(pd.DataFrame({
        "Item": ["Vp = Fy·tw·d/√3", "Vm,t (deeper tee)", "Vm,b (shallower tee)",
                 "ΣVm", f"Upper limit {'⅔' if r['stocky'] else '0.45'}·Vp",
                 "φVm = 0.9·Vm", "Vu/φVm"],
        "Value": [f"{r['Vp']:.2f} kips", f"{r['Vmt']:.2f} kips", f"{r['Vmb']:.2f} kips",
                  f"{r['sum_Vm']:.2f} kips", f"{r['Vm_cap']:.2f} kips",
                  f"{r['phiVm']:.2f} kips", f"{r['v_ratio']:.3f}"],
    }), width="stretch", hide_index=True)

st.subheader("Detailing — §3.7b")
s_req = "—  (Vu ≥ 0.9·Vp)" if math.isinf(r["S_req"]) else f"{r['S_req']:.2f} in"
st.dataframe(status_df(pd.DataFrame([
    ["Min corner radius ≥ max(2tw, ⅝″)", f"{r['r_min']:.3f} in", "n/a", "§3.7b2"],
    ["Required clear spacing S", s_req, r["s_status"], "Eqs 3-37 / 3-38"],
], columns=["Item", "Value", "Status", "Reference"])),
    width="stretch", hide_index=True)
st.caption("No concentrated loads above the opening; see §3.7b3 for bearing-stiffener criteria.")

with st.expander("Derived geometry"):
    st.dataframe(pd.DataFrame({
        "Item": ["h0 (shear)", "a0 (effective)", "ΔAs = h0·tw", "st (deeper tee)",
                 "sb (shallower tee)", "νt = a0/st", "νb = a0/sb", "Web class"],
        "Value": [f"{r['h0s']:.2f} in", f"{r['a0']:.2f} in", f"{r['dAs']:.2f} in²",
                  f"{r['st']:.3f} in", f"{r['sb']:.3f} in", f"{r['nut']:.3f}",
                  f"{r['nub']:.3f}", "Stocky" if r["stocky"] else "Non-stocky"],
    }), width="stretch", hide_index=True)

st.divider()
st.caption(
    "Method per AISC Design Guide 2 (Darwin), Ch. 3–4, unreinforced opening, LRFD, φ = 0.90. "
    "Section properties: AISC Shapes Database v15.0. This tool reproduces a spreadsheet marked "
    "**not checked** and is for preliminary use only — all results must be verified by a "
    "licensed engineer before use in design."
)
