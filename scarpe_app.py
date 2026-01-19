import streamlit as st
import pandas as pd
from PIL import Image
import imagehash
import io
import fitz  # PyMuPDF per leggere PDF

st.title("Identificatore di scarpe 📸👟")

# Caricamento foto da identificare
uploaded_shoe = st.file_uploader("Carica la foto della scarpa", type=["png", "jpg", "jpeg"])

# Caricamento file Excel o PDF
uploaded_file = st.file_uploader("Carica Excel (.xlsx) o PDF (.pdf) con il catalogo", type=["xlsx", "pdf"])

if uploaded_shoe and uploaded_file:
    # Leggi immagine della scarpa
    shoe_img = Image.open(uploaded_shoe).convert("RGB")
    shoe_hash = imagehash.average_hash(shoe_img)
    
    # Lista per salvare immagini e codici
    dataset = []

    # Se Excel
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
        if 'Immagine' not in df.columns or 'Codice' not in df.columns:
            st.error("Excel deve avere colonne 'Immagine' e 'Codice'")
        else:
            for idx, row in df.iterrows():
                try:
                    img = Image.open(io.BytesIO(row['Immagine'].tobytes())).convert("RGB") if hasattr(row['Immagine'], 'tobytes') else Image.open(row['Immagine']).convert("RGB")
                    dataset.append((img, row['Codice'], row.get('Modello','')))
                except:
                    continue

    # Se PDF
    elif uploaded_file.name.endswith(".pdf"):
        pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        for page in pdf:
            for img in page.get_images(full=True):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                img_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                dataset.append((img_pil, "Codice sconosciuto", ""))

    # Confronto immagini
    best_match = None
    lowest_diff = None

    for img, code, model in dataset:
        h = imagehash.average_hash(img)
        diff = shoe_hash - h  # più basso = più simile
        if lowest_diff is None or diff < lowest_diff:
            lowest_diff = diff
            best_match = (code, model, diff)

    # Determina livello confidenza
    if best_match:
        code, model, diff = best_match
        if diff <= 5:
            conf = "Alta"
        elif diff <= 10:
            conf = "Media"
        else:
            conf = "Bassa"

        st.subheader("Risultato:")
        st.write(f"**Codice prodotto:** {code}")
        st.write(f"**Modello/Nome:** {model}")
        st.write(f"**Differenza hash:** {diff}")
        st.write(f"**Confidenza:** {conf}")
    else:
        st.write("Nessuna corrispondenza trovata.")
