#!/usr/bin/env python3
"""
Script de migration pour créer/mettre à jour la table regles_avancement
Exécuter une seule fois : python migrate_rules_table.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.database import db_manager

def migrate_rules_table():
    """Créer ou mettre à jour la table regles_avancement"""
    print("🔄 Début de la migration de la table regles_avancement...")
    
    try:
        with db_manager.get_connection() as conn:
            # Vérifier si la table existe
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='regles_avancement'
            """)
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                print("⚠️  La table regles_avancement existe déjà")
                response = input("Voulez-vous la recréer ? (y/N): ")
                if response.lower() != 'y':
                    print("❌ Migration annulée")
                    return
                
                # Supprimer l'ancienne table
                conn.execute("DROP TABLE regles_avancement")
                print("🗑️  Ancienne table supprimée")
            
            # Créer la nouvelle table
            conn.execute("""
                CREATE TABLE regles_avancement (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    categorie TEXT NOT NULL,
                    grade_source TEXT NOT NULL,
                    grade_cible TEXT NOT NULL,
                    type_avancement TEXT DEFAULT 'Normal',
                    
                    anciennete_service_min INTEGER DEFAULT 0,
                    anciennete_grade_min INTEGER DEFAULT 0,
                    grade_specifique TEXT,
                    anciennete_grade_specifique INTEGER DEFAULT 0,
                    
                    diplomes_requis TEXT,
                    note_min_courante TEXT,
                    notes_interdites_n1_n2 TEXT,
                    
                    conditions_speciales TEXT,
                    
                    statut TEXT DEFAULT 'Actif',
                    actif BOOLEAN DEFAULT 1,
                    
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            print("✅ Table regles_avancement créée avec succès !")
            print("\n📋 Structure de la table :")
            print("   - Catégorie, grades source/cible, type avancement")
            print("   - Conditions d'ancienneté (service, grade, grade spécifique)")
            print("   - Diplômes requis, notes minimales, notes interdites")
            print("   - Conditions spéciales, statut, actif")
            
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return
    
    print("\n✅ Migration terminée avec succès !")
    print("Vous pouvez maintenant créer des règles depuis l'interface.")

if __name__ == "__main__":
    migrate_rules_table()