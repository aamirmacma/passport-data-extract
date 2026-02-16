import streamlit as st
from PIL import Image
import io

# ==========================================
# PASSPORT PHOTO MAKER (HAJI PHOTO SYSTEM)
# ==========================================

def run():

    st.title("📷 Passport Photo Maker")

    st.info("""
    NOTE:

    ✅ JPG format required  
    ✅ Width range: 70 – 165 px  
    ✅ Height range: 65 – 185 px  
    ✅ File size: 5KB – 12KB  
    """)

    uploaded = st.file_uploader(
        "Upload Photo",
        type=["jpg", "jpeg"]
    )

    if uploaded:

        img = Image.open(uploaded).convert("RGB")

        # -----------------------------
        # TARGET SAFE SIZE
        # -----------------------------
        target_width = 140
        target_height = 160

        # Keep aspect ratio
        img.thumbnail((target_width, target_height), Image.LANCZOS)

        # Create white background
        final_img = Image.new("RGB", (target_width, target_height), (255,255,255))

        # center paste
        x = (target_width - img.width) // 2
        y = (target_height - img.height) // 2
        final_img.paste(img, (x, y))

        # -----------------------------
        # FILE SIZE CONTROL (5-12 KB)
        # -----------------------------
        final_bytes = None
        final_size = 0

        for quality in range(95, 20, -5):

            buffer = io.BytesIO()
            final_img.save(buffer, format="JPEG", quality=quality, optimize=True)

            size_kb = len(buffer.getvalue()) / 1024

            if 5 <= size_kb <= 12:
                final_bytes = buffer.getvalue()
                final_size = size_kb
                break

        # fallback
        if final_bytes is None:
            buffer = io.BytesIO()
            final_img.save(buffer, format="JPEG", quality=40, optimize=True)
            final_bytes = buffer.getvalue()
            final_size = len(final_bytes) / 1024

        # -----------------------------
        # PREVIEW
        # -----------------------------
        st.image(final_img, caption="Passport Photo Preview")

        st.success(f"Final Size: {round(final_size,2)} KB")

        if final_size < 5:
            st.warning("⚠ File size 5KB se kam hai")

        if final_size > 12:
            st.warning("⚠ File size 12KB se zyada hai")

        # -----------------------------
        # DOWNLOAD
        # -----------------------------
        st.download_button(
            "⬇ Download Photo",
            data=final_bytes,
            file_name="passport_photo.jpg",
            mime="image/jpeg"
        )
