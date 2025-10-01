#!/usr/bin/env python3
"""
Script de migration pour ajouter la table historique_grades
Exécuter UNE SEULE FOIS : python migrate_historique_grades.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.database import db_manager
from datetime import date, timedelta

def migrate_historique_grades():
    """Créer la table historique_grades et migrer les données existantes"""
    print("🚀 Début de la migration - Ajout historique des grades")
    print("=" * 70)
    
    try:
        with db_manager.get_connection() as conn:
            # 1. Créer la table historique_grades
            print("\n1️⃣ Création de la table historique_grades...")
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS historique_grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id INTEGER NOT NULL,
                    grade TEXT NOT NULL,
                    date_debut DATE NOT NULL,
                    date_fin DATE,
                    duree_mois INTEGER,
                    actif BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
                )
            """)
            
            # Index pour optimiser les requêtes
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_historique_agent 
                ON historique_grades(agent_id, date_debut)
            """)
            
            conn.commit()
            print("   ✅ Table créée avec succès")
            
            # 2. Migrer les données existantes
            print("\n2️⃣ Migration des données existantes...")
            
            cursor = conn.execute("""
                SELECT id, matricule, grade_actuel, date_incorporation, date_entree_grade 
                FROM agents
            """)
            agents = cursor.fetchall()
            
            migrated_count = 0
            for agent in agents:
                agent_id = agent['id']
                grade_actuel = agent['grade_actuel']
                date_entree_grade = agent['date_entree_grade']
                
                if date_entree_grade:
                    # Ajouter une entrée pour le grade actuel
                    conn.execute("""
                        INSERT INTO historique_grades 
                        (agent_id, grade, date_debut, date_fin, actif)
                        VALUES (?, ?, ?, NULL, 1)
                    """, (agent_id, grade_actuel, date_entree_grade))
                    migrated_count += 1
                    
                    print(f"   ✅ {agent['matricule']}: {grade_actuel} depuis {date_entree_grade}")
            
            conn.commit()
            print(f"\n   📊 {migrated_count} entrées d'historique créées")
            
            # 3. Vérification
            print("\n3️⃣ Vérification de la migration...")
            
            count = conn.execute("SELECT COUNT(*) FROM historique_grades").fetchone()[0]
            print(f"   📊 Total entrées dans historique_grades: {count}")
            
            print("\n" + "=" * 70)
            print("✅ MIGRATION RÉUSSIE !")
            print("\nLa table historique_grades est maintenant disponible.")
            print("Vous pouvez maintenant utiliser le moteur d'évaluation Option C.")
            
    except Exception as e:
        print(f"\n❌ ERREUR lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = migrate_historique_grades()
    if not success:
        sys.exit(1)