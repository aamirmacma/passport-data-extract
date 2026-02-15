import streamlit as st
from passporteye import read_mrz
import datetime
import numpy as np
import cv2
import re

# ================= PAGE =================
st.set_page_config(page_title="Amadeus Auto PNR Builder", layout="wide")

st.markdown("""
<style>
.main-title{
    font-size:30px;
    font-weight:700;
    color:#0b5394;
}
.box{
    background:#f7f9fc;
    padding:15px;
    border-radius:10px;
    margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">✈️ Amadeus Auto PNR Builder</div>', unsafe_allow_html=True)
st.caption("Developed by Aamir Khan")


# ================= NAME CLEAN =================
def clean_name(txt):

    if not txt:
        return ""

    txt = txt.replace("<", " ")
    txt = re.sub(r'[^A-Z ]', '', txt.upper())
    txt = " ".join(txt.split())

    # remove KKKKK OCR garbage
    words=[]
    for w in txt.split():
        w=re.sub(r'(.)\1{2,}', r'\1', w)
        words.append(w)

    return " ".join(words)


# ================= DATE =================
def fix_mrz_date(d):

    try:
        y=int(d[:2])
        m=int(d[2:4])
        day=int(d[4:6])

        year = 1900+y if y>30 else 2000+y
        return datetime.date(year,m,day)
    except:
        return None


def calculate_age(d):

    birth=fix_mrz_date(d)
    if not birth:
        return None,""

    today=datetime.date.today()
    age=today.year-birth.year-(
        (today.month,today.day)<(birth.month,birth.day)
    )

    return age,birth.strftime("%d%b%y").upper()


# ================= TITLE =================
def get_title(age, gender):

    if age is None:
        return "MR"

    if age < 2:
        return "INF"

    if age < 12:
        return "CHD"

    if gender == "F":
        return "MRS"

    return "MR"


# ================= UPLOAD =================
files = st.file_uploader(
    "Upload Passport Images",
    type=["jpg","jpeg","png"],
    accept_multiple_files=True
)

if files:

    passengers=[]
    seen=set()

    for f in files:

        # -------- FIXED IMAGE LOAD (CLOUD SAFE) --------
        file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)

        if img is None:
            st.warning("Image not readable")
            continue

        try:
            mrz = read_mrz(img)
        except:
            mrz = None

        if not mrz:
            st.warning("MRZ not detected")
            continue

        d = mrz.to_dict()

        surname = clean_name(d.get("surname"))
        given = clean_name(d.get("names"))

        passport = d.get("number")
        dob_raw = d.get("date_of_birth")
        exp_raw = d.get("expiration_date")
        gender = d.get("sex")

        age, dob = calculate_age(dob_raw)

        expiry=""
        exp = fix_mrz_date(exp_raw)
        if exp:
            expiry = exp.strftime("%d%b%y").upper()

        title = get_title(age, gender)

        key = passport + dob
        if key in seen:
            continue
        seen.add(key)

        passengers.append({
            "surname":surname,
            "given":given,
            "title":title,
            "passport":passport,
            "dob":dob,
            "expiry":expiry
        })

    # ================= DISPLAY =================
    st.subheader("Extracted Passport Details")

    for i,p in enumerate(passengers,1):

        st.markdown(f"""
        <div class="box">
        <b>Passenger {i}: {p['surname']} {p['given']}</b><br><br>

        Surname: {p['surname']}<br>
        Given Name: {p['given']}<br>
        Title: {p['title']}<br>
        Passport: {p['passport']}<br>
        DOB: {p['dob']}<br>
        Expiry: {p['expiry']}
        </div>
        """, unsafe_allow_html=True)

    # ================= NM1 =================
    st.subheader("NM1 Entries")

    nm1=[]
    for p in passengers:
        nm1.append(f"NM1{p['surname']}/{p['given']} {p['title']}")

    st.code("\n".join(nm1))

    # ================= SRDOCS =================
    st.subheader("SRDOCS Entries")

    docs=[]
    for i,p in enumerate(passengers,1):

        line=(
            f"SRDOCS SV HK1-P-PK-{p['passport']}-PK-"
            f"{p['dob']}-{p['title'][0]}-{p['expiry']}-"
            f"{p['surname']}-{p['given'].replace(' ','-')}-H/P{i}"
        )

        docs.append(line)

    st.code("\n".join(docs))
