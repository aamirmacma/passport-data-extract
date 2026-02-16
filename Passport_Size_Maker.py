import streamlit as st
from PIL import Image
import io

# ===============================================
# MAIN RUN FUNCTION
# ===============================================
def run():

    st.title("🛂 Passport Size Maker")

    st.info("""
    Upload full passport image.

    ✔ Output Size: 1450 x 1010 px  
    ✔ Format: JPG  
    ✔ File Size: Minimum 450KB (less not allowed)
    """)

    uploaded = st.file_uploader(
        "Upload Passport Image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded:

        img = Image.open(uploaded).convert("RGB")

        # ---------- RESIZE ----------
        img = img.resize((1450, 1010), Image.LANCZOS)

        # ---------- SAVE WITH SIZE CONTROL ----------
        target_size = 450 * 1024   # 450 KB

        quality = 95
        final_bytes = None

        # first compress down if too big
        while quality >= 60:
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality, optimize=True)
            size = buffer.tell()

            if size <= target_size:
                final_bytes = buffer
                break

            quality -= 5

        # if size became smaller than 450KB, increase quality again
        if final_bytes is not None:
            while final_bytes.tell() < target_size and quality < 100:
                quality += 1
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=quality)
                final_bytes = buffer

        st.image(img, caption="Preview", use_column_width=True)

        size_kb = round(final_bytes.tell() / 1024, 2)

        st.success(f"Final Size: {size_kb} KB")

        st.download_button(
            "⬇ Download Passport Size",
            data=final_bytes.getvalue(),
            file_name="passport_1450x1010.jpg",
            mime="image/jpeg"
        )
