import streamlit as st
from passporteye import read_mrz
import datetime
import pytesseract
import os
import cv2
import uuid
import re
import streamlit.components.v1 as components

# ================= TESSERACT AUTO =================
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Amadeus Auto PNR Builder", layout="wide")

# ================= HEADER + STYLE =================
st.markdown("""
<style>
.stApp { background-color:#f4f7fb; }

.header-bar {
    background: linear-gradient(90deg,#0b5394,#1c7ed6);
    padding:14px 20px;
    border-radius:12px;
    margin-bottom:20px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    box-shadow:0 3px 8px rgba(0,0,0,0.15);
}

.header-title {
    font-size:26px;
    font-weight:700;
    color:white;
}

.header-dev {
    background:white;
    color:#0b5394;
    padding:6px 14px;
    border-radius:20px;
    font-size:14px;
    font-weight:600;
}

.passport-box {
    background:white;
    padding:15px;
    border-radius:12px;
    border-left:5px solid #1c7ed6;
    margin-bottom:10px;
}

.nm1-box {
    background:#eef5ff;
    padding:15px;
    border-radius:12px;
    border-left:5px solid #2f9e44;
}

.docs-box {
    background:#f1fff5;
    padding:15px;
    border-radius:12px;
    border-left:5px solid #37b24d;
}
</style>

<div class="header-bar">
    <div class="header-title">✈️ Amadeus Auto PNR Builder</div>
    <div class="header-dev">Developed by Aamir Khan</div>
</div>
""", unsafe_allow_html=True)

# ================= FUNCTIONS =================

def mrz_date_fix(d):
    if not d or len(d) < 6:
        return datetime.datetime(2000,1,1)

    y=int(d[:2])
    m=int(d[2:4])
    da=int(d[4:6])

    if y > datetime.datetime.now().year % 100:
        y += 1900
    else:
        y += 2000

    return datetime.datetime(y,m,da)

def safe_date(d):
    return mrz_date_fix(d).strftime("%d%b%y").upper()

def calculate_age(d):
    birth=mrz_date_fix(d)
    today=datetime.datetime.today()
    age=today.year-birth.year-((today.month,today.day)<(birth.month,birth.day))
    return age,birth.strftime("%d%b%y").upper()

def passenger_title(age,gender,dob):
    if age >= 12:
        return "MR" if gender=="M" else "MRS"
    elif age >= 2:
        return "CHD"
    else:
        return "INF"

def parse_mrz_names(surname,names):
    surname=surname.replace("<","").strip().upper()
    names=names.replace("<"," ")
    names=" ".join(names.split())

    clean=[]
    for w in names.split():
        if len(w)<=1:
            continue
        if len(set(w))==1:   # removes KKKKK
            continue
        if w.count("K")>len(w)*0.6:
            continue
        clean.append(w)

    return surname," ".join(clean)

def extract_extra_fields(path):
    img=cv2.imread(path)
    if img is None:
        return "","","",""

    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    text=pytesseract.image_to_string(gray)

    father=""; pob=""; doi=""; cnic=""
    lines=text.upper().split("\n")

    for i,line in enumerate(lines):
        if "FATHER" in line or "HUSBAND" in line:
            if i+1 < len(lines):
                father=lines[i+1].strip()

        if "PLACE OF BIRTH" in line:
            if i+1 < len(lines):
                pob=lines[i+1].strip()

        if "DATE OF ISSUE" in line:
            if i+1 < len(lines):
                doi=lines[i+1].strip()

        m=re.search(r"\d{5}-\d{7}-\d",line)
        if m:
            cnic=m.group()

    return father,pob,doi,cnic

def auto_rotate(path):
    img=cv2.imread(path)
    if img is None:
        return
    h,w=img.shape[:2]
    if h>w:
        img=cv2.rotate(img,cv2.ROTATE_90_CLOCKWISE)
    cv2.imwrite(path,img)

# ================= UPLOAD =================

files=st.file_uploader(
    "Upload Passport Images",
    type=["jpg","jpeg","png"],
    accept_multiple_files=True
)

passengers=[]
seen=set()

if files:

    for f in files:

        temp=f"temp_{uuid.uuid4().hex}.jpg"

        with open(temp,"wb") as fp:
            fp.write(f.getbuffer())

        auto_rotate(temp)

        try:
            mrz=read_mrz(temp)
        except:
            mrz=None

        if mrz:

            d=mrz.to_dict()
            passport=d.get("number","")

            if passport in seen:
                st.warning(f"Duplicate skipped: {passport}")
                os.remove(temp)
                continue

            seen.add(passport)

            surname,names=parse_mrz_names(
                d.get("surname",""),
                d.get("names","")
            )

            gender=d.get("sex","M")
            country=d.get("country","")

            age,dob=calculate_age(d.get("date_of_birth"))
            exp=safe_date(d.get("expiration_date"))

            father,pob,doi,cnic=extract_extra_fields(temp)
            title=passenger_title(age,gender,dob)

            passengers.append({
                "surname":surname,
                "names":names,
                "title":title,
                "passport":passport,
                "dob":dob,
                "exp":exp,
                "gender":gender,
                "country":country,
                "father":father,
                "pob":pob,
                "doi":doi,
                "cnic":cnic
            })

        os.remove(temp)

# ================= OUTPUT =================

from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import numpy as np
import io

passport_no = st.text_input("Enter Passport Number for Photo")

def enhance_passport_photo(pil_img):

    # ---- convert to numpy ----
    img = np.array(pil_img)

    # ---- background lightening ----
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # light pixels ko aur white karo
    _, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    img[mask == 255] = [255,255,255]

    img = Image.fromarray(img)

    # ---- enhancement ----
    img = ImageEnhance.Brightness(img).enhance(1.15)
    img = ImageEnhance.Contrast(img).enhance(1.20)
    img = ImageEnhance.Sharpness(img).enhance(1.25)

    return img


if files and passport_no:

    for file in files:

        img = Image.open(file).convert("RGB")

        # enhance + white background
        img = enhance_passport_photo(img)

        # passport size resize
        img = img.resize((140,180))

        # add passport number
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()

        draw.text((10,160), passport_no, fill="black", font=font)

        # prepare download
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)

        st.image(img, caption="Enhanced Passport Photo")

        st.download_button(
            "⬇ Download Passport Photo",
            data=buf.getvalue(),
            file_name=f"{passport_no}_passport.jpg",
            mime="image/jpeg"
        )
