import streamlit as st
from passporteye import read_mrz
import datetime
import pytesseract
import os
import cv2
import uuid
import re
import numpy as np
from PIL import Image, ImageEnhance
import streamlit.components.v1 as components

# ================= TESSERACT =================
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# ================= PAGE =================
st.set_page_config(page_title="Amadeus Auto PNR Builder", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp { background:#f4f7fb; }

.header-bar {
    background: linear-gradient(90deg,#0b5394,#1c7ed6);
    padding:14px 20px;
    border-radius:12px;
    margin-bottom:20px;
    display:flex;
    justify-content:space-between;
    align-items:center;
}
.header-title { font-size:26px; font-weight:700; color:white; }
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
</style>

<div class="header-bar">
<div class="header-title">✈️ Amadeus Auto PNR Builder</div>
<div class="header-dev">Developed by Aamir Khan</div>
</div>
""", unsafe_allow_html=True)

# ================= DATE SAFE FUNCTIONS =================

def mrz_date_fix(d):
    if not d or len(str(d)) < 6:
        return datetime.datetime(2000,1,1)

    try:
        d=str(d)
        y=int(d[:2])
        m=int(d[2:4])
        da=int(d[4:6])

        if y > datetime.datetime.now().year % 100:
            y += 1900
        else:
            y += 2000

        return datetime.datetime(y,m,da)
    except:
        return datetime.datetime(2000,1,1)

def safe_date(d):
    return mrz_date_fix(d).strftime("%d%b%y").upper()

def calculate_age(d):
    birth=mrz_date_fix(d)
    today=datetime.datetime.today()
    age=today.year-birth.year-((today.month,today.day)<(birth.month,birth.day))
    return age,birth.strftime("%d%b%y").upper()

# ================= TITLE =================
def passenger_title(age,gender,dob):
    if age >= 12:
        return "MR" if gender=="M" else "MRS"
    elif age >= 2:
        return "CHD"
    else:
        return "INF"

# ================= NAME CLEAN =================
def parse_mrz_names(surname,names):

    surname=surname.replace("<","").strip().upper()
    names=names.replace("<"," ")

    clean=[]
    for w in names.split():

        w=w.strip().upper()

        # remove garbage words like KKKKK
        if len(w)<=1: continue
        if len(set(w))==1: continue
        if w.count("K")>len(w)*0.5: continue

        clean.append(w)

    return surname," ".join(clean)

# ================= OCR EXTRA =================
def extract_extra_fields(path):

    img=cv2.imread(path)
    if img is None:
        return "","","",""

    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    text=pytesseract.image_to_string(gray)

    father=""; pob=""; doi=""; cnic=""

    for line in text.upper().split("\n"):

        if "FATHER" in line or "HUSBAND" in line:
            father=line

        if "KARACHI" in line or "PLACE OF BIRTH" in line:
            pob=line

        if "ISSUE" in line:
            doi=line

        m=re.search(r"\d{5}-\d{7}-\d",line)
        if m:
            cnic=m.group()

    return father,pob,doi,cnic

# ================= PHOTO ENHANCER =================
def enhance_photo(image):

    img=Image.open(image).convert("RGB")

    enhancer=ImageEnhance.Sharpness(img)
    img=enhancer.enhance(1.5)

    enhancer=ImageEnhance.Contrast(img)
    img=enhancer.enhance(1.2)

    enhancer=ImageEnhance.Brightness(img)
    img=enhancer.enhance(1.05)

    img=img.resize((120,150))
    return img

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

        try:
            mrz=read_mrz(temp)
        except:
            mrz=None

        if not mrz:
            st.warning("MRZ not detected")
            continue

        d=mrz.to_dict()

        passport=d.get("number","")

        if passport in seen:
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

        passengers.append({
            "surname":surname,
            "names":names,
            "passport":passport,
            "dob":dob,
            "exp":exp,
            "gender":gender,
            "country":country,
            "age":age,
            "father":father,
            "pob":pob,
            "doi":doi,
            "cnic":cnic
        })

        os.remove(temp)

# ================= OUTPUT =================
nm1_lines=[]
docs_lines=[]

if passengers:

    st.subheader("Extracted Passport Details")

    for i,p in enumerate(passengers,1):

        st.markdown('<div class="passport-box">',unsafe_allow_html=True)

        st.write(f"Passenger {i}: {p['surname']} {p['names']}")
        st.write("Surname:",p["surname"])
        st.write("Given Name:",p["names"])
        st.write("Passport:",p["passport"])
        st.write("DOB:",p["dob"])
        st.write("Expiry:",p["exp"])
        st.write("Father/Husband:",p["father"])
        st.write("Place of Birth:",p["pob"])
        st.write("Date of Issue:",p["doi"])
        st.write("CNIC:",p["cnic"])

        st.markdown('</div>',unsafe_allow_html=True)

    pax=1
    for p in passengers:

        title=passenger_title(p["age"],p["gender"],p["dob"])

        nm1_lines.append(f"NM1{p['surname']}/{p['names']} {title}")

        docs_lines.append(
            f"SRDOCS SV HK1-P-{p['country']}-{p['passport']}-"
            f"{p['country']}-{p['dob']}-{p['gender']}-"
            f"{p['exp']}-{p['surname']}-{p['names'].replace(' ','-')}-H/P{pax}"
        )
        pax+=1

    export_text="\n".join(nm1_lines)+"\n\n"+"\n".join(docs_lines)

    st.subheader("NM1 Entries")
    st.code("\n".join(nm1_lines))

    st.subheader("SRDOCS Entries")
    st.code("\n".join(docs_lines))

    st.download_button(
        "⬇ Download Amadeus PNR",
        data=export_text,
        file_name="amadeus_pnr.txt"
    )
