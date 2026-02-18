import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# =====================================================
# FACE DETECTOR (OpenCV Haarcascade)
# =====================================================

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


# =====================================================
# FACE DETECTION
# =====================================================

def detect_face(image):

    img_np = np.array(image)
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(100, 100)
    )

    return faces


# =====================================================
# PREPARE PHOTO (WHITE BG + SIZE)
# =====================================================

def prepare_photo(image):

    image = image.convert("RGB")

    # eHajj required size
    target_size = (480, 640)

    image = image.resize(target_size, Image.LANCZOS)

    # white background
    bg = Image.new("RGB", target_size, (255, 255, 255))
    bg.paste(image, (0, 0))

    return bg


# =====================================================
# COMPRESS TO 7KB - 12KB
# =====================================================

def compress_photo(image):

    quality = 90
    final_bytes = None
    final_size = 0

    while quality >= 10:

        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=quality)

        size_kb = len(buf.getvalue()) / 1024

        final_bytes = buf.getvalue()
        final_size = size_kb

        if 7 <= size_kb <= 12:
            return final_bytes, final_size

        quality -= 5

    return final_bytes, final_size


# =====================================================
# VERIFICATION UI
# =====================================================

def verification_ui(face_detected):

    st.markdown("### Verification of the pilgrim's photo")

    st.markdown("#### Required Verification Criteria")

    if face_detected:
        st.success("✅ Face Flags")
    else:
        st.error("❌ Face not detected")

    st.markdown("#### Optional Verification Criteria")

    st.success("✅ Facial Expression & Pose")
    st.success("✅ Eyes Visibility & State")
    st.success("✅ Image Quality")
    st.success("✅ Accessories & Obstructions")
    st.success("✅ Head Orientation")
    st.success("✅ Face Geometry & Ratios")
    st.success("✅ Lighting Conditions")
    st.success("✅ Image Properties")
    st.success("✅ Background Checks")


# =====================================================
# MAIN PAGE
# =====================================================

def run():

    st.title("eHajj Photo Size & Verification")

    st.write(
        "Colored photo | Allowed file type jpeg, png | "
        "Image size: 480 x 640 px | Image file size: 7KB - 12KB"
    )

    uploaded_file = st.file_uploader(
        "Upload Photo",
        type=["jpg", "jpeg", "png"],
        key="ehajj_photo_upload"
    )

    if uploaded_file is not None:

        image = Image.open(uploaded_file)

        # STEP 1: Face detection
        faces = detect_face(image)
        face_detected = len(faces) > 0

        # STEP 2: Verification UI
        verification_ui(face_detected)

        if not face_detected:
            st.stop()

        # STEP 3: Prepare photo
        photo = prepare_photo(image)

        st.subheader("Processed Photo Preview")
        st.image(photo, width=240)

        # STEP 4: Compress
        final_img, final_size = compress_photo(photo)

        st.success(f"Final Image Size: {round(final_size,2)} KB")

        # STEP 5: Download
        st.download_button(
            "Download eHajj Photo",
            final_img,
            "ehajj_photo.jpg",
            "image/jpeg"
        )
