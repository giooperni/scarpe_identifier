import streamlit as st
from PIL import Image
import imagehash
import os

st.title("Identificatore di scarpe 📸👟")

# Carica la foto da identificare
uploaded_shoe = st.file_uploader("Carica la foto della scarpa", type=["png", "jpg", "jpeg"])

# Percorso cartella catalogo immagini
CATALOG_PATH = "catalogo_scarpe"  # metti qui il nome della cartella con le immagini

def get_confidence(diff):
    if diff <= 5:
        return "Alta"
    elif diff <= 10:
        return "Media"
    else:
        return "Bassa"

if uploaded_shoe:
    shoe_img = Image.open(uploaded_shoe).convert("RGB")
    shoe_hash = imagehash.average_hash(shoe_img)

    # Carica tutte le immagini del catalogo
    dataset = []
    for file in os.listdir(CATALOG_PATH):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(CATALOG_PATH, file)
            img = Image.open(img_path).convert("RGB")
            
            # Estrai codice e modello dal nome del file
            name = os.path.splitext(file)[0]  # togli estensione
            parts = name.split("_")
            code = parts[0]
            model = "_".join(parts[1:]) if len(parts) > 1 else ""
            
            dataset.append((img, code, model))

    # Confronto immagini e calcolo differenze hash
    matches = []
    for img, code, model in dataset:
        diff = shoe_hash - imagehash.average_hash(img)
        matches.append((code, model, diff))

    # Ordina per differenza (più basso = più simile)
    matches.sort(key=lambda x: x[2])

    # Mostra top 3 match
    st.subheader("Top 3 match:")
    for i, (code, model, diff) in enumerate(matches[:3], start=1):
        conf = get_confidence(diff)
        st.write(f"**{i}. Codice:** {code}  |  **Modello:** {model}  |  **Differenza hash:** {diff}  |  **Confidenza:** {conf}")
