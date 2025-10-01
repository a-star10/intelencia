"""
Interface principale modulaire - VERSION AVEC AUTHENTIFICATION COMPLÈTE
gui/main_window.py
"""
import customtkinter as ctk
import sys
from pathlib import Path
from PIL import Image

# Import config
sys.path.append(str(Path(__file__).parent.parent))
from config import APP_TITLE, WINDOW_SIZE, MIN_WINDOW_SIZE

# Import du gestionnaire de préférences
from core.preferences_manager import preferences_manager

# Import de l'authentification
from core.auth_manager import auth_manager

# Charger le thème AVANT tout le reste
saved_theme = preferences_manager.get('theme', 'light')
ctk.set_appearance_mode(saved_theme)

# Configuration CustomTkinter
ctk.set_default_color_theme("blue")

# Imports des vues modulaires
from gui.dashboard_view import show_dashboard
from gui.agents_view import show_agents
from gui.rules_view import show_rules
from gui.evaluation_view import show_evaluation
from gui.reports_view import show_reports
from gui.settings_view import show_settings
from gui.components.actions import (
    quick_add_agent, quick_evaluate_all, quick_generate_report, 
    quick_import_excel, add_new_agent, export_agents, import_agents
)

class MilitaryCareerApp:
    """Application principale de gestion des carrieres militaires"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.current_page = "dashboard"
        self.current_user = auth_manager.current_user  # Utilisateur connecté
        
        # Appliquer les préférences au démarrage
        self.apply_preferences()
        
        self.setup_window()
        self.setup_ui()
        
    def apply_preferences(self):
        """Appliquer les préférences utilisateur au démarrage"""
        theme = preferences_manager.get('theme', 'light')
        ctk.set_appearance_mode(theme)
        print(f"🎨 Thème chargé : {theme}")
        
        accent_color = preferences_manager.get('accent_color', 'blue')
        print(f"🎨 Couleur d'accent : {accent_color}")
        
        font_size = preferences_manager.get('global_font_size', 'normal')
        print(f"📏 Taille de police : {font_size}")
    
    def setup_window(self):
        """Configuration de la fenetre principale"""
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(*[int(x) for x in MIN_WINDOW_SIZE.split('x')])
        
        # Centrer la fenetre
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_height()) // 2
        self.root.geometry(f"+{x}+{y}")
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Configuration grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.create_sidebar()
        
        # Zone de contenu principale
        self.create_main_content()
        
        # Charger le dashboard par defaut
        self.show_dashboard()
        
    def create_sidebar(self):
        """Créer la barre laterale de navigation - AVEC AUTHENTIFICATION"""
        self.sidebar = ctk.CTkFrame(self.root, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        # ===== SECTION LOGO =====
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.load_and_display_logo(logo_frame)
        
        # ===== SECTION TITRE =====
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
        
        # ===== 🆕 SECTION INFO UTILISATEUR =====
        user_frame = ctk.CTkFrame(
            self.sidebar, 
            corner_radius=10, 
            border_width=1, 
            border_color=("gray70", "gray30")
        )
        user_frame.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="ew")
        
        user_inner = ctk.CTkFrame(user_frame, fg_color="transparent")
        user_inner.pack(fill="x", padx=15, pady=12)
        
        if self.current_user:
            # Emoji selon le rôle
            role_emojis = {
                'admin': '👑',
                'manager': '👔',
                'operator': '💼',
                'viewer': '👁️'
            }
            emoji = role_emojis.get(self.current_user.get('role', 'viewer'), '👤')
            
            # Nom de l'utilisateur
            user_label = ctk.CTkLabel(
                user_inner,
                text=f"{emoji} {self.current_user.get('full_name', 'Utilisateur')}",
                font=ctk.CTkFont(size=11, weight="bold")
            )
            user_label.pack(anchor="w")
            
            # Rôle
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
        else:
            # Fallback si pas d'utilisateur
            user_label = ctk.CTkLabel(
                user_inner,
                text="👤 Non connecté",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            user_label.pack()
        
        # ===== BOUTONS DE NAVIGATION =====
        self.nav_buttons = {}
        
        nav_items = [
            ("📊 Dashboard", "dashboard"),
            ("👥 Agents", "agents"),
            ("⚙️ Regles", "rules"),
            ("🎯 Evaluation", "evaluation"),
            ("📈 Rapports", "reports"),
            ("🔧 Parametres", "settings")
        ]
        
        for i, (text, page_id) in enumerate(nav_items, 3):  # Commence à row 3
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                font=ctk.CTkFont(size=14),
                height=40,
                anchor="w",
                command=lambda p=page_id: self.navigate_to(p)
            )
            btn.grid(row=i, column=0, padx=20, pady=5, sticky="ew")
            self.nav_buttons[page_id] = btn
            
        # Spacer
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.grid(row=10, column=0, sticky="nsew")
        
        # ===== FOOTER AVEC DÉCONNEXION =====
        footer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer_frame.grid(row=11, column=0, padx=20, pady=20, sticky="ew")
        
        # 🆕 Bouton déconnexion
        logout_btn = ctk.CTkButton(
            footer_frame,
            text="🚪 Déconnexion",
            height=35,
            fg_color="#dc2626",
            hover_color="#991b1b",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.logout
        )
        logout_btn.pack(fill="x", pady=(0, 10))
        
        # Mode sombre
        theme_label = ctk.CTkLabel(footer_frame, text="Mode sombre", font=ctk.CTkFont(size=10))
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
    
    def load_and_display_logo(self, parent_frame):
        """Charger et afficher le logo depuis les préférences"""
        try:
            logo_path = preferences_manager.get('logo_path', 'assets/logo.png')
            logo_size = preferences_manager.get('logo_size', 180)
            use_custom = preferences_manager.get('use_custom_logo', False)
            
            logo_path = logo_path.replace('\\', '/')
            logo_file = Path(logo_path)
            
            print(f"🖼️ Chargement du logo : {logo_path}")
            
            if logo_file.exists():
                logo_image = Image.open(logo_file)
                logo_image = logo_image.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                
                logo_ctk = ctk.CTkImage(
                    light_image=logo_image,
                    dark_image=logo_image,
                    size=(logo_size, logo_size)
                )
                
                logo_label = ctk.CTkLabel(
                    parent_frame,
                    image=logo_ctk,
                    text=""
                )
                logo_label.pack()
                
                print(f"✅ Logo chargé avec succès !")
            else:
                print(f"⚠️ Logo non trouvé : {logo_path}, affichage du placeholder")
                self.display_logo_placeholder(parent_frame)
                
        except Exception as e:
            print(f"❌ Erreur chargement logo: {e}")
            import traceback
            traceback.print_exc()
            self.display_logo_placeholder(parent_frame)
    
    def display_logo_placeholder(self, parent_frame):
        """Afficher un placeholder si le logo n'existe pas"""
        placeholder_frame = ctk.CTkFrame(
            parent_frame,
            width=180,
            height=180,
            corner_radius=10,
            fg_color=("gray85", "gray25")
        )
        placeholder_frame.pack()
        
        placeholder_label = ctk.CTkLabel(
            placeholder_frame,
            text="🛡️\nMILITARY\nCAREER",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("gray50", "gray70")
        )
        placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
        
    def create_main_content(self):
        """Creer la zone de contenu principale"""
        self.main_content = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)
        
        # Header de la page
        self.page_header = ctk.CTkFrame(self.main_content)
        self.page_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        self.page_title = ctk.CTkLabel(
            self.page_header,
            text="",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.page_title.pack(side="left", padx=20, pady=15)
        
        # Zone de contenu scrollable
        self.content_frame = ctk.CTkScrollableFrame(self.main_content)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
    def navigate_to(self, page_id):
        """Naviguer vers une page"""
        print(f"Navigation vers: {page_id}")
        
        # Mettre a jour l'etat des boutons
        for btn_id, btn in self.nav_buttons.items():
            if btn_id == page_id:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color=["#3B8ED0", "#1F6AA5"])
        
        def cleanup_and_load():
            # Nettoyer le contenu actuel
            for widget in self.content_frame.winfo_children():
                try:
                    widget.destroy()
                except:
                    pass
            
            self.content_frame.update_idletasks()
            
            # Afficher la nouvelle page
            self.current_page = page_id
            
            if page_id == "dashboard":
                self.show_dashboard()
            elif page_id == "agents":
                self.show_agents()
            elif page_id == "rules":
                self.show_rules()
            elif page_id == "evaluation":
                self.show_evaluation()
            elif page_id == "reports":
                self.show_reports()
            elif page_id == "settings":
                self.show_settings()
        
        self.root.after_idle(cleanup_and_load)
    
    def toggle_theme(self):
        """Basculer entre theme clair/sombre ET SAUVEGARDER"""
        if self.theme_switch.get():
            new_theme = "dark"
        else:
            new_theme = "light"
        
        ctk.set_appearance_mode(new_theme)
        preferences_manager.set('theme', new_theme)
        
        print(f"🎨 Thème changé et sauvegardé : {new_theme}")
    
    def logout(self):
        """Déconnecter l'utilisateur et retourner à l'écran de connexion"""
        from tkinter import messagebox
        
        response = messagebox.askyesno(
            "Déconnexion",
            f"Voulez-vous vraiment vous déconnecter ?\n\n"
            f"Utilisateur : {self.current_user.get('full_name', 'Inconnu')}"
        )
        
        if response:
            print(f"\n👋 Déconnexion de {self.current_user.get('username', 'unknown')}")
            
            # Déconnecter
            auth_manager.logout()
            
            # Fermer la fenêtre actuelle
            self.root.destroy()
            
            # Relancer l'écran de connexion
            from gui.login_window import show_login
            
            def on_login_success(user):
                """Callback après reconnexion"""
                app = MilitaryCareerApp()
                app.run()
            
            show_login(on_login_success)
    
    # Delegation vers les modules
    def show_dashboard(self):
        show_dashboard(self)
    
    def show_agents(self):
        show_agents(self)
    
    def show_rules(self):
        show_rules(self)
    
    def show_evaluation(self):
        show_evaluation(self)
    
    def show_reports(self):
        show_reports(self)
    
    def show_settings(self):
        show_settings(self)
    
    # Actions delegues
    def quick_add_agent(self):
        quick_add_agent(self)
    
    def quick_evaluate_all(self):
        quick_evaluate_all(self)
    
    def quick_generate_report(self):
        quick_generate_report(self)
    
    def quick_import_excel(self):
        quick_import_excel(self)
    
    def add_new_agent(self):
        add_new_agent(self)
    
    def export_agents(self):
        export_agents(self)
    
    def import_agents(self):
        import_agents(self)
        
    def run(self):
        """Demarrer l'application"""
        print(f"Demarrage de {APP_TITLE}...")
        print("✅ Préférences chargées")
        print("Dashboard operationnel - Navigation disponible")
        self.root.mainloop()

if __name__ == "__main__":
    app = MilitaryCareerApp()
    app.run()