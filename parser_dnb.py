"""
Parser pour les fichiers DNB Mathalea
Extrait les questions individuelles des fichiers TEX
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class Question:
    """Structure d'une question DNB"""
    id: str
    annee: str
    session: str
    exercice: int
    numero: str
    texte_latex: str
    texte_brut: str
    images: List[str]
    equations: List[str]
    sous_questions: List['Question']
    type_question: str  # "principale" ou "sous-question"
    source_file: str


class DNBParser:
    """Parser pour les fichiers TEX du DNB"""

    def __init__(self):
        self.questions = []

    def parse_file_name(self, file_path: Path) -> Dict[str, Any]:
        """
        Extrait les métadonnées du nom de fichier
        Exemple: dnb_2022_06_ameriquenord_4.tex
        """
        name = file_path.stem
        parts = name.split('_')

        metadata = {
            'annee': parts[1] if len(parts) > 1 else 'unknown',
            'session': parts[3] if len(parts) > 3 else 'unknown',
            'exercice': int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0,
            'source_file': file_path.name
        }

        return metadata

    def clean_latex_text(self, text: str) -> str:
        """
        Nettoie le texte LaTeX pour en extraire une version lisible
        """
        # Supprimer les commandes LaTeX simples
        text = re.sub(r'\\textbf\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\emph\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\textit\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\og\s*', '"', text)
        text = re.sub(r'\s*\\fg', '"', text)
        text = re.sub(r'\\degres', '°', text)

        # Supprimer commandes de mise en page
        text = re.sub(r'\\(medskip|smallskip|bigskip|noindent)', '', text)
        text = re.sub(r'\\begin\{center\}', '', text)
        text = re.sub(r'\\end\{center\}', '', text)

        # Nettoyer espaces multiples
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    def extract_images(self, text: str) -> List[str]:
        """
        Extrait les références d'images du texte LaTeX
        """
        images = []

        # \includegraphics{nom}
        includes = re.findall(r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}', text)
        images.extend(includes)

        # Détecter dessins inline
        if 'pspicture' in text:
            images.append('[dessin_pspicture]')

        if '\\begin{scratch}' in text or 'scratch' in text.lower():
            images.append('[code_scratch]')

        if '\\begin{tabular}' in text:
            images.append('[tableau]')

        return images

    def extract_equations(self, text: str) -> List[str]:
        """
        Extrait les équations LaTeX du texte
        """
        equations = []

        # Équations inline $...$
        inline = re.findall(r'\$([^$]+)\$', text)
        equations.extend([f"${eq}$" for eq in inline])

        # Équations display \[...\]
        display = re.findall(r'\\\[(.*?)\\\]', text, re.DOTALL)
        equations.extend([f"\\[{eq}\\]" for eq in display])

        return equations

    def parse_enumerate(self, text: str, metadata: Dict, parent_num: str = "") -> List[Question]:
        """
        Parse récursivement les environnements enumerate
        """
        questions = []

        # Trouver le premier \begin{enumerate}...\end{enumerate}
        pattern = r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}'

        match = re.search(pattern, text, re.DOTALL)
        if not match:
            return questions

        enum_content = match.group(1)

        # Découper par \item
        items = re.split(r'\\item\s+', enum_content)

        for i, item_text in enumerate(items[1:], 1):  # Skip premier élément vide
            if not item_text.strip():
                continue

            # Numéro de la question
            if parent_num:
                numero = f"{parent_num}.{i}"
            else:
                numero = str(i)

            # ID unique
            question_id = f"{metadata['source_file'].replace('.tex', '')}_{numero.replace('.', '_')}"

            # Extraire images et équations
            images = self.extract_images(item_text)
            equations = self.extract_equations(item_text)

            # Chercher sous-questions
            sous_questions = []
            if '\\begin{enumerate}' in item_text:
                sous_questions = self.parse_enumerate(item_text, metadata, numero)
                # Retirer le contenu des sous-questions du texte principal
                item_text = re.sub(pattern, '', item_text, count=1, flags=re.DOTALL)

            # Nettoyer le texte
            texte_brut = self.clean_latex_text(item_text)

            question = Question(
                id=question_id,
                annee=metadata['annee'],
                session=metadata['session'],
                exercice=metadata['exercice'],
                numero=numero,
                texte_latex=item_text.strip(),
                texte_brut=texte_brut,
                images=images,
                equations=equations,
                sous_questions=sous_questions,
                type_question="principale" if not parent_num else "sous-question",
                source_file=metadata['source_file']
            )

            questions.append(question)

        return questions

    def parse_tex_file(self, file_path: Path) -> List[Question]:
        """
        Parse un fichier TEX complet
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Erreur lecture {file_path}: {e}")
            return []

        # Extraire métadonnées du nom de fichier
        metadata = self.parse_file_name(file_path)

        # Parser les questions
        questions = self.parse_enumerate(content, metadata)

        return questions

    def parse_directory(self, directory: Path, recursive: bool = True) -> List[Question]:
        """
        Parse tous les fichiers TEX d'un répertoire
        """
        all_questions = []

        pattern = "**/*.tex" if recursive else "*.tex"

        for tex_file in directory.glob(pattern):
            # Skip les corrections
            if "_cor" in tex_file.name:
                continue

            print(f"📄 Parsing {tex_file.name}...")
            questions = self.parse_tex_file(tex_file)
            all_questions.extend(questions)

        return all_questions

    def to_json(self, questions: List[Question]) -> str:
        """
        Convertit la liste de questions en JSON
        """
        # Convertir les dataclasses en dicts
        def convert_question(q: Question) -> Dict:
            d = asdict(q)
            # Convertir récursivement les sous-questions
            d['sous_questions'] = [convert_question(sq) for sq in q.sous_questions]
            return d

        questions_dict = [convert_question(q) for q in questions]
        return json.dumps(questions_dict, indent=2, ensure_ascii=False)

    def get_statistics(self, questions: List[Question]) -> Dict[str, Any]:
        """
        Calcule des statistiques sur les questions extraites
        """
        total_questions = len(questions)
        avec_images = len([q for q in questions if q.images])
        avec_equations = len([q for q in questions if q.equations])
        avec_sous_questions = len([q for q in questions if q.sous_questions])

        # Compter par année
        par_annee = {}
        for q in questions:
            par_annee[q.annee] = par_annee.get(q.annee, 0) + 1

        # Compter types d'images
        types_images = {
            'images_externes': 0,
            'dessins_pspicture': 0,
            'code_scratch': 0,
            'tableaux': 0
        }

        for q in questions:
            for img in q.images:
                if '[dessin_pspicture]' in img:
                    types_images['dessins_pspicture'] += 1
                elif '[code_scratch]' in img:
                    types_images['code_scratch'] += 1
                elif '[tableau]' in img:
                    types_images['tableaux'] += 1
                else:
                    types_images['images_externes'] += 1

        return {
            'total_questions': total_questions,
            'avec_images': avec_images,
            'avec_equations': avec_equations,
            'avec_sous_questions': avec_sous_questions,
            'par_annee': par_annee,
            'types_images': types_images
        }


if __name__ == "__main__":
    # Test rapide
    parser = DNBParser()

    # Test sur un fichier
    test_file = Path("/tmp/dnb/2022/tex/dnb_2022_06_ameriquenord_4.tex")
    if test_file.exists():
        questions = parser.parse_tex_file(test_file)
        print(f"\n✅ Extrait {len(questions)} questions")

        for q in questions[:3]:  # Afficher les 3 premières
            print(f"\n🔹 Question {q.numero}:")
            print(f"   Texte: {q.texte_brut[:100]}...")
            print(f"   Images: {q.images}")
            print(f"   Équations: {len(q.equations)}")
