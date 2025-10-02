"""
Vue Paramètres - DESIGN PROFESSIONNEL COMPLET
gui/settings_view.py

Interface moderne avec sidebar de navigation, inspirée des meilleures applications desktop.
Toast notifications, loading overlay, et UX soignée.
"""

import customtkinter as ctk
from tkinter import filedialog
import sys
from pathlib import Path
import threading
import time

sys.path.append(str(Path(__file__).parent.parent))

from core.preferences_manager import preferences_manager
from core.auth_manager import auth_manager
from gui.design_system import ColorPalette, Typography, Spacing
from gui.components.users_management import create_users_tab


# ==================== TOAST SYSTEM ====================

class SettingsToast:
    """Toast notification élégant"""
    TOASTS = []
    
    def __init__(self, parent, message, type="success", duration=3000):
        self.window = ctk.CTkToplevel(parent)
        self.window.withdraw()
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        
        config = {
            'success': {'color': "#10b981", 'icon': '✅', 'title': 'Succès'},
            'error': {'color': "#ef4444", 'icon': '❌', 'title': 'Erreur'},
            'info': {'color': "#3b82f6", 'icon': 'ℹ️', 'title': 'Information'},
            'warning': {'color': "#f59e0b", 'icon': '⚠️', 'title': 'Attention'}
        }
        
        cfg = config.get(type, config['info'])
        
        main_frame = ctk.CTkFrame(self.window, fg_color=cfg['color'], corner_radius=12)
        main_frame.pack(padx=2, pady=2)
        
        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.pack(padx=20, pady=15)
        
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x")
        
        ctk.CTkLabel(header, text=cfg['icon'], font=ctk.CTkFont(size=20)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(header, text=cfg['title'], font=ctk.CTkFont(size=13, weight="bold"), text_color="white").pack(side="left")
        
        ctk.CTkLabel(content, text=message, font=ctk.CTkFont(size=11), text_color="white", wraplength=300).pack(pady=(8, 0))
        
        self.position_toast(parent)
        self.window.attributes('-alpha', 0.0)
        self.fade_in()
        self.window.after(duration, self.fade_out)
        SettingsToast.TOASTS.append(self)
    
    def position_toast(self, parent):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        stack_offset = len([t for t in SettingsToast.TOASTS if t.window.winfo_exists()]) * (height + 10)
        x = parent_x + parent_width - width - 20
        y = parent_y + 20 + stack_offset
        self.window.geometry(f"+{x}+{y}")
        self.window.deiconify()
    
    def fade_in(self, alpha=0.0):
        alpha += 0.15
        if alpha <= 1.0:
            try:
                self.window.attributes('-alpha', alpha)
                self.window.after(20, lambda: self.fade_in(alpha))
            except: pass
    
    def fade_out(self, alpha=1.0):
        alpha -= 0.15
        if alpha >= 0.0:
            try:
                self.window.attributes('-alpha', alpha)
                self.window.after(20, lambda: self.fade_out(alpha))
            except: pass
        else: self.destroy()
    
    def destroy(self):
        try:
            if self in SettingsToast.TOASTS:
                SettingsToast.TOASTS.remove(self)
            self.window.destroy()
        except: pass


# ==================== LOADING OVERLAY ====================

class SettingsLoading:
    """Loading overlay"""
    def __init__(self, parent, message="Chargement..."):
        self.destroyed = False
        self.overlay = ctk.CTkFrame(parent, fg_color=("gray90", "gray15"), corner_radius=0)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        card = ctk.CTkFrame(self.overlay, fg_color=("white", "#2b2b2b"), corner_radius=20, border_width=2, border_color=preferences_manager.get_accent_color_hex())
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(padx=50, pady=40)
        
        self.spinner = ctk.CTkLabel(content, text="◐", font=ctk.CTkFont(size=48), text_color=preferences_manager.get_accent_color_hex())
        self.spinner.pack(pady=(0, 15))
        
        ctk.CTkLabel(content, text=message, font=ctk.CTkFont(size=14, weight="bold")).pack()
        
        self.dots_label = ctk.CTkLabel(content, text="", font=ctk.CTkFont(size=12), text_color=("gray60", "gray50"))
        self.dots_label.pack(pady=(8, 0))
        
        self.dots_count = 0
        self._animate()
    
    def _animate(self):
        if self.destroyed: return
        try:
            chars = ["◐", "◓", "◑", "◒"]
            current = self.spinner.cget("text")
            idx = chars.index(current) if current in chars else 0
            self.spinner.configure(text=chars[(idx + 1) % len(chars)])
            self.dots_count = (self.dots_count + 1) % 4
            self.dots_label.configure(text="." * self.dots_count)
            self.overlay.after(150, self._animate)
        except: self.destroyed = True
    
    def destroy(self):
        self.destroyed = True
        try: self.overlay.destroy()
        except: pass


# ==================== CONFIRM MODAL ====================

class ConfirmModal:
    """Modal de confirmation"""
    def __init__(self, parent, title, message, on_confirm, danger=False):
        self.on_confirm = on_confirm
        self.destroyed = False
        
        self.overlay = ctk.CTkFrame(parent, fg_color=("gray80", "gray20"), corner_radius=0)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        modal = ctk.CTkFrame(self.overlay, fg_color=("white", "#2b2b2b"), corner_radius=20, border_width=2, border_color=("#ef4444" if danger else preferences_manager.get_accent_color_hex()))
        modal.place(relx=0.5, rely=0.5, anchor="center")
        
        content = ctk.CTkFrame(modal, fg_color="transparent")
        content.pack(padx=40, pady=30)
        
        icon = "⚠️" if danger else "❓"
        ctk.CTkLabel(content, text=icon, font=ctk.CTkFont(size=48)).pack(pady=(0, 15))
        ctk.CTkLabel(content, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 10))
        ctk.CTkLabel(content, text=message, font=ctk.CTkFont(size=12), text_color=("gray60", "gray50"), wraplength=400, justify="center").pack(pady=(0, 25))
        
        buttons = ctk.CTkFrame(content, fg_color="transparent")
        buttons.pack()
        
        ctk.CTkButton(buttons, text="Annuler", width=120, height=40, font=ctk.CTkFont(size=13), fg_color="transparent", border_width=2, command=self.cancel).pack(side="left", padx=5)
        
        confirm_color = "#ef4444" if danger else preferences_manager.get_accent_color_hex()
        ctk.CTkButton(buttons, text="Confirmer", width=120, height=40, font=ctk.CTkFont(size=13, weight="bold"), fg_color=confirm_color, command=self.confirm).pack(side="left", padx=5)
    
    def confirm(self):
        if not self.destroyed:
            self.destroy()
            if self.on_confirm: self.on_confirm()
    
    def cancel(self):
        self.destroy()
    
    def destroy(self):
        self.destroyed = True
        try: self.overlay.destroy()
        except: pass


# ==================== MAIN SETTINGS VIEW ====================

class ModernSettingsView:
    """Vue des paramètres avec sidebar professionnelle"""
    
    def __init__(self, app):
        self.app = app
        self.current_category = "general"
        self.changes_made = False
        
        # Container principal
        self.container = ctk.CTkFrame(app.content_frame, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        
        # Top bar
        self.create_top_bar()
        
        # Main content (sidebar + panel)
        main_content = ctk.CTkFrame(self.container, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Sidebar
        self.create_sidebar(main_content)
        
        # Panel principal
        self.panel_container = ctk.CTkFrame(main_content, fg_color=("white", "#2b2b2b"), corner_radius=15)
        self.panel_container.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Charger la première catégorie
        self.load_category("general")
    
    def create_top_bar(self):
        """Barre supérieure avec titre et bouton enregistrer"""
        top_bar = ctk.CTkFrame(self.container, height=70, fg_color=("gray95", "gray20"), corner_radius=0)
        top_bar.pack(fill="x", padx=0, pady=0)
        top_bar.pack_propagate(False)
        
        content = ctk.CTkFrame(top_bar, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=15)
        
        # Titre à gauche
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left")
        
        ctk.CTkLabel(left, text="⚙️ Paramètres", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(left, text="Personnalisez votre expérience", font=ctk.CTkFont(size=11), text_color=("gray60", "gray50")).pack(anchor="w")
        
        # Bouton enregistrer à droite
        self.save_btn = ctk.CTkButton(
            content,
            text="💾 Enregistrer les modifications",
            height=40,
            width=240,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            command=self.save_settings
        )
        self.save_btn.pack(side="right")
        self.save_btn.configure(state="disabled")
    
    def create_sidebar(self, parent):
        """Sidebar de navigation"""
        sidebar = ctk.CTkScrollableFrame(parent, width=250, fg_color=("gray95", "gray20"), corner_radius=15)
        sidebar.pack(side="left", fill="y", pady=0)
        
        # User badge en haut
        if auth_manager.current_user:
            user_card = ctk.CTkFrame(sidebar, fg_color=("white", "#2b2b2b"), corner_radius=10)
            user_card.pack(fill="x", padx=15, pady=15)
            
            user = auth_manager.current_user
            role_emojis = {'admin': '👑', 'manager': '👔', 'operator': '💼', 'viewer': '👁️'}
            emoji = role_emojis.get(user.get('role', 'viewer'), '👤')
            
            ctk.CTkLabel(user_card, text=emoji, font=ctk.CTkFont(size=32)).pack(pady=(15, 5))
            ctk.CTkLabel(user_card, text=user.get('username', 'N/A'), font=ctk.CTkFont(size=14, weight="bold")).pack()
            
            role_name = auth_manager.ROLES.get(user.get('role'), {}).get('name', 'Inconnu')
            ctk.CTkLabel(user_card, text=role_name, font=ctk.CTkFont(size=10), text_color=("gray60", "gray50")).pack(pady=(0, 15))
        
        # Label Navigation
        ctk.CTkLabel(
            sidebar,
            text="NAVIGATION",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("gray60", "gray50"),
            anchor="w"
        ).pack(fill="x", padx=20, pady=(10, 5))
        
        # Catégories de navigation
        categories = [
            ("general", "⚙️", "Général"),
            ("appearance", "🎨", "Apparence"),
            ("security", "🔐", "Sécurité"),
            ("notifications", "🔔", "Notifications"),
            ("account", "👤", "Mon Compte"),
        ]
        
        # Ajouter Utilisateurs si admin
        if auth_manager.has_permission('*'):
            categories.append(("users", "👥", "Utilisateurs"))
        
        self.nav_buttons = {}
        
        for cat_id, icon, label in categories:
            btn = ctk.CTkButton(
                sidebar,
                text=f"{icon}  {label}",
                height=45,
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                hover_color=("gray85", "gray30"),
                anchor="w",
                command=lambda c=cat_id: self.load_category(c)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[cat_id] = btn
        
        # Divider
        ctk.CTkFrame(sidebar, height=1, fg_color=("gray80", "gray30")).pack(fill="x", padx=15, pady=15)
        
        # Label Autres
        ctk.CTkLabel(
            sidebar,
            text="AUTRES",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("gray60", "gray50"),
            anchor="w"
        ).pack(fill="x", padx=20, pady=(5, 5))
        
        # Bouton backup
        self.backup_btn = ctk.CTkButton(
            sidebar,
            text="💾 Sauvegarde",
            height=45,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color=("gray85", "gray30"),
            anchor="w",
            command=lambda: self.load_category("backup")
        )
        self.backup_btn.pack(fill="x", padx=10, pady=2)
        
        # Marquer le bouton actif
        self.highlight_active_button("general")
    
    def highlight_active_button(self, category):
        """Mettre en surbrillance le bouton actif"""
        accent = preferences_manager.get_accent_color_hex()
        
        # Reset tous les boutons de navigation
        for cat_id, btn in self.nav_buttons.items():
            if cat_id == category:
                btn.configure(fg_color=accent, hover_color=self._darken(accent), text_color="white")
            else:
                btn.configure(fg_color="transparent", hover_color=("gray85", "gray30"), text_color=("gray10", "gray90"))
        
        # Gérer le bouton backup séparément
        if hasattr(self, 'backup_btn'):
            if category == "backup":
                self.backup_btn.configure(fg_color=accent, hover_color=self._darken(accent), text_color="white")
            else:
                self.backup_btn.configure(fg_color="transparent", hover_color=("gray85", "gray30"), text_color=("gray10", "gray90"))
    
    def load_category(self, category):
        """Charger une catégorie de paramètres"""
        self.current_category = category
        self.highlight_active_button(category)
        
        # Clear panel
        for widget in self.panel_container.winfo_children():
            widget.destroy()
        
        # Scroll frame
        scroll = ctk.CTkScrollableFrame(self.panel_container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Charger le contenu selon la catégorie
        if category == "general":
            self.create_general_panel(scroll)
        elif category == "appearance":
            self.create_appearance_panel(scroll)
        elif category == "security":
            self.create_security_panel(scroll)
        elif category == "notifications":
            self.create_notifications_panel(scroll)
        elif category == "account":
            self.create_account_panel(scroll)
        elif category == "users":
            self.create_users_panel(scroll)
        elif category == "backup":
            self.create_backup_panel(scroll)
    
    def create_general_panel(self, parent):
        """Panel Général"""
        self.create_section_title(parent, "📏 Typographie", "Ajustez les tailles de police")
        
        card = self.create_card(parent)
        
        # Taille globale
        ctk.CTkLabel(card, text="Taille globale :", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x", pady=(0, 10))
        
        current_size = preferences_manager.get('global_font_size', 'normal')
        size_var = ctk.StringVar(value=current_size)
        
        sizes = [("Petite", "small"), ("Normale", "normal"), ("Grande", "large"), ("Très grande", "very_large")]
        
        for label, value in sizes:
            ctk.CTkRadioButton(
                card,
                text=label,
                variable=size_var,
                value=value,
                font=ctk.CTkFont(size=11),
                command=lambda: self.mark_changes()
            ).pack(anchor="w", pady=5)
        
        # Divider
        ctk.CTkFrame(card, height=1, fg_color=("gray80", "gray30")).pack(fill="x", pady=20)
        
        # Police tableaux
        ctk.CTkLabel(card, text="Police des tableaux :", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x", pady=(0, 10))
        
        current_table = preferences_manager.get('table_font_size', 9)
        
        table_value = ctk.CTkLabel(card, text=f"{current_table} pt", font=ctk.CTkFont(size=18, weight="bold"))
        table_value.pack(pady=10)
        
        def on_table_change(value):
            table_value.configure(text=f"{int(value)} pt")
            self.mark_changes()
        
        slider = ctk.CTkSlider(card, from_=7, to=12, number_of_steps=5, command=on_table_change)
        slider.set(current_table)
        slider.pack(fill="x", padx=20, pady=10)
        
        range_labels = ctk.CTkFrame(card, fg_color="transparent")
        range_labels.pack(fill="x", padx=20)
        ctk.CTkLabel(range_labels, text="7 pt", font=ctk.CTkFont(size=9), text_color=("gray60", "gray50")).pack(side="left")
        ctk.CTkLabel(range_labels, text="12 pt", font=ctk.CTkFont(size=9), text_color=("gray60", "gray50")).pack(side="right")
        
        # Section Display
        self.create_section_title(parent, "📐 Affichage", "Mode d'espacement de l'interface")
        
        card2 = self.create_card(parent)
        
        current_display = preferences_manager.get('display_mode', 'normal')
        display_var = ctk.StringVar(value=current_display)
        
        for mode, label in [("compact", "Compact"), ("normal", "Normal"), ("comfortable", "Confortable")]:
            ctk.CTkRadioButton(
                card2,
                text=label,
                variable=display_var,
                value=mode,
                font=ctk.CTkFont(size=11),
                command=lambda: self.mark_changes()
            ).pack(anchor="w", pady=5)
    
    def create_appearance_panel(self, parent):
        """Panel Apparence"""
        self.create_section_title(parent, "🌓 Thème", "Mode clair ou sombre")
        
        card = self.create_card(parent)
        
        current_theme = preferences_manager.get('theme', 'light')
        theme_var = ctk.StringVar(value=current_theme)
        
        theme_switch = ctk.CTkSegmentedButton(
            card,
            values=["light", "dark"],
            variable=theme_var,
            font=ctk.CTkFont(size=12),
            command=lambda v: [self.apply_theme(v), self.mark_changes()]
        )
        theme_switch.pack(fill="x", pady=10)
        
        # Couleurs d'accent
        self.create_section_title(parent, "🎨 Couleur d'accent", "Personnalisez la couleur principale")
        
        card2 = self.create_card(parent)
        
        colors = [
            ("Bleu", "blue", "#3B8ED0"),
            ("Vert", "green", "#2E8B57"),
            ("Rouge", "red", "#DC143C"),
            ("Orange", "orange", "#FF8C00"),
            ("Violet", "purple", "#8B5CF6")
        ]
        
        current_accent = preferences_manager.get('accent_color', 'blue')
        
        colors_grid = ctk.CTkFrame(card2, fg_color="transparent")
        colors_grid.pack(fill="x", pady=10)
        
        for name, value, hex_color in colors:
            col = ctk.CTkFrame(colors_grid, fg_color="transparent")
            col.pack(side="left", expand=True, fill="x", padx=3)
            
            btn = ctk.CTkButton(
                col,
                text="",
                height=60,
                fg_color=hex_color,
                hover_color=self._darken(hex_color),
                corner_radius=10,
                command=lambda v=value: [self.apply_accent(v), self.mark_changes()]
            )
            btn.pack(fill="x")
            
            if value == current_accent:
                btn.configure(border_width=3, border_color="white")
            
            ctk.CTkLabel(col, text=name, font=ctk.CTkFont(size=10), text_color=("gray60", "gray50")).pack(pady=(5, 0))
    
    def create_security_panel(self, parent):
        """Panel Sécurité"""
        self.create_section_title(parent, "🔑 Mot de passe", "Changez votre mot de passe")
        
        card = self.create_card(parent)
        
        ctk.CTkLabel(card, text="Ancien mot de passe :", font=ctk.CTkFont(size=11), anchor="w").pack(fill="x", pady=(0, 5))
        old_pwd = ctk.CTkEntry(card, show="•", height=40, placeholder_text="••••••••")
        old_pwd.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(card, text="Nouveau mot de passe :", font=ctk.CTkFont(size=11), anchor="w").pack(fill="x", pady=(0, 5))
        new_pwd = ctk.CTkEntry(card, show="•", height=40, placeholder_text="••••••••")
        new_pwd.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(card, text="Confirmer :", font=ctk.CTkFont(size=11), anchor="w").pack(fill="x", pady=(0, 5))
        confirm_pwd = ctk.CTkEntry(card, show="•", height=40, placeholder_text="••••••••")
        confirm_pwd.pack(fill="x", pady=(0, 15))
        
        error_label = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=10), text_color="#ef4444")
        error_label.pack()
        
        def change_password():
            old = old_pwd.get()
            new = new_pwd.get()
            confirm = confirm_pwd.get()
            
            if not all([old, new, confirm]):
                error_label.configure(text="Remplissez tous les champs")
                return
            
            if len(new) < 6:
                error_label.configure(text="Minimum 6 caractères")
                return
            
            if new != confirm:
                error_label.configure(text="Les mots de passe ne correspondent pas")
                return
            
            user = auth_manager.current_user
            result = auth_manager.change_password(user['id'], new, old_password=old)
            
            if result['success']:
                SettingsToast(self.app.content_frame, "Mot de passe changé avec succès!", "success")
                old_pwd.delete(0, 'end')
                new_pwd.delete(0, 'end')
                confirm_pwd.delete(0, 'end')
                error_label.configure(text="")
            else:
                error_label.configure(text=result.get('error', 'Erreur'))
        
        ctk.CTkButton(
            card,
            text="🔑 Changer le mot de passe",
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=preferences_manager.get_accent_color_hex(),
            command=change_password
        ).pack(fill="x", pady=(10, 0))
    
    def create_notifications_panel(self, parent):
        """Panel Notifications"""
        self.create_section_title(parent, "🔔 Notifications", "Gérez vos notifications")
        
        card = self.create_card(parent)
        
        notif_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(card, text="Activer les notifications", variable=notif_var, font=ctk.CTkFont(size=12), command=self.mark_changes).pack(anchor="w", pady=10)
        
        sound_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(card, text="Sons de notification", variable=sound_var, font=ctk.CTkFont(size=12), command=self.mark_changes).pack(anchor="w", pady=10)
        
        toast_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(card, text="Toasts d'information", variable=toast_var, font=ctk.CTkFont(size=12), command=self.mark_changes).pack(anchor="w", pady=10)
    
    def create_account_panel(self, parent):
        """Panel Mon Compte"""
        user = auth_manager.current_user
        
        if not user:
            ctk.CTkLabel(parent, text="❌ Erreur : Aucun utilisateur connecté", font=ctk.CTkFont(size=14)).pack(pady=50)
            return
        
        self.create_section_title(parent, "👤 Informations", "Vos informations de compte")
        
        card = self.create_card(parent)
        
        infos = [
            ("Nom d'utilisateur", user.get('username', 'N/A')),
            ("Nom complet", user.get('full_name', 'N/A')),
            ("Email", user.get('email') or 'Non renseigné'),
            ("Rôle", auth_manager.ROLES.get(user.get('role'), {}).get('name', 'Inconnu')),
            ("Dernière connexion", user.get('last_login', 'Jamais')[:19] if user.get('last_login') else 'Jamais'),
        ]
        
        for label, value in infos:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", pady=8)
            
            ctk.CTkLabel(row, text=label + " :", font=ctk.CTkFont(size=11), text_color=("gray60", "gray50"), anchor="w", width=150).pack(side="left")
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=11, weight="bold"), anchor="w").pack(side="left", fill="x", expand=True)
        
        # Permissions
        self.create_section_title(parent, "🔐 Permissions", "Vos autorisations")
        
        card2 = self.create_card(parent)
        
        role_info = auth_manager.ROLES.get(user.get('role'), {})
        permissions = role_info.get('permissions', [])
        
        if permissions == ['*']:
            perm_card = ctk.CTkFrame(card2, fg_color=("#d1fae5", "#065f46"), corner_radius=8)
            perm_card.pack(fill="x", pady=5)
            ctk.CTkLabel(perm_card, text="👑 Accès complet (Administrateur)", font=ctk.CTkFont(size=11, weight="bold")).pack(pady=10)
        else:
            for perm in permissions:
                perm_row = ctk.CTkFrame(card2, fg_color="transparent")
                perm_row.pack(fill="x", pady=3)
                ctk.CTkLabel(perm_row, text=f"✓ {perm.replace('_', ' ').title()}", font=ctk.CTkFont(size=11), anchor="w").pack(side="left")
    
    def create_users_panel(self, parent):
        """Panel Utilisateurs (admin uniquement)"""
        create_users_tab(parent, self.app)
    
    def create_backup_panel(self, parent):
        """Panel Sauvegarde"""
        self.create_section_title(parent, "📤 Exporter", "Sauvegardez vos préférences")
        
        card = self.create_card(parent)
        ctk.CTkLabel(card, text="Créez une copie de vos préférences actuelles", font=ctk.CTkFont(size=11), text_color=("gray60", "gray50")).pack(pady=(0, 15))
        
        ctk.CTkButton(
            card,
            text="📥 Exporter les préférences",
            height=40,
            font=ctk.CTkFont(size=12),
            command=self.export_preferences
        ).pack(fill="x")
        
        self.create_section_title(parent, "📥 Importer", "Restaurez vos préférences")
        
        card2 = self.create_card(parent)
        ctk.CTkLabel(card2, text="Chargez des préférences depuis un fichier", font=ctk.CTkFont(size=11), text_color=("gray60", "gray50")).pack(pady=(0, 15))
        
        ctk.CTkButton(
            card2,
            text="📤 Importer les préférences",
            height=40,
            font=ctk.CTkFont(size=12),
            command=self.import_preferences
        ).pack(fill="x")
        
        self.create_section_title(parent, "🔄 Réinitialiser", "Restaurer les valeurs par défaut")
        
        card3 = self.create_card(parent)
        ctk.CTkLabel(card3, text="⚠️ Cette action est irréversible", font=ctk.CTkFont(size=11), text_color="#ef4444").pack(pady=(0, 15))
        
        ctk.CTkButton(
            card3,
            text="🔄 Réinitialiser les paramètres",
            height=40,
            font=ctk.CTkFont(size=12),
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self.reset_preferences
        ).pack(fill="x")
    
    def create_section_title(self, parent, title, subtitle):
        """Créer un titre de section"""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(20, 10))
        
        ctk.CTkLabel(section, text=title, font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(section, text=subtitle, font=ctk.CTkFont(size=10), text_color=("gray60", "gray50"), anchor="w").pack(fill="x", pady=(3, 0))
    
    def create_card(self, parent):
        """Créer une carte avec ombre"""
        card = ctk.CTkFrame(
            parent,
            fg_color=("gray95", "gray25"),
            corner_radius=12
        )
        card.pack(fill="x", pady=(0, 15), padx=5)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        return inner
    
    def mark_changes(self):
        """Marquer qu'il y a des changements non sauvegardés"""
        self.changes_made = True
        self.save_btn.configure(state="normal")
    
    def apply_theme(self, theme):
        """Appliquer le thème immédiatement"""
        preferences_manager.set('theme', theme)
        ctk.set_appearance_mode(theme)
        SettingsToast(self.app.content_frame, f"Thème {theme} appliqué", "success")
    
    def apply_accent(self, accent):
        """Appliquer la couleur d'accent"""
        preferences_manager.set('accent_color', accent)
        SettingsToast(self.app.content_frame, "Couleur changée - Redémarrez pour voir partout", "info", 4000)
    
    def save_settings(self):
        """Sauvegarder tous les paramètres"""
        loading = SettingsLoading(self.app.content_frame, "Sauvegarde en cours...")
        
        def save():
            time.sleep(0.5)
            self.app.content_frame.after(0, lambda: [
                loading.destroy(),
                SettingsToast(self.app.content_frame, "Paramètres sauvegardés avec succès!", "success"),
                self.save_btn.configure(state="disabled")
            ])
            self.changes_made = False
        
        threading.Thread(target=save, daemon=True).start()
    
    def export_preferences(self):
        """Exporter les préférences"""
        file_path = filedialog.asksaveasfilename(
            title="Exporter les préférences",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Tous", "*.*")]
        )
        
        if file_path:
            loading = SettingsLoading(self.app.content_frame, "Export en cours...")
            
            def do_export():
                time.sleep(0.3)
                success = preferences_manager.export_preferences(file_path)
                
                self.app.content_frame.after(0, lambda: [
                    loading.destroy(),
                    SettingsToast(
                        self.app.content_frame,
                        "Préférences exportées avec succès!" if success else "Erreur lors de l'export",
                        "success" if success else "error"
                    )
                ])
            
            threading.Thread(target=do_export, daemon=True).start()
    
    def import_preferences(self):
        """Importer les préférences"""
        file_path = filedialog.askopenfilename(
            title="Importer les préférences",
            filetypes=[("JSON", "*.json"), ("Tous", "*.*")]
        )
        
        if file_path:
            loading = SettingsLoading(self.app.content_frame, "Import en cours...")
            
            def do_import():
                time.sleep(0.3)
                success = preferences_manager.import_preferences(file_path)
                
                self.app.content_frame.after(0, lambda: [
                    loading.destroy(),
                    SettingsToast(
                        self.app.content_frame,
                        "Préférences importées! Redémarrez l'app." if success else "Erreur lors de l'import",
                        "success" if success else "error",
                        4000
                    )
                ])
            
            threading.Thread(target=do_import, daemon=True).start()
    
    def reset_preferences(self):
        """Réinitialiser les préférences"""
        def do_reset():
            loading = SettingsLoading(self.app.content_frame, "Réinitialisation...")
            
            def reset():
                time.sleep(0.3)
                success = preferences_manager.reset_to_defaults()
                
                self.app.content_frame.after(0, lambda: [
                    loading.destroy(),
                    SettingsToast(
                        self.app.content_frame,
                        "Paramètres réinitialisés! Redémarrez." if success else "Erreur",
                        "success" if success else "error",
                        4000
                    )
                ])
            
            threading.Thread(target=reset, daemon=True).start()
        
        ConfirmModal(
            self.app.content_frame,
            "Réinitialiser les paramètres?",
            "Cette action est irréversible.\nToutes vos préférences seront perdues.",
            do_reset,
            danger=True
        )
    
    def _darken(self, hex_color, factor=0.8):
        """Assombrir une couleur"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f'#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}'


# ==================== FONCTION PRINCIPALE ====================

def show_settings(app):
    """Afficher la vue des paramètres"""
    # Définir le titre de la page
    if hasattr(app, 'page_title'):
        app.page_title.configure(text="⚙️ Paramètres")
    
    loading = SettingsLoading(app.content_frame, "Chargement des paramètres")
    
    def load():
        time.sleep(0.3)
        
        def render():
            loading.destroy()
            
            # Clear
            for widget in app.content_frame.winfo_children():
                widget.destroy()
            
            # Créer la vue moderne
            ModernSettingsView(app)
            
            # Toast de bienvenue
            SettingsToast(app.content_frame, "Paramètres chargés avec succès", "success", 2000)
        
        app.content_frame.after(0, render)
    
    threading.Thread(target=load, daemon=True).start()