# 📚 Parser DNB Mathalea

Application pour parser les fichiers TEX du repository [mathalea/dnb](https://github.com/mathalea/dnb) et extraire les questions individuelles.

## 🎯 Objectif

Transformer les 1245+ fichiers TEX des annales du Brevet (DNB) en une base de données structurée de questions exploitables, avec :
- ✅ Séparation automatique des questions
- ✅ Extraction du texte LaTeX
- ✅ Détection des images et schémas
- ✅ Extraction des équations mathématiques
- ✅ Gestion des sous-questions imbriquées
- ✅ Export en JSON, CSV ou Markdown

## 🚀 Utilisation

### Lancement en local

```bash
# 1. Cloner le repository DNB
git clone https://github.com/mathalea/dnb.git

# 2. Lancer l'application parser
streamlit run app_parser_dnb.py

# 3. Dans l'interface :
#    - Entrer le chemin vers le dossier dnb
#    - Sélectionner les années à traiter
#    - Cliquer sur "Lancer le parsing"
#    - Télécharger l'export JSON/CSV
```

### Test rapide du parser

```bash
# Tester le parser sur un fichier
python3 parser_dnb.py
```

## 📊 Exemple de sortie

### Structure JSON d'une question :

```json
{
  "id": "dnb_2022_06_polynesie_5_1_a",
  "annee": "2022",
  "session": "polynesie",
  "exercice": 5,
  "numero": "1.a",
  "texte_latex": "Vérifier que la profondeur $p$ de chaque escalator est égale à $12$ m",
  "texte_brut": "Vérifier que la profondeur p de chaque escalator est égale à 12 m",
  "images": ["Pomp", "[dessin_pspicture]"],
  "equations": ["$p$", "$12$ m"],
  "sous_questions": [],
  "type_question": "sous-question",
  "source_file": "dnb_2022_06_polynesie_5.tex"
}
```

## 🎨 Fonctionnalités

### 1. Parser TEX
- ✅ Parse récursivement les `\begin{enumerate}...\end{enumerate}`
- ✅ Sépare par `\item`
- ✅ Gère les sous-questions imbriquées
- ✅ Skip automatiquement les fichiers de correction (`*_cor.tex`)

### 2. Extraction d'images
Détecte :
- `\includegraphics{nom}` → Images externes (EPS, PNG)
- `\begin{pspicture}` → Dessins inline
- `\begin{scratch}` → Code Scratch
- `\begin{tabular}` → Tableaux

### 3. Extraction d'équations
- Équations inline : `$...$`
- Équations display : `\[...\]`
- Conservation du format LaTeX

### 4. Export
- **JSON** : Structure complète
- **JSON compressé (ZIP)** : Pour fichiers volumineux
- **CSV** : Vue tabulaire simplifiée
- **Markdown** : Pour lecture humaine

## 📈 Statistiques

Exemple sur l'année 2022 :
- **~250 questions** extraites
- **~150 avec images** (60%)
- **~200 avec équations** (80%)
- **~80 avec sous-questions** (32%)

Types d'images détectées :
- Images externes : ~50
- Dessins pspicture : ~80
- Code Scratch : ~20
- Tableaux : ~30

## 🛠️ Architecture

```
app_parser_dnb.py       # Interface Streamlit
parser_dnb.py           # Module de parsing
mathalea/dnb/          # Repository source
  ├── 2013/tex/        # Fichiers TEX 2013
  ├── 2014/tex/        # Fichiers TEX 2014
  └── ...
```

### Classes principales :

- `DNBParser` : Parser principal
- `Question` : Structure de données d'une question

## 🔮 Prochaines étapes possibles

### Phase 1 : OCR des images ✅ ACTUEL
- [x] Parser TEX
- [x] Détecter images
- [ ] OCR avec Mistral AI (à ajouter)
- [ ] Générer descriptions des schémas

### Phase 2 : Enrichissement
- [ ] Classification automatique des questions (géométrie, probabilité, etc.)
- [ ] Détection du niveau de difficulté
- [ ] Extraction des compétences évaluées
- [ ] Liens vers les corrections

### Phase 3 : Application complète
- [ ] Base de données MongoDB
- [ ] API REST
- [ ] Interface de recherche
- [ ] Générateur de sujets personnalisés

## 📝 Notes techniques

### Limitations actuelles :

1. **Images inline (pspicture)** : Détectées mais pas converties en PNG
2. **Code Scratch** : Détecté mais pas rendu visuellement
3. **Équations complexes** : Conservées en LaTeX brut
4. **Mise en page** : Non préservée (focus sur le contenu)

### Améliorations futures :

1. Convertir `pspicture` → PNG avec LaTeX
2. Rendre `scratch` → Image avec scratch-blocks
3. Ajouter OCR Mistral pour décrire les images
4. Parser les métadonnées (thèmes, compétences)

## 🤝 Contribution

Ce parser est conçu pour être extensible. Pour ajouter des fonctionnalités :

```python
from parser_dnb import DNBParser

parser = DNBParser()
questions = parser.parse_directory(Path("dnb/2022/tex"))

# Traiter les questions
for q in questions:
    # Votre code ici
    pass
```

## 📚 Ressources

- Repository source : https://github.com/mathalea/dnb
- Application OCR : [main.py](main.py)
- Documentation Mathalea : https://coopmaths.fr/

---

Développé pour faciliter l'exploitation pédagogique des annales du DNB 🎓
