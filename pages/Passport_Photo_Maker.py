import streamlit as st
import cv2
import numpy as np

st.set_page_config(page_title="Passport Photo Maker", layout="wide")

st.title("📷 Passport Photo Maker")

file = st.file_uploader("Upload Photo", type=["jpg","jpeg","png"])

if file:

    file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    # Enhance
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l,a,b = cv2.split(lab)
    l = cv2.equalizeHist(l)
    enhanced = cv2.merge((l,a,b))
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    st.image(enhanced, channels="BGR")

    _, buffer = cv2.imencode(".jpg", enhanced)
    st.download_button(
        "Download Photo",
        buffer.tobytes(),
        "passport_photo.jpg",
        "image/jpeg"
    )
