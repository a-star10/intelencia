"""
Modeles de donnees pour Military Career Manager
core/models.py
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional, Dict, Any
import sys
from pathlib import Path

# Import config
sys.path.append(str(Path(__file__).parent.parent))
from config import ANNEE_REFERENCE

@dataclass
class Diplome:
    """Represente un diplome obtenu par un agent"""
    nom: str
    date_obtention: date
    etablissement: str = ""
    actif: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            'nom': self.nom,
            'date_obtention': self.date_obtention.isoformat() if isinstance(self.date_obtention, date) else self.date_obtention,
            'etablissement': self.etablissement,
            'actif': self.actif
        }

@dataclass 
class Agent:
    """Modele principal pour un agent militaire"""
    # Identite
    id: Optional[int] = None
    statut: str = "Actif"
    matricule: str = ""
    nom: str = ""
    prenom: str = ""
    date_naissance: Optional[date] = None
    age: Optional[int] = None
    
    # Carriere
    grade_actuel: str = ""
    date_incorporation: Optional[date] = None
    date_entree_grade: Optional[date] = None
    anciennete_service: Optional[float] = None
    anciennete_grade: Optional[float] = None
    
    # Formation
    ecole: str = ""
    diplomes: List[Diplome] = field(default_factory=list)
    
    # Evaluations
    note_annee_moins_2: str = ""
    note_annee_moins_1: str = ""
    note_annee_courante: str = ""
    statut_disciplinaire: str = "RAS"
    
    # Affectation
    unite_provenance: str = ""
    
    # Resultats
    resultat_evaluation: str = ""
    derniere_evaluation: Optional[datetime] = None
    
    # Metadonnees
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def calculate_age(self) -> int:
        """Calcule l'age actuel"""
        if not self.date_naissance:
            return 0
        
        if isinstance(self.date_naissance, str):
            try:
                self.date_naissance = datetime.strptime(self.date_naissance, '%Y-%m-%d').date()
            except:
                return 0
        
        today = date.today()
        age = today.year - self.date_naissance.year
        if today.month < self.date_naissance.month or \
           (today.month == self.date_naissance.month and today.day < self.date_naissance.day):
            age -= 1
        return age
    
    def calculate_anciennete_service(self) -> float:
        """Calcule l'anciennete de service en annees"""
        if not self.date_incorporation:
            return 0.0
        
        if isinstance(self.date_incorporation, str):
            try:
                self.date_incorporation = datetime.strptime(self.date_incorporation, '%Y-%m-%d').date()
            except:
                return 0.0
        
        ref_date = date(ANNEE_REFERENCE, 12, 31)
        delta = ref_date - self.date_incorporation
        return round(delta.days / 365.25, 2)
    
    def calculate_anciennete_grade(self) -> float:
        """Calcule l'anciennete dans le grade en annees"""
        if not self.date_entree_grade:
            return 0.0
        
        if isinstance(self.date_entree_grade, str):
            try:
                self.date_entree_grade = datetime.strptime(self.date_entree_grade, '%Y-%m-%d').date()
            except:
                return 0.0
        
        ref_date = date(ANNEE_REFERENCE, 12, 31)
        delta = ref_date - self.date_entree_grade
        return round(delta.days / 365.25, 2)
    
    def update_calculated_fields(self):
        """Met a jour tous les champs calcules"""
        self.age = self.calculate_age()
        self.anciennete_service = self.calculate_anciennete_service()
        self.anciennete_grade = self.calculate_anciennete_grade()
        self.updated_at = datetime.now()
    
    def get_nom_complet(self) -> str:
        """Retourne le nom complet"""
        return f"{self.nom} {self.prenom}".strip()
    
    def get_diplomes_names(self) -> str:
        """Retourne les noms des diplomes separes par des virgules"""
        if not self.diplomes:
            return "Aucun"
        return ", ".join([d.nom for d in self.diplomes if d.actif])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour la base de donnees"""
        return {
            'id': self.id,
            'statut': self.statut,
            'matricule': self.matricule,
            'nom': self.nom,
            'prenom': self.prenom,
            'date_naissance': self.date_naissance.isoformat() if isinstance(self.date_naissance, date) else self.date_naissance,
            'age': self.age,
            'grade_actuel': self.grade_actuel,
            'date_incorporation': self.date_incorporation.isoformat() if isinstance(self.date_incorporation, date) else self.date_incorporation,
            'date_entree_grade': self.date_entree_grade.isoformat() if isinstance(self.date_entree_grade, date) else self.date_entree_grade,
            'anciennete_service': self.anciennete_service,
            'anciennete_grade': self.anciennete_grade,
            'ecole': self.ecole,
            'note_annee_moins_2': self.note_annee_moins_2,
            'note_annee_moins_1': self.note_annee_moins_1,
            'note_annee_courante': self.note_annee_courante,
            'statut_disciplinaire': self.statut_disciplinaire,
            'unite_provenance': self.unite_provenance,
            'resultat_evaluation': self.resultat_evaluation,
            'diplomes': [d.to_dict() for d in self.diplomes]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Creer un Agent depuis un dictionnaire - VERSION CORRIGEE"""
        # Convertir les dates string en objets date
        if 'date_naissance' in data and isinstance(data['date_naissance'], str):
            data['date_naissance'] = datetime.strptime(data['date_naissance'], '%Y-%m-%d').date()
        
        if 'date_incorporation' in data and isinstance(data['date_incorporation'], str):
            data['date_incorporation'] = datetime.strptime(data['date_incorporation'], '%Y-%m-%d').date()
        
        if 'date_entree_grade' in data and isinstance(data['date_entree_grade'], str):
            data['date_entree_grade'] = datetime.strptime(data['date_entree_grade'], '%Y-%m-%d').date()
        
        # Convertir les diplomes - FIX pour gerer les deux formats
        diplomes = []
        if 'diplomes' in data and data['diplomes']:
            for diplome_data in data['diplomes']:
                if isinstance(diplome_data, dict):
                    # FIX: Gerer les colonnes 'diplome' (DB) et 'nom' (objet)
                    diplome_nom = diplome_data.get('diplome', diplome_data.get('nom', ''))
                    diplome_date = diplome_data.get('date_obtention', '')
                    
                    if isinstance(diplome_date, str) and diplome_date:
                        try:
                            diplome_date = datetime.strptime(diplome_date, '%Y-%m-%d').date()
                        except:
                            diplome_date = date.today()
                    
                    if diplome_nom:
                        diplome = Diplome(
                            nom=diplome_nom,
                            date_obtention=diplome_date,
                            etablissement=diplome_data.get('etablissement', ''),
                            actif=diplome_data.get('actif', True)
                        )
                        diplomes.append(diplome)
        
        # Supprimer diplomes de data pour eviter les conflits
        agent_data = {k: v for k, v in data.items() if k != 'diplomes'}
        agent_data['diplomes'] = diplomes
        
        return cls(**agent_data)

@dataclass
class RegleAvancement:
    """Modele pour les regles d'avancement"""
    id: Optional[int] = None
    grade_source: str = ""
    grade_cible: str = ""
    type_avancement: str = "Normal"
    conditions: Dict[str, Any] = field(default_factory=dict)
    actif: bool = True
    created_at: Optional[datetime] = None

# Fonctions utilitaires
def create_sample_agent(matricule: str, nom: str, prenom: str, grade: str) -> Agent:
    """Creer un agent de test avec des donnees realistes"""
    from datetime import timedelta
    import random
    
    # Dates aleatoires mais realistes
    age = random.randint(20, 50)
    date_naissance = date.today() - timedelta(days=age * 365)
    
    anciennete_service = random.randint(2, 25)
    date_incorporation = date.today() - timedelta(days=anciennete_service * 365)
    
    anciennete_grade = random.randint(1, min(5, anciennete_service))
    date_entree_grade = date.today() - timedelta(days=anciennete_grade * 365)
    
    # Notes aleatoires
    notes = ["TB", "B", "AB", "P"]
    
    # Diplomes selon le grade
    diplomes = []
    if grade in ["Caporal", "Caporal-chef"]:
        diplomes.append(Diplome("FCB", date_incorporation, "Centre de Formation"))
    elif grade in ["Sergent", "Sergent-chef"]:
        diplomes.append(Diplome("C.M.1", date_entree_grade, "Ecole Militaire"))
    elif "Adjudant" in grade:
        diplomes.append(Diplome("B.M.P.1", date_entree_grade, "Ecole Superieure"))
    
    agent = Agent(
        matricule=matricule,
        nom=nom,
        prenom=prenom,
        date_naissance=date_naissance,
        grade_actuel=grade,
        date_incorporation=date_incorporation,
        date_entree_grade=date_entree_grade,
        ecole="Ecole Militaire Standard",
        note_annee_moins_2=random.choice(notes),
        note_annee_moins_1=random.choice(notes),
        note_annee_courante=random.choice(notes),
        statut_disciplinaire="RAS",
        unite_provenance=f"Unite {random.randint(1, 50)}",
        diplomes=diplomes
    )
    
    # Calculer les champs automatiques
    agent.update_calculated_fields()
    
    return agent

if __name__ == "__main__":
    # Test des modeles
    print("Test des modeles...")
    
    # Creer un agent de test
    agent = create_sample_agent("MT001234", "Dupont", "Jean", "Caporal")
    print(f"Agent cree: {agent.get_nom_complet()}")
    print(f"Age: {agent.age} ans")
    print(f"Anciennete service: {agent.anciennete_service} ans")
    print(f"Diplomes: {agent.get_diplomes_names()}")
    
    print("Modeles fonctionnels")