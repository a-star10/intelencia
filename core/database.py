"""
Gestionnaire de base de donnees SQLite - VERSION COMPLETE CORRIGÉE
core/database.py
"""
import sqlite3
import logging
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import sys

# Import config
sys.path.append(str(Path(__file__).parent.parent))
from config import DATABASE_PATH, ECHELLE_NOTES_DEFAULT

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestionnaire de la base de donnees SQLite avec gestion amelioree des verrous"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DATABASE_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Obtenir une connexion a la base de donnees avec timeout"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        return conn
    
    def init_database(self):
        """Initialiser la base de donnees avec les tables"""
        print("🗄️ Initialisation de la base de donnees...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.get_connection() as conn:
                    # Table agents
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS agents (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            statut TEXT DEFAULT 'Actif',
                            matricule TEXT UNIQUE NOT NULL,
                            nom TEXT NOT NULL,
                            prenom TEXT NOT NULL,
                            date_naissance DATE NOT NULL,
                            age INTEGER,
                            
                            grade_actuel TEXT NOT NULL,
                            date_incorporation DATE NOT NULL,
                            date_entree_grade DATE NOT NULL,
                            anciennete_service REAL,
                            anciennete_grade REAL,
                            
                            ecole TEXT,
                            note_annee_moins_2 TEXT,
                            note_annee_moins_1 TEXT,
                            note_annee_courante TEXT,
                            statut_disciplinaire TEXT DEFAULT 'RAS',
                            
                            unite_provenance TEXT,
                            
                            resultat_evaluation TEXT,
                            derniere_evaluation DATETIME,
                            
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Table historique diplomes
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS diplomes_historique (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            agent_id INTEGER,
                            diplome TEXT NOT NULL,
                            date_obtention DATE NOT NULL,
                            etablissement TEXT,
                            actif BOOLEAN DEFAULT 1,
                            FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
                        )
                    """)
                    
                    # Table regles d'avancement - VERSION COMPLETE
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS regles_avancement (
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
                    
                    # Table echelles de notes
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS echelles_notes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            note TEXT UNIQUE NOT NULL,
                            valeur_numerique INTEGER,
                            description TEXT,
                            actif BOOLEAN DEFAULT 1
                        )
                    """)
                    
                    # Table equivalences diplomes
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS equivalences_diplomes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            diplome_principal TEXT NOT NULL,
                            diplome_equivalent TEXT NOT NULL,
                            actif BOOLEAN DEFAULT 1,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Inserer echelle de notes par defaut si vide
                    existing_notes = conn.execute("SELECT COUNT(*) FROM echelles_notes").fetchone()[0]
                    if existing_notes == 0:
                        for note, valeur, description in ECHELLE_NOTES_DEFAULT:
                            conn.execute("""
                                INSERT INTO echelles_notes (note, valeur_numerique, description)
                                VALUES (?, ?, ?)
                            """, (note, valeur, description))
                        print("✅ Echelle de notes initialisee")
                    
                    conn.commit()
                    print("✅ Base de donnees initialisee avec succes")
                    return
                    
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"⚠️ Base verrouillée, tentative {attempt + 1}/{max_retries}")
                    time.sleep(1)
                    continue
                else:
                    raise e

    # ==================== GESTION DES AGENTS ====================
    
    def create_agent(self, agent_data: Dict[str, Any]) -> int:
        """Creer un nouvel agent avec retry automatique"""
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                with self.get_connection() as conn:
                    cursor = conn.execute("""
                        INSERT INTO agents (
                            statut, matricule, nom, prenom, date_naissance, age,
                            grade_actuel, date_incorporation, date_entree_grade,
                            anciennete_service, anciennete_grade, ecole,
                            note_annee_moins_2, note_annee_moins_1, note_annee_courante,
                            statut_disciplinaire, unite_provenance
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        agent_data.get('statut', 'Actif'),
                        agent_data['matricule'],
                        agent_data['nom'],
                        agent_data['prenom'],
                        agent_data['date_naissance'],
                        agent_data.get('age'),
                        agent_data['grade_actuel'],
                        agent_data['date_incorporation'],
                        agent_data['date_entree_grade'],
                        agent_data.get('anciennete_service'),
                        agent_data.get('anciennete_grade'),
                        agent_data.get('ecole', ''),
                        agent_data.get('note_annee_moins_2', ''),
                        agent_data.get('note_annee_moins_1', ''),
                        agent_data.get('note_annee_courante', ''),
                        agent_data.get('statut_disciplinaire', 'RAS'),
                        agent_data.get('unite_provenance', '')
                    ))
                    agent_id = cursor.lastrowid
                    
                    # Ajouter les diplomes si presents
                    if 'diplomes' in agent_data and agent_data['diplomes']:
                        for diplome in agent_data['diplomes']:
                            try:
                                self._add_diplome_direct(conn, agent_id, diplome)
                            except Exception as diplome_error:
                                print(f"⚠️ Erreur diplome pour {agent_data['matricule']}: {diplome_error}")
                    
                    conn.commit()
                    print(f"✅ Agent {agent_data['matricule']} cree avec ID {agent_id}")
                    return agent_id
                    
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    wait_time = 0.1 * (2 ** attempt)
                    print(f"⚠️ DB locked, retry {attempt + 1}/{max_retries} (wait {wait_time}s)")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Erreur DB pour {agent_data.get('matricule', 'UNKNOWN')}: {e}")
                    return None
                    
            except Exception as e:
                print(f"❌ Erreur insertion {agent_data.get('matricule', 'UNKNOWN')}: {e}")
                return None
        
        print(f"❌ Echec final pour {agent_data.get('matricule', 'UNKNOWN')} après {max_retries} tentatives")
        return None
    
    def _add_diplome_direct(self, conn: sqlite3.Connection, agent_id: int, diplome_data: Dict[str, Any]):
        """Ajouter un diplome directement avec une connexion existante"""
        conn.execute("""
            INSERT INTO diplomes_historique (agent_id, diplome, date_obtention, etablissement)
            VALUES (?, ?, ?, ?)
        """, (
            agent_id,
            diplome_data['nom'],
            diplome_data['date_obtention'],
            diplome_data.get('etablissement', '')
        ))
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Recuperer tous les agents"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                with self.get_connection() as conn:
                    cursor = conn.execute("""
                        SELECT * FROM agents 
                        ORDER BY grade_actuel, nom, prenom
                    """)
                    agents = [dict(row) for row in cursor.fetchall()]
                    
                    # Ajouter les diplomes pour chaque agent
                    for agent in agents:
                        agent['diplomes'] = self.get_diplomes_by_agent(agent['id'])
                    
                    return agents
                    
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.1)
                    continue
                else:
                    raise e
        
        return []
    
    def get_agent_by_id(self, agent_id: int) -> Optional[Dict[str, Any]]:
        """Recuperer un agent par son ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
                row = cursor.fetchone()
                if row:
                    agent = dict(row)
                    agent['diplomes'] = self.get_diplomes_by_agent(agent_id)
                    return agent
        except Exception as e:
            print(f"❌ Erreur get_agent_by_id: {e}")
        return None
    
    def get_agent_by_matricule(self, matricule: str) -> Optional[Dict[str, Any]]:
        """Recuperer un agent par son matricule"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM agents WHERE matricule = ?", (matricule,))
                row = cursor.fetchone()
                if row:
                    agent = dict(row)
                    agent['diplomes'] = self.get_diplomes_by_agent(agent['id'])
                    return agent
        except Exception as e:
            print(f"❌ Erreur get_agent_by_matricule: {e}")
        return None
    
    def update_agent(self, agent_id: int, agent_data: Dict[str, Any]) -> bool:
        """Mettre a jour un agent - VERSION CORRIGÉE AVEC GESTION DIPLÔMES"""
        try:
            with self.get_connection() as conn:
                # ===== PARTIE 1: Mettre à jour les champs de base =====
                fields = []
                values = []
                
                for field, value in agent_data.items():
                    # Ignorer 'id' et 'diplomes' pour la mise à jour des champs
                    if field != 'id' and field != 'diplomes':
                        fields.append(f"{field} = ?")
                        values.append(value)
                
                if fields:
                    fields.append("updated_at = ?")
                    values.append(datetime.now().isoformat())
                    values.append(agent_id)
                    
                    query = f"UPDATE agents SET {', '.join(fields)} WHERE id = ?"
                    conn.execute(query, values)
                
                # ===== PARTIE 2: Gérer les diplômes (NOUVEAU) =====
                if 'diplomes' in agent_data:
                    # 1. Supprimer tous les anciens diplômes de cet agent
                    conn.execute("""
                        DELETE FROM diplomes_historique WHERE agent_id = ?
                    """, (agent_id,))
                    
                    # 2. Ajouter les nouveaux diplômes
                    for diplome in agent_data['diplomes']:
                        # Gérer les deux formats possibles
                        diplome_nom = diplome.get('nom') or diplome.get('diplome', '')
                        diplome_date = diplome.get('date_obtention', '')
                        diplome_etablissement = diplome.get('etablissement', '')
                        
                        if diplome_nom:  # N'ajouter que si le diplôme a un nom
                            # Convertir la date si c'est une string
                            if isinstance(diplome_date, str) and diplome_date:
                                try:
                                    from datetime import datetime as dt
                                    diplome_date = dt.strptime(diplome_date, '%Y-%m-%d').date().isoformat()
                                except:
                                    diplome_date = diplome_date  # Garder tel quel si erreur
                            
                            conn.execute("""
                                INSERT INTO diplomes_historique (agent_id, diplome, date_obtention, etablissement, actif)
                                VALUES (?, ?, ?, ?, 1)
                            """, (agent_id, diplome_nom, diplome_date, diplome_etablissement))
                
                # Valider toutes les modifications
                conn.commit()
                
                print(f"✅ Agent ID {agent_id} mis a jour (y compris {len(agent_data.get('diplomes', []))} diplome(s))")
                return True
                
        except Exception as e:
            print(f"❌ Erreur mise a jour agent: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete_agent(self, agent_id: int) -> bool:
        """Supprimer un agent"""
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
                conn.commit()
                print(f"✅ Agent ID {agent_id} supprime")
                return True
        except Exception as e:
            print(f"❌ Erreur suppression agent: {e}")
            return False
    
    # ==================== GESTION DES DIPLOMES ====================
    
    def add_diplome_to_agent(self, agent_id: int, diplome_data: Dict[str, Any]) -> int:
        """Ajouter un diplome a un agent"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO diplomes_historique (agent_id, diplome, date_obtention, etablissement)
                    VALUES (?, ?, ?, ?)
                """, (
                    agent_id,
                    diplome_data['nom'],
                    diplome_data['date_obtention'],
                    diplome_data.get('etablissement', '')
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"❌ Erreur ajout diplome: {e}")
            return None
    
    def get_diplomes_by_agent(self, agent_id: int) -> List[Dict[str, Any]]:
        """Recuperer les diplomes d'un agent"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM diplomes_historique 
                    WHERE agent_id = ? AND actif = 1
                    ORDER BY date_obtention DESC
                """, (agent_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erreur get_diplomes: {e}")
            return []
    
    # ==================== GESTION DES REGLES D'AVANCEMENT ====================
    
    def create_rule(self, rule_data: Dict[str, Any]) -> int:
        """Creer une nouvelle regle d'avancement"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO regles_avancement (
                        categorie, grade_source, grade_cible, type_avancement,
                        anciennete_service_min, anciennete_grade_min,
                        grade_specifique, anciennete_grade_specifique,
                        diplomes_requis, note_min_courante, notes_interdites_n1_n2,
                        conditions_speciales, statut, actif
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rule_data.get('categorie', ''),
                    rule_data['grade_source'],
                    rule_data['grade_cible'],
                    rule_data.get('type_avancement', 'Normal'),
                    rule_data.get('anciennete_service_min', 0),
                    rule_data.get('anciennete_grade_min', 0),
                    rule_data.get('grade_specifique'),
                    rule_data.get('anciennete_grade_specifique', 0),
                    ','.join(rule_data.get('diplomes_requis', [])),
                    rule_data.get('note_min_courante'),
                    ','.join(rule_data.get('notes_interdites_n1_n2', [])),
                    rule_data.get('conditions_speciales', ''),
                    rule_data.get('statut', 'Actif'),
                    1
                ))
                rule_id = cursor.lastrowid
                conn.commit()
                print(f"✅ Regle {rule_data['grade_source']} → {rule_data['grade_cible']} creee avec ID {rule_id}")
                return rule_id
        except Exception as e:
            print(f"❌ Erreur creation regle: {e}")
            return None
    
    def get_all_rules(self) -> List[Dict[str, Any]]:
        """Recuperer toutes les regles"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM regles_avancement 
                    WHERE actif = 1
                    ORDER BY 
                        CASE categorie
                            WHEN 'Militaires du rang' THEN 1
                            WHEN 'Sous-officiers' THEN 2
                            WHEN 'Officiers' THEN 3
                            ELSE 4
                        END,
                        grade_source
                """)
                rules = []
                for row in cursor.fetchall():
                    rule = dict(row)
                    # Convertir les listes de string en listes Python
                    if rule.get('diplomes_requis'):
                        rule['diplomes_requis'] = [d.strip() for d in rule['diplomes_requis'].split(',') if d.strip()]
                    else:
                        rule['diplomes_requis'] = []
                    
                    if rule.get('notes_interdites_n1_n2'):
                        rule['notes_interdites_n1_n2'] = [n.strip() for n in rule['notes_interdites_n1_n2'].split(',') if n.strip()]
                    else:
                        rule['notes_interdites_n1_n2'] = []
                    
                    rules.append(rule)
                return rules
        except Exception as e:
            print(f"❌ Erreur recuperation regles: {e}")
            return []
    
    def get_rule_by_id(self, rule_id: int) -> Optional[Dict[str, Any]]:
        """Recuperer une regle par son ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM regles_avancement WHERE id = ? AND actif = 1
                """, (rule_id,))
                row = cursor.fetchone()
                if row:
                    rule = dict(row)
                    # Convertir les listes
                    if rule.get('diplomes_requis'):
                        rule['diplomes_requis'] = [d.strip() for d in rule['diplomes_requis'].split(',') if d.strip()]
                    else:
                        rule['diplomes_requis'] = []
                    
                    if rule.get('notes_interdites_n1_n2'):
                        rule['notes_interdites_n1_n2'] = [n.strip() for n in rule['notes_interdites_n1_n2'].split(',') if n.strip()]
                    else:
                        rule['notes_interdites_n1_n2'] = []
                    
                    return rule
            return None
        except Exception as e:
            print(f"❌ Erreur get_rule_by_id: {e}")
            return None
    
    def update_rule(self, rule_id: int, rule_data: Dict[str, Any]) -> bool:
        """Mettre a jour une regle"""
        try:
            with self.get_connection() as conn:
                # Convertir les listes en strings
                diplomes_str = ','.join(rule_data.get('diplomes_requis', []))
                notes_interdites_str = ','.join(rule_data.get('notes_interdites_n1_n2', []))
                
                conn.execute("""
                    UPDATE regles_avancement SET
                        categorie = ?,
                        grade_source = ?,
                        grade_cible = ?,
                        type_avancement = ?,
                        anciennete_service_min = ?,
                        anciennete_grade_min = ?,
                        grade_specifique = ?,
                        anciennete_grade_specifique = ?,
                        diplomes_requis = ?,
                        note_min_courante = ?,
                        notes_interdites_n1_n2 = ?,
                        conditions_speciales = ?,
                        statut = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    rule_data.get('categorie', ''),
                    rule_data['grade_source'],
                    rule_data['grade_cible'],
                    rule_data.get('type_avancement', 'Normal'),
                    rule_data.get('anciennete_service_min', 0),
                    rule_data.get('anciennete_grade_min', 0),
                    rule_data.get('grade_specifique'),
                    rule_data.get('anciennete_grade_specifique', 0),
                    diplomes_str,
                    rule_data.get('note_min_courante'),
                    notes_interdites_str,
                    rule_data.get('conditions_speciales', ''),
                    rule_data.get('statut', 'Actif'),
                    rule_id
                ))
                conn.commit()
                print(f"✅ Regle ID {rule_id} mise a jour")
                return True
        except Exception as e:
            print(f"❌ Erreur mise a jour regle: {e}")
            return False
    
    def delete_rule(self, rule_id: int) -> bool:
        """Supprimer (desactiver) une regle"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    UPDATE regles_avancement SET actif = 0 WHERE id = ?
                """, (rule_id,))
                conn.commit()
                print(f"✅ Regle ID {rule_id} desactivee")
                return True
        except Exception as e:
            print(f"❌ Erreur suppression regle: {e}")
            return False
    
    def get_rules_by_grade(self, grade_source: str) -> List[Dict[str, Any]]:
        """Recuperer les regles pour un grade source donne"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM regles_avancement 
                    WHERE grade_source = ? AND actif = 1
                    ORDER BY type_avancement
                """, (grade_source,))
                rules = []
                for row in cursor.fetchall():
                    rule = dict(row)
                    # Convertir les listes
                    if rule.get('diplomes_requis'):
                        rule['diplomes_requis'] = [d.strip() for d in rule['diplomes_requis'].split(',') if d.strip()]
                    else:
                        rule['diplomes_requis'] = []
                    
                    if rule.get('notes_interdites_n1_n2'):
                        rule['notes_interdites_n1_n2'] = [n.strip() for n in rule['notes_interdites_n1_n2'].split(',') if n.strip()]
                    else:
                        rule['notes_interdites_n1_n2'] = []
                    
                    rules.append(rule)
                return rules
        except Exception as e:
            print(f"❌ Erreur get_rules_by_grade: {e}")
            return []
    
    def toggle_rule_status(self, rule_id: int) -> bool:
        """Activer/Desactiver une regle"""
        try:
            with self.get_connection() as conn:
                # Recuperer le statut actuel
                cursor = conn.execute("""
                    SELECT statut FROM regles_avancement WHERE id = ?
                """, (rule_id,))
                row = cursor.fetchone()
                
                if row:
                    current_status = row['statut']
                    new_status = 'Inactif' if current_status == 'Actif' else 'Actif'
                    
                    conn.execute("""
                        UPDATE regles_avancement SET statut = ? WHERE id = ?
                    """, (new_status, rule_id))
                    conn.commit()
                    print(f"✅ Regle ID {rule_id} changee de {current_status} a {new_status}")
                    return True
            return False
        except Exception as e:
            print(f"❌ Erreur toggle_rule_status: {e}")
            return False
    
    # ==================== GESTION DES EQUIVALENCES DIPLOMES ====================
    
    def create_equivalence(self, diplome_principal: str, diplome_equivalent: str) -> int:
        """Creer une nouvelle equivalence de diplome"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO equivalences_diplomes (diplome_principal, diplome_equivalent, actif)
                    VALUES (?, ?, 1)
                """, (diplome_principal, diplome_equivalent))
                equiv_id = cursor.lastrowid
                conn.commit()
                print(f"✅ Equivalence {diplome_principal} ↔️ {diplome_equivalent} creee avec ID {equiv_id}")
                return equiv_id
        except Exception as e:
            print(f"❌ Erreur creation equivalence: {e}")
            return None
    
    def get_all_equivalences(self) -> List[Dict[str, Any]]:
        """Recuperer toutes les equivalences"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM equivalences_diplomes 
                    WHERE actif = 1
                    ORDER BY diplome_principal, diplome_equivalent
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erreur recuperation equivalences: {e}")
            return []
    
    def get_equivalence_by_id(self, equiv_id: int) -> Optional[Dict[str, Any]]:
        """Recuperer une equivalence par son ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM equivalences_diplomes WHERE id = ?
                """, (equiv_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"❌ Erreur get_equivalence_by_id: {e}")
            return None
    
    def get_equivalence(self, diplome_principal: str, diplome_equivalent: str) -> Optional[Dict[str, Any]]:
        """Verifier si une equivalence existe deja (dans les deux sens)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM equivalences_diplomes 
                    WHERE (diplome_principal = ? AND diplome_equivalent = ?)
                       OR (diplome_principal = ? AND diplome_equivalent = ?)
                """, (diplome_principal, diplome_equivalent, diplome_equivalent, diplome_principal))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"❌ Erreur get_equivalence: {e}")
            return None
    
    def delete_equivalence(self, equiv_id: int) -> bool:
        """Supprimer une equivalence"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    UPDATE equivalences_diplomes SET actif = 0 WHERE id = ?
                """, (equiv_id,))
                conn.commit()
                print(f"✅ Equivalence ID {equiv_id} supprimee")
                return True
        except Exception as e:
            print(f"❌ Erreur suppression equivalence: {e}")
            return False
    
    def update_equivalence(self, equiv_id: int, diplome_principal: str, diplome_equivalent: str) -> bool:
        """Mettre a jour une equivalence"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    UPDATE equivalences_diplomes 
                    SET diplome_principal = ?, diplome_equivalent = ?
                    WHERE id = ?
                """, (diplome_principal, diplome_equivalent, equiv_id))
                conn.commit()
                print(f"✅ Equivalence ID {equiv_id} mise a jour")
                return True
        except Exception as e:
            print(f"❌ Erreur mise a jour equivalence: {e}")
            return False
    
    def get_equivalents(self, diplome: str) -> List[str]:
        """Obtenir tous les diplomes equivalents a un diplome donne"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT diplome_equivalent FROM equivalences_diplomes 
                    WHERE diplome_principal = ? AND actif = 1
                    UNION
                    SELECT diplome_principal FROM equivalences_diplomes 
                    WHERE diplome_equivalent = ? AND actif = 1
                """, (diplome, diplome))
                return [row['diplome_equivalent'] if 'diplome_equivalent' in row.keys() else row['diplome_principal'] for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erreur get_equivalents: {e}")
            return []
    
    # ==================== STATISTIQUES ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Recuperer les statistiques generales"""
        try:
            with self.get_connection() as conn:
                # Total agents
                total_agents = conn.execute("SELECT COUNT(*) FROM agents WHERE statut = 'Actif'").fetchone()[0]
                
                # Repartition par grade
                grade_stats = conn.execute("""
                    SELECT grade_actuel, COUNT(*) as count 
                    FROM agents 
                    WHERE statut = 'Actif'
                    GROUP BY grade_actuel
                    ORDER BY count DESC
                """).fetchall()
                
                # Stats par statut d'evaluation (pour plus tard)
                eval_stats = {
                    'proposables': 0,
                    'bientot': 0, 
                    'non_proposables': 0
                }
                
                return {
                    'total_agents': total_agents,
                    'grade_stats': [dict(row) for row in grade_stats],
                    'eval_stats': eval_stats
                }
        except Exception as e:
            print(f"❌ Erreur get_stats: {e}")
            return {
                'total_agents': 0,
                'grade_stats': [],
                'eval_stats': {'proposables': 0, 'bientot': 0, 'non_proposables': 0}
            }
    
    def get_agents_count_by_status(self) -> Dict[str, int]:
        """Recuperer le nombre d'agents par statut"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT statut, COUNT(*) as count 
                    FROM agents 
                    GROUP BY statut
                """)
                return {row['statut']: row['count'] for row in cursor.fetchall()}
        except Exception as e:
            print(f"❌ Erreur get_agents_count_by_status: {e}")
            return {}

# Instance globale
db_manager = DatabaseManager()

# Test de la connexion
if __name__ == "__main__":
    print("🧪 Test de la base de donnees...")
    stats = db_manager.get_stats()
    print(f"📊 Total agents: {stats['total_agents']}")
    print("✅ Base de donnees fonctionnelle !")