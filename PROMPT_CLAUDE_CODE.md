# 🎯 Prompt Détaillé pour Claude Code - Projet OCR et Parser DNB

## 📋 CONTEXTE GÉNÉRAL

Je travaille sur un projet éducatif pour le Brevet des Collèges (DNB) français. L'objectif est de créer une plateforme complète permettant de :
1. Parser des documents d'examens DNB (format TEX/LaTeX)
2. Extraire individuellement chaque question avec ses métadonnées
3. Utiliser l'OCR pour analyser les images contenues dans les exercices
4. Générer des sujets personnalisés
5. Corriger automatiquement les devoirs d'élèves

## 🎯 OBJECTIFS PRÉCIS

### Objectif Principal
Créer une application Streamlit cloud qui exploite une base de données de **5000-8000 questions** issues du repository GitHub `mathalea/dnb` (sujets de Brevet 2013-2022).

### Fonctionnalités Requises
1. **Explorer** : Rechercher et filtrer parmi toutes les questions
2. **Générer un Sujet** : Créer des sujets personnalisés selon des critères
3. **Corriger des Devoirs** : Upload d'un devoir élève → OCR → Analyse IA → Feedback pédagogique
4. **Statistiques** : Visualisations sur la base de données

## 📁 STRUCTURE DU REPOSITORY MATHALEA/DNB

Le repository `https://github.com/mathalea/dnb.git` contient :

```
dnb/
├── 2013/
│   ├── 13-Antilles-Guyane-juin/
│   │   ├── tex/
│   │   │   └── dnb_2013_06_Antilles_Guyane.tex
│   │   └── img/
│   │       ├── figure1.png
│   │       └── figure2.eps
│   └── 13-Asie-juin/
├── 2014/
├── ...
├── 2022/
└── README.md
```

**Chiffres clés** :
- 1245 fichiers TEX
- 1290 images (PNG, EPS)
- 10 années de sujets (2013-2022)
- Environ 5000-8000 questions au total

### Structure Typique d'un Fichier TEX

```latex
\documentclass[10pt]{article}
...
\begin{exercice}
\begin{enumerate}
\item Première question avec du texte et une équation $x^2 + 3x = 5$
\item Question avec image :
\begin{center}
\includegraphics[width=6cm]{figure1.png}
\end{center}
Quelle est l'aire du triangle ?
\item Question avec sous-questions :
    \begin{enumerate}
    \item Sous-question a
    \item Sous-question b
    \end{enumerate}
\end{enumerate}
\end{exercice}

\begin{exercice}
...
\end{exercice}
```

## 🗂️ FICHIERS DÉJÀ CRÉÉS DANS LE PROJET

### 1. **main.py** ✅ (Déployé sur Streamlit Cloud)
Application OCR simple utilisant Mistral AI pour extraire du texte depuis PDF/images.

**API Mistral OCR utilisée** :
```python
from mistralai import DocumentURLChunk

# Pour URL
response = client.ocr.process(
    model="mistral-ocr-latest",
    document=DocumentURLChunk(document_url="https://...")
)

# Pour fichier local
files = {"file": ("document.pdf", file_bytes, "application/pdf")}
upload_response = requests.post(upload_url, files=files)
signed_url = upload_response.json()["url"]

response = client.ocr.process(
    model="mistral-ocr-latest",
    document=DocumentURLChunk(document_url=signed_url)
)

# Extraction du texte
markdowns = [page.markdown for page in response.pages]
result_text = "\n\n---\n\n".join(markdowns)
```

### 2. **parser_dnb.py** ✅ (~400 lignes)
Module de parsing pour fichiers TEX du DNB.

**Classe principale** : `DNBParser`

**Méthodes clés** :
```python
def parse_tex_file(self, file_path: Path) -> List[Question]:
    """Parse un fichier TEX et retourne la liste des questions"""

def parse_enumerate(self, text: str, metadata: Dict, parent_num: str = "") -> List[Question]:
    """Parse récursivement les environnements enumerate (gère les sous-questions)"""

def extract_images(self, text: str) -> List[str]:
    """Détecte \includegraphics, pspicture, scratch, tableaux"""

def extract_equations(self, text: str) -> List[str]:
    """Extrait les équations $ $ et \[ \]"""
```

**Structure de données Question** :
```python
@dataclass
class Question:
    id: str
    year: str
    session: str
    exercise_number: int
    question_number: str
    text_latex: str
    text_clean: str
    images: List[str]
    equations: List[str]
    has_subquestions: bool
    subquestions: List['Question']
```

### 3. **app_parser_dnb.py** ✅ (~300 lignes)
Interface Streamlit pour le parser (version locale, nécessite le repo DNB cloné).

### 4. **image_analyzer.py** ✅ (~300 lignes)
Module d'analyse d'images avec OCR + IA.

**Méthodes** :
```python
def analyze_image_with_ocr(self, image_path: Path) -> Dict[str, str]:
    """OCR + Description IA avec Pixtral-12B"""

def convert_eps_to_png(self, eps_path: Path) -> Optional[Path]:
    """Convertit EPS en PNG avec Ghostscript"""

def analyze_scratch_code(self, scratch_latex: str) -> str:
    """Analyse des blocs de code Scratch"""
```

### 5. **app_dnb_complete.py** ✅ (~600 lignes)
Plateforme complète avec 5 tabs (version locale).

### 6. **app_cloud.py** ✅ (~400 lignes) - RÉCEMMENT CRÉÉ
**Version cloud optimisée** qui charge depuis JSON pré-parsé.

**Fonction clé** :
```python
@st.cache_data
def load_database():
    """Charge la base de questions depuis JSON"""
    db_path = Path("dnb_database_sample.json")
    if not db_path.exists():
        return None
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data
```

**4 Tabs** :
1. Explorer (recherche/filtres)
2. Générer un Sujet (sélection personnalisée)
3. Corriger un Devoir (OCR + IA)
4. Statistiques (graphiques)

### 7. **dnb_database_sample.json** ✅ - RÉCEMMENT CRÉÉ
Base de données pré-parsée contenant **566 questions** des années 2019-2022.

**Structure JSON** :
```json
{
  "metadata": {
    "total_questions": 566,
    "years_parsed": ["2019", "2020", "2021", "2022"],
    "created_at": "2025-01-07T..."
  },
  "questions": [
    {
      "id": "2022_09_Metropole_1_1",
      "year": "2022",
      "session": "septembre-Metropole",
      "exercise_number": 1,
      "question_number": "1",
      "text_latex": "...",
      "text_clean": "...",
      "images": ["figure1.png"],
      "equations": ["$x^2 + 3x = 5$"],
      "has_subquestions": false,
      "subquestions": []
    },
    ...
  ]
}
```

### 8. **requirements.txt**
```
streamlit>=1.28.0
mistralai>=1.0.0
Pillow>=10.0.0
requests>=2.31.0
pandas
```

## ✅ CE QUI A ÉTÉ FAIT

1. ✅ Application OCR simple (`main.py`) déployée sur Streamlit Cloud
2. ✅ Parser DNB complet (`parser_dnb.py`)
3. ✅ Analyseur d'images (`image_analyzer.py`)
4. ✅ Application complète locale (`app_dnb_complete.py`)
5. ✅ **Application cloud** (`app_cloud.py`) créée
6. ✅ **Base de données sample** (566 questions 2019-2022) parsée et sauvegardée
7. ✅ Fichiers committés et pushés sur la branche `claude/essaye-d-011CUs9rKipReA7MN3U2NuB2`

## 🎯 CE QU'IL RESTE À FAIRE (TÂCHE ACTUELLE)

### Option A : Déploiement Immédiat (RECOMMANDÉ)
L'application cloud avec 566 questions est prête. Il suffit de :

1. **Déployer sur Streamlit Cloud** :
   - Repository : `CodBad25/OCR-app`
   - Branch : `claude/essaye-d-011CUs9rKipReA7MN3U2NuB2`
   - Main file : `app_cloud.py`
   - Secrets : `MISTRAL_API_KEY = "..."`

2. **Tester l'application** et vérifier que les 4 tabs fonctionnent

### Option B : Parser Toutes les Années (5000-8000 questions)

Si l'utilisateur veut la base complète :

1. **Cloner le repository DNB** :
```bash
git clone https://github.com/mathalea/dnb.git /tmp/dnb
```

2. **Créer un script de parsing complet** :
```python
# parse_all_years.py
from parser_dnb import DNBParser
from pathlib import Path
import json

parser = DNBParser(Path("/tmp/dnb"))
all_questions = []

for year in range(2013, 2023):  # 2013 à 2022
    print(f"Parsing {year}...")
    year_questions = parser.parse_year(str(year))
    all_questions.extend(year_questions)
    print(f"  → {len(year_questions)} questions")

# Sauvegarder
database = {
    "metadata": {
        "total_questions": len(all_questions),
        "years_parsed": [str(y) for y in range(2013, 2023)],
        "created_at": datetime.now().isoformat()
    },
    "questions": [q.to_dict() for q in all_questions]
}

with open("dnb_database_complete.json", "w", encoding="utf-8") as f:
    json.dump(database, f, ensure_ascii=False, indent=2)

print(f"\n✅ Base complète : {len(all_questions)} questions")
```

3. **Exécuter le parsing** :
```bash
python parse_all_years.py
```

4. **Remplacer le fichier JSON dans app_cloud.py** :
   - Renommer `dnb_database_sample.json` → `dnb_database_complete.json`
   - Mettre à jour le chemin dans `app_cloud.py`

5. **Commit et push** :
```bash
git add dnb_database_complete.json app_cloud.py
git commit -m "Feat: Base de données complète DNB (2013-2022)"
git push -u origin claude/essaye-d-011CUs9rKipReA7MN3U2NuB2
```

## 🛠️ INSTRUCTIONS TECHNIQUES DÉTAILLÉES

### Structure du Parsing

**Défi principal** : Les questions sont dans des environnements `\begin{enumerate}...\end{enumerate}` qui peuvent être imbriqués.

**Stratégie** :
1. Extraire chaque bloc `\begin{exercice}...\end{exercice}`
2. Pour chaque exercice, parser récursivement les `enumerate`
3. Gérer les sous-questions avec un système de numérotation parent (ex: "2.a", "2.b")
4. Extraire les images, équations, et nettoyer le LaTeX

**Regex clés** :
```python
# Extraction exercices
exercice_pattern = r'\\begin{exercice}(.*?)\\end{exercice}'

# Extraction enumerate
enumerate_pattern = r'\\begin{enumerate}(.*?)\\end{enumerate}'

# Extraction items
item_pattern = r'\\item\s+(.*?)(?=\\item|\\end{enumerate}|$)'

# Images
image_pattern = r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}'

# Équations
equation_pattern = r'\$(.*?)\$|\\\[(.*?)\\\]'
```

### Gestion de l'OCR avec Mistral

**Points importants** :
1. Utiliser `mistral-ocr-latest` (PAS Pixtral-12B pour l'OCR)
2. Pour Pixtral-12B (analyse intelligente), utiliser `client.chat.complete()`
3. Gérer les uploads de fichiers avec signed URLs
4. Extraire `page.markdown` depuis les résultats OCR

**Exemple complet** :
```python
from mistralai import Mistral, DocumentURLChunk
import requests

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# 1. Upload du fichier
upload_response = client.files.upload_url()
upload_url = upload_response.upload_url

files = {"file": ("homework.pdf", pdf_bytes, "application/pdf")}
requests.post(upload_url, files=files)
signed_url = upload_response.url

# 2. OCR
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document=DocumentURLChunk(document_url=signed_url)
)

# 3. Extraction
text = "\n\n".join([page.markdown for page in ocr_response.pages])

# 4. Analyse avec Pixtral (optionnel)
analysis = client.chat.complete(
    model="pixtral-12b-2409",
    messages=[{
        "role": "user",
        "content": f"Analyse ce devoir et donne un feedback : {text}"
    }]
)
```

### Structure de l'Application Streamlit

**Architecture recommandée** :
```python
import streamlit as st
import json
from pathlib import Path

# Configuration page
st.set_page_config(page_title="DNB App", layout="wide")

# Chargement base de données (avec cache)
@st.cache_data
def load_database():
    with open("dnb_database_sample.json", 'r', encoding='utf-8') as f:
        return json.load(f)

# Sidebar
with st.sidebar:
    st.title("🎓 DNB Platform")
    st.info(f"{db['metadata']['total_questions']} questions disponibles")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Explorer", "📝 Générer", "✅ Corriger", "📊 Stats"])

with tab1:
    # Filtres
    # Affichage questions

with tab2:
    # Sélection critères
    # Génération sujet

with tab3:
    # Upload fichier
    # OCR + Analyse

with tab4:
    # Graphiques
```

## 🔧 COMMANDES GIT ESSENTIELLES

```bash
# Vérifier le statut
git status

# Voir les commits récents
git log --oneline -5

# Ajouter des fichiers
git add app_cloud.py dnb_database_sample.json

# Commit
git commit -m "Feat: Description du commit"

# Push (ATTENTION : utiliser la bonne branche)
git push -u origin claude/essaye-d-011CUs9rKipReA7MN3U2NuB2
```

**⚠️ IMPORTANT** : La branche DOIT commencer par `claude/` et se terminer par l'ID de session, sinon le push échouera (403).

## 📊 EXEMPLES DE QUESTIONS PARSÉES

### Question Simple
```json
{
  "id": "2022_09_Metropole_1_1",
  "year": "2022",
  "session": "septembre-Metropole",
  "exercise_number": 1,
  "question_number": "1",
  "text_latex": "Calculer $\\dfrac{5}{3} + \\dfrac{2}{3}$",
  "text_clean": "Calculer 5/3 + 2/3",
  "images": [],
  "equations": ["$\\dfrac{5}{3} + \\dfrac{2}{3}$"],
  "has_subquestions": false,
  "subquestions": []
}
```

### Question avec Sous-questions
```json
{
  "id": "2022_09_Metropole_2_3",
  "year": "2022",
  "session": "septembre-Metropole",
  "exercise_number": 2,
  "question_number": "3",
  "text_latex": "Le triangle ABC est rectangle en A...",
  "text_clean": "Le triangle ABC est rectangle en A...",
  "images": ["triangle.png"],
  "equations": ["$AB = 6$ cm", "$AC = 8$ cm"],
  "has_subquestions": true,
  "subquestions": [
    {
      "id": "2022_09_Metropole_2_3_a",
      "question_number": "3.a",
      "text_clean": "Calculer BC"
    },
    {
      "id": "2022_09_Metropole_2_3_b",
      "question_number": "3.b",
      "text_clean": "Calculer l'aire du triangle"
    }
  ]
}
```

## 🎨 AMÉLIORATIONS POSSIBLES

### Immédiat
1. Ajouter plus d'années à la base de données (actuellement 566 questions, objectif 5000+)
2. Améliorer les filtres dans l'explorateur (difficulté, thèmes)
3. Ajouter un système de tags (géométrie, algèbre, probabilités, etc.)

### Court Terme
1. Analyse automatique des images avec OCR lors du parsing
2. Extraction automatique des thèmes mathématiques
3. Estimation de difficulté basée sur l'IA
4. Export en PDF des sujets générés

### Long Terme
1. Base de données PostgreSQL au lieu de JSON
2. Système d'authentification utilisateurs
3. Historique des corrections par élève
4. Recommandations personnalisées d'exercices

## 🚀 GUIDE DE DÉPLOIEMENT STREAMLIT CLOUD

### Étapes Détaillées

1. **Aller sur** : https://share.streamlit.io

2. **Cliquer sur "New app"**

3. **Configuration** :
   - Repository : `CodBad25/OCR-app`
   - Branch : `claude/essaye-d-011CUs9rKipReA7MN3U2NuB2`
   - Main file path : `app_cloud.py`

4. **Advanced Settings > Secrets** :
```toml
MISTRAL_API_KEY = "votre_clé_mistral_ici"
```

5. **Deploy** et attendre 2-3 minutes

6. **URL finale** : `https://votre-app.streamlit.app`

### Vérifications Post-Déploiement

✅ L'app charge sans erreur
✅ Tab Explorer affiche 566 questions
✅ Les filtres fonctionnent
✅ La génération de sujets marche
✅ Le correcteur accepte les uploads
✅ Les statistiques s'affichent

## 🐛 ERREURS COURANTES ET SOLUTIONS

### Erreur 1 : "401 Unauthorized" Mistral API
**Cause** : Clé API invalide ou expirée
**Solution** : Régénérer une clé sur https://console.mistral.ai

### Erreur 2 : "FileNotFoundError: dnb_database_sample.json"
**Cause** : Fichier JSON non trouvé
**Solution** : Vérifier que le fichier est bien dans le repository et committé

### Erreur 3 : "ModuleNotFoundError: mistralai"
**Cause** : requirements.txt incomplet
**Solution** : Vérifier que requirements.txt contient `mistralai>=1.0.0`

### Erreur 4 : "Cannot push to branch"
**Cause** : Nom de branche incorrect
**Solution** : Utiliser `claude/essaye-d-011CUs9rKipReA7MN3U2NuB2`

### Erreur 5 : Parsing échoue sur certains fichiers TEX
**Cause** : Syntaxe LaTeX non standard
**Solution** : Ajouter des try/except et logger les erreurs

## 📝 NOTES IMPORTANTES

1. **Encodage** : Toujours utiliser `encoding='utf-8'` pour les fichiers français
2. **Cache Streamlit** : Utiliser `@st.cache_data` pour les fonctions lourdes
3. **Gestion mémoire** : Le fichier JSON de 5000+ questions fera ~50-100 MB
4. **Coût API Mistral** :
   - OCR : ~$0.01 par page
   - Pixtral-12B : ~$0.001 par image
   - Budget recommandé : $10-20/mois pour usage modéré

5. **Performances** :
   - Parsing d'1 année : ~2-5 minutes
   - Parsing des 10 années : ~30-60 minutes
   - Préférer parser une fois et sauvegarder en JSON

## 🎯 TÂCHE IMMÉDIATE RECOMMANDÉE

**Option 1** : Déployer l'app actuelle (566 questions) pour tester
**Option 2** : Parser toutes les années d'abord (5000+ questions)

### Si Option 1 (Déploiement Rapide)

```bash
# Les fichiers sont déjà committés et pushés
# Aller directement sur share.streamlit.io et déployer
```

### Si Option 2 (Parsing Complet)

```bash
# 1. Cloner le repo DNB
git clone https://github.com/mathalea/dnb.git /tmp/dnb

# 2. Créer parse_all_years.py (voir code ci-dessus)

# 3. Exécuter
python parse_all_years.py

# 4. Vérifier la taille
ls -lh dnb_database_complete.json

# 5. Commit et push
git add dnb_database_complete.json
git commit -m "Feat: Base DNB complète (2013-2022)"
git push -u origin claude/essaye-d-011CUs9rKipReA7MN3U2NuB2
```

## ❓ QUESTIONS À POSER À L'UTILISATEUR

1. Veux-tu déployer l'app actuelle (566 questions) ou parser toutes les années d'abord ?
2. As-tu une préférence pour le nom de l'application sur Streamlit Cloud ?
3. Veux-tu ajouter des fonctionnalités spécifiques (export PDF, système de notes, etc.) ?
4. As-tu une clé API Mistral valide pour le correcteur de devoirs ?

## 📚 RESSOURCES UTILES

- Mistral AI Docs : https://docs.mistral.ai
- Streamlit Docs : https://docs.streamlit.io
- Repository DNB : https://github.com/mathalea/dnb
- LaTeX Guide : https://en.wikibooks.org/wiki/LaTeX

---

## 🎬 RÉSUMÉ EXÉCUTIF

**État actuel** : Application cloud prête avec 566 questions (2019-2022)

**Fichiers clés** :
- `app_cloud.py` : Application Streamlit
- `dnb_database_sample.json` : Base de données
- `parser_dnb.py` : Module de parsing

**Prochaine étape** :
1. Déployer sur Streamlit Cloud, OU
2. Parser les 10 années complètes puis déployer

**Branche Git** : `claude/essaye-d-011CUs9rKipReA7MN3U2NuB2`

**Tout est prêt pour le déploiement ! 🚀**
