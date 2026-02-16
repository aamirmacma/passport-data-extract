import streamlit as st

st.set_page_config(
    page_title="Amadeus Tools",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-title{
    font-size:32px;
    font-weight:700;
    color:#0b5394;
}
.sub{
    font-size:16px;
    color:#555;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">✈️ Amadeus Tools</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Select tool from left sidebar</div>', unsafe_allow_html=True)

st.divider()

st.info("""
Available Tools:

✅ Passport Auto PNR  
✅ Passport Photo Maker  
✅ Passport Size Maker
""")
