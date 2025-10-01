import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from core.database import db_manager

def add_missing_commandant_rule():
    """Ajoute la règle manquante : Capitaine → Commandant (Ancienneté)"""
    
    print("🚀 Ajout de la règle manquante : Capitaine → Commandant (Ancienneté)")
    print("=" * 70)
    
    # Vérifier si la règle existe déjà
    print("\n1️⃣ Vérification de l'existence de la règle...")
    
    try:
        # Récupérer toutes les règles existantes
        existing_rules = db_manager.get_all_rules()
        
        # Vérifier si la règle Capitaine → Commandant (Ancienneté) existe
        rule_exists = False
        for rule in existing_rules:
            if (rule['grade_source'] == 'Capitaine' and 
                rule['grade_cible'] == 'Commandant' and 
                rule['type_avancement'] == 'Ancienneté'):
                rule_exists = True
                print("   ✅ La règle existe déjà dans la base !")
                print(f"   ID: {rule['id']}")
                print(f"   Conditions: {rule.get('conditions_speciales', 'N/A')}")
                break
        
        if rule_exists:
            response = input("\n⚠️  La règle existe déjà. Voulez-vous la recréer ? (y/N): ")
            if response.lower() != 'y':
                print("❌ Opération annulée")
                return False
            
            # Supprimer l'ancienne règle
            print("🗑️  Suppression de l'ancienne règle...")
            for rule in existing_rules:
                if (rule['grade_source'] == 'Capitaine' and 
                    rule['grade_cible'] == 'Commandant' and 
                    rule['type_avancement'] == 'Ancienneté'):
                    db_manager.delete_rule(rule['id'])
                    print("   ✅ Ancienne règle supprimée")
        else:
            print("   ℹ️  La règle n'existe pas encore (comme prévu)")
        
        # Créer la nouvelle règle
        print("\n2️⃣ Création de la règle...")
        
        new_rule = {
            'categorie': 'Officiers',
            'grade_source': 'Capitaine',
            'grade_cible': 'Commandant',
            'type_avancement': 'Ancienneté',
            'anciennete_service_min': 0,
            'anciennete_grade_min': 8,
            'grade_specifique': 'Capitaine',
            'anciennete_grade_specifique': 8,
            'diplomes_requis': [],
            'note_min_courante': 'B',
            'notes_interdites_n1_n2': [],
            'conditions_speciales': '8 ans de grade de Capitaine au 31/12 de l\'année en cours - Être noté B pendant les 2 dernières années',
            'statut': 'Actif'
        }
        
        rule_id = db_manager.create_rule(new_rule)
        
        if rule_id:
            print("   ✅ Règle créée avec succès !")
            print(f"   ID: {rule_id}")
            print()
            print("📋 DÉTAILS DE LA RÈGLE :")
            print(f"   Catégorie         : {new_rule['categorie']}")
            print(f"   Grade source      : {new_rule['grade_source']}")
            print(f"   Grade cible       : {new_rule['grade_cible']}")
            print(f"   Type avancement   : {new_rule['type_avancement']}")
            print(f"   Ancienneté grade  : {new_rule['anciennete_grade_min']} ans")
            print(f"   Note minimum      : {new_rule['note_min_courante']}")
            print(f"   Conditions        : {new_rule['conditions_speciales']}")
            print(f"   Statut            : {new_rule['statut']}")
        else:
            print("   ❌ Erreur lors de la création de la règle")
            return False
        
        # Vérification finale
        print("\n3️⃣ Vérification finale...")
        
        all_rules = db_manager.get_all_rules()
        capitaine_rules = [r for r in all_rules if r['grade_source'] == 'Capitaine' and r['grade_cible'] == 'Commandant']
        
        print(f"   📊 Nombre de règles Capitaine → Commandant : {len(capitaine_rules)}")
        for rule in capitaine_rules:
            print(f"      - {rule['type_avancement']:15s} (ID: {rule['id']})")
        
        print()
        print("=" * 70)
        print("✅ OPÉRATION TERMINÉE AVEC SUCCÈS !")
        print()
        print("🎯 La règle manquante a été ajoutée à la base de données.")
        print("   Vous pouvez maintenant :")
        print("   1. Visualiser la règle dans l'interface (section Règles)")
        print("   2. Évaluer les agents Capitaine avec cette nouvelle règle")
        print("   3. Vérifier les résultats d'évaluation")
        print()
        print("💡 Conseil : Lancez une nouvelle évaluation globale pour mettre à jour")
        print("   les résultats des Capitaines concernés :")
        print("   Section Évaluation → Bouton 'Évaluer Tous les Agents'")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de l'ajout de la règle: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = add_missing_commandant_rule()
    sys.exit(0 if success else 1)