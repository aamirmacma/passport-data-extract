import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(layout="wide")

st.title("📷 Passport Photo Maker")

file = st.file_uploader("Upload Photo", type=["jpg","jpeg","png"])

if file:

    img = Image.open(file)
    img = np.array(img)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Enhance
    lab= cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l,a,b=cv2.split(lab)
    l=cv2.equalizeHist(l)
    enhanced=cv2.merge((l,a,b))
    enhanced=cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)

    st.image(enhanced, width=250)

    pil_img = Image.fromarray(enhanced)
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=90)

    st.download_button(
        "Download Photo",
        buf.getvalue(),
        "passport_photo.jpg",
        "image/jpeg"
    )
