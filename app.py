import streamlit as st
from passporteye import read_mrz
import datetime
import pytesseract
import os
import cv2
import uuid
import re
import numpy as np
from PIL import Image
import io

# ================= PAGE =================
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
.header-title{font-size:26px;font-weight:700;color:white;}
.header-dev{
 background:white;color:#0b5394;
 padding:6px 14px;border-radius:20px;
 font-size:14px;font-weight:600;
}
.box{
 background:white;padding:15px;
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

# ================= SAFE DATE =================
def mrz_date_fix(d):
    try:
        if not d or len(str(d)) < 6:
            return datetime.datetime(2000,1,1)

        d=str(d)
        y=int(d[:2])
        m=int(d[2:4])
        da=int(d[4:6])

        if y > datetime.datetime.now().year % 100:
            y+=1900
        else:
            y+=2000

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
def passenger_title(age,gender):
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
        if len(w)<=1: continue
        if len(set(w))==1: continue
        if w.count("K")>len(w)*0.5: continue
        clean.append(w)
    return surname," ".join(clean)

# ================= FAST MRZ =================
def read_mrz_fast(path):

    img=cv2.imread(path)
    if img is None:
        return None

    h,w=img.shape[:2]

    # bottom MRZ area crop
    mrz_crop=img[int(h*0.65):h,0:w]

    temp=path+"_mrz.jpg"
    cv2.imwrite(temp,mrz_crop)

    try:
        mrz=read_mrz(temp)
    except:
        mrz=None

    if os.path.exists(temp):
        os.remove(temp)

    return mrz

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

        if "PLACE OF BIRTH" in line:
            pob=line

        if "ISSUE" in line:
            doi=line

        m=re.search(r"\d{5}-\d{7}-\d",line)
        if m:
            cnic=m.group()

    return father,pob,doi,cnic

# ================= FAST PHOTO =================
def enhance_photo_fast(uploaded_file):

    file_bytes=np.asarray(bytearray(uploaded_file.read()),dtype=np.uint8)
    img=cv2.imdecode(file_bytes,1)

    img=cv2.resize(img,(140,180))

    # fast enhance
    img=cv2.convertScaleAbs(img,alpha=1.15,beta=10)

    _,buffer=cv2.imencode(".jpg",img,[int(cv2.IMWRITE_JPEG_QUALITY),85])

    return img,buffer.tobytes()

# ================= TABS =================
tab1, tab2 = st.tabs(["📘 Passport Auto PNR", "📷 Passport Photo Maker"])

# =========================================================
# ================= TAB 1 PASSPORT ========================
# =========================================================
with tab1:

    files = st.file_uploader(
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

            # ---------- TRY NORMAL MRZ ----------
            mrz=None
            try:
                mrz=read_mrz(temp)
            except:
                pass

            # ---------- TRY BOTTOM MRZ ----------
            if not mrz:
                img=cv2.imread(temp)
                if img is not None:
                    h,w=img.shape[:2]
                    crop=img[int(h*0.65):h,0:w]
                    cv2.imwrite(temp+"_mrz.jpg",crop)
                    try:
                        mrz=read_mrz(temp+"_mrz.jpg")
                    except:
                        pass

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

            title=passenger_title(age,gender)

            father,pob,doi,cnic=extract_extra_fields(temp)

            passengers.append({
                "surname":surname,
                "names":names,
                "passport":passport,
                "dob":dob,
                "exp":exp,
                "gender":gender,
                "country":country,
                "title":title,
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

            st.markdown('<div class="box">',unsafe_allow_html=True)

            st.write(f"Passenger {i}")
            st.write("Surname:",p["surname"])
            st.write("Given Name:",p["names"])
            st.write("Title:",p["title"])
            st.write("Passport:",p["passport"])
            st.write("DOB:",p["dob"])
            st.write("Expiry:",p["exp"])
            st.write("Father/Husband:",p["father"])
            st.write("Place of Birth:",p["pob"])
            st.write("CNIC:",p["cnic"])

            st.markdown('</div>',unsafe_allow_html=True)

        pax=1
        for p in passengers:

            nm1_lines.append(
                f"NM1{p['surname']}/{p['names']} {p['title']}"
            )

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


# =========================================================
# ================= TAB 2 PHOTO ===========================
# =========================================================
with tab2:

    photo=st.file_uploader(
        "Upload Passport Photo",
        type=["jpg","jpeg","png"]
    )

    if photo:

        img,buf=enhance_photo_fast(photo)

        st.image(img[:,:,::-1],caption="Enhanced Passport Photo")

        st.download_button(
            "⬇ Download Passport Photo",
            data=buf,
            file_name="passport_photo.jpg",
            mime="image/jpeg"
        )

