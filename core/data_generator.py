"""
Generateur d'agents de test realistes
core/data_generator.py
"""
import random
from datetime import date, timedelta
from typing import List
import sys
from pathlib import Path

# Imports
sys.path.append(str(Path(__file__).parent.parent))
from core.models import Agent, Diplome, create_sample_agent
from core.database import db_manager
from config import GRADES_HIERARCHY

class DataGenerator:
    """Generateur de donnees de test"""
    
    def __init__(self):
        self.noms = [
            "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Petit", "Durand", "Leroy",
            "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Garcia", "David",
            "Bertrand", "Roux", "Vincent", "Fournier", "Morel", "Girard", "Andre",
            "Lefevre", "Mercier", "Dupont", "Lambert", "Bonnet", "Francois", "Martinez"
        ]
        
        self.prenoms = [
            "Jean", "Pierre", "Michel", "Alain", "Patrick", "Philippe", "Daniel",
            "Marie", "Francoise", "Monique", "Sylvie", "Catherine", "Nathalie",
            "Isabelle", "Martine", "Christine", "Sophie", "Brigitte", "Chantal",
            "Sandrine", "Valerie", "Pascale", "Stephanie", "Laurence", "Caroline",
            "Nicolas", "Christophe", "Laurent", "Olivier", "Bruno", "Eric", "David",
            "Sebastien", "Pascal", "Frederic", "Antoine", "Julien", "Alexandre",
            "Maxime", "Kevin", "Thomas", "Florian", "Jeremy", "Benjamin", "Lucas"
        ]
        
        self.unites = [
            "1er Regiment d'Infanterie", "2e Regiment de Dragons", "3e Regiment d'Artillerie",
            "4e Regiment du Genie", "5e Regiment de Chasseurs", "6e Regiment de Cuirassiers",
            "7e Regiment de Transmissions", "8e Regiment Parachutiste", "9e Regiment d'Helicopteres",
            "10e Regiment Logistique", "Base Aerienne 105", "Base Navale de Toulon",
            "Centre d'Instruction", "Etat-Major Regional", "Service de Sante",
            "Gendarmerie Mobile", "Police Militaire", "Service des Essences"
        ]
        
        self.ecoles = [
            "Ecole Militaire de Saint-Cyr", "Ecole Navale", "Ecole de l'Air",
            "Ecole du Service de Sante", "Ecole du Commissariat", "Ecole Polytechnique",
            "Centre de Formation Initiale", "Institut des Hautes Etudes",
            "Ecole d'Application de l'Infanterie", "Ecole d'Artillerie"
        ]
        
        self.notes = ["TB", "B", "AB", "P"]
        
        # Diplomes par categorie de grade
        self.diplomes_par_grade = {
            "militaires_rang": ["FCB", "C.M.E", "C.T.E"],
            "sous_officiers": ["C.M.1", "C.T.1", "B.M.P.E", "B.M.P.1"],
            "officiers": ["Diplome d'ecole", "C.M.2", "C.T.2", "B.M.P.2", "CPOS"]
        }
    
    def get_category_from_grade(self, grade: str) -> str:
        """Determiner la categorie d'un grade"""
        if grade in ["2e Classe", "Caporal", "Caporal-chef"]:
            return "militaires_rang"
        elif "Sergent" in grade or "Adjudant" in grade:
            return "sous_officiers"
        else:
            return "officiers"
    
    def generate_realistic_agent(self, grade: str) -> Agent:
        """Generer un agent realiste pour un grade donne"""
        # Donnees de base
        nom = random.choice(self.noms)
        prenom = random.choice(self.prenoms)
        matricule = f"MT{random.randint(100000, 999999)}"
        
        # Age selon le grade (plus realiste)
        category = self.get_category_from_grade(grade)
        if category == "militaires_rang":
            age = random.randint(19, 35)
        elif category == "sous_officiers":
            age = random.randint(25, 45)
        else:  # officiers
            age = random.randint(25, 55)
        
        date_naissance = date.today() - timedelta(days=age * 365 + random.randint(0, 365))
        
        # Anciennete selon le grade
        if category == "militaires_rang":
            anciennete_service = random.randint(1, 15)
        elif category == "sous_officiers":
            anciennete_service = random.randint(5, 25)
        else:
            anciennete_service = random.randint(3, 30)
        
        date_incorporation = date.today() - timedelta(days=anciennete_service * 365)
        
        # Anciennete dans le grade (plus petite que l'anciennete service)
        anciennete_grade = random.randint(1, min(6, anciennete_service))
        date_entree_grade = date.today() - timedelta(days=anciennete_grade * 365)
        
        # Diplomes selon la categorie (COPIE de la liste pour eviter modification)
        diplomes = []
        diplomes_possibles = self.diplomes_par_grade[category].copy()  # FIX: copie de la liste
        
        if len(diplomes_possibles) > 0:  # FIX: verifier que la liste n'est pas vide
            nb_diplomes = random.randint(1, min(3, len(diplomes_possibles)))
            
            for _ in range(nb_diplomes):
                if diplomes_possibles:  # FIX: verifier qu'il reste des diplomes
                    diplome_nom = random.choice(diplomes_possibles)
                    diplome_date = date_incorporation + timedelta(days=random.randint(30, anciennete_service * 300))
                    diplome = Diplome(
                        nom=diplome_nom,
                        date_obtention=diplome_date,
                        etablissement=random.choice(self.ecoles)
                    )
                    diplomes.append(diplome)
                    diplomes_possibles.remove(diplome_nom)  # Maintenant on peut enlever sans probleme
        
        # Notes (plus de bonnes notes pour les grades eleves)
        if category == "officiers":
            notes_ponderees = ["TB"] * 4 + ["B"] * 3 + ["AB"] * 1
        elif category == "sous_officiers":
            notes_ponderees = ["TB"] * 2 + ["B"] * 4 + ["AB"] * 2 + ["P"] * 1
        else:
            notes_ponderees = ["TB"] * 1 + ["B"] * 3 + ["AB"] * 3 + ["P"] * 2
        
        # Statut disciplinaire (majorite RAS)
        statut_disciplinaire = "RAS" if random.random() < 0.85 else random.choice([
            "Avertissement", "Blame", "Punition", "En observation"
        ])
        
        agent = Agent(
            matricule=matricule,
            nom=nom,
            prenom=prenom,
            date_naissance=date_naissance,
            grade_actuel=grade,
            date_incorporation=date_incorporation,
            date_entree_grade=date_entree_grade,
            ecole=random.choice(self.ecoles),
            note_annee_moins_2=random.choice(notes_ponderees),
            note_annee_moins_1=random.choice(notes_ponderees),
            note_annee_courante=random.choice(notes_ponderees),
            statut_disciplinaire=statut_disciplinaire,
            unite_provenance=random.choice(self.unites),
            diplomes=diplomes
        )
        
        # Calculer les champs automatiques
        agent.update_calculated_fields()
        
        return agent
    def generate_test_dataset(self, total_agents: int = 50) -> List[Agent]:
        """Generer un jeu de donnees de test equilibre"""
        agents = []
        
        # Repartition realiste par grade
        repartition = {
            "2e Classe": int(total_agents * 0.15),
            "Caporal": int(total_agents * 0.20),
            "Caporal-chef": int(total_agents * 0.15),
            "Sergent": int(total_agents * 0.12),
            "Sergent-chef": int(total_agents * 0.10),
            "Adjudant": int(total_agents * 0.08),
            "Adjudant-chef": int(total_agents * 0.06),
            "Sous-Lieutenant": int(total_agents * 0.04),
            "Lieutenant": int(total_agents * 0.04),
            "Capitaine": int(total_agents * 0.03),
            "Commandant": int(total_agents * 0.02),
            "Lieutenant-Colonel": int(total_agents * 0.01)
        }
        
        # Ajuster pour avoir exactement total_agents
        total_calculated = sum(repartition.values())
        if total_calculated < total_agents:
            repartition["Caporal"] += total_agents - total_calculated
        
        # Generer les agents
        for grade, nombre in repartition.items():
            for _ in range(nombre):
                agent = self.generate_realistic_agent(grade)
                
                # Verifier l'unicite du matricule
                while any(a.matricule == agent.matricule for a in agents):
                    agent.matricule = f"MT{random.randint(100000, 999999)}"
                
                agents.append(agent)
        
        print(f"✅ {len(agents)} agents generes avec repartition realiste")
        return agents
    
    def populate_database(self, nb_agents: int = 50):
        """Peupler la base de donnees avec des agents de test"""
        print(f"🔄 Generation de {nb_agents} agents de test...")
        
        # Verifier si la base contient deja des donnees
        stats = db_manager.get_stats()
        if stats['total_agents'] > 0:
            print(f"⚠️ La base contient deja {stats['total_agents']} agents")
            response = input("Voulez-vous les supprimer et regenerer? (y/N): ")
            if response.lower() != 'y':
                print("Operation annulee")
                return
            
            # Supprimer tous les agents existants
            with db_manager.get_connection() as conn:
                conn.execute("DELETE FROM diplomes_historique")
                conn.execute("DELETE FROM agents")
                conn.commit()
            print("🗑️ Anciens agents supprimes")
        
        # Generer les nouveaux agents
        agents = self.generate_test_dataset(nb_agents)
        
        # Les inserer en base
        print("💾 Insertion en base de donnees...")
        success_count = 0
        
        for agent in agents:
            try:
                agent_id = db_manager.create_agent(agent.to_dict())
                if agent_id:
                    success_count += 1
            except Exception as e:
                print(f"❌ Erreur insertion {agent.matricule}: {e}")
        
        print(f"✅ {success_count}/{len(agents)} agents inseres avec succes")
        
        # Afficher les statistiques finales
        final_stats = db_manager.get_stats()
        print(f"📊 Total en base: {final_stats['total_agents']} agents")
        
        if final_stats['grade_stats']:
            print("📈 Repartition par grade:")
            for grade_stat in final_stats['grade_stats'][:5]:  # Top 5
                print(f"   {grade_stat['grade_actuel']}: {grade_stat['count']} agents")

# Instance globale
data_generator = DataGenerator()

if __name__ == "__main__":
    print("🧪 Test du generateur de donnees...")
    
    # Generer un agent de test
    agent = data_generator.generate_realistic_agent("Sergent")
    print(f"✅ Agent genere: {agent.get_nom_complet()}")
    print(f"   Grade: {agent.grade_actuel}")
    print(f"   Age: {agent.age} ans")
    print(f"   Anciennete: {agent.anciennete_service} ans")
    print(f"   Diplomes: {agent.get_diplomes_names()}")
    print(f"   Unite: {agent.unite_provenance}")
    
    # Option pour peupler la base
    print("\n🎯 Pour peupler la base de donnees:")
    print("   python -c \"from core.data_generator import data_generator; data_generator.populate_database(30)\"")
    
    print("✅ Generateur fonctionnel !")