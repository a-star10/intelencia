"""
Écran de connexion moderne - VERSION DESIGN SYSTEM ÉPURÉ
gui/login_window.py

✨ Nouveautés:
- Design System unifié
- Toast notifications au lieu de MessageBox
- Loading lors de la connexion
- Interface minimaliste et élégante
- Animations fluides
- CORRECTION: Bouton visible avec hauteur ajustée
"""

import customtkinter as ctk
from PIL import Image
from pathlib import Path
import sys
import threading
import time

sys.path.append(str(Path(__file__).parent.parent))
from core.auth_manager import auth_manager
from core.preferences_manager import preferences_manager

# ==================== TOAST NOTIFICATION ====================

class LoginToast:
    """Toast notification pour le login"""
    
    def __init__(self, parent, message, type="error"):
        self.window = ctk.CTkToplevel(parent)
        self.window.withdraw()
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        
        # Couleurs
        colors = {
            'success': "#16a34a",
            'error': "#dc2626",
            'info': "#3b82f6"
        }
        
        icons = {
            'success': '✅',
            'error': '❌',
            'info': 'ℹ️'
        }
        
        color = colors.get(type, "#dc2626")
        icon = icons.get(type, '❌')
        
        # Frame
        frame = ctk.CTkFrame(
            self.window,
            fg_color=color,
            corner_radius=10
        )
        frame.pack()
        
        # Contenu
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(padx=20, pady=12)
        
        row = ctk.CTkFrame(content, fg_color="transparent")
        row.pack()
        
        ctk.CTkLabel(
            row,
            text=icon,
            font=ctk.CTkFont(size=18)
        ).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(
            row,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color="white"
        ).pack(side="left")
        
        # Position
        self.window.update_idletasks()
        width = self.window.winfo_width()
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + 100
        
        self.window.geometry(f"+{x}+{y}")
        self.window.deiconify()
        
        # Fade in
        self.window.attributes('-alpha', 0.0)
        self.fade_in()
        
        # Auto close
        self.window.after(3000, self.fade_out)
    
    def fade_in(self, alpha=0.0):
        alpha += 0.1
        if alpha <= 1.0:
            self.window.attributes('-alpha', alpha)
            self.window.after(15, lambda: self.fade_in(alpha))
    
    def fade_out(self, alpha=1.0):
        alpha -= 0.1
        if alpha >= 0.0:
            self.window.attributes('-alpha', alpha)
            self.window.after(15, lambda: self.fade_out(alpha))
        else:
            self.window.destroy()


# ==================== LOADING OVERLAY ====================

class LoginLoading:
    """Loading overlay pour le login"""
    
    def __init__(self, parent):
        self.overlay = ctk.CTkFrame(
            parent,
            fg_color=("white", "#1a1a1a"),
            corner_radius=0
        )
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Contenu
        content = ctk.CTkFrame(self.overlay, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        
        # Spinner (animation)
        self.spinner = ctk.CTkLabel(
            content,
            text="⏳",
            font=ctk.CTkFont(size=40)
        )
        self.spinner.pack(pady=(0, 10))
        
        ctk.CTkLabel(
            content,
            text="Connexion en cours...",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack()
        
        # Animation
        self.animate()
    
    def animate(self):
        """Animer le spinner"""
        current = self.spinner.cget("text")
        chars = ["⏳", "⌛"]
        idx = chars.index(current) if current in chars else 0
        next_char = chars[(idx + 1) % len(chars)]
        self.spinner.configure(text=next_char)
        self.overlay.after(500, self.animate)
    
    def destroy(self):
        self.overlay.destroy()


# ==================== FENÊTRE DE LOGIN ====================

class LoginWindow:
    """Fenêtre de connexion moderne et épurée"""
    
    def __init__(self, on_success_callback):
        self.on_success = on_success_callback
        self.window = ctk.CTk()
        self.loading = None
        
        # Config - HAUTEUR AUGMENTÉE POUR VOIR LE BOUTON
        self.window.title("Military Career Manager")
        self.window.geometry("480x700")
        self.window.resizable(False, False)
        
        # Appliquer le thème
        theme = preferences_manager.get('theme', 'light')
        ctk.set_appearance_mode(theme)
        
        # Couleur d'accent
        self.accent_color = preferences_manager.get_accent_color_hex()
        
        # Centrer
        self.center_window()
        
        # Créer l'UI
        self.create_ui()
        
        # Focus
        self.username_entry.focus()
    
    def center_window(self):
        """Centrer la fenêtre"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 480) // 2
        y = (self.window.winfo_screenheight() - 700) // 2
        self.window.geometry(f"+{x}+{y}")
    
    def create_ui(self):
        """Créer l'interface épurée"""
        # Container principal - PADDING RÉDUIT
        main = ctk.CTkFrame(self.window, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Logo minimaliste - PADDING RÉDUIT
        logo_frame = ctk.CTkFrame(main, fg_color="transparent")
        logo_frame.pack(pady=(0, 20))
        
        # Icône élégante
        icon = ctk.CTkLabel(
            logo_frame,
            text="🛡️",
            font=ctk.CTkFont(size=60)
        )
        icon.pack(pady=(0, 15))
        
        # Titre épuré
        title = ctk.CTkLabel(
            logo_frame,
            text="MILITARY CAREER",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.accent_color
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            logo_frame,
            text="Gestion des Carrières",
            font=ctk.CTkFont(size=11),
            text_color=("gray60", "gray50")
        )
        subtitle.pack(pady=(5, 0))
        
        # Card de connexion
        card = ctk.CTkFrame(
            main,
            corner_radius=15,
            border_width=1,
            border_color=("gray80", "gray30")
        )
        card.pack(fill="both", expand=True, pady=(10, 0))
        
        # Contenu de la card - PADDING RÉDUIT
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=25)
        
        # Titre formulaire
        form_title = ctk.CTkLabel(
            content,
            text="Connexion",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        form_title.pack(pady=(0, 20))
        
        # Champ username
        username_label = ctk.CTkLabel(
            content,
            text="Nom d'utilisateur",
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        )
        username_label.pack(fill="x", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            content,
            placeholder_text="Entrez votre identifiant",
            height=42,
            font=ctk.CTkFont(size=12),
            border_width=1,
            corner_radius=8
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        
        # Champ password
        password_label = ctk.CTkLabel(
            content,
            text="Mot de passe",
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        )
        password_label.pack(fill="x", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            content,
            placeholder_text="••••••••",
            show="•",
            height=42,
            font=ctk.CTkFont(size=12),
            border_width=1,
            corner_radius=8
        )
        self.password_entry.pack(fill="x", pady=(0, 10))
        
        # Remember me (optionnel, épuré)
        remember_frame = ctk.CTkFrame(content, fg_color="transparent")
        remember_frame.pack(fill="x", pady=(0, 15))
        
        self.remember_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            remember_frame,
            text="Se souvenir",
            variable=self.remember_var,
            font=ctk.CTkFont(size=10),
            checkbox_width=18,
            checkbox_height=18
        ).pack(side="left")
        
        # Bouton connexion - MAINTENANT VISIBLE
        self.login_btn = ctk.CTkButton(
            content,
            text="Se connecter",
            height=44,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.accent_color,
            hover_color=self.darken_color(self.accent_color),
            corner_radius=8,
            command=self.do_login
        )
        self.login_btn.pack(fill="x", pady=(0, 12))
        
        # Info discrète
        info = ctk.CTkFrame(
            content,
            fg_color=("gray90", "gray25"),
            corner_radius=8
        )
        info.pack(fill="x", pady=(8, 0))
        
        info_label = ctk.CTkLabel(
            info,
            text="AVERTISSEMENT - Ce système est exclusivement réservé à un usage autorisé. ",
            font=ctk.CTkFont(size=9),
            text_color=("gray60", "gray50")
        )
        info_label.pack(pady=8)
        
        # Bind Enter
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.do_login())
    
    def darken_color(self, hex_color, factor=0.8):
        """Assombrir une couleur"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * factor))
        g = max(0, int(g * factor))
        b = max(0, int(b * factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def show_toast(self, message, type="error"):
        """Afficher un toast"""
        LoginToast(self.window, message, type)
    
    def do_login(self):
        """Effectuer la connexion avec loading"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Validation
        if not username or not password:
            self.show_toast("Veuillez remplir tous les champs", "error")
            return
        
        # Désactiver les champs
        self.username_entry.configure(state="disabled")
        self.password_entry.configure(state="disabled")
        self.login_btn.configure(state="disabled", text="Connexion...")
        
        # Afficher loading
        self.loading = LoginLoading(self.window)
        
        def authenticate():
            """Authentifier en arrière-plan"""
            try:
                time.sleep(0.5)  # Petit délai pour l'UX
                
                result = auth_manager.authenticate(username, password)
                
                def handle_result():
                    """Gérer le résultat dans le thread principal"""
                    if self.loading:
                        self.loading.destroy()
                    
                    if result['success']:
                        # Vérifier changement de mot de passe
                        if result.get('must_change_password'):
                            self.window.withdraw()
                            self.show_change_password_dialog(result['user'])
                        else:
                            # Succès
                            self.window.destroy()
                            self.on_success(result['user'])
                    else:
                        # Erreur
                        self.show_toast(result.get('error', 'Identifiants invalides'), "error")
                        
                        # Réactiver
                        self.username_entry.configure(state="normal")
                        self.password_entry.configure(state="normal")
                        self.password_entry.delete(0, 'end')
                        self.login_btn.configure(state="normal", text="Se connecter")
                        self.password_entry.focus()
                
                self.window.after(0, handle_result)
                
            except Exception as e:
                def show_error():
                    if self.loading:
                        self.loading.destroy()
                    self.show_toast(f"Erreur: {e}", "error")
                    
                    self.username_entry.configure(state="normal")
                    self.password_entry.configure(state="normal")
                    self.login_btn.configure(state="normal", text="Se connecter")
                
                self.window.after(0, show_error)
        
        # Lancer en arrière-plan
        threading.Thread(target=authenticate, daemon=True).start()
    
    def show_change_password_dialog(self, user):
        """Dialogue de changement de mot de passe épuré"""
        dialog = ctk.CTkToplevel()
        dialog.title("Changement de mot de passe")
        dialog.geometry("420x450")
        dialog.resizable(False, False)
        dialog.transient()
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 420) // 2
        y = (dialog.winfo_screenheight() - 450) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Container
        main = ctk.CTkFrame(dialog, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Warning card
        warning_card = ctk.CTkFrame(
            main,
            fg_color=("#fff3cd", "#664d03"),
            corner_radius=10
        )
        warning_card.pack(fill="x", pady=(0, 20))
        
        warning_content = ctk.CTkFrame(warning_card, fg_color="transparent")
        warning_content.pack(padx=15, pady=12)
        
        ctk.CTkLabel(
            warning_content,
            text="⚠️  Changement de mot de passe requis",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#856404", "#fff3cd")
        ).pack()
        
        # Titre
        ctk.CTkLabel(
            main,
            text="Sécurité de votre compte",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 8))
        
        ctk.CTkLabel(
            main,
            text="Pour protéger votre compte, veuillez\nchanger votre mot de passe initial.",
            font=ctk.CTkFont(size=11),
            text_color=("gray60", "gray50"),
            justify="center"
        ).pack(pady=(0, 25))
        
        # Nouveau mot de passe
        ctk.CTkLabel(
            main,
            text="Nouveau mot de passe",
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        new_pass = ctk.CTkEntry(
            main,
            show="•",
            height=40,
            placeholder_text="6 caractères minimum",
            border_width=1,
            corner_radius=8
        )
        new_pass.pack(fill="x", pady=(0, 15))
        
        # Confirmation
        ctk.CTkLabel(
            main,
            text="Confirmer le mot de passe",
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        confirm_pass = ctk.CTkEntry(
            main,
            show="•",
            height=40,
            placeholder_text="Retapez le mot de passe",
            border_width=1,
            corner_radius=8
        )
        confirm_pass.pack(fill="x", pady=(0, 20))
        
        def change_password():
            """Changer le mot de passe"""
            new_pwd = new_pass.get()
            confirm_pwd = confirm_pass.get()
            
            if not new_pwd or not confirm_pwd:
                LoginToast(dialog, "Remplissez tous les champs", "error")
                return
            
            if len(new_pwd) < 6:
                LoginToast(dialog, "Minimum 6 caractères", "error")
                return
            
            if new_pwd != confirm_pwd:
                LoginToast(dialog, "Les mots de passe ne correspondent pas", "error")
                return
            
            # Changer
            result = auth_manager.change_password(user['id'], new_pwd)
            
            if result['success']:
                dialog.destroy()
                LoginToast(self.window, "Mot de passe changé avec succès", "success")
                
                # Petit délai puis ouvrir l'app
                self.window.after(500, lambda: [self.window.destroy(), self.on_success(user)])
            else:
                LoginToast(dialog, result.get('error', 'Erreur'), "error")
        
        # Boutons
        buttons_frame = ctk.CTkFrame(main, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(5, 0))
        
        ctk.CTkButton(
            buttons_frame,
            text="✅ Valider",
            height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.accent_color,
            hover_color=self.darken_color(self.accent_color),
            corner_radius=8,
            command=change_password
        ).pack(fill="x")
        
        # Info sécurité
        security_info = ctk.CTkLabel(
            main,
            text="💡 Choisissez un mot de passe sécurisé",
            font=ctk.CTkFont(size=9),
            text_color=("gray60", "gray50")
        )
        security_info.pack(pady=(10, 0))
        
        # Focus et bind Enter
        new_pass.focus()
        new_pass.bind('<Return>', lambda e: confirm_pass.focus())
        confirm_pass.bind('<Return>', lambda e: change_password())
    
    def run(self):
        """Lancer la fenêtre"""
        self.window.mainloop()


def show_login(on_success_callback):
    """Afficher l'écran de connexion"""
    login = LoginWindow(on_success_callback)
    login.run()