import streamlit as st

import passport_auto_pnr
import passport_photo_maker
import passport_size_maker

st.set_page_config(page_title="Amadeus Auto PNR Builder", layout="wide")

st.title("✈️ Amadeus Auto PNR Builder")

tab1, tab2, tab3 = st.tabs([
    "Passport Auto PNR",
    "Passport Photo Maker",
    "Passport Size Maker"
])

with tab1:
    passport_auto_pnr.app()

with tab2:
    passport_photo_maker.app()

with tab3:
    passport_size_maker.app()

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Amadeus Auto PNR Builder",
    layout="wide"
)

# ================= HEADER =================
st.markdown("""
<style>
.stApp { background-color:#f4f7fb; }

.header-bar {
    background: linear-gradient(90deg,#0b5394,#1c7ed6);
    padding:14px 20px;
    border-radius:12px;
    margin-bottom:20px;
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.header-title {
    font-size:26px;
    font-weight:700;
    color:white;
}

.header-dev {
    background:white;
    color:#0b5394;
    padding:6px 14px;
    border-radius:20px;
    font-size:14px;
    font-weight:600;
}
</style>

<div class="header-bar">
    <div class="header-title">✈️ Amadeus Auto PNR Builder</div>
    <div class="header-dev">Developed by Aamir Khan</div>
</div>
""", unsafe_allow_html=True)

# ================= TABS =================
tab1, tab2, tab3 = st.tabs([
    "🛂 Passport Auto PNR",
    "📷 Passport Photo Maker",
    "📏 Passport Size Maker"
])

with tab1:
    Passport_Auto_PNR.app()

with tab2:
    Passport_Photo_Maker.app()

with tab3:
    Passport_Size_Maker.app()

