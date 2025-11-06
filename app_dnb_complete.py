"""
Application complète DNB Mathalea
Combine parsing TEX, OCR, analyse intelligente et outils pédagogiques
"""

import streamlit as st
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
import os

# Import des modules
from parser_dnb import DNBParser, Question
from image_analyzer import ImageAnalyzer

st.set_page_config(
    page_title="DNB Mathalea - Plateforme Complète",
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
.info-box {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #d1ecf1;
    border: 1px solid #bee5eb;
}
</style>
""", unsafe_allow_html=True)

# Initialisation session state
if 'parser' not in st.session_state:
    st.session_state.parser = DNBParser()

if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None

if 'questions_db' not in st.session_state:
    st.session_state.questions_db = []

if 'current_step' not in st.session_state:
    st.session_state.current_step = 'config'

# =============================================================================
# SIDEBAR - Configuration
# =============================================================================

with st.sidebar:
    st.image("https://via.placeholder.com/200x80/4CAF50/FFFFFF?text=DNB+Mathalea", use_container_width=True)

    st.markdown("## ⚙️ Configuration")

    # Clé API Mistral
    api_key = st.text_input(
        "Clé API Mistral",
        type="password",
        value=os.getenv('MISTRAL_API_KEY', ''),
        help="Nécessaire pour l'OCR et l'analyse intelligente"
    )

    if api_key:
        if not st.session_state.analyzer:
            st.session_state.analyzer = ImageAnalyzer(api_key)
        st.success("✅ API configurée")
    else:
        st.warning("⚠️ Clé API requise pour OCR")

    st.markdown("---")

    # Chemin repository DNB
    dnb_path = st.text_input(
        "Chemin mathalea/dnb",
        value="/tmp/dnb",
        help="Chemin vers le repository cloné"
    )

    dnb_dir = Path(dnb_path)
    if dnb_dir.exists():
        st.success(f"✅ Repository trouvé")

        # Années disponibles
        annees_dispo = [d.name for d in dnb_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        st.info(f"📚 {len(annees_dispo)} années disponibles")
    else:
        st.error("❌ Repository introuvable")

    st.markdown("---")

    # Statistiques rapides
    if st.session_state.questions_db:
        st.metric("📊 Questions en base", len(st.session_state.questions_db))

        avec_images = len([q for q in st.session_state.questions_db if q.get('images')])
        st.metric("🖼️ Avec images", avec_images)

# =============================================================================
# HEADER PRINCIPAL
# =============================================================================

st.title("🎓 DNB Mathalea - Plateforme Complète")
st.markdown("""
**Plateforme tout-en-un pour l'exploitation des annales du Brevet des Collèges**
""")

# =============================================================================
# TABS PRINCIPAUX
# =============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📚 1. Parser & Analyser",
    "🔍 2. Explorer la Base",
    "📝 3. Générer un Sujet",
    "✅ 4. Corriger un Devoir",
    "📊 5. Statistiques"
])

# =============================================================================
# TAB 1 : PARSER & ANALYSER
# =============================================================================

with tab1:
    st.header("📚 Parser et Analyser les Sujets DNB")

    st.markdown("""
    **Pipeline complet :**
    1. 📄 Parser les fichiers TEX
    2. 🖼️ Détecter les images
    3. 🤖 Analyser avec OCR Mistral
    4. 💾 Stocker dans la base
    """)

    col1, col2 = st.columns([2, 1])

    with col1:
        # Sélection des années
        if dnb_dir.exists():
            annees_dispo = [d.name for d in dnb_dir.iterdir() if d.is_dir() and d.name.isdigit()]
            annees_dispo.sort(reverse=True)

            annees_selected = st.multiselect(
                "Années à traiter",
                options=annees_dispo,
                default=[annees_dispo[0]] if annees_dispo else [],
                help="Sélectionnez une ou plusieurs années"
            )

            # Options d'analyse
            st.markdown("**Options d'analyse :**")
            col_opt1, col_opt2 = st.columns(2)

            with col_opt1:
                analyse_images = st.checkbox("🖼️ Analyser les images", value=True, disabled=not api_key)

            with col_opt2:
                analyse_scratch = st.checkbox("💻 Analyser le code Scratch", value=False, disabled=not api_key)

    with col2:
        st.markdown("**🎯 Estimation**")

        if annees_selected:
            nb_fichiers_estimes = len(annees_selected) * 120  # ~120 fichiers par an
            nb_questions_estimes = nb_fichiers_estimes * 5  # ~5 questions par fichier

            st.metric("Fichiers", f"~{nb_fichiers_estimes}")
            st.metric("Questions", f"~{nb_questions_estimes}")

            if analyse_images and api_key:
                cout_estime = nb_questions_estimes * 0.001  # ~0.001€ par question
                st.metric("Coût API", f"~{cout_estime:.2f}€")

    # Bouton de lancement
    st.markdown("---")

    if st.button("🚀 Lancer le Traitement Complet", type="primary", use_container_width=True):
        if not annees_selected:
            st.error("❌ Sélectionnez au moins une année")
            st.stop()

        if not dnb_dir.exists():
            st.error("❌ Repository DNB introuvable")
            st.stop()

        # Pipeline de traitement
        with st.spinner("⏳ Traitement en cours..."):
            progress_bar = st.progress(0)
            status_text = st.empty()

            all_questions = []
            total_steps = len(annees_selected)

            for idx, annee in enumerate(annees_selected):
                annee_dir = dnb_dir / annee / "tex"

                if not annee_dir.exists():
                    st.warning(f"⚠️ {annee}/tex introuvable")
                    continue

                # ÉTAPE 1 : Parsing TEX
                status_text.markdown(f"**📄 Étape 1/{total_steps} : Parsing {annee}...**")
                questions = st.session_state.parser.parse_directory(annee_dir, recursive=False)

                # ÉTAPE 2 : Analyse des images (si activé)
                if analyse_images and api_key and st.session_state.analyzer:
                    status_text.markdown(f"**🖼️ Étape 2/{total_steps} : Analyse OCR {annee}...**")

                    for i, q in enumerate(questions):
                        if q.images:
                            # Convertir Question en dict pour l'analyse
                            q_dict = {
                                'annee': q.annee,
                                'images': q.images,
                                'texte_latex': q.texte_latex
                            }

                            analyzed = st.session_state.analyzer.process_question_images(
                                q_dict,
                                dnb_dir
                            )

                            # Ajouter les analyses à la question
                            if 'images_analyses' in analyzed:
                                q.images_analyses = analyzed['images_analyses']

                all_questions.extend(questions)

                # Mise à jour progression
                progress_bar.progress((idx + 1) / total_steps)

            progress_bar.empty()
            status_text.empty()

            # Stocker dans la base
            st.session_state.questions_db = all_questions

            # Statistiques
            stats = st.session_state.parser.get_statistics(all_questions)

            st.success(f"✅ **Traitement terminé !**")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📝 Questions", stats['total_questions'])
            col2.metric("🖼️ Avec images", stats['avec_images'])
            col3.metric("🔢 Avec équations", stats['avec_equations'])
            col4.metric("📑 Sous-questions", stats['avec_sous_questions'])

            # Export automatique
            st.markdown("---")
            st.markdown("### 💾 Export")

            json_data = st.session_state.parser.to_json(all_questions)

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="📥 Télécharger JSON",
                    data=json_data,
                    file_name=f"dnb_questions_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    use_container_width=True
                )

            with col2:
                # Sauvegarder localement aussi
                output_file = Path("dnb_database.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(json_data)

                st.info(f"💾 Sauvegardé dans `{output_file}`")

# =============================================================================
# TAB 2 : EXPLORER LA BASE
# =============================================================================

with tab2:
    st.header("🔍 Explorer la Base de Questions")

    if not st.session_state.questions_db:
        st.info("ℹ️ Parsez d'abord les sujets dans l'onglet 1")
    else:
        # Filtres
        st.markdown("### 🎯 Filtres")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Filtre par année
            annees_uniques = sorted(list(set(q.annee for q in st.session_state.questions_db)))
            annee_filter = st.multiselect("Année", options=annees_uniques, default=annees_uniques)

        with col2:
            # Filtre par présence d'images
            image_filter = st.selectbox("Images", ["Toutes", "Avec images", "Sans images"])

        with col3:
            # Filtre par équations
            eq_filter = st.selectbox("Équations", ["Toutes", "Avec équations", "Sans équations"])

        # Appliquer les filtres
        questions_filtered = st.session_state.questions_db

        if annee_filter:
            questions_filtered = [q for q in questions_filtered if q.annee in annee_filter]

        if image_filter == "Avec images":
            questions_filtered = [q for q in questions_filtered if q.images]
        elif image_filter == "Sans images":
            questions_filtered = [q for q in questions_filtered if not q.images]

        if eq_filter == "Avec équations":
            questions_filtered = [q for q in questions_filtered if q.equations]
        elif eq_filter == "Sans équations":
            questions_filtered = [q for q in questions_filtered if not q.equations]

        st.info(f"📊 {len(questions_filtered)} questions correspondent aux filtres")

        # Recherche textuelle
        search_query = st.text_input("🔎 Rechercher dans le texte", placeholder="Ex: pythagore, probabilité, etc.")

        if search_query:
            questions_filtered = [
                q for q in questions_filtered
                if search_query.lower() in q.texte_brut.lower()
            ]
            st.info(f"🔍 {len(questions_filtered)} résultats pour '{search_query}'")

        # Affichage des résultats
        st.markdown("---")
        st.markdown("### 📋 Résultats")

        if questions_filtered:
            for i, q in enumerate(questions_filtered[:20]):  # Limiter à 20
                with st.expander(f"**Question {i+1}** - {q.id}"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**📝 Texte :**")
                        st.write(q.texte_brut)

                        if q.equations:
                            st.markdown(f"**🔢 Équations ({len(q.equations)}) :**")
                            for eq in q.equations[:3]:
                                st.code(eq, language="latex")

                        if hasattr(q, 'images_analyses') and q.images_analyses:
                            st.markdown("**🖼️ Analyses d'images :**")
                            for analysis in q.images_analyses:
                                if analysis.get('description'):
                                    st.info(f"📷 {analysis['reference']}: {analysis['description']}")

                    with col2:
                        st.json({
                            "Année": q.annee,
                            "Session": q.session,
                            "Exercice": q.exercice,
                            "Numéro": q.numero,
                            "Images": len(q.images),
                            "Équations": len(q.equations)
                        })

            if len(questions_filtered) > 20:
                st.info(f"💡 Affichage des 20 premières sur {len(questions_filtered)} questions")

# =============================================================================
# TAB 3 : GÉNÉRER UN SUJET
# =============================================================================

with tab3:
    st.header("📝 Générer un Sujet Personnalisé")

    if not st.session_state.questions_db:
        st.info("ℹ️ Parsez d'abord les sujets dans l'onglet 1")
    else:
        st.markdown("""
        Créez un sujet personnalisé en sélectionnant des questions de la base.
        """)

        col1, col2 = st.columns([2, 1])

        with col1:
            nb_questions = st.slider("Nombre de questions", 1, 10, 5)

            st.markdown("**Critères de sélection :**")

            critere_difficulte = st.select_slider(
                "Avec équations (plus difficile)",
                options=["Aucune préférence", "Plutôt sans", "Mélangé", "Plutôt avec", "Uniquement avec"],
                value="Aucune préférence"
            )

            critere_images = st.checkbox("Inclure des questions avec images", value=True)

        with col2:
            st.markdown("**Aperçu du sujet**")
            st.metric("Questions", nb_questions)
            if critere_images:
                st.info("🖼️ Avec images")

        if st.button("🎲 Générer le Sujet", type="primary", use_container_width=True):
            import random

            # Filtrer selon critères
            pool = st.session_state.questions_db.copy()

            if critere_images:
                pool = [q for q in pool if q.images]

            if critere_difficulte == "Uniquement avec":
                pool = [q for q in pool if q.equations]
            elif critere_difficulte == "Plutôt avec":
                avec_eq = [q for q in pool if q.equations]
                sans_eq = [q for q in pool if not q.equations]
                pool = avec_eq * 3 + sans_eq  # 75% avec équations
            elif critere_difficulte == "Plutôt sans":
                avec_eq = [q for q in pool if q.equations]
                sans_eq = [q for q in pool if not q.equations]
                pool = avec_eq + sans_eq * 3  # 75% sans équations

            if len(pool) < nb_questions:
                st.warning(f"⚠️ Seulement {len(pool)} questions disponibles avec ces critères")
                nb_questions = len(pool)

            # Sélectionner aléatoirement
            questions_selected = random.sample(pool, nb_questions)

            st.success(f"✅ Sujet généré avec {nb_questions} questions !")

            # Afficher le sujet
            st.markdown("---")
            st.markdown("## 📄 Sujet Généré")

            for i, q in enumerate(questions_selected, 1):
                st.markdown(f"### Exercice {i}")
                st.markdown(q.texte_brut)

                if q.images:
                    st.caption(f"🖼️ Images : {', '.join(q.images)}")

                if q.equations:
                    with st.expander("Voir les équations"):
                        for eq in q.equations:
                            st.code(eq, language="latex")

                st.markdown("---")

            # Export du sujet
            sujet_md = f"# Sujet DNB Personnalisé\n\n"
            sujet_md += f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n\n"

            for i, q in enumerate(questions_selected, 1):
                sujet_md += f"## Exercice {i}\n\n"
                sujet_md += f"{q.texte_brut}\n\n"
                if q.images:
                    sujet_md += f"*Images : {', '.join(q.images)}*\n\n"
                sujet_md += "---\n\n"

            st.download_button(
                label="📥 Télécharger le Sujet (Markdown)",
                data=sujet_md,
                file_name=f"sujet_dnb_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True
            )

# =============================================================================
# TAB 4 : CORRIGER UN DEVOIR
# =============================================================================

with tab4:
    st.header("✅ Scanner et Corriger un Devoir")

    st.markdown("""
    Scannez un devoir d'élève (manuscrit) et obtenez une correction automatique.
    """)

    col1, col2 = st.columns([2, 1])

    with col1:
        # Upload du devoir
        devoir_file = st.file_uploader(
            "📤 Upload du devoir scanné",
            type=["pdf", "png", "jpg", "jpeg"],
            help="Photo ou scan du devoir manuscrit"
        )

        if devoir_file:
            st.success("✅ Devoir chargé")

            # Afficher l'aperçu
            if devoir_file.type == "application/pdf":
                st.info("📄 PDF détecté")
            else:
                from PIL import Image
                img = Image.open(devoir_file)
                st.image(img, caption="Aperçu du devoir", use_container_width=True)

    with col2:
        if devoir_file:
            st.markdown("**Options de correction**")

            correction_mode = st.radio(
                "Mode",
                ["Extraction seule", "Extraction + Analyse"],
                help="Analyse = comparer avec questions de la base"
            )

    if devoir_file and st.button("🔍 Analyser le Devoir", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ Clé API requise pour l'OCR")
            st.stop()

        with st.spinner("📖 Extraction du texte en cours..."):
            # Logique OCR (similaire à main.py)
            from mistralai import Mistral
            from mistralai.models import DocumentURLChunk
            import base64

            client = Mistral(api_key=api_key)

            file_bytes = devoir_file.read()

            # Upload et OCR
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

        st.success("✅ Extraction terminée !")

        # Afficher le texte extrait
        st.markdown("### 📄 Texte Extrait")
        st.text_area("Texte du devoir", texte_extrait, height=300)

        # Analyse intelligente (si mode avancé)
        if correction_mode == "Extraction + Analyse":
            st.markdown("---")
            st.markdown("### 🤖 Analyse Intelligente")

            with st.spinner("Analyse en cours..."):
                # Utiliser Mistral pour analyser le devoir
                analysis_response = client.chat.complete(
                    model="mistral-large-latest",
                    messages=[{
                        "role": "user",
                        "content": f"""Analyse ce devoir de mathématiques de niveau Brevet (DNB) :

{texte_extrait}

Fournis :
1. **Exercices identifiés** (liste numérotée)
2. **Points positifs** (ce qui est bien fait)
3. **Erreurs détectées** (avec explications pédagogiques)
4. **Suggestions d'amélioration**

Format ta réponse en Markdown avec des sections claires."""
                    }],
                    temperature=0.3
                )

                analyse = analysis_response.choices[0].message.content

            st.markdown(analyse)

            # Téléchargement du rapport
            rapport = f"# Rapport de Correction\n\n"
            rapport += f"Date : {datetime.now().strftime('%d/%m/%Y')}\n\n"
            rapport += f"## Texte Extrait\n\n{texte_extrait}\n\n"
            rapport += f"## Analyse\n\n{analyse}\n"

            st.download_button(
                label="📥 Télécharger le Rapport",
                data=rapport,
                file_name=f"rapport_correction_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True
            )

# =============================================================================
# TAB 5 : STATISTIQUES
# =============================================================================

with tab5:
    st.header("📊 Statistiques et Visualisations")

    if not st.session_state.questions_db:
        st.info("ℹ️ Parsez d'abord les sujets dans l'onglet 1")
    else:
        stats = st.session_state.parser.get_statistics(st.session_state.questions_db)

        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("📝 Total Questions", stats['total_questions'])
        col2.metric("🖼️ Avec Images", stats['avec_images'])
        col3.metric("🔢 Avec Équations", stats['avec_equations'])
        col4.metric("📑 Avec Sous-Q", stats['avec_sous_questions'])

        st.markdown("---")

        # Graphiques
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📅 Questions par Année")
            if stats['par_annee']:
                df_annee = pd.DataFrame(
                    list(stats['par_annee'].items()),
                    columns=['Année', 'Nombre']
                )
                st.bar_chart(df_annee.set_index('Année'))

        with col2:
            st.subheader("🖼️ Types d'Images")
            if stats['types_images']:
                df_images = pd.DataFrame(
                    list(stats['types_images'].items()),
                    columns=['Type', 'Nombre']
                )
                st.bar_chart(df_images.set_index('Type'))

        # Tableau détaillé
        st.markdown("---")
        st.subheader("📋 Détails par Année")

        if stats['par_annee']:
            tableau_data = []
            for annee in sorted(stats['par_annee'].keys()):
                questions_annee = [q for q in st.session_state.questions_db if q.annee == annee]

                tableau_data.append({
                    'Année': annee,
                    'Questions': len(questions_annee),
                    'Avec Images': len([q for q in questions_annee if q.images]),
                    'Avec Équations': len([q for q in questions_annee if q.equations]),
                    'Sous-questions': len([q for q in questions_annee if q.sous_questions])
                })

            df_detail = pd.DataFrame(tableau_data)
            st.dataframe(df_detail, use_container_width=True)

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 2rem;'>
    <p>🎓 <strong>DNB Mathalea - Plateforme Complète</strong></p>
    <p>Parsing TEX • OCR Intelligent • Analyse IA • Génération de Sujets • Correction Automatique</p>
    <p style='font-size: 0.8rem;'>Développé avec ❤️ pour les enseignants</p>
</div>
""", unsafe_allow_html=True)
