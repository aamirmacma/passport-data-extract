import streamlit as st
import Passport_Auto_PNR
import Passport_Photo_Maker
import Passport_Size_Maker

st.set_page_config(page_title="Passport | Photo | Auto Builder", layout="wide")

# ===== HEADER =====
st.markdown("""
<style>
.header-bar{
    background:linear-gradient(90deg,#0b5394,#1c7ed6);
    padding:14px 20px;
    border-radius:12px;
    margin-bottom:20px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    color:white;
}
</style>

<div class="header-bar">
    <h3>✈ Passport | Photo | Auto Builder</h3>
    <b>Developed by Aamir Khan</b>
</div>
""", unsafe_allow_html=True)

# ===== TABS =====
tab1, tab2, tab3 = st.tabs([
    "Passport Auto PNR",
    "Passport Photo Maker",
    "Passport Size Maker"
])

with tab1:
    Passport_Auto_PNR.run()

with tab2:
    Passport_Photo_Maker.run()

with tab3:
    Passport_Size_Maker.run()
