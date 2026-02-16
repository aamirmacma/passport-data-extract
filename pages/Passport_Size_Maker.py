import streamlit as st
from PIL import Image
import io

st.set_page_config(layout="wide")

st.title("🪪 Passport Size Maker")

st.info("""
NOTE:
• JPG format only
• Max size 500KB
• Auto passport size adjustment
""")

file = st.file_uploader("Upload Image", type=["jpg","jpeg"])

if file:

    img = Image.open(file)

    # resize within range
    img = img.resize((140,170))

    st.image(img)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)

    st.download_button(
        "Download Passport Size",
        buf.getvalue(),
        "passport_size.jpg",
        "image/jpeg"
    )
