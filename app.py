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
    background-color:#f4f7fb;
}

/* Header */
.header-bar {
    background: linear-gradient(90deg,#0b5394,#1c7ed6);
    padding:18px 25px;
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
    opacity:0.9;
}

/* Cards */
.tool-card {
    background:white;
    padding:22px;
    border-radius:12px;
    box-shadow:0 2px 6px rgba(0,0,0,0.08);
    border-left:5px solid #1c7ed6;
    height:180px;
}

.tool-title {
    font-size:20px;
    font-weight:600;
    margin-bottom:10px;
}

.tool-desc {
    color:#555;
    font-size:14px;
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

# ================= WELCOME =================
st.markdown("## Welcome")

st.write(
"""
Left sidebar se ap apna tool select kar sakte hain.
Har system alag page par run hota hai taake speed aur stability maintain rahe.
"""
)

st.markdown("<br>", unsafe_allow_html=True)

# ================= DASHBOARD CARDS =================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-title">🛂 Passport Auto PNR</div>
        <div class="tool-desc">
        Passport MRZ read karke automatic Amadeus NM1 aur SRDOCS entries banata hai.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-title">📷 Passport Photo Maker</div>
        <div class="tool-desc">
        Photo enhance karta hai, white background apply karta hai aur download ready banata hai.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-title">📐 Passport Size Maker</div>
        <div class="tool-desc">
        Haji passport format ke mutabiq auto resize aur compress karta hai.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

st.info("⬅️ Left sidebar se tool open karein.")
