import streamlit as st
from PIL import Image
import io

# ==================================================
# MAIN RUN FUNCTION
# ==================================================
def run():

    st.title("📘 Passport Size Maker")

    st.info("""
    Upload full passport image.
    
    ✔ No auto cutting  
    ✔ Image balance same rahega  
    ✔ Auto resize to 1450 x 1010 px  
    ✔ JPG output approx 450KB
    """)

    uploaded_file = st.file_uploader(
        "Upload Passport Image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:

        # ---------- LOAD IMAGE ----------
        image = Image.open(uploaded_file).convert("RGB")

        st.subheader("Original Image")
        st.image(image, use_column_width=True)

        # ---------- RESIZE ----------
        target_width = 1450
        target_height = 1010

        resized = image.resize(
            (target_width, target_height),
            Image.LANCZOS
        )

        # ---------- COMPRESS TO ~450KB ----------
        buffer = io.BytesIO()

        quality = 95
        final_size_kb = 0

        # quality reduce karte rahenge jab tak size near 450KB na ho
        while quality > 20:
            buffer.seek(0)
            buffer.truncate()

            resized.save(
                buffer,
                format="JPEG",
                quality=quality,
                optimize=True
            )

            final_size_kb = len(buffer.getvalue()) / 1024

            if final_size_kb <= 450:
                break

            quality -= 5

        # ---------- PREVIEW ----------
        st.subheader("Resized Output (1450 x 1010)")
        st.image(resized, use_column_width=True)

        st.success(f"Final Size: {int(final_size_kb)} KB")

        # ---------- DOWNLOAD ----------
        st.download_button(
            "⬇ Download Passport Image",
            data=buffer.getvalue(),
            file_name="passport_resized.jpg",
            mime="image/jpeg"
        )
