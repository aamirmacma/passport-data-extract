import streamlit as st
from passporteye import read_mrz
import datetime
import os
import cv2
import uuid

def mrz_date_fix(d):
    if not d or len(str(d)) < 6:
        return None

    d=str(d)
    y=int(d[:2])
    m=int(d[2:4])
    da=int(d[4:6])

    if y > datetime.datetime.now().year % 100:
        y+=1900
    else:
        y+=2000

    return datetime.datetime(y,m,da)


def calculate_age(d):
    birth = mrz_date_fix(d)
    if birth is None:
        return 0,""

    today=datetime.datetime.today()
    age=today.year-birth.year
    return age,birth.strftime("%d%b%y").upper()


def run():

    st.title("Passport Auto PNR")

    files = st.file_uploader(
        "Upload Passport Images",
        type=["jpg","jpeg","png"],
        accept_multiple_files=True
    )

    if not files:
        return

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

        age,dob=calculate_age(d.get("date_of_birth"))

        st.write("Passport:",d.get("number"))
        st.write("DOB:",dob)

        os.remove(temp)
