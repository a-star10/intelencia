#!/usr/bin/env python3
"""
Script de test des préférences utilisateur
Exécuter : python test_preferences.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.preferences_manager import preferences_manager

def test_preferences():
    """Tester le système de préférences"""
    print("🧪 TEST DU SYSTÈME DE PRÉFÉRENCES")
    print("=" * 70)
    print()
    
    # 1. Afficher les préférences actuelles
    print("1️⃣ PRÉFÉRENCES ACTUELLES :")
    print("-" * 70)
    for key, value in preferences_manager.preferences.items():
        print(f"   {key:30s} : {value}")
    print()
    
    # 2. Test de modification
    print("2️⃣ TEST DE MODIFICATION :")
    print("-" * 70)
    
    # Sauvegarder l'ancien thème
    old_theme = preferences_manager.get('theme')
    print(f"   Thème actuel : {old_theme}")
    
    # Changer le thème
    new_theme = 'dark' if old_theme == 'light' else 'light'
    preferences_manager.set('theme', new_theme)
    print(f"   ✅ Thème changé en : {preferences_manager.get('theme')}")
    
    # Restaurer l'ancien thème
    preferences_manager.set('theme', old_theme)
    print(f"   🔄 Thème restauré à : {preferences_manager.get('theme')}")
    print()
    
    # 3. Test des getters spéciaux
    print("3️⃣ GETTERS SPÉCIAUX :")
    print("-" * 70)
    
    font_multiplier = preferences_manager.get_font_size_multiplier()
    print(f"   Multiplicateur de police : {font_multiplier}")
    
    accent_color = preferences_manager.get_accent_color_hex()
    print(f"   Couleur d'accent (hex) : {accent_color}")
    print()
    
    # 4. Vérifier le fichier JSON
    print("4️⃣ FICHIER DE CONFIGURATION :")
    print("-" * 70)
    config_file = preferences_manager.preferences_file
    print(f"   Emplacement : {config_file}")
    print(f"   Existe : {'✅' if config_file.exists() else '❌'}")
    
    if config_file.exists():
        size = config_file.stat().st_size
        print(f"   Taille : {size} octets")
        
        # Afficher le contenu
        print(f"\n   📄 Contenu du fichier :")
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
            for line in content.split('\n')[:10]:  # 10 premières lignes
                print(f"      {line}")
    print()
    
    # 5. Test Export/Import
    print("5️⃣ TEST EXPORT/IMPORT :")
    print("-" * 70)
    
    export_path = "config/test_export.json"
    print(f"   Export vers : {export_path}")
    
    if preferences_manager.export_preferences(export_path):
        print(f"   ✅ Export réussi")
        
        # Vérifier que le fichier existe
        if Path(export_path).exists():
            print(f"   ✅ Fichier créé : {export_path}")
            
            # Test d'import
            print(f"   Test import depuis : {export_path}")
            if preferences_manager.import_preferences(export_path):
                print(f"   ✅ Import réussi")
            else:
                print(f"   ❌ Erreur import")
        else:
            print(f"   ❌ Fichier non créé")
    else:
        print(f"   ❌ Erreur export")
    print()
    
    # 6. Tester les valeurs par défaut
    print("6️⃣ VALEURS PAR DÉFAUT :")
    print("-" * 70)
    
    defaults = preferences_manager.default_preferences
    print(f"   Nombre de préférences : {len(defaults)}")
    print(f"   Thème par défaut : {defaults['theme']}")
    print(f"   Couleur par défaut : {defaults['accent_color']}")
    print(f"   Police tableaux : {defaults['table_font_size']} pt")
    print()
    
    # 7. Test réinitialisation (confirmation requise)
    print("7️⃣ TEST RÉINITIALISATION :")
    print("-" * 70)
    print("   ⚠️ Voulez-vous tester la réinitialisation ?")
    response = input("   (Cela écrasera vos préférences actuelles) (y/N): ")
    
    if response.lower() == 'y':
        # Sauvegarder les préférences actuelles
        backup_path = "config/backup_before_reset.json"
        preferences_manager.export_preferences(backup_path)
        print(f"   💾 Backup créé : {backup_path}")
        
        # Réinitialiser
        if preferences_manager.reset_to_defaults():
            print(f"   ✅ Réinitialisation réussie")
            
            # Restaurer depuis le backup
            print(f"   🔄 Restauration depuis le backup...")
            preferences_manager.import_preferences(backup_path)
            print(f"   ✅ Préférences restaurées")
        else:
            print(f"   ❌ Erreur réinitialisation")
    else:
        print("   ⏭️ Test de réinitialisation ignoré")
    
    print()
    print("=" * 70)
    print("✅ TESTS TERMINÉS !")
    print()
    print("📋 RÉSUMÉ :")
    print(f"   • Fichier config : {config_file}")
    print(f"   • Thème : {preferences_manager.get('theme')}")
    print(f"   • Couleur : {preferences_manager.get('accent_color')}")
    print(f"   • Logo : {preferences_manager.get('logo_path')}")
    print(f"   • Lignes/page : {preferences_manager.get('rows_per_page')}")
    print()
    print("🎯 Vous pouvez maintenant lancer l'application et aller dans Paramètres !")

if __name__ == "__main__":
    try:
        test_preferences()
    except KeyboardInterrupt:
        print("\n❌ Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()