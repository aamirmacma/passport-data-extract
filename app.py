import streamlit as st

# ===== IMPORT TAB FILES =====
import passport_auto_pnr
import passport_photo_maker
import passport_size_maker


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Amadeus Auto PNR Builder",
    layout="wide"
)

# ================= HEADER STYLE =================
st.markdown("""
<style>

.stApp {
    background-color: #f4f7fb;
}

/* Header */
.header-bar {
    background: linear-gradient(90deg,#0b5394,#1c7ed6);
    padding:14px 20px;
    border-radius:12px;
    margin-bottom:20px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    box-shadow:0 3px 8px rgba(0,0,0,0.15);
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

/* Tabs spacing */
.block-container {
    padding-top: 1rem;
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


# ================= TAB 1 =================
with tab1:
    passport_auto_pnr.app()


# ================= TAB 2 =================
with tab2:
    passport_photo_maker.app()


# ================= TAB 3 =================
with tab3:
    passport_size_maker.app()
