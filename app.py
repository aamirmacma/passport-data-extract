import streamlit as st

# ================= PAGE CONFIG =================
<div class="header-bar">
    <div>
        <div class="header-title">✈️ Passport | Photo | Auto Builder</div>
        <div style="color:white;font-size:14px;margin-top:2px;">
            Developed by Aamir Khan
        </div>
    </div>
</div>

)

# ================= HEADER STYLE =================
st.markdown("""
<style>

.stApp {
    background-color:#f4f7fb;
}

.header-bar {
    background: linear-gradient(90deg,#0b5394,#1c7ed6);
    padding:16px 22px;
    border-radius:12px;
    margin-bottom:25px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    box-shadow:0 3px 10px rgba(0,0,0,0.15);
}

.header-title {
    font-size:26px;
    font-weight:700;
    color:white;
}

.header-dev {
    background:white;
    color:#0b5394;
    padding:6px 16px;
    border-radius:20px;
    font-size:14px;
    font-weight:600;
}

.home-box {
    background:white;
    padding:20px;
    border-radius:12px;
    box-shadow:0 2px 8px rgba(0,0,0,0.08);
    margin-top:10px;
}

</style>

<div class="header-bar">
    <div class="header-title">✈️ Amadeus Auto PNR Builder</div>
    <div class="header-dev">Developed by Aamir Khan</div>
</div>
""", unsafe_allow_html=True)

# ================= HOME CONTENT =================

st.markdown("""
<div class="home-box">

<h3>Welcome to Amadeus Tools</h3>

<p>Select tool from the left sidebar:</p>

<ul>
<li>Passport Auto PNR</li>
<li>Passport Photo Maker</li>
<li>Passport Size Maker</li>
</ul>

<p>This system helps travel agents quickly generate Amadeus entries and prepare passport photos automatically.</p>

</div>
""", unsafe_allow_html=True)

