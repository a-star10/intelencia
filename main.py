#!/usr/bin/env python3
"""
Military Career Manager - VERSION AVEC AUTHENTIFICATION
Application de gestion des carrières militaires
Point d'entrée principal avec système d'authentification
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Point d'entrée principal avec authentification"""
    try:
        print(" Démarrage du Système de gestion automatisée des carrières DGSS...")
        print("=" * 70)
        
        # Import dynamique pour éviter les erreurs de dépendances
        from gui.login_window import show_login
        from gui.main_window import MilitaryCareerApp
        from core.auth_manager import auth_manager
        
        print("✅ Modules chargés avec succès")
        print("🔐 Système d'authentification activé")
        print("=" * 70)
        print()
        
        def on_login_success(user):
            """Callback appelé après connexion réussie"""
            print(f"\n✅ Connexion réussie !")
            print(f"   👤 Utilisateur : {user['full_name']}")
            print(f"   🎖️  Rôle       : {auth_manager.ROLES[user['role']]['name']}")
            print(f"   📧 Email      : {user.get('email', 'Non renseigné')}")
            print()
            print("🚀 Lancement de l'interface principale...")
            print("=" * 70)
            
            # Lancer l'application principale
            app = MilitaryCareerApp()
            app.run()
            
            # Après fermeture de l'application
            print("\n👋 Application fermée")
            print("   À bientôt !")
        
        # Afficher l'écran de connexion
        show_login(on_login_success)
        
    except ImportError as e:
        print(f"\n❌ Erreur d'import : {e}")
        print("\n💡 Vérifiez que :")
        print("   1. L'environnement virtuel est activé")
        print("   2. Les dépendances sont installées (pip install -r requirements.txt)")
        print("   3. Le système d'authentification est initialisé (python migrate_auth.py)")
        print("\n📝 Commandes :")
        print("   Windows : venv\\Scripts\\Activate.ps1")
        print("   Linux/Mac : source venv/bin/activate")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Application interrompue par l'utilisateur")
        print("   Déconnexion en cours...")
        
        # Nettoyer la session si elle existe
        try:
            from core.auth_manager import auth_manager
            auth_manager.logout()
            print("   ✅ Déconnexion effectuée")
        except:
            pass
        
        print("   👋 Au revoir !")
        
    except Exception as e:
        print(f"\n❌ Erreur critique : {e}")
        print("\n🔍 Détails de l'erreur :")
        import traceback
        traceback.print_exc()
        
        print("\n💡 Solutions possibles :")
        print("   1. Vérifiez que la base de données existe")
        print("   2. Exécutez : python migrate_auth.py")
        print("   3. Vérifiez les permissions des fichiers")
        print("   4. Consultez les logs d'audit dans l'application")
        
        sys.exit(1)

if __name__ == "__main__":
    main()