"""
Vue Règles d'Avancement - DESIGN SIDEBAR
gui/rules_view.py

Navigation latérale moderne avec affichage des tableaux au clic
"""
import customtkinter as ctk
import sys
from pathlib import Path
from tkinter import Canvas, Scrollbar, Frame
import threading
import time

sys.path.append(str(Path(__file__).parent.parent))

from core.preferences_manager import preferences_manager


# ==================== TOAST SYSTEM ====================

class RulesToast:
    """Toast notification pour Rules"""
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
        RulesToast.TOASTS.append(self)
    
    def position_toast(self, parent):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        stack_offset = len([t for t in RulesToast.TOASTS if t.window.winfo_exists()]) * (height + 10)
        x = parent_x + parent_width - width - 20
        y = parent_y + 20 + stack_offset
        self.window.geometry(f"+{x}+{y}")
        self.window.deiconify()
    
    def fade_in(self, alpha=0.0):
        if not self.window.winfo_exists():
            return
        alpha += 0.15
        if alpha <= 1.0:
            try:
                self.window.attributes('-alpha', alpha)
                self.window.after(20, lambda: self.fade_in(alpha))
            except: pass
    
    def fade_out(self, alpha=1.0):
        if not self.window.winfo_exists():
            return
        alpha -= 0.15
        if alpha >= 0.0:
            try:
                self.window.attributes('-alpha', alpha)
                self.window.after(20, lambda: self.fade_out(alpha))
            except: pass
        else: self.destroy()
    
    def destroy(self):
        try:
            if self in RulesToast.TOASTS:
                RulesToast.TOASTS.remove(self)
            if self.window.winfo_exists():
                self.window.destroy()
        except: pass


# ==================== LOADING OVERLAY ====================

class RulesLoading:
    """Loading overlay pour Rules"""
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
        if self.destroyed or not self.overlay.winfo_exists():
            return
        try:
            chars = ["◐", "◓", "◑", "◒"]
            current = self.spinner.cget("text")
            idx = chars.index(current) if current in chars else 0
            self.spinner.configure(text=chars[(idx + 1) % len(chars)])
            self.dots_count = (self.dots_count + 1) % 4
            self.dots_label.configure(text="." * self.dots_count)
            self.overlay.after(150, self._animate)
        except: 
            self.destroyed = True
    
    def destroy(self):
        self.destroyed = True
        try: 
            if self.overlay.winfo_exists():
                self.overlay.destroy()
        except: pass


# ==================== CONFIRM MODAL ====================

class RulesConfirmModal:
    """Modal de confirmation pour Rules"""
    def __init__(self, parent, title, message, on_confirm, danger=True):
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
        try: 
            if self.overlay.winfo_exists():
                self.overlay.destroy()
        except: pass


# ==================== FONCTIONS MÉTIER (AVANT TOUT) ====================

def get_all_rules_data():
    """Récupérer toutes les règles"""
    try:
        from core.database import db_manager
        rules_from_db = db_manager.get_all_rules()
        
        if rules_from_db:
            formatted_rules = []
            for rule in rules_from_db:
                formatted_rule = {
                    'id': rule.get('id'),
                    'categorie': rule.get('categorie', ''),
                    'grade_source': rule.get('grade_source', ''),
                    'grade_cible': rule.get('grade_cible', ''),
                    'type_avancement': rule.get('type_avancement', 'Normal'),
                    'statut': rule.get('statut', 'Actif')
                }
                
                if rule.get('categorie') == 'Officiers':
                    conditions = []
                    if rule.get('anciennete_service_min'):
                        conditions.append(f"{rule['anciennete_service_min']} ans service")
                    if rule.get('diplomes_requis'):
                        conditions.append(f"Diplômes: {', '.join(rule['diplomes_requis'])}")
                    if rule.get('note_min_courante'):
                        conditions.append(f"Note min: {rule['note_min_courante']}")
                    if rule.get('conditions_speciales'):
                        conditions.append(rule['conditions_speciales'])
                    
                    formatted_rule['conditions_principales'] = ' - '.join(conditions) if conditions else 'Aucune'
                else:
                    anciennete_parts = []
                    if rule.get('anciennete_service_min'):
                        anciennete_parts.append(f"{rule['anciennete_service_min']}a service")
                    if rule.get('anciennete_grade_min'):
                        anciennete_parts.append(f"{rule['anciennete_grade_min']}a grade")
                    if rule.get('grade_specifique') and rule.get('anciennete_grade_specifique'):
                        anciennete_parts.append(f"{rule['anciennete_grade_specifique']}a {rule['grade_specifique']}")
                    
                    formatted_rule['anciennete_requise'] = ', '.join(anciennete_parts) if anciennete_parts else 'Aucune'
                    formatted_rule['diplomes'] = ', '.join(rule.get('diplomes_requis', [])) if rule.get('diplomes_requis') else 'Aucun'
                    
                    notes_parts = []
                    if rule.get('note_min_courante'):
                        notes_parts.append(f"{rule['note_min_courante']} min")
                    if rule.get('notes_interdites_n1_n2'):
                        notes_parts.append(f"Pas {','.join(rule['notes_interdites_n1_n2'])}")
                    
                    formatted_rule['notes'] = ', '.join(notes_parts) if notes_parts else 'Aucune'
                    formatted_rule['conditions_speciales'] = rule.get('conditions_speciales', 'Aucune')[:50]
                
                formatted_rules.append(formatted_rule)
            
            return formatted_rules
    except Exception as e:
        print(f"Erreur get_all_rules_data: {e}")
    
    return []


def create_new_rule(app):
    """Créer une nouvelle règle"""
    try:
        from gui.components.rule_form import show_rule_form
        show_rule_form(app, mode="create")
    except Exception as e:
        RulesToast(app.content_frame, f"Erreur: {e}", "error")


def edit_rule(app, rule_id):
    """Modifier une règle"""
    try:
        from gui.components.rule_form import show_rule_form
        from core.database import db_manager
        
        rule_data = db_manager.get_rule_by_id(rule_id)
        if rule_data:
            show_rule_form(app, rule_data=rule_data, mode="edit")
        else:
            RulesToast(app.content_frame, "Règle non trouvée", "error")
    except Exception as e:
        RulesToast(app.content_frame, f"Erreur: {e}", "error")


def delete_rule(app, rule_id):
    """Supprimer une règle"""
    try:
        from core.database import db_manager
        
        rule_data = db_manager.get_rule_by_id(rule_id)
        if not rule_data:
            RulesToast(app.content_frame, "Règle non trouvée", "error")
            return
        
        def do_delete():
            loading = RulesLoading(app.content_frame, "Suppression en cours...")
            
            def delete():
                time.sleep(0.3)
                success = db_manager.delete_rule(rule_id)
                
                app.content_frame.after(0, lambda: [
                    loading.destroy(),
                    RulesToast(app.content_frame, "Règle supprimée avec succès!", "success") if success else RulesToast(app.content_frame, "Erreur lors de la suppression", "error"),
                    app.navigate_to("rules") if success else None
                ])
            
            threading.Thread(target=delete, daemon=True).start()
        
        RulesConfirmModal(
            app.content_frame,
            "Supprimer cette règle?",
            f"{rule_data['grade_source']} → {rule_data['grade_cible']}\n\nCette action est irréversible.",
            do_delete,
            danger=True
        )
    except Exception as e:
        RulesToast(app.content_frame, f"Erreur: {e}", "error")


def export_rules(app):
    """Exporter les règles avec loading"""
    loading = RulesLoading(app.content_frame, "Export en cours...")
    
    def do_export():
        try:
            time.sleep(0.3)
            
            from core.database import db_manager
            import pandas as pd
            from pathlib import Path
            
            rules_data = db_manager.get_all_rules()
            if not rules_data:
                app.content_frame.after(0, lambda: [
                    loading.destroy(),
                    RulesToast(app.content_frame, "Aucune règle à exporter", "warning")
                ])
                return
            
            export_data = []
            for rule in rules_data:
                export_data.append({
                    'Catégorie': rule.get('categorie', ''),
                    'Grade Source': rule.get('grade_source', ''),
                    'Grade Cible': rule.get('grade_cible', ''),
                    'Type': rule.get('type_avancement', ''),
                    'Anc. Service': rule.get('anciennete_service_min', 0),
                    'Anc. Grade': rule.get('anciennete_grade_min', 0),
                    'Diplômes': ', '.join(rule.get('diplomes_requis', [])),
                    'Note Min': rule.get('note_min_courante', ''),
                    'Statut': rule.get('statut', '')
                })
            
            df = pd.DataFrame(export_data)
            export_path = Path("data/exports/regles_export.xlsx")
            export_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_excel(export_path, index=False, sheet_name="Règles")
            
            app.content_frame.after(0, lambda: [
                loading.destroy(),
                RulesToast(app.content_frame, f"Export réussi! {len(rules_data)} règles exportées", "success", 4000)
            ])
        except Exception as e:
            app.content_frame.after(0, lambda: [
                loading.destroy(),
                RulesToast(app.content_frame, f"Erreur lors de l'export: {e}", "error")
            ])
    
    threading.Thread(target=do_export, daemon=True).start()


# ==================== VUE PRINCIPALE ====================

def show_rules(app):
    """Afficher la gestion des règles avec sidebar"""
    app.page_title.configure(text="⚙️ Règles d'Avancement")
    
    # Loading initial
    loading = RulesLoading(app.content_frame, "Chargement des règles")
    
    def load_rules():
        time.sleep(0.3)
        
        # Charger les préférences
        table_font_size = preferences_manager.get('table_font_size', 9)
        rows_per_page = preferences_manager.get('rows_per_page', 30)
        alternate_colors = preferences_manager.get('alternate_row_colors', True)
        row_spacing = preferences_manager.get('row_spacing', 'normal')
        accent_color = preferences_manager.get_accent_color_hex()
        
        # Charger les données
        rules_data = get_all_rules_data()
        
        def render():
            loading.destroy()
            
            # Container principal avec sidebar + content
            main_container = ctk.CTkFrame(app.content_frame, fg_color="transparent")
            main_container.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Sidebar gauche (navigation)
            sidebar = create_sidebar(main_container, rules_data, accent_color)
            sidebar.pack(side="left", fill="y", padx=(0, 20))
            
            # Zone de contenu droite
            content_area = ctk.CTkFrame(main_container, fg_color="transparent")
            content_area.pack(side="left", fill="both", expand=True)
            
            # État de navigation
            nav_state = {
                'current_view': 'dashboard',
                'content_area': content_area,
                'rules_data': rules_data,
                'app': app,
                'table_font_size': table_font_size,
                'rows_per_page': rows_per_page,
                'alternate_colors': alternate_colors,
                'row_spacing': row_spacing,
                'accent_color': accent_color
            }
            
            # Afficher le dashboard par défaut
            show_dashboard(nav_state)
            
            # Configurer les boutons de navigation
            setup_navigation(sidebar, nav_state)
            
            # Toast de bienvenue
            RulesToast(app.content_frame, f"{len(rules_data)} règles chargées", "success", 2000)
        
        app.content_frame.after(0, render)
    
    threading.Thread(target=load_rules, daemon=True).start()


def create_sidebar(parent, rules_data, accent_color):
    """Créer la sidebar de navigation SCROLLABLE"""
    # Container avec largeur fixe
    sidebar_container = ctk.CTkFrame(parent, width=280, fg_color="transparent")
    sidebar_container.pack_propagate(False)
    
    # Sidebar SCROLLABLE
    sidebar = ctk.CTkScrollableFrame(
        sidebar_container,
        width=260,
        fg_color=("gray95", "gray20"),
        corner_radius=15
    )
    sidebar.pack(fill="both", expand=True)
    
    # Header sidebar
    header = ctk.CTkFrame(sidebar, fg_color="transparent")
    header.pack(fill="x", padx=20, pady=(20, 15))
    
    ctk.CTkLabel(
        header,
        text="📋 Navigation",
        font=ctk.CTkFont(size=18, weight="bold")
    ).pack(anchor="w")
    
    # Stats rapides (VERSION COMPACTE)
    stats_card = ctk.CTkFrame(sidebar, fg_color=("white", "#2b2b2b"), corner_radius=12)
    stats_card.pack(fill="x", padx=15, pady=(0, 15))
    
    stats_content = ctk.CTkFrame(stats_card, fg_color="transparent")
    stats_content.pack(padx=12, pady=10)
    
    ctk.CTkLabel(
        stats_content,
        text=f"📊 {len(rules_data)} règles",
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color=accent_color
    ).pack(anchor="w")
    
    militaires_rang = len([r for r in rules_data if r['categorie'] == 'Militaires du rang'])
    sous_officiers = len([r for r in rules_data if r['categorie'] == 'Sous-officiers'])
    officiers = len([r for r in rules_data if r['categorie'] == 'Officiers'])
    
    # Stats en ligne compacte
    stats_line = ctk.CTkFrame(stats_content, fg_color="transparent")
    stats_line.pack(fill="x", pady=(5, 0))
    
    for icon, count in [("🎖️", militaires_rang), ("⭐", sous_officiers), ("👑", officiers)]:
        ctk.CTkLabel(
            stats_line,
            text=f"{icon} {count}",
            font=ctk.CTkFont(size=10),
            text_color=("gray60", "gray50")
        ).pack(side="left", padx=(0, 8))
    
    # Séparateur
    ctk.CTkFrame(sidebar, height=1, fg_color=("gray85", "gray25")).pack(fill="x", padx=15, pady=10)
    
    # Label "Catégories"
    ctk.CTkLabel(
        sidebar,
        text="CATÉGORIES",
        font=ctk.CTkFont(size=10, weight="bold"),
        text_color=("gray60", "gray50")
    ).pack(anchor="w", padx=20, pady=(0, 8))
    
    # Boutons de navigation
    nav_buttons_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    nav_buttons_frame.pack(fill="x", padx=15, pady=(0, 10))
    
    # Boutons plus compacts
    buttons = [
        ("🏠", "Vue d'ensemble", "dashboard", accent_color),
        ("🎖️", "Militaires du rang", "militaires_rang", "#2E8B57"),
        ("⭐", "Sous-officiers", "sous_officiers", "#DAA520"),
        ("👑", "Officiers", "officiers", "#DC143C"),
        ("🔄", "Équivalences", "equivalences", "#8b5cf6")
    ]
    
    nav_buttons_frame.buttons = []
    
    print("🔨 Création des boutons de navigation...")
    for icon, label, view_id, color in buttons:
        btn = ctk.CTkButton(
            nav_buttons_frame,
            text=f"{icon}  {label}",
            font=ctk.CTkFont(size=12),
            height=38,
            anchor="w",
            fg_color="transparent",
            hover_color=("gray88", "gray28"),
            text_color=("gray20", "gray90"),
            corner_radius=8
        )
        btn.pack(fill="x", pady=2)
        btn.view_id = view_id
        btn.original_color = color
        nav_buttons_frame.buttons.append(btn)
        print(f"   ✅ Bouton créé: {label}")
    
    print(f"🎯 Total: {len(nav_buttons_frame.buttons)} boutons créés")
    
    # Stocker la référence pour setup_navigation
    sidebar_container.nav_buttons_frame = nav_buttons_frame
    
    return sidebar_container


def setup_navigation(sidebar, nav_state):
    """Configurer les boutons de navigation"""
    # Récupérer le frame des boutons stocké dans la sidebar
    nav_buttons_frame = getattr(sidebar, 'nav_buttons_frame', None)
    
    if not nav_buttons_frame or not hasattr(nav_buttons_frame, 'buttons'):
        print("⚠️ Erreur: nav_buttons_frame introuvable")
        return
    
    print(f"✅ Configuration navigation avec {len(nav_buttons_frame.buttons)} boutons")
    
    def on_nav_click(view_id, btn):
        print(f"🔘 Navigation vers: {view_id}")
        
        # Réinitialiser tous les boutons
        for b in nav_buttons_frame.buttons:
            b.configure(
                fg_color="transparent",
                text_color=("gray20", "gray90"),
                font=ctk.CTkFont(size=12)
            )
        
        # Activer le bouton cliqué
        btn.configure(
            fg_color=btn.original_color,
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        
        # Changer la vue
        nav_state['current_view'] = view_id
        
        # Effacer le contenu actuel
        for widget in nav_state['content_area'].winfo_children():
            widget.destroy()
        
        # Afficher la nouvelle vue
        if view_id == 'dashboard':
            show_dashboard(nav_state)
        elif view_id == 'militaires_rang':
            show_category_table(nav_state, 'Militaires du rang', "🎖️", "#2E8B57")
        elif view_id == 'sous_officiers':
            show_category_table(nav_state, 'Sous-officiers', "⭐", "#DAA520")
        elif view_id == 'officiers':
            show_category_table(nav_state, 'Officiers', "👑", "#DC143C")
        elif view_id == 'equivalences':
            show_equivalences_view(nav_state)
    
    # Lier les boutons
    for btn in nav_buttons_frame.buttons:
        btn.configure(command=lambda v=btn.view_id, b=btn: on_nav_click(v, b))
        print(f"   → Bouton configuré: {btn.cget('text')}")
    
    # Activer le premier bouton par défaut
    if nav_buttons_frame.buttons:
        nav_buttons_frame.buttons[0].configure(
            fg_color=nav_buttons_frame.buttons[0].original_color,
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        print("✅ Bouton 'Vue d'ensemble' activé par défaut")


def show_dashboard(nav_state):
    """Afficher le dashboard d'overview"""
    content = nav_state['content_area']
    rules_data = nav_state['rules_data']
    accent_color = nav_state['accent_color']
    
    # Header
    header = ctk.CTkFrame(content, fg_color="transparent")
    header.pack(fill="x", pady=(0, 20))
    
    ctk.CTkLabel(
        header,
        text="📊 Vue d'ensemble des règles",
        font=ctk.CTkFont(size=24, weight="bold")
    ).pack(side="left")
    
    # Actions rapides
    actions = ctk.CTkFrame(header, fg_color="transparent")
    actions.pack(side="right")
    
    ctk.CTkButton(
        actions,
        text="➕ Nouvelle Règle",
        height=40,
        font=ctk.CTkFont(size=12, weight="bold"),
        fg_color=accent_color,
        command=lambda: create_new_rule(nav_state['app'])
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        actions,
        text="📊 Exporter",
        height=40,
        font=ctk.CTkFont(size=12),
        fg_color="transparent",
        border_width=2,
        command=lambda: export_rules(nav_state['app'])
    ).pack(side="left", padx=5)
    
    # Cards statistiques
    stats_container = ctk.CTkFrame(content, fg_color="transparent")
    stats_container.pack(fill="x", pady=(0, 20))
    
    militaires_rang = len([r for r in rules_data if r['categorie'] == 'Militaires du rang'])
    sous_officiers = len([r for r in rules_data if r['categorie'] == 'Sous-officiers'])
    officiers = len([r for r in rules_data if r['categorie'] == 'Officiers'])
    
    stats = [
        ("Total Règles", len(rules_data), accent_color, "📊"),
        ("Militaires du rang", militaires_rang, "#2E8B57", "🎖️"),
        ("Sous-officiers", sous_officiers, "#DAA520", "⭐"),
        ("Officiers", officiers, "#DC143C", "👑")
    ]
    
    for i, (label, value, color, icon) in enumerate(stats):
        card = ctk.CTkFrame(
            stats_container,
            fg_color=("white", "#2b2b2b"),
            corner_radius=15,
            border_width=2,
            border_color=color
        )
        card.grid(row=0, column=i, padx=8, sticky="ew")
        stats_container.grid_columnconfigure(i, weight=1)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=20, pady=15)
        
        ctk.CTkLabel(inner, text=icon, font=ctk.CTkFont(size=32)).pack()
        ctk.CTkLabel(
            inner,
            text=str(value),
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=color
        ).pack(pady=(5, 0))
        ctk.CTkLabel(
            inner,
            text=label,
            font=ctk.CTkFont(size=11),
            text_color=("gray60", "gray50")
        ).pack()
    
    # Message d'information
    info_card = ctk.CTkFrame(
        content,
        fg_color=("white", "#2b2b2b"),
        corner_radius=15,
        border_width=2,
        border_color=("#3b82f6")
    )
    info_card.pack(fill="x", pady=(0, 20))
    
    info_content = ctk.CTkFrame(info_card, fg_color="transparent")
    info_content.pack(padx=30, pady=20)
    
    ctk.CTkLabel(
        info_content,
        text="ℹ️  Utilisez la navigation pour consulter les règles par catégorie",
        font=ctk.CTkFont(size=13),
        text_color=("#3b82f6")
    ).pack()


def show_category_table(nav_state, category_name, icon, color):
    """Afficher le tableau d'une catégorie spécifique"""
    content = nav_state['content_area']
    rules_data = [r for r in nav_state['rules_data'] if r['categorie'] == category_name]
    
    # Header
    header = ctk.CTkFrame(content, fg_color="transparent")
    header.pack(fill="x", pady=(0, 20))
    
    title_frame = ctk.CTkFrame(header, fg_color="transparent")
    title_frame.pack(side="left")
    
    ctk.CTkLabel(
        title_frame,
        text=f"{icon} {category_name}",
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color=color
    ).pack(side="left")
    
    ctk.CTkLabel(
        title_frame,
        text=f"  •  {len(rules_data)} règle(s)",
        font=ctk.CTkFont(size=14),
        text_color=("gray60", "gray50")
    ).pack(side="left")
    
    # Actions
    actions = ctk.CTkFrame(header, fg_color="transparent")
    actions.pack(side="right")
    
    ctk.CTkButton(
        actions,
        text="➕ Ajouter",
        height=40,
        font=ctk.CTkFont(size=12, weight="bold"),
        fg_color=color,
        command=lambda: create_new_rule(nav_state['app'])
    ).pack(side="left", padx=5)
    
    # Info pagination
    if len(rules_data) > nav_state['rows_per_page']:
        info = ctk.CTkFrame(content, fg_color=("gray92", "gray18"), corner_radius=10)
        info.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            info,
            text=f"ℹ️ Affichage limité à {nav_state['rows_per_page']} règles sur {len(rules_data)} • Modifiable dans Paramètres",
            font=ctk.CTkFont(size=11),
            text_color=("gray60", "gray50")
        ).pack(padx=15, pady=10)
    
    # Tableau
    rules_to_display = rules_data[:nav_state['rows_per_page']]
    create_detailed_table(
        content,
        rules_to_display,
        category_name,
        nav_state['app'],
        nav_state['table_font_size'],
        nav_state['alternate_colors'],
        nav_state['row_spacing'],
        nav_state['accent_color'],
        color
    )


def create_detailed_table(parent, rules, category_name, app, font_size, alternate_colors, row_spacing, accent_color, category_color):
    """Créer le tableau détaillé"""
    table_card = ctk.CTkFrame(
        parent,
        fg_color=("white", "#2b2b2b"),
        corner_radius=15,
        border_width=1,
        border_color=("gray80", "gray30")
    )
    table_card.pack(fill="both", expand=True)
    
    # Canvas avec scrollbars
    canvas = Canvas(
        table_card,
        bg=("white" if ctk.get_appearance_mode() == "Light" else "#2b2b2b"),
        highlightthickness=0
    )
    
    v_scrollbar = Scrollbar(table_card, orient="vertical", command=canvas.yview)
    v_scrollbar.pack(side="right", fill="y")
    
    h_scrollbar = Scrollbar(table_card, orient="horizontal", command=canvas.xview)
    h_scrollbar.pack(side="bottom", fill="x")
    
    canvas.pack(side="left", fill="both", expand=True)
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    table_inner = Frame(
        canvas,
        bg=("white" if ctk.get_appearance_mode() == "Light" else "#2b2b2b")
    )
    canvas_window = canvas.create_window((0, 0), window=table_inner, anchor="nw")
    
    # Espacement
    spacing_config = {
        "compact": (1, 22),
        "large": (5, 38),
        "normal": (2, 30)
    }
    pady_value, cell_height = spacing_config.get(row_spacing, (2, 30))
    
    # Headers
    if category_name == "Officiers":
        headers = [
            ("Grade Source", 140),
            ("Grade Cible", 140),
            ("Type", 120),
            ("Conditions", 400),
            ("Statut", 90),
            ("Actions", 110)
        ]
    else:
        headers = [
            ("Grade Source", 130),
            ("Grade Cible", 130),
            ("Type", 100),
            ("Ancienneté", 150),
            ("Diplômes", 120),
            ("Notes", 100),
            ("Conditions", 200),
            ("Statut", 80),
            ("Actions", 110)
        ]
    
    # Header row
    header_frame = ctk.CTkFrame(table_inner, fg_color=category_color)
    header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 3))
    
    for i, (header, width) in enumerate(headers):
        ctk.CTkLabel(
            header_frame,
            text=header,
            font=ctk.CTkFont(size=font_size+1, weight="bold"),
            width=width,
            text_color="white"
        ).grid(row=0, column=i, padx=2, pady=5, sticky="ew")
    
    # Data rows
    for idx, rule in enumerate(rules):
        bg_color = ("gray92", "gray17") if (alternate_colors and idx % 2 == 0) else ("gray97", "gray21")
        
        row_frame = ctk.CTkFrame(table_inner, fg_color=bg_color)
        row_frame.grid(row=idx+1, column=0, sticky="ew", pady=pady_value)
        
        # Préparer les données
        if category_name == "Officiers":
            row_data = [
                rule['grade_source'],
                rule['grade_cible'],
                rule['type_avancement'],
                rule['conditions_principales'][:60] + "..." if len(rule['conditions_principales']) > 60 else rule['conditions_principales'],
                rule['statut']
            ]
        else:
            row_data = [
                rule['grade_source'],
                rule['grade_cible'],
                rule['type_avancement'],
                rule['anciennete_requise'][:25],
                rule['diplomes'][:18],
                rule['notes'][:15],
                rule['conditions_speciales'][:30],
                rule['statut']
            ]
        
        # Cellules
        for i, (data, (header, width)) in enumerate(zip(row_data, headers[:-1])):
            if header == "Statut":
                text_color = {"Actif": "#16a34a", "Inactif": "#dc2626"}.get(data, "#eab308")
                font_weight = "bold"
            else:
                text_color = ("gray10", "gray90")
                font_weight = "normal"
            
            ctk.CTkLabel(
                row_frame,
                text=str(data),
                font=ctk.CTkFont(size=font_size, weight=font_weight),
                width=width,
                anchor="w",
                text_color=text_color,
                wraplength=width-10,
                height=cell_height
            ).grid(row=0, column=i, padx=2, pady=2, sticky="ew")
        
        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=len(headers)-1, padx=2, pady=2)
        
        ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=35,
            height=cell_height-4,
            font=ctk.CTkFont(size=font_size),
            fg_color=accent_color,
            command=lambda r_id=rule.get('id'): edit_rule(app, r_id)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=35,
            height=cell_height-4,
            font=ctk.CTkFont(size=font_size),
            fg_color="#dc2626",
            hover_color="#991b1b",
            command=lambda r_id=rule.get('id'): delete_rule(app, r_id)
        ).pack(side="left", padx=2)
    
    # Configure scroll
    def on_frame_configure(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    table_inner.bind("<Configure>", on_frame_configure)
    
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", on_mousewheel)


def show_equivalences_view(nav_state):
    """Afficher la vue des équivalences"""
    content = nav_state['content_area']
    
    # Header
    header = ctk.CTkFrame(content, fg_color="transparent")
    header.pack(fill="x", pady=(0, 20))
    
    ctk.CTkLabel(
        header,
        text="🔄 Équivalences de Diplômes",
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color="#8b5cf6"
    ).pack(side="left")
    
    # Contenu équivalences
    try:
        from gui.components.equivalences_section import show_equivalences_section
        show_equivalences_section(content, nav_state['app'])
    except ImportError:
        # Fallback si le module n'existe pas
        info_card = ctk.CTkFrame(
            content,
            fg_color=("white", "#2b2b2b"),
            corner_radius=15,
            border_width=2,
            border_color="#8b5cf6"
        )
        info_card.pack(fill="both", expand=True)
        
        info_content = ctk.CTkFrame(info_card, fg_color="transparent")
        info_content.pack(padx=50, pady=50)
        
        ctk.CTkLabel(
            info_content,
            text="🔄",
            font=ctk.CTkFont(size=64)
        ).pack(pady=(0, 20))
        
        ctk.CTkLabel(
            info_content,
            text="Section Équivalences",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack()
        
        ctk.CTkLabel(
            info_content,
            text="Le module d'équivalences sera disponible prochainement",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray50")
        ).pack(pady=(10, 0))