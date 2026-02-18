import streamlit as st
from PIL import Image
import io

# ==========================================
# IMAGE COMPRESS FUNCTION
# ==========================================

def compress_image_to_range(image, min_kb=400, max_kb=500):

    quality = 95
    best_bytes = None

    while quality >= 20:
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="JPEG", quality=quality)
        size_kb = len(img_bytes.getvalue()) / 1024

        if min_kb <= size_kb <= max_kb:
            return img_bytes.getvalue(), size_kb

        best_bytes = img_bytes.getvalue()
        quality -= 5

    return best_bytes, size_kb


# ==========================================
# MAIN PAGE
# ==========================================

def run():

    st.title("Passport")
    st.write("Upload passport image (Auto 400KB – 500KB)")

    uploaded_file = st.file_uploader(
        "Upload passport image",
        type=["jpg", "jpeg", "png"],
        key="ehajj_passport_upload"
    )

    if uploaded_file is not None:

        image = Image.open(uploaded_file).convert("RGB")

        st.subheader("Original Image")
        st.image(image, use_column_width=True)

        # Compress image
        compressed_img, final_size = compress_image_to_range(image)

        st.success(f"Final Size: {round(final_size,2)} KB")

        st.download_button(
            label="Download Compressed Passport",
            data=compressed_img,
            file_name="ehajj_passport_400_500kb.jpg",
            mime="image/jpeg"
        )
