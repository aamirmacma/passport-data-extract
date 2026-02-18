import streamlit as st
from PIL import Image
import io

# ==========================================
# FIX SIZE AND WHITE BACKGROUND
# ==========================================

def prepare_photo(image):

    # Convert RGB
    image = image.convert("RGB")

    # eHajj required size
    target_width = 480
    target_height = 640

    # Resize image
    image = image.resize((target_width, target_height), Image.LANCZOS)

    # White background canvas
    bg = Image.new("RGB", (target_width, target_height), (255, 255, 255))
    bg.paste(image, (0, 0))

    return bg


# ==========================================
# COMPRESS TO 7KB - 12KB
# ==========================================

def compress_to_small_range(image, min_kb=7, max_kb=12):

    quality = 95
    final_bytes = None
    final_size = 0

    while quality >= 10:

        img_bytes = io.BytesIO()
        image.save(img_bytes, format="JPEG", quality=quality)

        size_kb = len(img_bytes.getvalue()) / 1024

        final_bytes = img_bytes.getvalue()
        final_size = size_kb

        if min_kb <= size_kb <= max_kb:
            return final_bytes, final_size

        if size_kb > max_kb:
            quality -= 5
        else:
            break

    return final_bytes, final_size


# ==========================================
# MAIN PAGE
# ==========================================

def run():

    st.title("eHajj Photo Size")
    st.write(
        "Colored photo | Allowed file type jpeg, png | "
        "Image size: 480 x 640 px | File size: 7KB - 12KB"
    )

    uploaded_file = st.file_uploader(
        "Upload Photo",
        type=["jpg", "jpeg", "png"],
        key="ehajj_photo_upload"
    )

    if uploaded_file is not None:

        image = Image.open(uploaded_file)

        # Step 1: Prepare photo
        photo = prepare_photo(image)

        st.subheader("Preview")
        st.image(photo, width=240)

        # Step 2: Compress
        final_img, final_size = compress_to_small_range(photo)

        st.success(f"Final Size: {round(final_size,2)} KB")

        st.download_button(
            "Download eHajj Photo",
            final_img,
            "ehajj_photo_7_12kb.jpg",
            "image/jpeg"
        )
