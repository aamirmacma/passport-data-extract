import streamlit as st

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Passport | Photo | Auto Builder",
    layout="wide"
)

# ================= HEADER STYLE =================
st.markdown("""
<style>

.stApp { background-color:#f4f7fb; }

.header-bar {
    background: linear-gradient(90deg,#0b5394,#1c7ed6);
    padding:16px 25px;
    border-radius:12px;
    margin-bottom:20px;
    box-shadow:0 3px 8px rgba(0,0,0,0.15);
}

.header-title {
    font-size:26px;
    font-weight:700;
    color:white;
}

.header-dev {
    float:right;
    color:white;
    font-size:14px;
}

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="header-bar">
    <span class="header-title">✈️ Passport | Photo | Auto Builder</span>
    <span class="header-dev">Developed by Aamir Khan</span>
</div>
""", unsafe_allow_html=True)

# ================= TABS =================
tab1, tab2, tab3 = st.tabs([
    "🛂 Passport Auto PNR",
    "📷 Passport Photo Maker",
    "📐 Passport Size Maker"
])

# ================= TAB 1 =================
with tab1:
    import Passport_Auto_PNR
    Passport_Auto_PNR.run()

# ================= TAB 2 =================
with tab2:
    import Passport_Photo_Maker
    Passport_Photo_Maker.run()

# ================= TAB 3 =================
with tab3:
    import Passport_Size_Maker
    Passport_Size_Maker.run()
