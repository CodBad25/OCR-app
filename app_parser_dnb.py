"""
Application Streamlit pour parser les fichiers DNB
"""

import streamlit as st
import sys
from pathlib import Path
import json
import pandas as pd
from parser_dnb import DNBParser
import zipfile
import io

st.set_page_config(
    page_title="Parser DNB Mathalea",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Parser DNB Mathalea")
st.markdown("""
Cette application parse les fichiers TEX du repository mathalea/dnb et extrait les questions individuelles.
""")

# Initialiser le parser
if 'parser' not in st.session_state:
    st.session_state.parser = DNBParser()

if 'questions' not in st.session_state:
    st.session_state.questions = []

if 'statistics' not in st.session_state:
    st.session_state.statistics = None

# Sidebar : Configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    dnb_path = st.text_input(
        "Chemin vers mathalea/dnb",
        value="/tmp/dnb",
        help="Chemin absolu vers le repository cloné"
    )

    annees = st.multiselect(
        "Années à traiter",
        options=["2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022"],
        default=["2022"],
        help="Sélectionnez les années à parser"
    )

    st.markdown("---")

    st.markdown("""
    ### 📖 Guide rapide
    1. **Cloner le repo** :
       ```bash
       git clone https://github.com/mathalea/dnb.git
       ```
    2. **Entrer le chemin** ci-dessus
    3. **Sélectionner les années**
    4. **Cliquer sur Parser**
    """)

# Main content
tab1, tab2, tab3 = st.tabs(["🔍 Parser", "📊 Statistiques", "📥 Export"])

with tab1:
    st.header("Extraction des questions")

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("🚀 Lancer le parsing", type="primary", use_container_width=True):
            dnb_dir = Path(dnb_path)

            if not dnb_dir.exists():
                st.error(f"❌ Le répertoire {dnb_path} n'existe pas")
                st.info("💡 Clonez d'abord le repository : `git clone https://github.com/mathalea/dnb.git`")
                st.stop()

            # Parser
            with st.spinner("📖 Parsing des fichiers TEX en cours..."):
                all_questions = []

                # Créer une barre de progression
                progress_bar = st.progress(0)
                status_text = st.empty()

                total_annees = len(annees)

                for idx, annee in enumerate(annees):
                    annee_dir = dnb_dir / annee / "tex"

                    if not annee_dir.exists():
                        st.warning(f"⚠️ Répertoire {annee} introuvable")
                        continue

                    status_text.text(f"📄 Traitement année {annee}...")

                    # Parser les fichiers de cette année
                    questions = st.session_state.parser.parse_directory(annee_dir, recursive=False)
                    all_questions.extend(questions)

                    # Mettre à jour la progression
                    progress_bar.progress((idx + 1) / total_annees)

                progress_bar.empty()
                status_text.empty()

                # Stocker les résultats
                st.session_state.questions = all_questions
                st.session_state.statistics = st.session_state.parser.get_statistics(all_questions)

                st.success(f"✅ Extraction terminée ! {len(all_questions)} questions extraites")

    with col2:
        if st.session_state.questions:
            st.metric("Questions extraites", len(st.session_state.questions))

    # Afficher un aperçu
    if st.session_state.questions:
        st.markdown("---")
        st.subheader("📋 Aperçu des questions")

        # Sélecteur de question
        question_idx = st.selectbox(
            "Sélectionner une question",
            range(min(20, len(st.session_state.questions))),
            format_func=lambda x: f"Question {st.session_state.questions[x].numero} - {st.session_state.questions[x].source_file}"
        )

        if question_idx is not None:
            q = st.session_state.questions[question_idx]

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**📝 Texte de la question :**")
                st.text_area("Texte brut", q.texte_brut, height=150, disabled=True)

                if q.equations:
                    st.markdown(f"**🔢 Équations ({len(q.equations)}) :**")
                    for eq in q.equations[:5]:  # Limiter à 5
                        st.code(eq, language="latex")

                if q.sous_questions:
                    st.markdown(f"**📑 Sous-questions ({len(q.sous_questions)}) :**")
                    for sq in q.sous_questions:
                        st.markdown(f"- {sq.numero}: {sq.texte_brut[:100]}...")

            with col2:
                st.markdown("**ℹ️ Métadonnées :**")
                st.json({
                    "ID": q.id,
                    "Année": q.annee,
                    "Session": q.session,
                    "Exercice": q.exercice,
                    "Numéro": q.numero,
                    "Type": q.type_question
                })

                if q.images:
                    st.markdown(f"**🖼️ Images ({len(q.images)}) :**")
                    for img in q.images:
                        st.markdown(f"- `{img}`")

with tab2:
    st.header("📊 Statistiques")

    if st.session_state.statistics:
        stats = st.session_state.statistics

        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📝 Total questions", stats['total_questions'])

        with col2:
            st.metric("🖼️ Avec images", stats['avec_images'])

        with col3:
            st.metric("🔢 Avec équations", stats['avec_equations'])

        with col4:
            st.metric("📑 Avec sous-questions", stats['avec_sous_questions'])

        st.markdown("---")

        # Graphiques
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Questions par année")
            if stats['par_annee']:
                df_annee = pd.DataFrame(
                    list(stats['par_annee'].items()),
                    columns=['Année', 'Nombre de questions']
                )
                st.bar_chart(df_annee.set_index('Année'))

        with col2:
            st.subheader("Types d'images")
            if stats['types_images']:
                df_images = pd.DataFrame(
                    list(stats['types_images'].items()),
                    columns=['Type', 'Nombre']
                )
                st.bar_chart(df_images.set_index('Type'))

    else:
        st.info("ℹ️ Lancez le parsing pour voir les statistiques")

with tab3:
    st.header("📥 Export des données")

    if st.session_state.questions:
        st.markdown("""
        Exportez les questions extraites dans différents formats pour les utiliser dans votre application.
        """)

        format_export = st.radio(
            "Format d'export",
            ["JSON", "JSON compressé (ZIP)", "CSV", "Markdown"],
            horizontal=True
        )

        if st.button("📥 Générer l'export", type="primary"):
            with st.spinner("Génération en cours..."):

                if format_export == "JSON":
                    json_data = st.session_state.parser.to_json(st.session_state.questions)

                    st.download_button(
                        label="💾 Télécharger JSON",
                        data=json_data,
                        file_name="dnb_questions.json",
                        mime="application/json"
                    )

                elif format_export == "JSON compressé (ZIP)":
                    json_data = st.session_state.parser.to_json(st.session_state.questions)

                    # Créer un ZIP en mémoire
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        zip_file.writestr("dnb_questions.json", json_data)

                    st.download_button(
                        label="💾 Télécharger ZIP",
                        data=zip_buffer.getvalue(),
                        file_name="dnb_questions.zip",
                        mime="application/zip"
                    )

                elif format_export == "CSV":
                    # Créer un CSV simplifié
                    data = []
                    for q in st.session_state.questions:
                        data.append({
                            'id': q.id,
                            'annee': q.annee,
                            'session': q.session,
                            'exercice': q.exercice,
                            'numero': q.numero,
                            'texte': q.texte_brut,
                            'nb_images': len(q.images),
                            'nb_equations': len(q.equations),
                            'images': '|'.join(q.images),
                            'source': q.source_file
                        })

                    df = pd.DataFrame(data)
                    csv_data = df.to_csv(index=False)

                    st.download_button(
                        label="💾 Télécharger CSV",
                        data=csv_data,
                        file_name="dnb_questions.csv",
                        mime="text/csv"
                    )

                elif format_export == "Markdown":
                    # Créer un fichier Markdown
                    md_lines = ["# Questions DNB Extraites\n"]

                    for q in st.session_state.questions[:100]:  # Limiter à 100
                        md_lines.append(f"\n## Question {q.numero} - {q.source_file}\n")
                        md_lines.append(f"**Année:** {q.annee} | **Session:** {q.session}\n")
                        md_lines.append(f"\n{q.texte_brut}\n")

                        if q.images:
                            md_lines.append(f"\n**Images:** {', '.join(q.images)}\n")

                        if q.equations:
                            md_lines.append(f"\n**Équations:**\n")
                            for eq in q.equations[:3]:
                                md_lines.append(f"- {eq}\n")

                        md_lines.append("\n---\n")

                    md_data = ''.join(md_lines)

                    st.download_button(
                        label="💾 Télécharger Markdown",
                        data=md_data,
                        file_name="dnb_questions.md",
                        mime="text/markdown"
                    )

                st.success("✅ Export généré !")

        # Aperçu JSON
        if st.session_state.questions:
            with st.expander("👁️ Aperçu JSON (première question)"):
                q = st.session_state.questions[0]
                st.json({
                    "id": q.id,
                    "annee": q.annee,
                    "session": q.session,
                    "exercice": q.exercice,
                    "numero": q.numero,
                    "texte_latex": q.texte_latex[:200] + "...",
                    "texte_brut": q.texte_brut,
                    "images": q.images,
                    "equations": q.equations[:3] if len(q.equations) > 3 else q.equations,
                    "type_question": q.type_question,
                    "source_file": q.source_file
                })

    else:
        st.info("ℹ️ Parsez d'abord les fichiers pour pouvoir exporter")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
📚 Parser DNB Mathalea | Développé pour l'analyse des sujets du Brevet
</div>
""", unsafe_allow_html=True)
