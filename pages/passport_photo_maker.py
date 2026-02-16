import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

def enhance(img):
    img = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)
    img = cv2.convertScaleAbs(img, alpha=1.1, beta=10)
    return img

def run():

    st.subheader("📷 Passport Photo Maker")

    file = st.file_uploader("Upload Photo", type=["jpg","jpeg","png"])

    if file:

        image = Image.open(file).convert("RGB")
        img = np.array(image)

        img = enhance(img)

        white_bg = np.ones_like(img) * 255
        result = cv2.addWeighted(img, 0.9, white_bg, 0.1, 0)

        st.image(result, width=250)

        buffer = io.BytesIO()
        Image.fromarray(result).save(buffer, format="JPEG", quality=95)

        st.download_button(
            "Download Photo",
            data=buffer.getvalue(),
            file_name="passport_photo.jpg",
            mime="image/jpeg"
        )
