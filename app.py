import streamlit as st

st.set_page_config(page_title="Amadeus Tools", layout="wide")

st.markdown("""
<style>
.main-title{
    font-size:28px;
    font-weight:700;
    color:#0b5394;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">✈️ Amadeus Tools</div>', unsafe_allow_html=True)
st.write("Left menu se tool select karein:")
st.write("• Passport Auto PNR")
st.write("• Passport Photo Maker")
st.write("• Passport Size Maker")
