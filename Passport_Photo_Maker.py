import streamlit as st
from PIL import Image
import io


# ============================================
# MAIN FUNCTION
# ============================================
def run():

    st.title("📷 Passport Photo Maker (Haji Format)")

    st.info("""
NOTE:
Haji picture must be in JPG format.

• Only ONE photo allowed per Haji  
• Width range: 70 – 165 px  
• Height range: 65 – 185 px  
• File size range: 5KB – 12KB  
""")

    # ============================================
    # FILE UPLOAD
    # ============================================

    uploaded_file = st.file_uploader(
        "Upload Passport Photo (JPG only)",
        type=["jpg", "jpeg"]
    )

    if uploaded_file is None:
        return

    image = Image.open(uploaded_file).convert("RGB")

    st.subheader("Original Image")
    st.image(image, width=200)

    # ============================================
    # AUTO RESIZE FUNCTION
    # ============================================

    def resize_to_haji_standard(img):

        # target safe size inside allowed range
        target_width = 120
        target_height = 150

        img = img.resize((target_width, target_height))

        return img


    # ============================================
    # FILE SIZE CONTROL
    # ============================================

    def compress_to_size(img):

        min_size = 5 * 1024
        max_size = 12 * 1024

        quality = 95

        while quality > 10:

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality)

            size = buffer.tell()

            if min_size <= size <= max_size:
                return buffer, size

            quality -= 5

        # fallback
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=40)
        return buffer, buffer.tell()


    # ============================================
    # PROCESS IMAGE
    # ============================================

    processed_img = resize_to_haji_standard(image)
    buffer, final_size = compress_to_size(processed_img)

    final_size_kb = round(final_size / 1024, 2)

    st.subheader("Processed Photo")
    st.image(processed_img, width=200)

    st.success(
        f"Final Size: {processed_img.width}px × {processed_img.height}px | "
        f"{final_size_kb} KB"
    )

    # ============================================
    # VALIDATION
    # ============================================

    if not (70 <= processed_img.width <= 165):
        st.error("Width not in allowed range")

    if not (65 <= processed_img.height <= 185):
        st.error("Height not in allowed range")

    if not (5 <= final_size_kb <= 12):
        st.error("File size not in allowed range (5–12KB)")

    # ============================================
    # DOWNLOAD BUTTON
    # ============================================

    st.download_button(
        label="⬇ Download Haji Photo (JPG)",
        data=buffer.getvalue(),
        file_name="haji_photo.jpg",
        mime="image/jpeg"
    )
