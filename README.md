# Mistral OCR App

Cette application Streamlit permet d'utiliser l'OCR avec l'API Mistral.

## Déploiement sur Streamlit Cloud ou Render

1. **Cloner ce dépôt sur la plateforme de votre choix (Streamlit Cloud, Render, etc.).**
2. **Ajouter la clé API Mistral comme variable d'environnement** :
   - Sur Streamlit Cloud : Paramètres > Secrets > Ajouter `MISTRAL_API_KEY`
   - Sur Render : Settings > Environment > Add Secret `MISTRAL_API_KEY`
3. **Installer les dépendances** (automatique si requirements.txt est présent).
4. **Lancer l'application** :
   - Sur Streamlit Cloud, le lancement est automatique.
   - En local :
     ```bash
     streamlit run main.py
     ```

## Configuration requise
- Python 3.8+
- Fichier `requirements.txt` présent

## Sécurité
Ne jamais exposer la clé API dans le code. Utilisez toujours les variables d'environnement/secrets proposés par la plateforme d'hébergement.