import streamlit as st
from PIL import Image
import io

# ==========================================
# eHAJJ PASSPORT SIZE MAKER
# ==========================================

def run():

    st.markdown("""
    <style>
    .box {
        background:#f5f7fa;
        padding:20px;
        border-radius:10px;
        border:1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Passport")
    st.write("Please upload the pilgrim's passport")

    st.markdown('<div class="box">', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload passport image (JPG/PNG, 400–1200 x 400–2000px, max 2MB).",
        type=["jpg", "jpeg", "png"],
        key="ehajj_passport_upload"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ===============================
    # IMAGE PROCESS
    # ===============================
    if uploaded_file is not None:

        image = Image.open(uploaded_file)

        width, height = image.size

        st.subheader("Preview")
        st.image(image, use_column_width=True)

        st.write(f"Image Size: {width} x {height}px")

        # Basic validation
        if width < 400 or height < 400:
            st.error("Image size is too small. Minimum size is 400x400 px.")
        elif width > 2000 or height > 2000:
            st.warning("Image is larger than recommended size.")
        else:
            st.success("Passport image uploaded successfully.")

        # Download option
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")

        st.download_button(
            label="Download Image",
            data=img_bytes.getvalue(),
            file_name="ehajj_passport.png",
            mime="image/png"
        )
