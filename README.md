# 🔍 Mistral OCR App

Application Streamlit utilisant l'**API OCR officielle de Mistral** (`mistral-ocr-latest`) pour extraire du texte à partir d'images et de PDF.

## ✨ Fonctionnalités

- 📄 Support des PDF et images (PNG, JPG, JPEG)
- 🌐 Upload local ou via URL
- 🤖 Extraction de texte intelligente via Mistral AI
- 💾 Téléchargement des résultats
- 🎨 Interface utilisateur intuitive

## 🚀 Installation locale

1. **Cloner le dépôt** :
   ```bash
   git clone <votre-repo>
   cd OCR-app
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer la clé API** :
   - Copiez `.streamlit/secrets.toml.example` vers `.streamlit/secrets.toml`
   - Ajoutez votre clé API Mistral (obtenez-la sur https://console.mistral.ai/)
   ```toml
   MISTRAL_API_KEY = "votre-clé-api-ici"
   ```

4. **Lancer l'application** :
   ```bash
   streamlit run main.py
   ```

## ☁️ Déploiement Cloud

### Streamlit Cloud

1. Connectez votre dépôt GitHub à Streamlit Cloud
2. Ajoutez votre clé API dans **Settings > Secrets** :
   ```toml
   MISTRAL_API_KEY = "votre-clé-api-ici"
   ```
3. Déployez l'application

### Render

1. Créez un nouveau Web Service
2. Configurez la variable d'environnement :
   - Clé : `MISTRAL_API_KEY`
   - Valeur : votre clé API Mistral
3. Déployez l'application

## 📋 Configuration requise

- Python 3.8+
- Clé API Mistral AI
- Dépendances listées dans `requirements.txt`

## 🔒 Sécurité

⚠️ **Important** : Ne jamais exposer votre clé API dans le code ou le dépôt Git.
- Utilisez toujours les secrets Streamlit ou variables d'environnement
- Le fichier `.gitignore` protège automatiquement `.streamlit/secrets.toml`

## 🛠️ Technologies utilisées

- **Streamlit** - Interface web
- **Mistral AI OCR** (`mistral-ocr-latest`) - API OCR officielle de Mistral
- **Pillow** - Traitement d'images
- **Python** - Backend

## 🔬 Fonctionnement technique

L'application utilise l'**API OCR dédiée de Mistral** :
- Pour les URLs : traitement direct via `client.ocr.process()`
- Pour les fichiers locaux : upload vers Mistral → URL signée → traitement OCR
- Modèle : `mistral-ocr-latest` (reconnaissance haute précision)
- Tarification : ~1$/1000 pages
- Support : jusqu'à 50 MB ou 1000 pages par requête

## 📝 Utilisation

1. Lancez l'application
2. Choisissez le type de fichier (PDF ou Image)
3. Sélectionnez la source (URL ou upload local)
4. Cliquez sur "Traiter"
5. Consultez les résultats et téléchargez le texte extrait