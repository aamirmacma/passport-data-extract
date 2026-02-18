import streamlit as st
from PIL import Image
import io

# ==========================================
# COMPRESS IMAGE BETWEEN 400KB - 600KB
# ==========================================

def compress_image_to_range(image, min_kb=400, max_kb=600):

    low = 20
    high = 95
    best_bytes = None
    best_size = 0

    while low <= high:
        quality = (low + high) // 2

        img_bytes = io.BytesIO()
        image.save(img_bytes, format="JPEG", quality=quality)

        size_kb = len(img_bytes.getvalue()) / 1024

        best_bytes = img_bytes.getvalue()
        best_size = size_kb

        if min_kb <= size_kb <= max_kb:
            return best_bytes, size_kb

        elif size_kb < min_kb:
            low = quality + 1   # size barhao
        else:
            high = quality - 1  # size kam karo

    return best_bytes, best_size


# ==========================================
# MAIN PAGE
# ==========================================

def run():

    st.title("Passport")
    st.write("Upload passport image (Auto 400KB – 600KB)")

    uploaded_file = st.file_uploader(
        "Upload passport image",
        type=["jpg", "jpeg", "png"],
        key="ehajj_passport_upload"
    )

    if uploaded_file is not None:

        image = Image.open(uploaded_file).convert("RGB")

        st.image(image, use_column_width=True)

        compressed_img, final_size = compress_image_to_range(image)

        st.success(f"Final Size: {round(final_size,2)} KB")

        st.download_button(
            "Download Passport Image",
            compressed_img,
            "ehajj_passport_400_600kb.jpg",
            "image/jpeg"
        )
