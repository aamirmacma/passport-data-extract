import streamlit as st

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Amadeus Auto PNR Builder",
    layout="wide"
)

# ================= STYLE =================
st.markdown("""
<style>

.stApp { background-color:#f4f7fb; }

.header-bar {
    background: linear-gradient(90deg,#0b5394,#1c7ed6);
    padding:14px 20px;
    border-radius:12px;
    margin-bottom:25px;
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

.home-box {
    background:white;
    padding:25px;
    border-radius:12px;
    box-shadow:0 2px 6px rgba(0,0,0,0.08);
}

</style>

<div class="header-bar">
    <div class="header-title">✈️ Amadeus Auto PNR Builder</div>
    <div class="header-dev">Developed by Aamir Khan</div>
</div>
""", unsafe_allow_html=True)

# ================= HOME CONTENT =================

st.markdown('<div class="home-box">', unsafe_allow_html=True)

st.title("Welcome")

st.write("""
This is the home page of Amadeus Auto PNR Builder.

Use the left sidebar to open different tools:

✅ Passport Auto PNR Builder  
✅ Passport Photo Maker  
✅ Passport Size Maker  

Each tool works on a separate page.
""")

st.info("Select a page from the sidebar to start.")

st.markdown('</div>', unsafe_allow_html=True)
