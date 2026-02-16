import streamlit as st
import cv2
import numpy as np

st.set_page_config(page_title="Passport Size Maker", layout="wide")

st.title("📐 Passport Size Maker")

st.info("JPG format | Max size 500KB")

file = st.file_uploader("Upload Photo", type=["jpg","jpeg"])

if file:

    file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    resized = cv2.resize(img,(120,150))

    st.image(resized, channels="BGR")

    _, buffer = cv2.imencode(".jpg", resized, [int(cv2.IMWRITE_JPEG_QUALITY),90])

    st.download_button(
        "Download Passport Size",
        buffer.tobytes(),
        "passport_size.jpg",
        "image/jpeg"
    )
