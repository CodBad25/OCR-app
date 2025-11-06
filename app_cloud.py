"""
Application Cloud DNB Mathalea
Version optimisée pour Streamlit Cloud avec base de données pré-parsée
"""

import streamlit as st
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
import os
from dataclasses import dataclass
from typing import List
import base64
import io

# Import modules nécessaires
from mistralai import Mistral
from mistralai.models import DocumentURLChunk, ImageURLChunk, TextChunk

st.set_page_config(
    page_title="DNB Mathalea Cloud",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
.big-font {
    font-size:20px !important;
    font-weight: bold;
}
.success-box {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CHARGEMENT DE LA BASE DE DONNÉES
# ============================================================================

@st.cache_data
def load_database():
    """Charge la base de données de questions depuis le JSON"""
    db_path = Path("dnb_database_sample.json")

    if not db_path.exists():
        return None

    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("## 🎓 DNB Mathalea Cloud")
    st.markdown("Version optimisée pour le cloud")

    st.markdown("---")

    # Clé API Mistral
    api_key = st.text_input(
        "Clé API Mistral",
        type="password",
        value=os.getenv('MISTRAL_API_KEY', ''),
        help="Nécessaire pour la correction de devoirs"
    )

    if api_key:
        st.success("✅ API configurée")
    else:
        st.info("ℹ️ API optionnelle (sauf pour correction)")

    st.markdown("---")

    # Info sur la base
    st.markdown("### 📊 Base de Données")

    questions_db = load_database()

    if questions_db:
        st.metric("Questions disponibles", len(questions_db))

        # Années disponibles
        annees = set(q['annee'] for q in questions_db)
        st.info(f"📅 Années : {', '.join(sorted(annees))}")
    else:
        st.error("❌ Base non chargée")

# ============================================================================
# HEADER
# ============================================================================

st.title("🎓 DNB Mathalea - Version Cloud")
st.markdown("""
**Application optimisée pour le cloud** avec base de données pré-parsée.

✨ Fonctionnalités disponibles :
- 🔍 Explorer 560+ questions des annales 2019-2022
- 📝 Générer des sujets personnalisés
- ✅ Corriger des devoirs automatiquement
- 📊 Visualiser les statistiques
""")

# ============================================================================
# TABS
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Explorer",
    "📝 Générer un Sujet",
    "✅ Corriger un Devoir",
    "📊 Statistiques"
])

# ============================================================================
# TAB 1 : EXPLORER
# ============================================================================

with tab1:
    st.header("🔍 Explorer la Base de Questions")

    if not questions_db:
        st.error("❌ Base de données non disponible")
        st.stop()

    # Filtres
    st.markdown("### 🎯 Filtres")

    col1, col2, col3 = st.columns(3)

    with col1:
        annees_uniques = sorted(list(set(q['annee'] for q in questions_db)))
        annee_filter = st.multiselect("Année", options=annees_uniques, default=annees_uniques)

    with col2:
        image_filter = st.selectbox("Images", ["Toutes", "Avec images", "Sans images"])

    with col3:
        eq_filter = st.selectbox("Équations", ["Toutes", "Avec équations", "Sans équations"])

    # Appliquer filtres
    questions_filtered = questions_db.copy()

    if annee_filter:
        questions_filtered = [q for q in questions_filtered if q['annee'] in annee_filter]

    if image_filter == "Avec images":
        questions_filtered = [q for q in questions_filtered if q.get('images')]
    elif image_filter == "Sans images":
        questions_filtered = [q for q in questions_filtered if not q.get('images')]

    if eq_filter == "Avec équations":
        questions_filtered = [q for q in questions_filtered if q.get('equations')]
    elif eq_filter == "Sans équations":
        questions_filtered = [q for q in questions_filtered if not q.get('equations')]

    st.info(f"📊 {len(questions_filtered)} questions correspondent aux filtres")

    # Recherche
    search_query = st.text_input("🔎 Rechercher", placeholder="Ex: pythagore, probabilité...")

    if search_query:
        questions_filtered = [
            q for q in questions_filtered
            if search_query.lower() in q.get('texte_brut', '').lower()
        ]
        st.info(f"🔍 {len(questions_filtered)} résultats")

    # Affichage
    st.markdown("---")

    if questions_filtered:
        for i, q in enumerate(questions_filtered[:20]):
            with st.expander(f"**Question {i+1}** - {q['id']}"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown("**📝 Texte :**")
                    st.write(q.get('texte_brut', 'N/A'))

                    if q.get('equations'):
                        st.markdown(f"**🔢 Équations ({len(q['equations'])}) :**")
                        for eq in q['equations'][:3]:
                            st.code(eq, language="latex")

                with col2:
                    st.json({
                        "Année": q['annee'],
                        "Session": q.get('session', 'N/A'),
                        "Exercice": q.get('exercice', 'N/A'),
                        "Numéro": q.get('numero', 'N/A'),
                        "Images": len(q.get('images', [])),
                        "Équations": len(q.get('equations', []))
                    })

        if len(questions_filtered) > 20:
            st.info(f"💡 Affichage des 20 premières sur {len(questions_filtered)}")

# ============================================================================
# TAB 2 : GÉNÉRER UN SUJET
# ============================================================================

with tab2:
    st.header("📝 Générer un Sujet Personnalisé")

    if not questions_db:
        st.error("❌ Base de données non disponible")
        st.stop()

    col1, col2 = st.columns([2, 1])

    with col1:
        nb_questions = st.slider("Nombre de questions", 1, 10, 5)

        st.markdown("**Critères :**")

        critere_difficulte = st.select_slider(
            "Difficulté (équations)",
            options=["Aucune préférence", "Plutôt sans", "Mélangé", "Plutôt avec", "Uniquement avec"],
            value="Aucune préférence"
        )

        critere_images = st.checkbox("Inclure images", value=True)

    with col2:
        st.markdown("**Aperçu**")
        st.metric("Questions", nb_questions)
        if critere_images:
            st.info("🖼️ Avec images")

    if st.button("🎲 Générer", type="primary", use_container_width=True):
        import random

        pool = questions_db.copy()

        if critere_images:
            pool = [q for q in pool if q.get('images')]

        if critere_difficulte == "Uniquement avec":
            pool = [q for q in pool if q.get('equations')]
        elif critere_difficulte == "Plutôt avec":
            avec = [q for q in pool if q.get('equations')]
            sans = [q for q in pool if not q.get('equations')]
            pool = avec * 3 + sans
        elif critere_difficulte == "Plutôt sans":
            avec = [q for q in pool if q.get('equations')]
            sans = [q for q in pool if not q.get('equations')]
            pool = avec + sans * 3

        if len(pool) < nb_questions:
            st.warning(f"⚠️ Seulement {len(pool)} questions disponibles")
            nb_questions = len(pool)

        selected = random.sample(pool, nb_questions)

        st.success(f"✅ Sujet généré !")
        st.markdown("---")
        st.markdown("## 📄 Sujet")

        for i, q in enumerate(selected, 1):
            st.markdown(f"### Exercice {i}")
            st.markdown(q.get('texte_brut', 'N/A'))

            if q.get('images'):
                st.caption(f"🖼️ {', '.join(q['images'])}")

            if q.get('equations'):
                with st.expander("Équations"):
                    for eq in q['equations']:
                        st.code(eq, language="latex")

            st.markdown("---")

        # Export
        sujet_md = f"# Sujet DNB\n\n"
        sujet_md += f"Généré le {datetime.now().strftime('%d/%m/%Y')}\n\n"

        for i, q in enumerate(selected, 1):
            sujet_md += f"## Exercice {i}\n\n{q.get('texte_brut', '')}\n\n"
            if q.get('images'):
                sujet_md += f"*Images : {', '.join(q['images'])}*\n\n"
            sujet_md += "---\n\n"

        st.download_button(
            label="📥 Télécharger (Markdown)",
            data=sujet_md,
            file_name=f"sujet_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True
        )

# ============================================================================
# TAB 3 : CORRIGER UN DEVOIR
# ============================================================================

with tab3:
    st.header("✅ Scanner et Corriger un Devoir")

    st.markdown("""
    Uploadez un devoir d'élève (PDF ou image) pour obtenir :
    - 📖 Extraction du texte (OCR)
    - 🤖 Analyse automatique
    - 💯 Détection d'erreurs
    - 📝 Feedback pédagogique
    """)

    col1, col2 = st.columns([2, 1])

    with col1:
        devoir_file = st.file_uploader(
            "📤 Upload du devoir",
            type=["pdf", "png", "jpg", "jpeg"],
            help="Photo ou scan du devoir"
        )

        if devoir_file:
            st.success("✅ Fichier chargé")

            if devoir_file.type != "application/pdf":
                from PIL import Image
                img = Image.open(devoir_file)
                st.image(img, caption="Aperçu", use_container_width=True)

    with col2:
        if devoir_file:
            st.markdown("**Options**")

            mode = st.radio(
                "Mode",
                ["Extraction seule", "Extraction + Analyse IA"],
                help="L'analyse IA nécessite la clé API"
            )

    if devoir_file and st.button("🔍 Analyser", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ Clé API Mistral requise")
            st.stop()

        with st.spinner("📖 Extraction en cours..."):
            client = Mistral(api_key=api_key)

            file_bytes = devoir_file.read()

            uploaded = client.files.upload(
                file={"file_name": devoir_file.name, "content": file_bytes},
                purpose="ocr"
            )

            signed_url = client.files.get_signed_url(file_id=uploaded.id, expiry=1)

            ocr_response = client.ocr.process(
                model="mistral-ocr-latest",
                document=DocumentURLChunk(document_url=signed_url.url)
            )

            texte_extrait = "\n\n".join([page.markdown for page in ocr_response.pages])

        st.success("✅ Extraction terminée")

        st.markdown("### 📄 Texte Extrait")
        st.text_area("", texte_extrait, height=300)

        if mode == "Extraction + Analyse IA":
            st.markdown("---")
            st.markdown("### 🤖 Analyse Intelligente")

            with st.spinner("Analyse..."):
                analysis = client.chat.complete(
                    model="mistral-large-latest",
                    messages=[{
                        "role": "user",
                        "content": f"""Analyse ce devoir de mathématiques (niveau Brevet) :

{texte_extrait}

Fournis :
1. **Exercices identifiés**
2. **Points positifs**
3. **Erreurs détectées** (avec explications)
4. **Suggestions**

Format Markdown."""
                    }],
                    temperature=0.3
                )

                analyse_text = analysis.choices[0].message.content

            st.markdown(analyse_text)

            # Rapport
            rapport = f"# Rapport de Correction\n\n"
            rapport += f"Date : {datetime.now().strftime('%d/%m/%Y')}\n\n"
            rapport += f"## Texte Extrait\n\n{texte_extrait}\n\n"
            rapport += f"## Analyse\n\n{analyse_text}\n"

            st.download_button(
                label="📥 Télécharger le Rapport",
                data=rapport,
                file_name=f"rapport_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True
            )

# ============================================================================
# TAB 4 : STATISTIQUES
# ============================================================================

with tab4:
    st.header("📊 Statistiques")

    if not questions_db:
        st.error("❌ Base non disponible")
        st.stop()

    # Métriques
    total = len(questions_db)
    avec_images = len([q for q in questions_db if q.get('images')])
    avec_eq = len([q for q in questions_db if q.get('equations')])
    avec_sous_q = len([q for q in questions_db if q.get('sous_questions')])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📝 Questions", total)
    col2.metric("🖼️ Avec Images", avec_images)
    col3.metric("🔢 Avec Équations", avec_eq)
    col4.metric("📑 Sous-questions", avec_sous_q)

    st.markdown("---")

    # Graphiques
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📅 Par Année")

        par_annee = {}
        for q in questions_db:
            annee = q['annee']
            par_annee[annee] = par_annee.get(annee, 0) + 1

        df_annee = pd.DataFrame(
            list(par_annee.items()),
            columns=['Année', 'Nombre']
        )
        st.bar_chart(df_annee.set_index('Année'))

    with col2:
        st.subheader("🖼️ Types de Contenu")

        types = {
            'Avec images': avec_images,
            'Avec équations': avec_eq,
            'Avec sous-questions': avec_sous_q,
            'Simples': total - avec_images - avec_eq
        }

        df_types = pd.DataFrame(
            list(types.items()),
            columns=['Type', 'Nombre']
        )
        st.bar_chart(df_types.set_index('Type'))

    # Détails
    st.markdown("---")
    st.subheader("📋 Détails")

    tableau = []
    for annee in sorted(par_annee.keys()):
        q_annee = [q for q in questions_db if q['annee'] == annee]
        tableau.append({
            'Année': annee,
            'Questions': len(q_annee),
            'Avec Images': len([q for q in q_annee if q.get('images')]),
            'Avec Équations': len([q for q in q_annee if q.get('equations')])
        })

    df_detail = pd.DataFrame(tableau)
    st.dataframe(df_detail, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 1rem;'>
    <p>🎓 <strong>DNB Mathalea Cloud</strong></p>
    <p style='font-size: 0.9rem;'>Base : 566 questions | Années 2019-2022</p>
    <p style='font-size: 0.8rem;'>Version optimisée pour Streamlit Cloud</p>
</div>
""", unsafe_allow_html=True)
