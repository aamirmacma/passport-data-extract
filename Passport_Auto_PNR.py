import streamlit as st
from passporteye import read_mrz
from PIL import Image
from datetime import datetime
import pytesseract

# Tesseract Path (Check karein agar aapka path yahi hai)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.set_page_config(page_title="Amadeus Passport Extractor", layout="centered")

st.title("✈️ Amadeus Passport Data Extractor")
st.write("Passport ki photo upload karein aur Amadeus entries hasil karein.")

def format_date(date_str):
    try:
        d = datetime.strptime(date_str, '%y%m%d')
        return d.strftime('%d%b%y').upper()
    except:
        return date_str

def get_title(gender, dob_raw):
    birth_date = datetime.strptime(dob_raw, '%y%m%d')
    today = datetime.now()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    if age < 2: return "INF", "MI" if gender == 'M' else "FI"
    if age < 12: return ("MSTR" if gender == 'M' else "MISS"), gender
    return ("MR" if gender == 'M' else "MRS"), gender

# File Upload Button
uploaded_file = st.file_uploader("Passport Photo Select Karein...", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Passport", width=300)
    
    with st.spinner('Data nikal raha hoon...'):
        # MRZ Read karna
        mrz = read_mrz(uploaded_file)
        
        if mrz:
            d = mrz.to_dict()
            
            # Extracting Data
            surname = d.get('surname', '').upper()
            given_name = d.get('names', '').upper()
            pp_no = d.get('number', '').upper()
            nat = d.get('country', '').upper()
            dob = d.get('date_of_birth', '')
            exp = d.get('expiration_date', '')
            gender = d.get('sex', 'M').upper()
            
            dob_fmt = format_date(dob)
            exp_fmt = format_date(exp)
            title, g_code = get_title(gender, dob)

            # --- AMADEUS ENTRIES ---
            nm1_entry = f"NM1{surname}/{given_name} {title}"
            docs_entry = f"SRDOCS YY HK1-P-{nat}-{pp_no}-{nat}-{dob_fmt}-{g_code}-{exp_fmt}-{surname}-{given_name}-H/P1"

            st.success("Data Extract Ho Gaya!")

            # Name Entry Box
            st.subheader("1. Name Entry (NM1)")
            st.code(nm1_entry, language="bash")
            
            # Passport Entry Box
            st.subheader("2. Passport Details (SRDOCS)")
            st.code(docs_entry, language="bash")
            
            st.info("Upar diye gaye codes ko copy karke Amadeus mein paste karein.")
        else:
            st.error("Ghalti: Passport saaf nahi hai ya MRZ lines nahi mil rahi hain.")
