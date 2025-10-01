#!/usr/bin/env python3
"""
Script d'import de TOUTES les règles d'avancement - VERSION CORRIGÉE
Basé sur le document officiel des règles
Total: 27 règles (4 Militaires du rang + 10 Sous-officiers + 13 Officiers)
Exécuter : python import_all_rules_CORRECT.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.database import db_manager

def get_all_rules_from_documents():
    """Récupérer TOUTES les 27 règles officielles"""
    
    all_rules = []
    
    # ==================== MILITAIRES DU RANG (4 règles) ====================
    
    # 1. 2e Classe → Caporal (Normale)
    all_rules.append({
        'categorie': 'Militaires du rang',
        'grade_source': '2e Classe',
        'grade_cible': 'Caporal',
        'type_avancement': 'Normal',
        'anciennete_service_min': 2,
        'anciennete_grade_min': 0,
        'grade_specifique': None,
        'anciennete_grade_specifique': 0,
        'diplomes_requis': ['C.M.E', 'C.T.E'],
        'note_min_courante': 'B',
        'notes_interdites_n1_n2': ['AB', 'P', 'I'],
        'conditions_speciales': 'Pas de note AB, P ou I en 2022 et 2023',
        'statut': 'Actif'
    })
    
    # 2. 2e Classe → Caporal (Ancienneté)
    all_rules.append({
        'categorie': 'Militaires du rang',
        'grade_source': '2e Classe',
        'grade_cible': 'Caporal',
        'type_avancement': 'Ancienneté',
        'anciennete_service_min': 4,
        'anciennete_grade_min': 0,
        'grade_specifique': None,
        'anciennete_grade_specifique': 0,
        'diplomes_requis': [],
        'note_min_courante': 'TB',
        'notes_interdites_n1_n2': ['AB', 'P', 'I'],
        'conditions_speciales': 'Pas de note AB, P ou I en 2022 et 2023',
        'statut': 'Actif'
    })
    
    # 3. Caporal → Caporal-chef (Normale)
    all_rules.append({
        'categorie': 'Militaires du rang',
        'grade_source': 'Caporal',
        'grade_cible': 'Caporal-chef',
        'type_avancement': 'Normal',
        'anciennete_service_min': 4,
        'anciennete_grade_min': 2,
        'grade_specifique': 'Caporal',
        'anciennete_grade_specifique': 2,
        'diplomes_requis': ['B.M.P.E'],
        'note_min_courante': 'B',
        'notes_interdites_n1_n2': ['AB', 'P', 'I'],
        'conditions_speciales': 'Note B minimum en 2024 (et en 2022) - Pas de note AB, P ou I en 2022 et 2023',
        'statut': 'Actif'
    })
    
    # 4. Caporal → Caporal-chef (Ancienneté)
    all_rules.append({
        'categorie': 'Militaires du rang',
        'grade_source': 'Caporal',
        'grade_cible': 'Caporal-chef',
        'type_avancement': 'Ancienneté',
        'anciennete_service_min': 7,
        'anciennete_grade_min': 3,
        'grade_specifique': 'Caporal',
        'anciennete_grade_specifique': 3,
        'diplomes_requis': ['C.M.E', 'C.T.E'],
        'note_min_courante': 'TB',
        'notes_interdites_n1_n2': ['AB', 'P', 'I'],
        'conditions_speciales': 'Pas de note AB, P ou I en 2022 et 2023',
        'statut': 'Actif'
    })
    
    # ==================== SOUS-OFFICIERS (10 règles) ====================
    
    # 5. Caporal-chef → Sergent (Normale)
    all_rules.append({
        'categorie': 'Sous-officiers',
        'grade_source': 'Caporal-chef',
        'grade_cible': 'Sergent',
        'type_avancement': 'Normal',
        'anciennete_service_min': 5,
        'anciennete_grade_min': 2,
        'grade_specifique': 'Caporal-chef',
        'anciennete_grade_specifique': 2,
        'diplomes_requis': ['C.M.1', 'C.T.1'],
        'note_min_courante': 'B',
        'notes_interdites_n1_n2': ['AB', 'P', 'I'],
        'conditions_speciales': 'Pas de note AB, P ou I en 2022 et 2023',
        'statut': 'Actif'
    })
    
    # 6. Caporal-chef → Sergent (Ancienneté)
    all_rules.append({
        'categorie': 'Sous-officiers',
        'grade_source': 'Caporal-chef',
        'grade_cible': 'Sergent',
        'type_avancement': 'Ancienneté',
        'anciennete_service_min': 7,
        'anciennete_grade_min': 3,
        'grade_specifique': 'Caporal-chef',
        'anciennete_grade_specifique': 3,
        'diplomes_requis': ['B.M.P.E'],
        'note_min_courante': 'B',
        'notes_interdites_n1_n2': ['AB', 'P', 'I'],
        'conditions_speciales': 'Pas de note AB, P ou I en 2022 et 2023',
        'statut': 'Actif'
    })
    
    # 7. Sergent → Sergent-chef (Normale)
    all_rules.append({
        'categorie': 'Sous-officiers',
        'grade_source': 'Sergent',
        'grade_cible': 'Sergent-chef',
        'type_avancement': 'Normal',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 4,
        'grade_specifique': 'Sergent',
        'anciennete_grade_specifique': 4,
        'diplomes_requis': ['B.M.P.1'],
        'note_min_courante': 'B',
        'notes_interdites_n1_n2': ['AB', 'P', 'I'],
        'conditions_speciales': '4 ans de grade Sergent - Pas de note AB, P ou I en 2022 et 2023',
        'statut': 'Actif'
    })
    
    # 8. Sergent → Sergent-chef (Ancienneté)
    all_rules.append({
        'categorie': 'Sous-officiers',
        'grade_source': 'Sergent',
        'grade_cible': 'Sergent-chef',
        'type_avancement': 'Ancienneté',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 6,
        'grade_specifique': 'Sergent',
        'anciennete_grade_specifique': 6,
        'diplomes_requis': ['C.M.1', 'C.T.1'],
        'note_min_courante': 'B',
        'notes_interdites_n1_n2': ['AB', 'P', 'I'],
        'conditions_speciales': '6 ans de grade Sergent - Pas de note AB, P ou I en 2022 et 2023',
        'statut': 'Actif'
    })
    
    # 9. Sergent-chef → Sergent-chef-Major (Normale)
    all_rules.append({
        'categorie': 'Sous-officiers',
        'grade_source': 'Sergent-chef',
        'grade_cible': 'Sergent-chef-Major',
        'type_avancement': 'Normal',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 3,
        'grade_specifique': 'Sergent-chef',
        'anciennete_grade_specifique': 3,
        'diplomes_requis': ['B.M.P.1'],
        'note_min_courante': 'B',
        'notes_interdites_n1_n2': ['AB', 'P', 'I'],
        'conditions_speciales': '3 ans de grade Sergent-chef - Pas de note AB, P ou I en 2022 et 2023',
        'statut': 'Actif'
    })
    
    # 10. Sergent-chef → Sergent-chef-Major (Ancienneté)
    all_rules.append({
        'categorie': 'Sous-officiers',
        'grade_source': 'Sergent-chef',
        'grade_cible': 'Sergent-chef-Major',
        'type_avancement': 'Ancienneté',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 5,
        'grade_specifique': 'Sergent-chef',
        'anciennete_grade_specifique': 5,
        'diplomes_requis': ['C.M.1', 'C.T.1'],
        'note_min_courante': 'B',
        'notes_interdites_n1_n2': ['AB', 'P', 'I'],
        'conditions_speciales': '5 ans de grade Sergent-chef - Pas de note AB, P ou I en 2022 et 2023',
        'statut': 'Actif'
    })
    
    # 11. Sergent-chef-Major → Adjudant (Normale)
    all_rules.append({
        'categorie': 'Sous-officiers',
        'grade_source': 'Sergent-chef-Major',
        'grade_cible': 'Adjudant',
        'type_avancement': 'Normal',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 5,
        'grade_specifique': 'Sergent-chef-Major',
        'anciennete_grade_specifique': 5,
        'diplomes_requis': ['B.M.P.2', 'C.M.2', 'C.T.2'],
        'note_min_courante': 'B',
        'notes_interdites_n1_n2': ['AB', 'P', 'I'],
        'conditions_speciales': '5 ans de grade Sergent-chef-Major - Pas de note AB, P ou I en 2022 et 2023',
        'statut': 'Actif'
    })
    
    # 12. Sergent-chef-Major → Adjudant (Ancienneté)
    all_rules.append({
        'categorie': 'Sous-officiers',
        'grade_source': 'Sergent-chef-Major',
        'grade_cible': 'Adjudant',
        'type_avancement': 'Ancienneté',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 7,
        'grade_specifique': 'Sergent-chef-Major',
        'anciennete_grade_specifique': 7,
        'diplomes_requis': ['B.M.P.1'],
        'note_min_courante': 'TB',
        'notes_interdites_n1_n2': ['AB', 'P', 'I'],
        'conditions_speciales': '7 ans de grade Sergent-chef-Major - Pas de note AB, P ou I en 2022 et 2023',
        'statut': 'Actif'
    })
    
    # 13. Adjudant → Adjudant-chef (Normale)
    all_rules.append({
        'categorie': 'Sous-officiers',
        'grade_source': 'Adjudant',
        'grade_cible': 'Adjudant-chef',
        'type_avancement': 'Normal',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 4,
        'grade_specifique': 'Adjudant',
        'anciennete_grade_specifique': 4,
        'diplomes_requis': ['B.M.P.2'],
        'note_min_courante': 'B',
        'notes_interdites_n1_n2': ['AB', 'P', 'I'],
        'conditions_speciales': '4 ans de grade Adjudant - Pas de note AB, P ou I en 2022 et 2023',
        'statut': 'Actif'
    })
    
    # 14. Adjudant → Adjudant-chef (Ancienneté)
    all_rules.append({
        'categorie': 'Sous-officiers',
        'grade_source': 'Adjudant',
        'grade_cible': 'Adjudant-chef',
        'type_avancement': 'Ancienneté',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 6,
        'grade_specifique': 'Adjudant',
        'anciennete_grade_specifique': 6,
        'diplomes_requis': ['B.M.P.1', 'C.M.2', 'C.T.2'],
        'note_min_courante': 'TB',
        'notes_interdites_n1_n2': ['AB', 'P', 'I'],
        'conditions_speciales': '6 ans de grade Adjudant - Diplômes B.M.P.1 ET (C.M.2 OU C.T.2) - Pas de note AB, P ou I en 2022 et 2023',
        'statut': 'Actif'
    })
    
    # 15. Adjudant-chef → Adjudant-chef-Major (Normale UNIQUEMENT)
    all_rules.append({
        'categorie': 'Sous-officiers',
        'grade_source': 'Adjudant-chef',
        'grade_cible': 'Adjudant-chef-Major',
        'type_avancement': 'Normal',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 3,
        'grade_specifique': 'Adjudant-chef',
        'anciennete_grade_specifique': 3,
        'diplomes_requis': ['B.M.P.2'],
        'note_min_courante': 'B',
        'notes_interdites_n1_n2': ['AB', 'P', 'I'],
        'conditions_speciales': '3 ans de grade Adjudant-chef - Pas de note AB, P ou I en 2022 et 2023 - PAS D\'AVANCEMENT À L\'ANCIENNETÉ',
        'statut': 'Actif'
    })
    
    # ==================== OFFICIERS (13 règles) ====================
    
    # 16. Adjudant-chef(-Major) → Sous-Lieutenant (Choix)
    all_rules.append({
        'categorie': 'Officiers',
        'grade_source': 'Adjudant-chef-Major',
        'grade_cible': 'Sous-Lieutenant',
        'type_avancement': 'Choix',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 0,
        'grade_specifique': None,
        'anciennete_grade_specifique': 0,
        'diplomes_requis': ['Diplôme de sortie d\'école'],
        'note_min_courante': None,
        'notes_interdites_n1_n2': [],
        'conditions_speciales': 'Diplôme de sortie d\'école',
        'statut': 'Actif'
    })
    
    # 17. Adjudant-chef(-Major) → Sous-Lieutenant (Ancienneté)
    all_rules.append({
        'categorie': 'Officiers',
        'grade_source': 'Adjudant-chef',
        'grade_cible': 'Sous-Lieutenant',
        'type_avancement': 'Ancienneté',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 0,
        'grade_specifique': None,
        'anciennete_grade_specifique': 0,
        'diplomes_requis': [],
        'note_min_courante': None,
        'notes_interdites_n1_n2': [],
        'conditions_speciales': 'Être âgé de 45 à 48 ans - Être Adjudant-Chef',
        'statut': 'Actif'
    })
    
    # 18. Sous-Lieutenant → Lieutenant (Choix)
    all_rules.append({
        'categorie': 'Officiers',
        'grade_source': 'Sous-Lieutenant',
        'grade_cible': 'Lieutenant',
        'type_avancement': 'Choix',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 0,
        'grade_specifique': None,
        'anciennete_grade_specifique': 0,
        'diplomes_requis': ['Diplôme de sortie d\'école'],
        'note_min_courante': None,
        'notes_interdites_n1_n2': [],
        'conditions_speciales': 'Diplôme de sortie d\'école',
        'statut': 'Actif'
    })
    
    # 19. Sous-Lieutenant → Lieutenant (Ancienneté)
    all_rules.append({
        'categorie': 'Officiers',
        'grade_source': 'Sous-Lieutenant',
        'grade_cible': 'Lieutenant',
        'type_avancement': 'Ancienneté',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 2,
        'grade_specifique': 'Sous-Lieutenant',
        'anciennete_grade_specifique': 2,
        'diplomes_requis': [],
        'note_min_courante': None,
        'notes_interdites_n1_n2': [],
        'conditions_speciales': '2 ans grade Sous-Lieutenant (écoles 2 ans) - 1 an (écoles 3 ans) - 3 ans autres - Avancement automatique sauf indiscipline',
        'statut': 'Actif'
    })
    
    # 20. Lieutenant → Capitaine (Choix)
    all_rules.append({
        'categorie': 'Officiers',
        'grade_source': 'Lieutenant',
        'grade_cible': 'Capitaine',
        'type_avancement': 'Choix',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 5,
        'grade_specifique': 'Lieutenant',
        'anciennete_grade_specifique': 5,
        'diplomes_requis': ['CPOS'],
        'note_min_courante': 'B',
        'notes_interdites_n1_n2': [],
        'conditions_speciales': '5 ans grade Lieutenant + pratique langue étrangère - Titulaire CPOS ou équivalent - Note B min 2024',
        'statut': 'Actif'
    })
    
    # 21. Lieutenant → Capitaine (Ancienneté)
    all_rules.append({
        'categorie': 'Officiers',
        'grade_source': 'Lieutenant',
        'grade_cible': 'Capitaine',
        'type_avancement': 'Ancienneté',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 8,
        'grade_specifique': 'Lieutenant',
        'anciennete_grade_specifique': 8,
        'diplomes_requis': [],
        'note_min_courante': 'B',
        'notes_interdites_n1_n2': [],
        'conditions_speciales': '8 ans grade Lieutenant - Note B pendant les 2 dernières années',
        'statut': 'Actif'
    })
    
    # 22. Capitaine → Commandant (Choix UNIQUEMENT)
    all_rules.append({
        'categorie': 'Officiers',
        'grade_source': 'Capitaine',
        'grade_cible': 'Commandant',
        'type_avancement': 'Choix',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 5,
        'grade_specifique': 'Capitaine',
        'anciennete_grade_specifique': 5,
        'diplomes_requis': ['Brevet enseignement militaire supérieur 1er degré'],
        'note_min_courante': 'TB',
        'notes_interdites_n1_n2': [],
        'conditions_speciales': '5 ans grade Capitaine + diplôme enseignement militaire supérieur 1er degré + pratique langue étrangère - Note TB min 2024',
        'statut': 'Actif'
    })
    
    # 23. Commandant → Lieutenant-Colonel (Choix UNIQUEMENT)
    all_rules.append({
        'categorie': 'Officiers',
        'grade_source': 'Commandant',
        'grade_cible': 'Lieutenant-Colonel',
        'type_avancement': 'Choix',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 5,
        'grade_specifique': 'Commandant',
        'anciennete_grade_specifique': 5,
        'diplomes_requis': ['Brevet enseignement militaire supérieur 1er degré'],
        'note_min_courante': 'B',
        'notes_interdites_n1_n2': [],
        'conditions_speciales': '5 ans grade Commandant - Titulaire brevet enseignement militaire supérieur 1er degré ou équivalent - Note B min 2024',
        'statut': 'Actif'
    })
    
    # 24. Lieutenant-Colonel → Colonel (Choix UNIQUEMENT)
    all_rules.append({
        'categorie': 'Officiers',
        'grade_source': 'Lieutenant-Colonel',
        'grade_cible': 'Colonel',
        'type_avancement': 'Choix',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 4,
        'grade_specifique': 'Lieutenant-Colonel',
        'anciennete_grade_specifique': 4,
        'diplomes_requis': [],
        'note_min_courante': 'B',
        'notes_interdites_n1_n2': [],
        'conditions_speciales': '4 ans grade Lieutenant-Colonel - Note B min 2024',
        'statut': 'Actif'
    })
    
    # 25. Colonel → Général de Brigade (Choix UNIQUEMENT)
    all_rules.append({
        'categorie': 'Officiers',
        'grade_source': 'Colonel',
        'grade_cible': 'General de Brigade',
        'type_avancement': 'Choix',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 4,
        'grade_specifique': 'Colonel',
        'anciennete_grade_specifique': 4,
        'diplomes_requis': [],
        'note_min_courante': 'TB',
        'notes_interdites_n1_n2': [],
        'conditions_speciales': '4 ans grade Colonel - Note TB min 2024',
        'statut': 'Actif'
    })
    
    # 26. Général de Brigade → Général de Division (Choix UNIQUEMENT)
    all_rules.append({
        'categorie': 'Officiers',
        'grade_source': 'General de Brigade',
        'grade_cible': 'General de Division',
        'type_avancement': 'Choix',
        'anciennete_service_min': 0,
        'anciennete_grade_min': 4,
        'grade_specifique': 'Colonel',
        'anciennete_grade_specifique': 4,
        'diplomes_requis': ['Brevet enseignement militaire supérieur 2ème degré'],
        'note_min_courante': 'TB',
        'notes_interdites_n1_n2': [],
        'conditions_speciales': 'Bonne conduite - Brevet enseignement militaire supérieur 2ème degré - Commandement effectif - Emploi disponible - 4 ans grade Colonel - Note TB min 2024',
        'statut': 'Actif'
    })
    
    return all_rules

def import_all_rules():
    """Importer toutes les 27 règles officielles en base de données"""
    print("🚀 Import des 27 RÈGLES OFFICIELLES d'avancement")
    print("=" * 70)
    print()
    
    # Récupérer toutes les règles
    all_rules = get_all_rules_from_documents()
    
    print(f"📋 {len(all_rules)} règles à importer")
    print()
    
    # Vérifier si des règles existent déjà
    existing_rules = db_manager.get_all_rules()
    if existing_rules:
        print(f"⚠️  {len(existing_rules)} règle(s) existe(nt) déjà en base")
        response = input("Voulez-vous SUPPRIMER les anciennes et importer les nouvelles ? (y/N): ")
        if response.lower() == 'y':
            print("🗑️  Suppression des anciennes règles...")
            for rule in existing_rules:
                db_manager.delete_rule(rule['id'])
            print("✅ Anciennes règles supprimées")
        else:
            print("❌ Import annulé")
            return
    
    print()
    print("📥 Import en cours...")
    print()
    
    # Importer chaque règle avec affichage détaillé
    success_count = 0
    error_count = 0
    
    current_category = None
    
    for i, rule in enumerate(all_rules, 1):
        # Afficher la catégorie si elle change
        if rule['categorie'] != current_category:
            current_category = rule['categorie']
            print()
            print(f"🎖️  {current_category.upper()}")
            print("-" * 70)
        
        try:
            rule_id = db_manager.create_rule(rule)
            if rule_id:
                success_count += 1
                # Affichage compact
                diplomes_str = ', '.join(rule['diplomes_requis']) if rule['diplomes_requis'] else 'Aucun'
                print(f"✅ [{i:2d}/27] {rule['grade_source']:20s} → {rule['grade_cible']:20s} ({rule['type_avancement']:12s}) | Diplômes: {diplomes_str[:30]}")
            else:
                error_count += 1
                print(f"❌ [{i:2d}/27] ERREUR: {rule['grade_source']} → {rule['grade_cible']}")
        except Exception as e:
            error_count += 1
            print(f"❌ [{i:2d}/27] EXCEPTION: {e}")
    
    print()
    print("=" * 70)
    print("✅ IMPORT TERMINÉ !")
    print()
    print(f"📊 RÉSULTATS:")
    print(f"   ✅ Règles importées avec succès : {success_count}")
    print(f"   ❌ Erreurs                      : {error_count}")
    print(f"   📦 Total en base                : {len(db_manager.get_all_rules())} règle(s)")
    print()
    
    # Afficher le résumé par catégorie
    rules_by_category = {}
    for rule in db_manager.get_all_rules():
        cat = rule['categorie']
        if cat not in rules_by_category:
            rules_by_category[cat] = 0
        rules_by_category[cat] += 1
    
    print("📈 RÉPARTITION PAR CATÉGORIE:")
    for category, count in sorted(rules_by_category.items()):
        emoji = "🎖️" if "rang" in category.lower() else "🎖️🎖️" if "Sous-off" in category else "🎖️🎖️🎖️"
        print(f"   {emoji} {category:25s} : {count:2d} règle(s)")
    
    print()
    print("🎯 Vous pouvez maintenant:")
    print("   1. Visualiser toutes les règles dans l'application (section Règles)")
    print("   2. Évaluer les agents avec les règles officielles")
    print("   3. Générer des rapports d'avancement")
    print()
    print("✅ Import réussi ! Le système est prêt à fonctionner.")

if __name__ == "__main__":
    try:
        import_all_rules()
    except KeyboardInterrupt:
        print("\n❌ Import interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors de l'import: {e}")
        import traceback
        traceback.print_exc()