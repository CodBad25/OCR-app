"""
Module d'analyse OCR pour les images du DNB
Analyse les images avec Mistral AI et génère des descriptions
"""

from pathlib import Path
from typing import Dict, List, Optional
from mistralai import Mistral
from mistralai.models import DocumentURLChunk, ImageURLChunk, TextChunk
import base64
import subprocess
import tempfile
from PIL import Image
import io


class ImageAnalyzer:
    """Analyse les images des exercices DNB avec Mistral AI"""

    def __init__(self, api_key: str):
        self.client = Mistral(api_key=api_key)

    def convert_eps_to_png(self, eps_path: Path) -> Optional[Path]:
        """
        Convertit un fichier EPS en PNG
        Nécessite Ghostscript installé
        """
        try:
            png_path = eps_path.with_suffix('.png')

            # Utiliser Ghostscript pour convertir
            cmd = [
                'gs',
                '-dSAFER',
                '-dBATCH',
                '-dNOPAUSE',
                '-dEPSCrop',
                '-sDEVICE=png16m',
                '-r150',
                f'-sOutputFile={png_path}',
                str(eps_path)
            ]

            subprocess.run(cmd, capture_output=True, check=True)

            if png_path.exists():
                return png_path
        except Exception as e:
            print(f"Erreur conversion EPS→PNG: {e}")

        return None

    def render_pspicture_to_png(self, pspicture_code: str, output_path: Path) -> bool:
        """
        Rend un code pspicture en PNG
        Crée un document LaTeX minimal et le compile
        """
        try:
            # Créer un document LaTeX minimal
            latex_doc = f"""
\\documentclass[border=2pt]{{standalone}}
\\usepackage{{pstricks}}
\\usepackage{{pst-plot}}
\\begin{{document}}
{pspicture_code}
\\end{{document}}
"""

            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
                f.write(latex_doc)
                tex_path = Path(f.name)

            # Compiler avec LaTeX → DVI → PNG
            # Note : Ceci nécessite latex, dvips, et gs installés

            # 1. Compiler en DVI
            subprocess.run(['latex', '-interaction=nonstopmode', str(tex_path)],
                          capture_output=True, cwd=tex_path.parent)

            dvi_path = tex_path.with_suffix('.dvi')

            # 2. Convertir DVI → PS
            ps_path = tex_path.with_suffix('.ps')
            subprocess.run(['dvips', str(dvi_path), '-o', str(ps_path)],
                          capture_output=True)

            # 3. Convertir PS → PNG
            subprocess.run(['gs', '-dSAFER', '-dBATCH', '-dNOPAUSE',
                          '-sDEVICE=png16m', '-r150',
                          f'-sOutputFile={output_path}', str(ps_path)],
                          capture_output=True)

            # Nettoyer fichiers temporaires
            for ext in ['.tex', '.dvi', '.ps', '.aux', '.log']:
                temp_file = tex_path.with_suffix(ext)
                if temp_file.exists():
                    temp_file.unlink()

            return output_path.exists()

        except Exception as e:
            print(f"Erreur rendu pspicture: {e}")
            return False

    def analyze_image_with_ocr(self, image_path: Path) -> Dict[str, str]:
        """
        Analyse une image avec Mistral OCR
        Retourne le texte extrait et une description intelligente
        """
        try:
            # Upload du fichier
            with open(image_path, 'rb') as f:
                uploaded_file = self.client.files.upload(
                    file={
                        "file_name": image_path.name,
                        "content": f.read(),
                    },
                    purpose="ocr",
                )

            # Obtenir URL signée
            signed_url = self.client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)

            # OCR
            ocr_response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document=DocumentURLChunk(document_url=signed_url.url),
                include_image_base64=False
            )

            # Extraire le texte
            text_content = "\n\n".join([page.markdown for page in ocr_response.pages])

            # Générer description intelligente avec Pixtral
            with open(image_path, 'rb') as f:
                img_base64 = base64.b64encode(f.read()).decode('utf-8')
                img_data_url = f"data:image/png;base64,{img_base64}"

            description_response = self.client.chat.complete(
                model="pixtral-12b-latest",
                messages=[{
                    "role": "user",
                    "content": [
                        ImageURLChunk(image_url=img_data_url),
                        TextChunk(text=f"""Analyse ce schéma/image d'un exercice de mathématiques du Brevet (DNB).

Texte OCR extrait : {text_content[:500]}

Fournis une description détaillée en français incluant :
1. Type d'image (schéma géométrique, graphique, tableau, photo, etc.)
2. Éléments principaux visibles
3. Mesures ou valeurs indiquées
4. Contexte mathématique (théorème concerné, type de problème)

Sois concis mais précis (3-5 lignes max).""")
                    ]
                }],
                temperature=0.3
            )

            description = description_response.choices[0].message.content

            return {
                "ocr_text": text_content,
                "description": description,
                "status": "success"
            }

        except Exception as e:
            return {
                "ocr_text": "",
                "description": f"Erreur lors de l'analyse: {str(e)}",
                "status": "error"
            }

    def analyze_scratch_code(self, scratch_latex: str) -> str:
        """
        Analyse un code Scratch en LaTeX et génère une description
        """
        # Utiliser Mistral pour comprendre le code Scratch
        response = self.client.chat.complete(
            model="mistral-large-latest",
            messages=[{
                "role": "user",
                "content": f"""Analyse ce code Scratch écrit en LaTeX et décris son fonctionnement en français :

{scratch_latex[:1000]}

Fournis :
1. Objectif du programme (1 ligne)
2. Étapes principales (3-4 points)
3. Résultat attendu (1 ligne)

Sois concis et pédagogique."""
            }],
            temperature=0.3
        )

        return response.choices[0].message.content

    def analyze_tableau(self, tableau_latex: str) -> str:
        """
        Analyse un tableau LaTeX et génère une description
        """
        response = self.client.chat.complete(
            model="mistral-large-latest",
            messages=[{
                "role": "user",
                "content": f"""Analyse ce tableau écrit en LaTeX et décris son contenu :

{tableau_latex[:800]}

Fournis une description concise (2-3 lignes) mentionnant :
- Type de données
- Nombre de lignes/colonnes
- Informations principales

Format : Description directe, pas de "Ce tableau..."."""
            }],
            temperature=0.3
        )

        return response.choices[0].message.content

    def process_question_images(self, question_data: Dict, dnb_base_path: Path) -> Dict:
        """
        Traite toutes les images d'une question et ajoute les analyses
        """
        if not question_data.get('images'):
            return question_data

        analyses = []

        for image_ref in question_data['images']:
            analysis = {
                'reference': image_ref,
                'type': 'unknown',
                'ocr_text': '',
                'description': ''
            }

            # Déterminer le type d'image
            if '[dessin_pspicture]' in image_ref:
                analysis['type'] = 'pspicture'
                analysis['description'] = "Dessin géométrique inline (pspicture LaTeX)"
                # TODO: Extraire et rendre le code pspicture

            elif '[code_scratch]' in image_ref:
                analysis['type'] = 'scratch'
                # TODO: Extraire le code Scratch et l'analyser
                analysis['description'] = "Code de programmation Scratch"

            elif '[tableau]' in image_ref:
                analysis['type'] = 'tableau'
                # TODO: Extraire le tableau et l'analyser
                analysis['description'] = "Tableau de données"

            else:
                # Image externe (EPS/PNG)
                analysis['type'] = 'image_externe'

                # Chercher l'image dans le repo DNB
                annee = question_data.get('annee', '2022')
                image_name = image_ref.replace('.eps', '').replace('.png', '')

                # Chemins possibles
                possible_paths = [
                    dnb_base_path / annee / 'tex' / 'eps' / f'{image_name}.eps',
                    dnb_base_path / annee / 'tex' / 'png' / f'{image_name}.png',
                    dnb_base_path / annee / 'tex' / f'{image_name}.eps',
                    dnb_base_path / annee / 'tex' / f'{image_name}.png',
                ]

                for img_path in possible_paths:
                    if img_path.exists():
                        print(f"  📷 Analyse de {img_path.name}...")

                        # Convertir EPS en PNG si nécessaire
                        if img_path.suffix == '.eps':
                            png_path = self.convert_eps_to_png(img_path)
                            if png_path:
                                img_path = png_path

                        # Analyser avec OCR
                        if img_path.suffix == '.png':
                            ocr_result = self.analyze_image_with_ocr(img_path)
                            analysis.update(ocr_result)

                        break

            analyses.append(analysis)

        question_data['images_analyses'] = analyses
        return question_data


if __name__ == "__main__":
    # Test rapide
    import os

    api_key = os.getenv('MISTRAL_API_KEY')
    if api_key:
        analyzer = ImageAnalyzer(api_key)

        # Test sur une image exemple
        test_img = Path("/tmp/dnb/2022/tex/eps/Pomp.eps")
        if test_img.exists():
            print("Test d'analyse d'image...")
            # Convertir d'abord
            png = analyzer.convert_eps_to_png(test_img)
            if png:
                result = analyzer.analyze_image_with_ocr(png)
                print(f"Description: {result['description']}")
    else:
        print("⚠️ MISTRAL_API_KEY non définie")
