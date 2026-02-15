import streamlit as st
from passporteye import read_mrz
import datetime
import pytesseract
import os
import cv2
import uuid
import re
import streamlit.components.v1 as components

# ================= TESSERACT =================
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

st.set_page_config(page_title="Amadeus Auto PNR Builder", layout="wide")

# ================= HEADER =================
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

def passenger_title(age, gender, dob):
    if age >= 12:
        return "MR" if gender=="M" else "MRS"
    elif age >= 2:
        return f"MSTR(CHD/{dob})" if gender=="M" else f"MISS(CHD/{dob})"
    else:
        return "INF"

def parse_mrz_names(surname,names):
    surname=surname.replace("<","").strip().upper()
    names=names.replace("<"," ")
    names=" ".join(names.split())
    return surname,names

# ================= OCR EXTRA =================
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

        mrz=read_mrz(temp)

        if mrz:

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

            title=passenger_title(age,gender,dob)

            father,pob,doi,cnic=extract_extra_fields(temp)

            passengers.append({
                "surname":surname,
                "given":names,
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
nm1_lines=[]
docs_lines=[]

if passengers:

    st.subheader("Extracted Passport Details")

    for i,p in enumerate(passengers,1):

        st.markdown('<div class="passport-box">',unsafe_allow_html=True)
        st.write("Surname:",p["surname"])
        st.write("Given Name:",p["given"])
        st.write("Title:",p["title"])
        st.write("Passport:",p["passport"])
        st.write("DOB:",p["dob"])
        st.write("Expiry:",p["exp"])
        st.write("Father/Husband Name:",p["father"])
        st.write("Place of Birth:",p["pob"])
        st.write("Date of Issue:",p["doi"])
        st.write("CNIC:",p["cnic"])
        st.markdown('</div>',unsafe_allow_html=True)

    pax=1
    for p in passengers:

        nm1_lines.append(
            f"NM1{p['surname']}/{p['given']} {p['title']}"
        )

        docs_lines.append(
            f"SRDOCS SV HK1-P-{p['country']}-{p['passport']}-"
            f"{p['country']}-{p['dob']}-{p['gender']}-"
            f"{p['exp']}-{p['surname']}-{p['given'].replace(' ','-')}-H/P{pax}"
        )
        pax+=1

    export_text="\n".join(nm1_lines)+"\n\n"+"\n".join(docs_lines)

    st.markdown('<div class="nm1-box">',unsafe_allow_html=True)
    st.subheader("NM1 Entries")
    st.code("\n".join(nm1_lines))
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="docs-box">',unsafe_allow_html=True)
    st.subheader("SRDOCS Entries")
    st.code("\n".join(docs_lines))
    st.markdown('</div>',unsafe_allow_html=True)

    st.download_button(
        "⬇ Download Amadeus PNR (TXT)",
        data=export_text,
        file_name="amadeus_pnr.txt",
        mime="text/plain"
    )
