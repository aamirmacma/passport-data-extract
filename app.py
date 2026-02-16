import streamlit as st

# IMPORTANT IMPORT FIX
from pages import Passport_Auto_PNR
from pages import Passport_Photo_Maker
from pages import Passport_Size_Maker


st.set_page_config(
    page_title="Passport | Photo | Auto Builder",
    layout="wide"
)

# HEADER
st.markdown("""
<div style="
background: linear-gradient(90deg,#0b5394,#1c7ed6);
padding:18px;
border-radius:12px;
margin-bottom:20px;
color:white;
font-size:26px;
font-weight:700;">
✈️ Passport | Photo | Auto Builder
<br>
<span style="font-size:14px;">Developed by Aamir Khan</span>
</div>
""", unsafe_allow_html=True)


# ====== TABS ======
tab1, tab2, tab3 = st.tabs([
    "🛂 Passport Auto PNR",
    "📷 Passport Photo Maker",
    "📐 Passport Size Maker"
])

with tab1:
    Passport_Auto_PNR.run()

with tab2:
    Passport_Photo_Maker.run()

with tab3:
    Passport_Size_Maker.run()
