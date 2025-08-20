## Installation
 
Pour travailler ou utiliser ce référentiel, suivez les étapes ci-dessous :

1. Ouvrir le dossier dans un terminal

2. Aller dans le dossier du backend:
```bash
cd back
```

3. Créer un environnement virtuel nommé venv:
```bash
python -m venv venv
``` 

4. Activer l'environnement virtuel
```bash
venv\Scripts\activate
```

5. Installer Django et les dépendances du projet:
```bash
pip install -r requirements.txt
```

6. Demarrer le serveur d'application django:
```bash
python manage.py runserver
```

## PDF des devis

Les PDF sont générés lors de la création d’un devis. Le backend tente d’abord un rendu fidèle via Playwright en ouvrant la page front `/print/quotes/:id` et en exportant en PDF. En cas d’échec (navigateur non installé, etc.), un rendu minimal via ReportLab est utilisé.

Configuration:
- FRONTEND_BASE_URL: URL du front (ex: http://localhost:3000)
- Installation Playwright/Chromium dans l’environnement Python:
	- pip install playwright
	- python -m playwright install chromium

Notes:
- L’auth est gérée par cookie JWT déposé dans le contexte Playwright si le créateur du devis est connu.
- Le PDF est stocké dans le champ `Quote.pdf` et nommé d’après `Quote.number`.
