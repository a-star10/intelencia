#!/usr/bin/env python3
"""
Script d'import des équivalences diplômes par défaut
Exécuter : python import_equivalences.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.database import db_manager

def get_default_equivalences():
    """Récupérer les équivalences par défaut"""
    
    return [
        ("C.M.E", "C.T.E"),
        ("C.M.1", "C.T.1"),
        ("C.M.2", "C.T.2"),
        ("B.M.P.1", "B.M.P.2"),
    ]

def import_equivalences():
    """Importer les équivalences par défaut"""
    print("🚀 Import des équivalences diplômes par défaut...")
    print()
    
    equivalences = get_default_equivalences()
    
    print(f"📋 {len(equivalences)} équivalence(s) à importer")
    print()
    
    # Vérifier si des équivalences existent déjà
    existing = db_manager.get_all_equivalences()
    if existing:
        print(f"⚠️  {len(existing)} équivalence(s) existe(nt) déjà")
        response = input("Voulez-vous continuer et ajouter les nouvelles ? (y/N): ")
        if response.lower() != 'y':
            print("❌ Import annulé")
            return
    
    # Importer chaque équivalence
    success_count = 0
    skip_count = 0
    
    for diplome_principal, diplome_equivalent in equivalences:
        # Vérifier si existe déjà
        existing_equiv = db_manager.get_equivalence(diplome_principal, diplome_equivalent)
        
        if existing_equiv:
            print(f"⏭️  {diplome_principal} ↔️ {diplome_equivalent} (existe déjà)")
            skip_count += 1
            continue
        
        try:
            equiv_id = db_manager.create_equivalence(diplome_principal, diplome_equivalent)
            if equiv_id:
                success_count += 1
                print(f"✅ {diplome_principal} ↔️ {diplome_equivalent}")
            else:
                print(f"❌ Erreur: {diplome_principal} ↔️ {diplome_equivalent}")
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print()
    print("=" * 60)
    print(f"✅ Import terminé !")
    print(f"📊 Résultats:")
    print(f"   - Équivalences importées: {success_count}")
    print(f"   - Déjà existantes: {skip_count}")
    print(f"   - Total en base: {len(db_manager.get_all_equivalences())} équivalence(s)")
    print()
    print("🎯 Vous pouvez maintenant visualiser et gérer les équivalences dans l'application !")

if __name__ == "__main__":
    try:
        import_equivalences()
    except KeyboardInterrupt:
        print("\n❌ Import interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors de l'import: {e}")