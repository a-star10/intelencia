"""
Script de migration pour l'historique des connexions
migrate_connection_history.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.connection_history import connection_history

def migrate_connection_history():
    """Initialiser le système d'historique des connexions"""
    print("🔍 Initialisation de l'historique des connexions")
    print("=" * 70)
    print()
    
    print("1️⃣ Création de la table connection_history...")
    connection_history.init_database()
    print("   ✅ Table créée avec succès")
    print()
    
    print("2️⃣ Vérification de l'intégrité...")
    stats = connection_history.get_statistics(days=30)
    print(f"   📊 Total connexions : {stats['total_connections']}")
    print(f"   👥 Utilisateurs uniques : {stats['unique_users']}")
    print()
    
    print("=" * 70)
    print("✅ INITIALISATION TERMINÉE !")
    print()
    print("📋 L'historique des connexions est maintenant opérationnel.")
    print()
    print("🎯 Fonctionnalités disponibles :")
    print("   • Historique complet des connexions/déconnexions")
    print("   • Sessions actives en temps réel")
    print("   • Détection des tentatives d'accès échouées")
    print("   • Statistiques détaillées")
    print("   • Graphiques d'activité")
    print()

if __name__ == "__main__":
    try:
        migrate_connection_history()
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# GUIDE D'INTÉGRATION COMPLET
# ============================================================================

"""
📋 GUIDE D'INTÉGRATION - AUTHENTIFICATION + HISTORIQUE
======================================================================

🎯 ÉTAPE 1 : COPIER LES FICHIERS
---------------------------------

Nouveaux fichiers à créer :

1. core/auth_manager.py (voir artifact "auth_system_complete")
2. core/connection_history.py (voir artifact "connection_history")
3. gui/login_window.py (voir artifact "login_screen")
4. gui/components/users_management.py (voir artifact "user_management_ui")
5. gui/components/connection_history_ui.py (voir artifact "connection_history_ui")
6. migrate_auth.py (voir artifact "auth_integration")
7. migrate_connection_history.py (ce fichier)


🎯 ÉTAPE 2 : INITIALISER LES BASES DE DONNÉES
----------------------------------------------

Dans le terminal :

```bash
# 1. Initialiser l'authentification
python migrate_auth.py

# 2. Initialiser l'historique
python migrate_connection_history.py
```


🎯 ÉTAPE 3 : MODIFIER core/auth_manager.py
-------------------------------------------

Ajouter ces lignes dans auth_manager.py :

```python
# En haut du fichier
from core.connection_history import connection_history

# Dans authenticate(), après connexion réussie (ligne ~150) :
# Enregistrer la connexion
connection_history.record_login(dict(user), success=True)

# Dans authenticate(), après échec (ligne ~145) :
# Enregistrer l'échec
connection_history.record_login(
    {'id': None, 'username': username, 'full_name': 'Unknown'},
    success=False,
    failure_reason="Invalid credentials"
)

# Dans logout() (ligne ~175) :
# Enregistrer la déconnexion
if self.current_user:
    connection_history.record_logout(self.current_user['id'])
```


🎯 ÉTAPE 4 : REMPLACER main.py
-------------------------------

Utiliser le code complet de l'artifact "main_py_complete"


🎯 ÉTAPE 5 : MODIFIER gui/main_window.py
-----------------------------------------

A. Ajouter les imports (ligne 10) :
```python
from core.auth_manager import auth_manager
```

B. Dans __init__ (ligne 25) :
```python
def __init__(self):
    self.root = ctk.CTk()
    self.current_page = "dashboard"
    self.current_user = auth_manager.current_user  # NOUVEAU
    
    # ... reste du code ...
```

C. Remplacer la méthode create_sidebar() par la version avec :
   - Info utilisateur en haut
   - Navigation avec permissions
   - Bouton de déconnexion

D. Ajouter la méthode logout() à la fin de la classe :
```python
def logout(self):
    \"\"\"Déconnecter l'utilisateur\"\"\"
    from tkinter import messagebox
    
    response = messagebox.askyesno(
        "Déconnexion",
        "Voulez-vous vraiment vous déconnecter ?"
    )
    
    if response:
        auth_manager.logout()
        self.root.destroy()
        
        from gui.login_window import show_login
        
        def on_login_success(user):
            app = MilitaryCareerApp()
            app.run()
        
        show_login(on_login_success)
```


🎯 ÉTAPE 6 : MODIFIER gui/settings_view.py
-------------------------------------------

A. Ajouter l'import (ligne 10) :
```python
from core.auth_manager import auth_manager
```

B. Dans show_settings(), ajouter l'onglet Utilisateurs :
```python
def show_settings(app):
    # ... code existant ...
    
    # Créer les onglets
    tabview.add("🎨 Apparence")
    tabview.add("📏 Typographie")
    tabview.add("🖼️ Logo")
    tabview.add("📊 Tableaux")
    tabview.add("📈 Dashboard")
    
    # NOUVEAU: Onglet utilisateurs (si admin)
    if auth_manager.has_permission('*'):
        tabview.add("👥 Utilisateurs")
    
    tabview.add("💾 Sauvegarde")
    
    # Remplir les onglets
    create_appearance_tab(tabview.tab("🎨 Apparence"), app)
    # ... autres onglets ...
    
    # NOUVEAU: Tab utilisateurs
    if auth_manager.has_permission('*'):
        from gui.components.users_management import create_users_tab
        create_users_tab(tabview.tab("👥 Utilisateurs"), app)
    
    create_backup_tab(tabview.tab("💾 Sauvegarde"), app)
```


🎯 ÉTAPE 7 : MODIFIER gui/components/users_management.py
---------------------------------------------------------

À la fin de la fonction create_users_tab(), ajouter :

```python
def create_users_tab(parent, app):
    # ... code existant ...
    
    # Logs d'audit
    create_audit_logs_section(scroll_frame)
    
    # NOUVEAU: Séparateur
    separator = ctk.CTkFrame(scroll_frame, height=2, fg_color=("gray70", "gray30"))
    separator.pack(fill="x", padx=20, pady=30)
    
    # NOUVEAU: Section historique des connexions
    from gui.components.connection_history_ui import create_connection_history_section
    create_connection_history_section(scroll_frame, app)
```


🎯 ÉTAPE 8 : TESTER L'APPLICATION
----------------------------------

```bash
python main.py
```

1. Écran de connexion devrait s'afficher
2. Se connecter avec admin/admin123
3. Changer le mot de passe obligatoire
4. Accéder à l'application
5. Aller dans Paramètres → Utilisateurs
6. Voir l'historique des connexions en bas


📊 STRUCTURE DE LA BASE DE DONNÉES
===================================

Nouvelles tables créées :

1. users
   - Utilisateurs du système
   - Mots de passe hashés
   - Rôles et permissions

2. sessions
   - Sessions actives
   - Tokens d'authentification
   - Expiration automatique

3. audit_logs
   - Logs de toutes les actions
   - Traçabilité complète

4. connection_history
   - Historique des connexions/déconnexions
   - Informations système
   - Statistiques d'utilisation


🔐 RÔLES ET PERMISSIONS
========================

| Rôle          | Permissions                                    |
|---------------|------------------------------------------------|
| Admin         | Tout + Gestion utilisateurs                    |
| Manager       | Agents, Règles, Évaluations, Rapports         |
| Operator      | Consultation + Modification agents             |
| Viewer        | Lecture seule                                  |


✅ CHECKLIST FINALE
====================

Installation :
- [ ] Copier tous les nouveaux fichiers
- [ ] Exécuter migrate_auth.py
- [ ] Exécuter migrate_connection_history.py
- [ ] Modifier main.py
- [ ] Modifier gui/main_window.py
- [ ] Modifier gui/settings_view.py
- [ ] Modifier gui/components/users_management.py

Test :
- [ ] Lancer l'application
- [ ] Se connecter (admin/admin123)
- [ ] Changer le mot de passe
- [ ] Créer un nouvel utilisateur
- [ ] Vérifier les permissions
- [ ] Consulter l'historique des connexions
- [ ] Tester la déconnexion
- [ ] Tester une connexion échouée

Fonctionnalités :
- [ ] Authentification fonctionne
- [ ] Sidebar affiche l'utilisateur
- [ ] Navigation avec permissions
- [ ] Gestion des utilisateurs (CRUD)
- [ ] Logs d'audit visibles
- [ ] Historique des connexions visible
- [ ] Sessions actives affichées
- [ ] Tentatives échouées détectées
- [ ] Statistiques calculées
- [ ] Déconnexion fonctionne


🎉 FÉLICITATIONS !
==================

Votre système d'authentification est maintenant complètement opérationnel avec :

✅ Authentification sécurisée (PBKDF2-SHA256)
✅ 4 rôles avec permissions granulaires
✅ Gestion complète des utilisateurs
✅ Logs d'audit détaillés
✅ Historique des connexions
✅ Sessions actives en temps réel
✅ Détection des tentatives échouées
✅ Statistiques d'utilisation
✅ Interface moderne et intuitive


📞 SUPPORT
==========

En cas de problème :

1. Vérifier les logs dans l'application
2. Consulter l'historique des connexions
3. Vérifier les permissions des utilisateurs
4. S'assurer que les tables sont créées

Commandes utiles :

# Voir la structure de la base
sqlite3 data/military_careers.db ".schema"

# Compter les utilisateurs
sqlite3 data/military_careers.db "SELECT COUNT(*) FROM users;"

# Voir l'historique
sqlite3 data/military_careers.db "SELECT * FROM connection_history ORDER BY login_time DESC LIMIT 10;"
"""

if __name__ == "__main__":
    print(__doc__)