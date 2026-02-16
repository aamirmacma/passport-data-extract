import streamlit as st
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Passport Photo Tool", layout="centered")

st.title("📷 Passport Photo Auto Adjust & Enhancer")

passport_no = st.text_input("Enter Passport Number")

uploaded = st.file_uploader("Upload Photo (JPG)", type=["jpg","jpeg"])

MIN_W, MAX_W = 70, 165
MIN_H, MAX_H = 65, 185
MIN_KB, MAX_KB = 5, 12


# ===== IMAGE ENHANCE =====
def enhance_image(img):
    img = ImageEnhance.Brightness(img).enhance(1.1)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = ImageEnhance.Sharpness(img).enhance(1.2)
    return img


# ===== RESIZE =====
def resize_passport(img):
    w, h = img.size

    scale = min(MAX_W/w, MAX_H/h)
    new_w = int(w * scale)
    new_h = int(h * scale)

    new_w = max(MIN_W, min(MAX_W, new_w))
    new_h = max(MIN_H, min(MAX_H, new_h))

    return img.resize((new_w, new_h))


# ===== ADD PASSPORT TEXT =====
def add_passport_text(img, passport_no):
    draw = ImageDraw.Draw(img)

    font_size = int(img.height * 0.08)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    text = f"{passport_no}"

    text_w, text_h = draw.textbbox((0,0), text, font=font)[2:]

    x = (img.width - text_w) // 2
    y = img.height - text_h - 2

    draw.text((x,y), text, fill="black", font=font)

    return img


# ===== COMPRESS =====
def compress_to_size(img):
    quality = 95
    buffer = io.BytesIO()

    while quality > 10:
        buffer.seek(0)
        img.save(buffer, format="JPEG", quality=quality)
        size_kb = len(buffer.getvalue()) / 1024

        if MIN_KB <= size_kb <= MAX_KB:
            break

        quality -= 5

    return buffer


# ===== MAIN =====
if uploaded and passport_no:

    img = Image.open(uploaded).convert("RGB")

    img = enhance_image(img)
    img = resize_passport(img)
    img = add_passport_text(img, passport_no)

    output = compress_to_size(img)

    st.subheader("Preview")
    st.image(img)

    final_size = len(output.getvalue())/1024
    st.success(f"Final Size: {round(final_size,2)} KB")

    st.download_button(
        "⬇ Download Passport Photo",
        data=output.getvalue(),
        file_name="passport_photo.jpg",
        mime="image/jpeg"
    )
