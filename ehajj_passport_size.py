import streamlit as st
from PIL import Image, ImageChops, ImageOps
import io

# ==========================================
# AUTO ROTATE (FIX MOBILE ROTATION)
# ==========================================

def auto_rotate(image):
    try:
        image = ImageOps.exif_transpose(image)
    except:
        pass
    return image


# ==========================================
# AUTO CROP EXTRA BORDER
# ==========================================

def auto_crop(image):
    bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)
    return image


# ==========================================
# UPSCALE IMAGE (IF SIZE SMALL)
# ==========================================

def upscale_image(image, scale=1.15):
    w, h = image.size
    return image.resize((int(w*scale), int(h*scale)), Image.LANCZOS)


# ==========================================
# COMPRESS BETWEEN 400KB - 600KB
# ==========================================

def compress_to_range(image, min_kb=400, max_kb=600):

    quality = 95

    while True:

        img_bytes = io.BytesIO()
        image.save(img_bytes, format="JPEG", quality=quality)

        size_kb = len(img_bytes.getvalue()) / 1024

        if min_kb <= size_kb <= max_kb:
            return img_bytes.getvalue(), size_kb

        if size_kb < min_kb:
            image = upscale_image(image)
            continue

        if size_kb > max_kb:
            quality -= 5

        if quality < 20:
            return img_bytes.getvalue(), size_kb


# ==========================================
# MAIN PAGE
# ==========================================

def run():

    st.title("Passport")
    st.write("Upload passport image (Auto Straight + 400KB–600KB)")

    uploaded_file = st.file_uploader(
        "Upload passport image",
        type=["jpg", "jpeg", "png"],
        key="ehajj_passport_upload"
    )

    if uploaded_file is not None:

        image = Image.open(uploaded_file).convert("RGB")

        # ✅ Step 1 Rotate
        image = auto_rotate(image)

        # ✅ Step 2 Crop borders
        image = auto_crop(image)

        st.subheader("Processed Preview")
        st.image(image, use_column_width=True)

        # ✅ Step 3 Compress
        final_img, final_size = compress_to_range(image)

        st.success(f"Final Size: {round(final_size,2)} KB")

        st.download_button(
            "Download Passport Image",
            final_img,
            "ehajj_passport_400_600kb.jpg",
            "image/jpeg"
        )
