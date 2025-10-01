"""
Configuration de l'application Military Career Manager
"""
from pathlib import Path
from datetime import datetime

# Chemins
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
ASSETS_DIR = PROJECT_ROOT / "assets"
EXPORTS_DIR = DATA_DIR / "exports"

# Base de donnees
DATABASE_PATH = DATA_DIR / "military_careers.db"

# Interface
APP_TITLE = "Military Career Manager"
APP_VERSION = "1.0.0"
WINDOW_SIZE = "1400x900"
MIN_WINDOW_SIZE = "1200x700"

# Grades militaires
GRADES_HIERARCHY = [
    "2e Classe",
    "Caporal", 
    "Caporal-chef",
    "Sergent",
    "Sergent-chef", 
    "Sergent-chef-Major",
    "Adjudant",
    "Adjudant-chef",
    "Adjudant-chef Major",
    "Sous-Lieutenant",
    "Lieutenant", 
    "Capitaine",
    "Commandant",
    "Lieutenant-Colonel",
    "Colonel",
    "General de Brigade",
    "General de Division"
]

# Notes par defaut
ECHELLE_NOTES_DEFAULT = [
    ("TB", 4, "Tres Bien"),
    ("B", 3, "Bien"), 
    ("AB", 2, "Assez Bien"),
    ("P", 1, "Passable"),
    ("I", 0, "Insuffisant")
]

# Statuts
STATUTS_AGENT = ["Actif", "Radie", "En conge", "Detache"]

# Annee de reference
ANNEE_REFERENCE = datetime.now().year

print(f"Configuration chargee - Annee: {ANNEE_REFERENCE}")
