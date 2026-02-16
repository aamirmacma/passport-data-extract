import streamlit as st
from passporteye import read_mrz
import datetime
import uuid
import os
import cv2

st.set_page_config(layout="wide")

st.markdown("""
<div style="background:#1c7ed6;padding:12px;border-radius:10px;color:white">
<h3>✈️ Amadeus Auto PNR Builder</h3>
</div>
""", unsafe_allow_html=True)


def mrz_date_fix(d):
    if not d or len(d) < 6:
        return None
    y=int(d[:2])
    m=int(d[2:4])
    da=int(d[4:6])

    if y > datetime.datetime.now().year % 100:
        y += 1900
    else:
        y += 2000

    return datetime.datetime(y,m,da)


def safe_date(d):
    dt = mrz_date_fix(d)
    if not dt:
        return ""
    return dt.strftime("%d%b%y").upper()


files = st.file_uploader(
    "Upload Passport Images",
    type=["jpg","jpeg","png"],
    accept_multiple_files=True
)

seen=set()
passengers=[]

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
            os.remove(temp)
            continue

        d=mrz.to_dict()
        passport=d.get("number","")

        if passport in seen:
            st.warning(f"Duplicate skipped: {passport}")
            os.remove(temp)
            continue

        seen.add(passport)

        passengers.append({
            "surname":d.get("surname",""),
            "names":d.get("names","").replace("<"," "),
            "passport":passport,
            "dob":safe_date(d.get("date_of_birth")),
            "exp":safe_date(d.get("expiration_date")),
            "gender":d.get("sex","")
        })

        os.remove(temp)


if passengers:

    st.subheader("Extracted Passport Details")

    for i,p in enumerate(passengers,1):
        st.write(f"Passenger {i}: {p['surname']} {p['names']}")
        st.write("Passport:",p["passport"])
        st.write("DOB:",p["dob"])
        st.write("Expiry:",p["exp"])
        st.divider()
