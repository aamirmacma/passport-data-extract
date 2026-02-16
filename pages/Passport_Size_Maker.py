import streamlit as st
from PIL import Image
import io

def run():

    st.subheader("📐 Passport Size Maker")

    st.info(
        "NOTE: JPG format only. Max file size 500KB."
    )

    file = st.file_uploader("Upload Photo", type=["jpg","jpeg"])

    if file:

        img = Image.open(file)

        # Haji size approx
        img = img.resize((120,150))

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)

        size_kb = len(buffer.getvalue())/1024

        st.image(img)

        st.write(f"Final Size: {round(size_kb,2)} KB")

        st.download_button(
            "Download Passport Size Photo",
            buffer.getvalue(),
            "passport_size.jpg",
            "image/jpeg"
        )
