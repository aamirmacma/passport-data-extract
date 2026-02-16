import streamlit as st
from passporteye import read_mrz
import datetime
import pytesseract
import os
import cv2
import uuid
import re
from PIL import Image
import io

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
</style>

<div class="header-bar">
    <div class="header-title">✈️ Amadeus Auto PNR Builder</div>
    <div class="header-dev">Developed by Aamir Khan</div>
</div>
""", unsafe_allow_html=True)

# ================= TABS =================
tab1, tab2, tab3 = st.tabs(
    ["🛂 Passport Auto PNR",
     "📷 Passport Photo Maker",
     "🪪 Passport Size Maker"]
)

# =========================================================
# ================= FUNCTIONS =============================
# =========================================================

def mrz_date_fix(d):
    if not d or len(d) < 6:
        return datetime.datetime(2000,1,1)
    try:
        y=int(d[:2]); m=int(d[2:4]); da=int(d[4:6])
    except:
        return datetime.datetime(2000,1,1)

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
    age=today.year-birth.year-((today.month,today.day)<(birth.month,birth.day))
    return age,birth.strftime("%d%b%y").upper()

def passenger_title(age,gender,dob):
    if age>=12:
        return "MR" if gender=="M" else "MRS"
    elif age>=2:
        return "CHD"
    else:
        return "INF"

def parse_mrz_names(surname,names):
    surname=surname.replace("<","").strip().upper()
    names=names.replace("<"," ").upper()

    clean=[]
    for w in names.split():
        if len(w)<=1: continue
        if len(set(w))==1: continue
        clean.append(w)

    clean=list(dict.fromkeys(clean))
    return surname," ".join(clean)

def fast_mrz_read(path):
    img=cv2.imread(path)
    if img is None:
        return None

    h,w=img.shape[:2]
    crop=img[int(h*0.65):h,0:w]

    temp=f"mrz_{uuid.uuid4().hex}.jpg"
    cv2.imwrite(temp,crop)

    try:
        mrz=read_mrz(temp)
    except:
        mrz=None

    os.remove(temp)
    return mrz

# =========================================================
# ================= TAB 1 : PASSPORT ======================
# =========================================================

with tab1:

    st.subheader("Upload Passport Images")

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

            mrz=fast_mrz_read(temp)

            if not mrz:
                st.warning("MRZ not detected")
                os.remove(temp)
                continue

            d=mrz.to_dict()
            passport=d.get("number","")

            if passport in seen:
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

            passengers.append({
                "surname":surname,
                "names":names,
                "passport":passport,
                "dob":dob,
                "exp":exp,
                "gender":gender,
                "country":country,
                "age":age
            })

            os.remove(temp)

    if passengers:

        nm1=[]
        docs=[]

        st.subheader("Extracted Passport Details")

        for i,p in enumerate(passengers,1):

            st.write(f"Passenger {i}")
            st.write("Surname:",p["surname"])
            st.write("Given Name:",p["names"])
            st.write("Passport:",p["passport"])
            st.write("DOB:",p["dob"])
            st.write("Expiry:",p["exp"])
            st.divider()

        for i,p in enumerate(passengers,1):

            title=passenger_title(p["age"],p["gender"],p["dob"])

            nm1.append(f"NM1{p['surname']}/{p['names']} {title}")

            docs.append(
                f"SRDOCS SV HK1-P-{p['country']}-{p['passport']}-"
                f"{p['country']}-{p['dob']}-{p['gender']}-"
                f"{p['exp']}-{p['surname']}-{p['names'].replace(' ','-')}-H/P{i}"
            )

        st.subheader("NM1 Entries")
        st.code("\n".join(nm1))

        st.subheader("SRDOCS Entries")
        st.code("\n".join(docs))


# =========================================================
# ================= TAB 2 : PHOTO MAKER ===================
# =========================================================

with tab2:

    st.subheader("Passport Photo Maker")

    photo=st.file_uploader("Upload Photo",type=["jpg","jpeg","png"])

    if photo:

        img=Image.open(photo).convert("RGB")
        img=img.resize((300,400))

        st.image(img)

        buf=io.BytesIO()
        img.save(buf,format="JPEG",quality=90)

        st.download_button(
            "Download Photo",
            buf.getvalue(),
            "passport_photo.jpg",
            "image/jpeg"
        )

# =========================================================
# ================= TAB 3 : HAJI PHOTO ====================
# =========================================================

with tab3:

    st.subheader("Haji Passport Size Maker")

    st.info("""
NOTE:
Haji Passport should be in JPG format.
Only one file allowed.
Maximum file size 500KB.
""")

    photo=st.file_uploader(
        "Upload Haji Photo (JPG only)",
        type=["jpg","jpeg"]
    )

    if photo:

        img=Image.open(photo).convert("RGB")

        img=img.resize((165,185))

        buf=io.BytesIO()
        img.save(buf,format="JPEG",quality=85,optimize=True)

        st.image(img)

        st.download_button(
            "Download Haji Photo",
            buf.getvalue(),
            "haji_passport.jpg",
            "image/jpeg"
        )
