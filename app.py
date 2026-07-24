import sys
import subprocess
import streamlit as st

# App start hone se pehle zabardasti dono OpenCV ura kar sirf sahi wala (Headless) install karna
subprocess.call([sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python", "opencv-python-headless"])
subprocess.call([sys.executable, "-m", "pip", "install", "opencv-python-headless==4.8.1.78"])

# ==============================
# PAGE CONFIG (Yeh hamesha sab se upar hona chahiye)
# ==============================
st.set_page_config(
    page_title="Passport | Photo | Auto Builder",
    layout="wide"
)

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {visibility: hidden !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ==============================
# IMPORT ALL PAGES
# ==============================
import Passport_Auto_PNR
import Passport_Photo_Maker
import Passport_Size_Maker
import Hajj_Form_Extractor
import ehajj_passport_size
import ehajj_photo_size

# ==============================
# HEADER DESIGN
# ==============================
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg,#0d47a1,#1976d2);
    padding: 18px;
    border-radius: 10px;
    color: white;
    font-size: 26px;
    font-weight: bold;
}
.dev {
    float:right;
    background:white;
    color:#0d47a1;
    padding:5px 12px;
    border-radius:20px;
    font-size:14px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
✈️ Passport | Photo | Auto Builder
<span class="dev">Developed by Aamir Khan</span>
</div>
""", unsafe_allow_html=True)

st.write("")

# ==============================
# MAIN TABS
# ==============================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Passport Auto PNR",
    "Passport Photo Maker",
    "Passport Size Maker",
    "Hajj Form Extractor",
    "eHajj Passport Size",
    "eHajj Photo Size"
])

# ==============================
# TABS CONTENT
# ==============================
with tab1:
    Passport_Auto_PNR.run()

with tab2:
    Passport_Photo_Maker.run()

with tab3:
    Passport_Size_Maker.run()

with tab4:
    Hajj_Form_Extractor.run()

with tab5:
    ehajj_passport_size.run()

with tab6:
    ehajj_photo_size.run()
