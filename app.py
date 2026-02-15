import streamlit as st
from passporteye import read_mrz
import datetime
import pytesseract
import os
import cv2
import uuid
import re
import streamlit.components.v1 as components

# ---------------- TESSERACT AUTO DETECT ----------------
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

st.set_page_config(page_title="Amadeus Auto PNR Builder", layout="wide")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
.main-title {
    font-size:30px;
    font-weight:700;
    color:#0b5394;
    margin-bottom:0px;
}
.dev-name {
    font-size:14px;
    color:#6b7280;
    margin-top:-8px;
    margin-bottom:20px;
}
.box {
    background:#f7f9fc;
    padding:15px;
    border-radius:10px;
    margin-bottom:10px;
    border:1px solid #e3e8ef;
}
.nm1 {
    background:#eef7ff;
    padding:15px;
    border-left:5px solid #1c7ed6;
    border-radius:10px;
}
.docs {
    background:#eefaf3;
    padding:15px;
    border-left:5px solid #2f9e44;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# -------- HEADER --------
st.markdown(
    '<div class="main-title">✈️ Amadeus Auto PNR Builder</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="dev-name">Developed by Aamir Khan</div>',
    unsafe_allow_html=True
)

# ---------------- DATE FUNCTIONS ----------------
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

# ---------------- TITLE ----------------
def passenger_title(age,gender,dob):
    if age>=12:
        return "MR" if gender=="M" else "MRS"
    elif age>=2:
        return f"MSTR(CHD/{dob})" if gender=="M" else f"MISS(CHD/{dob})"
    else:
        return "INF"

# ---------------- NAME CLEAN ----------------
def parse_mrz_names(surname,names):
    surname=surname.replace("<","").strip().upper()
    names=names.replace("<"," ")
    names=" ".join(names.split())

    clean=[]
    for w in names.split():
        if len(w)<=1: continue
        if len(set(w))==1: continue
        if w.count("K")>len(w)*0.5: continue
        if not re.search(r"[AEIOU]",w): continue
        clean.append(w)

    return surname," ".join(clean)

# ---------------- OCR EXTRA ----------------
def extract_extra_fields(path):

    img=cv2.imread(path)
    if img is None:
        return "","","",""

    h,w=img.shape[:2]

    left=img[int(h*0.35):h,0:int(w*0.6)]
    right=img[int(h*0.35):h,int(w*0.55):w]

    left_text=pytesseract.image_to_string(left)
    right_text=pytesseract.image_to_string(right)

    father=""; pob=""; doi=""; cnic=""

    lines=[l.strip() for l in left_text.split("\n") if l.strip()]

    for i,line in enumerate(lines):
        l=line.lower()
        if "father name" in l or "husband name" in l:
            if i+1<len(lines): father=lines[i+1]
        if "place of birth" in l:
            if i+1<len(lines): pob=lines[i+1]
        if "date of issue" in l:
            if i+1<len(lines): doi=lines[i+1]

    for line in right_text.split("\n"):
        m=re.search(r"\d{5}-\d{7}-\d",line)
        if m: cnic=m.group()

    return father,pob,doi,cnic

# ---------------- ROTATE ----------------
def auto_rotate(path):
    img=cv2.imread(path)
    if img is None: return
    h,w=img.shape[:2]
    if h>w:
        img=cv2.rotate(img,cv2.ROTATE_90_CLOCKWISE)
    cv2.imwrite(path,img)

# ---------------- UPLOAD ----------------
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

# ---------------- OUTPUT ----------------
nm1_lines=[]
docs_lines=[]

if passengers:

    st.subheader("Extracted Passport Details")

    for i,p in enumerate(passengers,1):

        st.markdown('<div class="box">',unsafe_allow_html=True)
        st.write(f"Passenger {i}: {p['surname']} {p['names']}")
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

        title=passenger_title(p["age"],p["gender"],p["dob"])

        nm1_lines.append(f"NM1{p['surname']}/{p['names']} {title}")

        docs_lines.append(
            f"SRDOCS SV HK1-P-{p['country']}-{p['passport']}-"
            f"{p['country']}-{p['dob']}-{p['gender']}-"
            f"{p['exp']}-{p['surname']}-{p['names'].replace(' ','-')}-H/P{pax}"
        )
        pax+=1

    export_text="\n".join(nm1_lines)+"\n\n"+"\n".join(docs_lines)

    st.markdown('<div class="nm1">',unsafe_allow_html=True)
    st.subheader("NM1 Entries")
    st.code("\n".join(nm1_lines))
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="docs">',unsafe_allow_html=True)
    st.subheader("SRDOCS Entries")
    st.code("\n".join(docs_lines))
    st.markdown('</div>',unsafe_allow_html=True)

    st.download_button(
        "⬇ Download Amadeus PNR (TXT)",
        data=export_text,
        file_name="amadeus_pnr.txt",
        mime="text/plain"
    )

    components.html(f"""
    <button style="background:#1c7ed6;color:white;
    padding:10px 18px;border:none;border-radius:6px;
    font-size:16px;cursor:pointer;"
    onclick="navigator.clipboard.writeText(`{export_text}`)">
    📋 Copy PNR to Clipboard
    </button>
    """, height=60)
