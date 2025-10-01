"""
Script de migration pour initialiser l'authentification
migrate_auth.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.auth_manager import auth_manager

def migrate_auth():
    """Initialiser le système d'authentification"""
    print("🔐 Initialisation du système d'authentification")
    print("=" * 70)
    print()
    
    print("1️⃣ Création des tables...")
    auth_manager.init_database()
    print()
    
    print("2️⃣ Création de l'utilisateur admin par défaut...")
    auth_manager.create_default_admin()
    print()
    
    print("3️⃣ Vérification...")
    users = auth_manager.get_all_users()
    print(f"   📊 {len(users)} utilisateur(s) en base")
    
    for user in users:
        print(f"   👤 {user['username']} ({user['full_name']}) - Rôle: {user['role']}")
    
    print()
    print("=" * 70)
    print("✅ INITIALISATION TERMINÉE !")
    print()
    print("📋 Informations de connexion par défaut:")
    print("   Utilisateur : admin")
    print("   Mot de passe: admin123")
    print()
    print("⚠️  IMPORTANT : Changez ce mot de passe lors de la première connexion!")
    print()
    print("🎯 Vous pouvez maintenant lancer l'application:")
    print("   python main.py")

if __name__ == "__main__":
    try:
        migrate_auth()
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# main.py - VERSION AVEC AUTHENTIFICATION
# ============================================================================

"""
#!/usr/bin/env python3
\"\"\"
Military Career Manager - VERSION AVEC AUTHENTIFICATION
Application de gestion des carrieres militaires
\"\"\"

import sys
from pathlib import Path

# Ajouter le repertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    \"\"\"Point d'entree principal avec authentification\"\"\"
    try:
        print("Demarrage de Military Career Manager...")
        
        # Import dynamique
        from gui.login_window import show_login
        from gui.main_window import MilitaryCareerApp
        from core.auth_manager import auth_manager
        
        def on_login_success(user):
            \"\"\"Callback après connexion réussie\"\"\"
            print(f"✅ Connexion réussie: {user['full_name']} ({user['role']})")
            
            # Lancer l'application principale
            app = MilitaryCareerApp()
            app.run()
        
        # Afficher l'écran de connexion
        show_login(on_login_success)
        
    except ImportError as e:
        print(f"Erreur d'import: {e}")
        print("Verifiez que l'environnement virtuel est active")
        
    except KeyboardInterrupt:
        print("\\nApplication fermee par l'utilisateur")
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
\"\"\"


# ============================================================================
# gui/main_window.py - MODIFICATIONS POUR L'AUTHENTIFICATION
# ============================================================================

# Ajouter ces imports en haut du fichier:
from core.auth_manager import auth_manager

# Modifier la classe MilitaryCareerApp:

class MilitaryCareerApp:
    \"\"\"Application principale avec authentification\"\"\"
    
    def __init__(self):
        self.root = ctk.CTk()
        self.current_page = "dashboard"
        self.current_user = auth_manager.current_user  # NOUVEAU
        
        # Appliquer les préférences
        self.apply_preferences()
        
        self.setup_window()
        self.setup_ui()
    
    def setup_ui(self):
        \"\"\"Configuration de l'interface utilisateur avec authentification\"\"\"
        # Configuration grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Sidebar avec info utilisateur
        self.create_sidebar()
        
        # Zone de contenu principale
        self.create_main_content()
        
        # Charger le dashboard par defaut
        self.show_dashboard()
    
    def create_sidebar(self):
        \"\"\"Créer la barre laterale avec info utilisateur\"\"\"
        self.sidebar = ctk.CTkFrame(self.root, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)  # MODIFIÉ: index 10 au lieu de 9
        
        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.load_and_display_logo(logo_frame)
        
        # Titre
        header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Gestion",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Gestion des carrieres",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle_label.pack()
        
        # NOUVEAU: Info utilisateur
        user_frame = ctk.CTkFrame(self.sidebar, corner_radius=10)
        user_frame.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="ew")
        
        user_inner = ctk.CTkFrame(user_frame, fg_color="transparent")
        user_inner.pack(fill="x", padx=15, pady=12)
        
        # Emoji selon le rôle
        role_emojis = {
            'admin': '👑',
            'manager': '👔',
            'operator': '💼',
            'viewer': '👁️'
        }
        emoji = role_emojis.get(self.current_user.get('role', 'viewer'), '👤')
        
        user_label = ctk.CTkLabel(
            user_inner,
            text=f"{emoji} {self.current_user.get('full_name', 'Utilisateur')}",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        user_label.pack(anchor="w")
        
        role_name = auth_manager.ROLES.get(
            self.current_user.get('role', 'viewer'), {}
        ).get('name', 'Utilisateur')
        
        role_label = ctk.CTkLabel(
            user_inner,
            text=role_name,
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        role_label.pack(anchor="w")
        
        # Boutons de navigation (avec permissions)
        self.nav_buttons = {}
        
        nav_items = [
            ("📊 Dashboard", "dashboard", None),
            ("👥 Agents", "agents", "view_agents"),
            ("⚙️ Regles", "rules", "view_rules"),
            ("🎯 Evaluation", "evaluation", "view_evaluation"),
            ("📈 Rapports", "reports", "view_reports"),
            ("🔧 Parametres", "settings", None)
        ]
        
        row_idx = 3
        for text, page_id, permission in nav_items:
            # Vérifier la permission
            if permission and not auth_manager.has_permission(permission):
                continue  # Masquer si pas la permission
            
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                font=ctk.CTkFont(size=14),
                height=40,
                anchor="w",
                command=lambda p=page_id: self.navigate_to(p)
            )
            btn.grid(row=row_idx, column=0, padx=20, pady=5, sticky="ew")
            self.nav_buttons[page_id] = btn
            row_idx += 1
        
        # Spacer
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.grid(row=10, column=0, sticky="nsew")
        
        # Footer avec déconnexion
        footer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer_frame.grid(row=11, column=0, padx=20, pady=20, sticky="ew")
        
        # Bouton déconnexion
        logout_btn = ctk.CTkButton(
            footer_frame,
            text="🚪 Déconnexion",
            height=35,
            fg_color="#dc2626",
            hover_color="#991b1b",
            command=self.logout
        )
        logout_btn.pack(fill="x", pady=(0, 10))
        
        # Mode sombre
        theme_label = ctk.CTkLabel(footer_frame, text="Mode sombre")
        theme_label.pack()
        
        current_theme = preferences_manager.get('theme', 'light')
        self.theme_switch = ctk.CTkSwitch(
            footer_frame,
            text="",
            command=self.toggle_theme
        )
        if current_theme == 'dark':
            self.theme_switch.select()
        self.theme_switch.pack(pady=5)
    
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
            
            # Relancer l'écran de connexion
            from gui.login_window import show_login
            
            def on_login_success(user):
                app = MilitaryCareerApp()
                app.run()
            
            show_login(on_login_success)


# ============================================================================
# gui/settings_view.py - AJOUTER L'ONGLET UTILISATEURS
# ============================================================================

# Modifier la fonction show_settings pour ajouter l'onglet:

def show_settings(app):
    \"\"\"Afficher les paramètres avec onglet utilisateurs\"\"\"
    app.page_title.configure(text="🔧 Paramètres")
    
    # Frame principal avec onglets
    tabview = ctk.CTkTabview(app.content_frame, width=1200)
    tabview.pack(fill="both", expand=True, padx=20, pady=20)
    
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
    
    # Remplir chaque onglet
    create_appearance_tab(tabview.tab("🎨 Apparence"), app)
    create_typography_tab(tabview.tab("📏 Typographie"), app)
    create_logo_tab(tabview.tab("🖼️ Logo"), app)
    create_tables_tab(tabview.tab("📊 Tableaux"), app)
    create_dashboard_tab(tabview.tab("📈 Dashboard"), app)
    
    # NOUVEAU: Tab utilisateurs
    if auth_manager.has_permission('*'):
        from gui.components.users_management import create_users_tab
        create_users_tab(tabview.tab("👥 Utilisateurs"), app)
    
    create_backup_tab(tabview.tab("💾 Sauvegarde"), app)
    
    # Boutons globaux en bas
    create_global_buttons(app.content_frame, app)
"""

if __name__ == "__main__":
    print(__doc__)