import streamlit as st
from mistralai import Mistral
import base64
import io
from PIL import Image
import requests

st.set_page_config(
    page_title="Application OCR avec Mistral",
    page_icon="🔍",
    layout="wide"
)

def get_download_link(content, filename, text):
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'

def display_pdf(file_content=None, file_url=None):
    if file_url:
        return f'<iframe src="{file_url}" width="100%" height="600" type="application/pdf"></iframe>'
    elif file_content:
        base64_pdf = base64.b64encode(file_content).decode('utf-8')
        return f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    return None

st.title("🔍 Application OCR avec Mistral")
st.markdown("""
Cette application utilise l'API Mistral OCR pour extraire du texte à partir d'images et de PDF.
Fournissez simplement votre clé API Mistral et commencez à analyser vos documents !
""")

# Récupérer la clé API depuis les secrets ou l'interface utilisateur
api_key = st.secrets.get("MISTRAL_API_KEY", None)
if not api_key:
    with st.expander("⚙️ Configuration", expanded=True):
        api_key = st.text_input("Entrez votre clé API Mistral", type="password")
        if api_key:
            st.success("Clé API configurée avec succès!")

if 'ocr_result' not in st.session_state:
    st.session_state.ocr_result = None
if 'file_preview' not in st.session_state:
    st.session_state.file_preview = None
if 'file_content' not in st.session_state:
    st.session_state.file_content = None
if 'is_pdf' not in st.session_state:
    st.session_state.is_pdf = False

file_type = st.radio("Sélectionnez le type de fichier :", ["PDF", "Image"])
source_type = st.radio("Source :", ["URL", "Upload local"])

if source_type == "URL":
    file_url = st.text_input(f"Entrez l'URL du {'PDF' if file_type == 'PDF' else 'image'}")
    file_path = None
else:
    if file_type == "PDF":
        uploaded_file = st.file_uploader("Chargez un PDF", type=["pdf"])
    else:
        uploaded_file = st.file_uploader("Chargez une image", type=["png", "jpg", "jpeg"])
    file_url = None
    file_path = uploaded_file

if st.button("Traiter", type="primary", use_container_width=True):
    if not api_key:
        st.error("❌ Veuillez entrer une clé API Mistral valide")
        st.stop()
    if (source_type == "URL" and not file_url) or (source_type == "Upload local" and not file_path):
        st.error("❌ Veuillez fournir un fichier ou une URL valide")
        st.stop()

    client = Mistral(api_key=api_key)

    with st.spinner("🔄 Traitement du document..."):
        try:
            # Déterminer le type MIME
            if file_type == "PDF":
                mime_type = "application/pdf"
            else:
                mime_type = "image/jpeg"  # Par défaut

            # Construire le message pour l'API
            if source_type == "URL" and file_url:
                # Utiliser l'URL directement
                image_content = {
                    "type": "image_url",
                    "image_url": file_url
                }
                st.session_state.file_preview = file_url
                st.session_state.is_pdf = file_type == "PDF"
                st.session_state.file_content = None
            else:
                # Encoder le fichier en base64
                file_bytes = file_path.read()
                st.session_state.file_content = file_bytes
                st.session_state.is_pdf = file_type == "PDF"
                base64_encoded = base64.b64encode(file_bytes).decode('utf-8')

                # Déterminer le type MIME précis pour les images uploadées
                if file_type == "Image":
                    if file_path.name.lower().endswith('.png'):
                        mime_type = "image/png"
                    elif file_path.name.lower().endswith(('.jpg', '.jpeg')):
                        mime_type = "image/jpeg"

                image_content = {
                    "type": "image_url",
                    "image_url": f"data:{mime_type};base64,{base64_encoded}"
                }

            # Créer le message avec l'image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extrais tout le texte de ce document. Fournis uniquement le texte extrait, sans commentaires ni formatage supplémentaire."
                        },
                        image_content
                    ]
                }
            ]

            # Appeler l'API Mistral avec le modèle vision
            response = client.chat.complete(
                model="pixtral-12b-2409",
                messages=messages
            )

            st.session_state.ocr_result = response.choices[0].message.content
            st.success("✅ Traitement OCR terminé avec succès !")
        except Exception as e:
            st.error(f"❌ Erreur lors du traitement: {str(e)}")
            st.stop()

if st.session_state.ocr_result:
    st.markdown("---")
    st.subheader("📄 Résultats")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Aperçu du document")
        if st.session_state.is_pdf:
            if st.session_state.file_preview:
                st.markdown(display_pdf(file_url=st.session_state.file_preview), unsafe_allow_html=True)
            elif st.session_state.file_content:
                st.markdown(display_pdf(file_content=st.session_state.file_content), unsafe_allow_html=True)
        else:
            if st.session_state.file_preview:
                st.image(st.session_state.file_preview)
            elif st.session_state.file_content:
                image = Image.open(io.BytesIO(st.session_state.file_content))
                st.image(image, use_column_width=True)
    with col2:
        st.subheader("🔍 Résultat OCR")
        st.markdown(st.session_state.ocr_result)
        st.markdown(get_download_link(st.session_state.ocr_result, "resultat_ocr.txt", "📥 Télécharger le résultat"), unsafe_allow_html=True)