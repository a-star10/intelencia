"""
Vue Évaluation - VERSION DESIGN SYSTEM ÉPURÉ
gui/evaluation_view.py

✨ Nouveautés:
- Design System unifié avec couleurs cohérentes
- Toast notifications au lieu de MessageBox
- Loading pour export et évaluation
- Loading initial au chargement
- Interface épurée et moderne
- Animations fluides
"""

import customtkinter as ctk
from tkinter import Canvas, Scrollbar, Frame
import sys
from pathlib import Path
import threading
import time

sys.path.append(str(Path(__file__).parent.parent))

from core.preferences_manager import preferences_manager
from gui.design_system import (
    ColorPalette, Typography, Spacing,
    DSButton, DSCard, DSSectionHeader, DSLoadingOverlay
)

# ==================== TOAST NOTIFICATIONS ====================

class ToastNotification:
    """Toast notification moderne"""
    
    def __init__(self, parent, message, type="info", duration=3000):
        self.window = ctk.CTkToplevel(parent)
        self.window.withdraw()
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        
        # Couleurs selon le type
        colors = {
            'success': ColorPalette.SUCCESS,
            'error': ColorPalette.DANGER,
            'warning': ColorPalette.WARNING,
            'info': ColorPalette.INFO
        }
        
        icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        
        color = ColorPalette.get_color(colors.get(type, ColorPalette.INFO))
        icon = icons.get(type, 'ℹ️')
        
        # Frame principal
        main_frame = ctk.CTkFrame(
            self.window,
            fg_color=color,
            corner_radius=12,
            border_width=0
        )
        main_frame.pack(padx=0, pady=0)
        
        # Contenu
        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.pack(padx=Spacing.LG, pady=Spacing.MD)
        
        # Icône + Message sur la même ligne
        row = ctk.CTkFrame(content, fg_color="transparent")
        row.pack()
        
        ctk.CTkLabel(
            row,
            text=icon,
            font=Typography.get_font(size=20)
        ).pack(side="left", padx=(0, Spacing.SM))
        
        ctk.CTkLabel(
            row,
            text=message,
            font=Typography.body_regular(),
            text_color="white"
        ).pack(side="left")
        
        # Positionner en haut à droite
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        screen_width = self.window.winfo_screenwidth()
        x = screen_width - width - 20
        y = 20
        
        self.window.geometry(f"+{x}+{y}")
        self.window.deiconify()
        
        # Animation d'entrée (fade in)
        self.window.attributes('-alpha', 0.0)
        self.fade_in()
        
        # Auto-fermeture
        self.window.after(duration, self.fade_out)
    
    def fade_in(self, alpha=0.0):
        """Animation fade in"""
        alpha += 0.1
        if alpha <= 1.0:
            self.window.attributes('-alpha', alpha)
            self.window.after(20, lambda: self.fade_in(alpha))
    
    def fade_out(self, alpha=1.0):
        """Animation fade out"""
        alpha -= 0.1
        if alpha >= 0.0:
            self.window.attributes('-alpha', alpha)
            self.window.after(20, lambda: self.fade_out(alpha))
        else:
            self.window.destroy()


def show_toast(parent, message, type="info", duration=3000):
    """Afficher un toast"""
    ToastNotification(parent, message, type, duration)


# ==================== FONCTION PRINCIPALE ====================

def show_evaluation(app):
    """Afficher l'évaluation avec loading initial"""
    
    # Nettoyer le contenu
    for widget in app.content_frame.winfo_children():
        widget.destroy()
    
    # Titre de la page
    app.page_title.configure(text="🎯 Évaluation des Agents")
    
    # Afficher loading
    loading = DSLoadingOverlay(app.root, "Chargement de l'évaluation...")
    
    def load_data_async():
        """Charger les données en arrière-plan"""
        try:
            time.sleep(0.3)  # Petit délai pour l'UX
            
            # Charger les préférences
            table_font_size = preferences_manager.get('table_font_size', 9)
            rows_per_page = preferences_manager.get('rows_per_page', 30)
            alternate_colors = preferences_manager.get('alternate_row_colors', True)
            row_spacing = preferences_manager.get('row_spacing', 'normal')
            accent_color = preferences_manager.get_accent_color_hex()
            
            # Charger les données
            from core.database import db_manager
            agents_data = db_manager.get_all_agents()
            
            # Construire l'UI dans le thread principal
            def build_ui():
                try:
                    loading.close()
                    
                    # Header avec stats
                    create_modern_header(app, agents_data, accent_color)
                    
                    # Actions
                    create_actions_bar(app, agents_data, accent_color)
                    
                    # Tableau
                    create_results_table(
                        app, agents_data, table_font_size, 
                        rows_per_page, alternate_colors, 
                        row_spacing, accent_color
                    )
                    
                except Exception as e:
                    loading.close()
                    show_toast(app.root, f"Erreur: {e}", "error")
            
            app.root.after(0, build_ui)
            
        except Exception as e:
            app.root.after(0, loading.close)
            app.root.after(100, lambda: show_toast(app.root, f"Erreur de chargement: {e}", "error"))
    
    # Lancer en arrière-plan
    threading.Thread(target=load_data_async, daemon=True).start()


# ==================== HEADER MODERNE ====================

def create_modern_header(app, agents_data, accent_color):
    """Header épuré avec stats"""
    
    header = DSCard(app.content_frame, padding=Spacing.XL)
    header.pack(fill="x", padx=Spacing.LG, pady=(Spacing.MD, 0))
    
    # Titre élégant
    title_frame = ctk.CTkFrame(header.content, fg_color="transparent")
    title_frame.pack(fill="x", pady=(0, Spacing.LG))
    
    ctk.CTkLabel(
        title_frame,
        text="Tableau de Bord des Évaluations",
        font=Typography.heading_1(),
        anchor="w"
    ).pack(side="left")
    
    ctk.CTkLabel(
        title_frame,
        text="Vue d'ensemble en temps réel",
        font=Typography.body_small(),
        text_color=ColorPalette.TEXT_SECONDARY,
        anchor="w"
    ).pack(side="left", padx=(Spacing.LG, 0))
    
    # Calculer stats
    total = len(agents_data)
    proposables = len([a for a in agents_data if 'Proposable' in str(a.get('resultat_evaluation', '')) and 'Non' not in str(a.get('resultat_evaluation', ''))])
    bientot = len([a for a in agents_data if 'Bientot' in str(a.get('resultat_evaluation', ''))])
    non_prop = total - proposables - bientot
    evalues = len([a for a in agents_data if a.get('derniere_evaluation')])
    
    # Grid de stats moderne
    stats_grid = ctk.CTkFrame(header.content, fg_color="transparent")
    stats_grid.pack(fill="x")
    
    for i in range(5):
        stats_grid.grid_columnconfigure(i, weight=1, uniform="stat")
    
    stats = [
        ("👥", total, "Total Agents", ColorPalette.PRIMARY),
        ("🟢", proposables, "Proposables", ColorPalette.SUCCESS),
        ("🟡", bientot, "Bientôt", ColorPalette.WARNING),
        ("🔴", non_prop, "Non prop.", ColorPalette.DANGER),
        ("✅", evalues, "Évalués", ColorPalette.INFO)
    ]
    
    for i, (icon, value, label, color) in enumerate(stats):
        create_stat_card(stats_grid, icon, value, label, color, i)


def create_stat_card(parent, icon, value, label, color, col):
    """Carte stat épurée"""
    card = ctk.CTkFrame(
        parent,
        corner_radius=10,
        border_width=1,
        border_color=ColorPalette.BORDER_DEFAULT
    )
    card.grid(row=0, column=col, padx=Spacing.SM, pady=0, sticky="ew")
    
    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(fill="both", padx=Spacing.MD, pady=Spacing.MD)
    
    # Icône
    ctk.CTkLabel(
        inner,
        text=icon,
        font=Typography.get_font(size=24)
    ).pack()
    
    # Valeur
    ctk.CTkLabel(
        inner,
        text=str(value),
        font=Typography.get_font(size=28, weight="bold"),
        text_color=ColorPalette.get_color(color)
    ).pack(pady=(Spacing.XS, 0))
    
    # Label
    ctk.CTkLabel(
        inner,
        text=label,
        font=Typography.caption(),
        text_color=ColorPalette.TEXT_SECONDARY
    ).pack()


# ==================== BARRE D'ACTIONS ====================

def create_actions_bar(app, agents_data, accent_color):
    """Barre d'actions épurée"""
    
    actions_card = DSCard(app.content_frame, padding=Spacing.LG)
    actions_card.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)
    
    # Container horizontal
    container = ctk.CTkFrame(actions_card.content, fg_color="transparent")
    container.pack(fill="x")
    
    # Filtres à gauche
    filters_frame = ctk.CTkFrame(container, fg_color="transparent")
    filters_frame.pack(side="left", fill="x", expand=True)
    
    ctk.CTkLabel(
        filters_frame,
        text="Filtrer:",
        font=Typography.body_regular(),
        text_color=ColorPalette.TEXT_SECONDARY
    ).pack(side="left", padx=(0, Spacing.SM))
    
    filter_var = ctk.StringVar(value="Tous")
    filter_combo = ctk.CTkComboBox(
        filters_frame,
        values=["Tous", "🟢 Proposables", "🟡 Bientôt", "🔴 Non proposables", "⚪ Non évalués"],
        variable=filter_var,
        width=200,
        height=36
    )
    filter_combo.pack(side="left", padx=Spacing.SM)
    
    # Boutons à droite
    buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
    buttons_frame.pack(side="right")
    
    DSButton(
        buttons_frame,
        text="Évaluer Tous",
        variant="success",
        size="md",
        icon="🎯",
        width=140,
        command=lambda: run_evaluation_async(app)
    ).pack(side="left", padx=Spacing.XS)
    
    DSButton(
        buttons_frame,
        text="Actualiser",
        variant="primary",
        size="md",
        icon="🔄",
        width=120,
        command=lambda: app.navigate_to("evaluation")
    ).pack(side="left", padx=Spacing.XS)
    
    DSButton(
        buttons_frame,
        text="Exporter",
        variant="primary",
        size="md",
        icon="📊",
        width=120,
        command=lambda: export_results_async(app, agents_data)
    ).pack(side="left", padx=Spacing.XS)


# ==================== TABLEAU ====================

def create_results_table(app, agents_data, font_size, rows_per_page, alternate_colors, row_spacing, accent_color):
    """Tableau épuré avec scroll"""
    
    if not agents_data:
        no_data_card = DSCard(app.content_frame, padding=Spacing.XXL)
        no_data_card.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.MD)
        
        ctk.CTkLabel(
            no_data_card.content,
            text="❌ Aucun agent",
            font=Typography.heading_2(),
            text_color=ColorPalette.TEXT_SECONDARY
        ).pack()
        return
    
    # Card tableau
    table_card = DSCard(app.content_frame, padding=0)
    table_card.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.MD))
    
    # Header interne
    header = ctk.CTkFrame(table_card.content, fg_color="transparent")
    header.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)
    
    ctk.CTkLabel(
        header,
        text=f"📋 {len(agents_data)} résultat(s)",
        font=Typography.get_font(size=14, weight="bold")
    ).pack(side="left")
    
    if len(agents_data) > rows_per_page:
        ctk.CTkLabel(
            header,
            text=f"Affichage de {rows_per_page} premiers • Modifiez dans Paramètres",
            font=Typography.caption(),
            text_color=ColorPalette.TEXT_SECONDARY
        ).pack(side="right")
    
    # Canvas avec scroll
    canvas_frame = ctk.CTkFrame(table_card.content)
    canvas_frame.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))
    
    canvas = Canvas(
        canvas_frame,
        bg=ColorPalette.get_color(ColorPalette.BG_PRIMARY),
        highlightthickness=0,
        height=450
    )
    
    v_scroll = Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    h_scroll = Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
    
    v_scroll.pack(side="right", fill="y")
    h_scroll.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)
    
    canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    
    inner = Frame(canvas, bg=ColorPalette.get_color(ColorPalette.BG_PRIMARY))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    
    # Espacement
    spacing_map = {"compact": (1, 26), "large": (4, 40), "normal": (2, 32)}
    pady_val, cell_h = spacing_map.get(row_spacing, (2, 32))
    
    # Headers
    headers = [
        ("Matricule", 100), ("Nom", 160), ("Grade Actuel", 130),
        ("Grade Cible", 130), ("Type", 120), ("Statut", 160),
        ("Dernière Éval", 140), ("Action", 80)
    ]
    
    hdr = ctk.CTkFrame(inner)
    hdr.grid(row=0, column=0, sticky="ew", pady=(0, Spacing.XS))
    
    for i, (h, w) in enumerate(headers):
        ctk.CTkLabel(
            hdr,
            text=h,
            font=Typography.get_font(size=font_size+1, weight="bold"),
            width=w
        ).grid(row=0, column=i, padx=2, pady=Spacing.SM)
    
    # Lignes
    display_agents = agents_data[:rows_per_page]
    
    for idx, agent in enumerate(display_agents):
        bg = ColorPalette.get_color(
            ColorPalette.BG_SECONDARY if (alternate_colors and idx % 2 == 0) else ColorPalette.BG_PRIMARY
        )
        
        row = ctk.CTkFrame(inner, fg_color=bg)
        row.grid(row=idx+1, column=0, sticky="ew", pady=pady_val)
        
        # Données
        resultat = agent.get('resultat_evaluation', 'Non évalué')
        
        # Parser résultat
        if resultat and resultat != 'Non évalué':
            parts = resultat.split('->')
            grade_cible = parts[1].strip() if len(parts) == 2 else "N/A"
            type_av = next((t for t in ["Normal", "Choix", "Ancienneté", "Anciennete"] if t in parts[0]), "N/A") if len(parts) == 2 else "N/A"
        else:
            grade_cible = type_av = "N/A"
        
        # Statut
        if 'Proposable' in resultat and 'Non' not in resultat:
            statut_txt, statut_col = "🟢 Proposable", ColorPalette.SUCCESS
        elif 'Bientot' in resultat:
            statut_txt, statut_col = "🟡 Bientôt", ColorPalette.WARNING
        elif 'Non proposable' in resultat:
            statut_txt, statut_col = "🔴 Non prop.", ColorPalette.DANGER
        else:
            statut_txt, statut_col = "⚪ Non évalué", ColorPalette.TEXT_SECONDARY
        
        # Date
        derniere_eval = agent.get('derniere_evaluation', 'Jamais')
        if derniere_eval and derniere_eval != 'Jamais':
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(derniere_eval)
                derniere_eval = dt.strftime("%d/%m/%Y %H:%M")
            except:
                pass
        
        nom = f"{agent.get('nom', '')} {agent.get('prenom', '')}"[:22]
        
        data = [
            agent.get('matricule', ''),
            nom,
            agent.get('grade_actuel', ''),
            grade_cible,
            type_av,
            statut_txt,
            derniere_eval
        ]
        
        for i, (val, (h, w)) in enumerate(zip(data, headers[:-1])):
            col = ColorPalette.get_color(statut_col) if i == 5 else ColorPalette.get_color(ColorPalette.TEXT_PRIMARY)
            wgt = "bold" if i == 5 else "normal"
            
            ctk.CTkLabel(
                row,
                text=str(val),
                font=Typography.get_font(size=font_size, weight=wgt),
                width=w,
                anchor="w",
                text_color=col,
                height=cell_h
            ).grid(row=0, column=i, padx=2, pady=2)
        
        # Bouton
        DSButton(
            row,
            text="👁️",
            size="sm",
            width=70,
            command=lambda a=agent: show_details(app, a)
        ).grid(row=0, column=7, padx=2, pady=2)
    
    # Config scroll
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))


# ==================== ACTIONS ASYNC ====================

def run_evaluation_async(app):
    """Évaluer avec loading"""
    
    loading = DSLoadingOverlay(app.root, "Évaluation en cours...")
    
    def evaluate():
        try:
            time.sleep(0.2)
            
            from core.evaluator import evaluator
            resultats = evaluator.evaluer_tous_agents()
            
            prop = len([r for r in resultats if r.statut == "proposable"])
            bientot = len([r for r in resultats if r.statut == "bientot"])
            non_prop = len([r for r in resultats if r.statut == "non_proposable"])
            
            def finish():
                loading.close()
                show_toast(
                    app.root,
                    f"✅ {len(resultats)} agents évalués • {prop} proposables",
                    "success",
                    4000
                )
                app.navigate_to("evaluation")
            
            app.root.after(0, finish)
            
        except Exception as e:
            app.root.after(0, loading.close)
            app.root.after(100, lambda: show_toast(app.root, f"❌ Erreur: {e}", "error"))
    
    threading.Thread(target=evaluate, daemon=True).start()


def export_results_async(app, agents_data):
    """Exporter avec loading"""
    
    loading = DSLoadingOverlay(app.root, "Export en cours...")
    
    def export():
        try:
            time.sleep(0.3)
            
            import pandas as pd
            from pathlib import Path
            from datetime import datetime
            
            export_data = []
            for agent in agents_data:
                resultat = str(agent.get('resultat_evaluation', 'Non évalué'))
                
                if 'Proposable' in resultat and 'Non' not in resultat:
                    statut = "Proposable"
                elif 'Bientot' in resultat:
                    statut = "Bientôt"
                elif 'Non proposable' in resultat:
                    statut = "Non proposable"
                else:
                    statut = "Non évalué"
                
                export_data.append({
                    'Matricule': agent.get('matricule', ''),
                    'Nom': agent.get('nom', ''),
                    'Prénom': agent.get('prenom', ''),
                    'Grade': agent.get('grade_actuel', ''),
                    'Statut': statut,
                    'Résultat': resultat,
                    'Date': agent.get('derniere_evaluation', '')
                })
            
            df = pd.DataFrame(export_data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = Path(f"data/exports/eval_{timestamp}.xlsx")
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_excel(export_path, index=False, sheet_name="Évaluations", engine='openpyxl')
            
            def finish():
                loading.close()
                show_toast(
                    app.root,
                    f"✅ Export réussi • {len(agents_data)} agents",
                    "success",
                    4000
                )
            
            app.root.after(0, finish)
            
        except Exception as e:
            app.root.after(0, loading.close)
            app.root.after(100, lambda: show_toast(app.root, f"❌ Erreur export: {e}", "error"))
    
    threading.Thread(target=export, daemon=True).start()


def show_details(app, agent):
    """Afficher détails"""
    try:
        from gui.components.agent_popup import show_agent_popup
        show_agent_popup(app, agent)
    except Exception as e:
        show_toast(app.root, f"❌ Erreur: {e}", "error")