import streamlit as st
from passporteye import read_mrz
import datetime
import pytesseract
import os
import cv2
import uuid
import re
from PIL import Image, ImageEnhance
import numpy as np
import io

# ================= CONFIG =================
st.set_page_config(page_title="Amadeus Auto PNR Builder", layout="wide")

# ================= TESSERACT =================
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# ================= HEADER =================
st.markdown("""
<style>
.stApp {background:#f4f7fb;}

.header-bar{
 background:linear-gradient(90deg,#0b5394,#1c7ed6);
 padding:14px 20px;
 border-radius:12px;
 margin-bottom:20px;
 display:flex;
 justify-content:space-between;
 align-items:center;
}

.header-title{
 font-size:26px;
 font-weight:700;
 color:white;
}

.header-dev{
 background:white;
 color:#0b5394;
 padding:6px 14px;
 border-radius:20px;
 font-size:14px;
 font-weight:600;
}

.box{
 background:white;
 padding:15px;
 border-radius:12px;
 margin-bottom:12px;
}
</style>

<div class="header-bar">
<div class="header-title">✈️ Amadeus Auto PNR Builder</div>
<div class="header-dev">Developed by Aamir Khan</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✈️ Passport PNR Builder", "📷 Passport Photo Maker"])

# =========================================================
# ================= PASSPORT SYSTEM =======================
# =========================================================

def mrz_date_fix(d):
    if not d or len(d)<6:
        return datetime.datetime(2000,1,1)
    y=int(d[:2])
    m=int(d[2:4])
    da=int(d[4:6])

    if y > datetime.datetime.now().year % 100:
        y+=1900
    else:
        y+=2000
    return datetime.datetime(y,m,da)

def safe_date(d):
    return mrz_date_fix(d).strftime("%d%b%y").upper()

def calculate_age(d):
    birth=mrz_date_fix(d)
    today=datetime.datetime.today()
    age=today.year-birth.year
    return age,birth.strftime("%d%b%y").upper()

def passenger_title(age,gender,dob):
    if age>=12:
        return "MR" if gender=="M" else "MRS"
    elif age>=2:
        return f"CHD({dob})"
    else:
        return "INF"

def clean_names(surname,names):
    surname=surname.replace("<","").strip().upper()
    names=names.replace("<"," ").split()

    clean=[]
    for w in names:
        if len(w)<=1: continue
        if len(set(w))==1: continue
        if w.count("K")>len(w)*0.5: continue
        clean.append(w)

    return surname," ".join(clean)

with tab1:

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

            if mrz:

                d=mrz.to_dict()
                passport=d.get("number","")

                if passport in seen:
                    continue
                seen.add(passport)

                surname,names=clean_names(
                    d.get("surname",""),
                    d.get("names","")
                )

                age,dob=calculate_age(d.get("date_of_birth"))
                exp=safe_date(d.get("expiration_date"))

                passengers.append({
                    "surname":surname,
                    "names":names,
                    "passport":passport,
                    "dob":dob,
                    "exp":exp,
                    "gender":d.get("sex","M"),
                    "country":d.get("country",""),
                    "age":age
                })

            os.remove(temp)

    if passengers:

        st.subheader("Extracted Passport Details")

        nm1=[]
        docs=[]
        pax=1

        for p in passengers:

            title=passenger_title(p["age"],p["gender"],p["dob"])

            st.markdown('<div class="box">',unsafe_allow_html=True)
            st.write(f"{p['surname']} {p['names']}")
            st.write("Passport:",p["passport"])
            st.write("DOB:",p["dob"])
            st.write("Expiry:",p["exp"])
            st.markdown('</div>',unsafe_allow_html=True)

            nm1.append(f"NM1{p['surname']}/{p['names']} {title}")

            docs.append(
                f"SRDOCS SV HK1-P-{p['country']}-{p['passport']}-"
                f"{p['country']}-{p['dob']}-{p['gender']}-"
                f"{p['exp']}-{p['surname']}-{p['names'].replace(' ','-')}-H/P{pax}"
            )
            pax+=1

        st.subheader("NM1 Entries")
        st.code("\n".join(nm1))

        st.subheader("SRDOCS Entries")
        st.code("\n".join(docs))


# =========================================================
# ================= PHOTO SYSTEM ==========================
# =========================================================

def enhance_photo(img):
    img=ImageEnhance.Brightness(img).enhance(1.1)
    img=ImageEnhance.Contrast(img).enhance(1.2)
    img=ImageEnhance.Sharpness(img).enhance(1.2)
    return img

with tab2:

    photo=st.file_uploader(
        "Upload Passport Photo",
        type=["jpg","jpeg","png"]
    )

    if photo:

        img=Image.open(photo).convert("RGB")

        img=enhance_photo(img)

        img=img.resize((140,170))

        st.image(img,caption="Passport Photo Preview")

        buf=io.BytesIO()
        img.save(buf,format="JPEG",quality=90)

        st.download_button(
            "⬇ Download Passport Photo",
            buf.getvalue(),
            file_name="passport_photo.jpg",
            mime="image/jpeg"
        )
