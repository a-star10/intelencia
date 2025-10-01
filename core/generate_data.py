# generate_data.py
import sys
from pathlib import Path

# Ajouter le chemin racine
sys.path.append(str(Path(__file__).parent))

from core.data_generator import data_generator

if __name__ == "__main__":
    print("🚀 Generation des donnees de test...")
    data_generator.populate_database(30)
    print("✅ Termine !")