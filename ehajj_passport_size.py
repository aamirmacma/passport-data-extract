import streamlit as st
from PIL import Image
import io

# ==========================================
# RESIZE IMAGE UP (IF SIZE TOO SMALL)
# ==========================================

def upscale_image(image, scale=1.2):
    w, h = image.size
    new_size = (int(w * scale), int(h * scale))
    return image.resize(new_size, Image.LANCZOS)


# ==========================================
# COMPRESS BETWEEN 400KB - 600KB
# ==========================================

def compress_to_range(image, min_kb=400, max_kb=600):

    quality = 95
    final_bytes = None
    final_size = 0

    while True:

        img_bytes = io.BytesIO()
        image.save(img_bytes, format="JPEG", quality=quality)

        size_kb = len(img_bytes.getvalue()) / 1024

        # ✅ Perfect range
        if min_kb <= size_kb <= max_kb:
            return img_bytes.getvalue(), size_kb

        # ✅ Too small → upscale image
        if size_kb < min_kb:
            image = upscale_image(image, 1.15)
            continue

        # ✅ Too large → reduce quality
        if size_kb > max_kb:
            quality -= 5

        if quality < 20:
            return img_bytes.getvalue(), size_kb


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

        final_img, final_size = compress_to_range(image)

        st.success(f"Final Size: {round(final_size,2)} KB")

        st.download_button(
            "Download Passport Image",
            final_img,
            "ehajj_passport_400_600kb.jpg",
            "image/jpeg"
        )
