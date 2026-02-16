import streamlit as st

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Passport | Photo | Auto Builder",
    layout="wide"
)

# ================= STYLE =================
st.markdown("""
<style>

.stApp {
    background-color: #f4f7fb;
}

/* Header */
.header-bar {
    background: linear-gradient(90deg,#0b5394,#1c7ed6);
    padding:18px 24px;
    border-radius:14px;
    margin-bottom:25px;
    box-shadow:0 4px 12px rgba(0,0,0,0.15);
}

.header-title {
    font-size:28px;
    font-weight:700;
    color:white;
}

.header-dev {
    color:white;
    font-size:14px;
    margin-top:4px;
    opacity:0.9;
}

/* Info box */
.info-box {
    background:white;
    padding:20px;
    border-radius:12px;
    box-shadow:0 2px 6px rgba(0,0,0,0.08);
    margin-top:15px;
}

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="header-bar">
    <div class="header-title">✈️ Passport | Photo | Auto Builder</div>
    <div class="header-dev">Developed by Aamir Khan</div>
</div>
""", unsafe_allow_html=True)

# ================= MAIN CONTENT =================
st.markdown("""
<div class="info-box">
<h3>Welcome</h3>

<p>
Left side menu se ap apna tool select kar sakte hain:
</p>

<ul>
<li><b>Passport Auto PNR</b> — Passport se automatic Amadeus NM1 & SRDOCS banata hai</li>
<li><b>Passport Photo Maker</b> — Photo enhance + white background + download</li>
<li><b>Passport Size Maker</b> — Passport size photo auto resize (Haji format)</li>
</ul>

<p>
Har tool alag page par run hota hai taake system stable rahe.
</p>
</div>
""", unsafe_allow_html=True)
