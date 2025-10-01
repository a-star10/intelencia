"""
Vue Dashboard - VERSION MODERNE ET ÉPURÉE avec préférences
gui/dashboard_view.py
"""
import customtkinter as ctk
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

# ✅ Import des préférences
from core.preferences_manager import preferences_manager

def show_dashboard(app):
    """Afficher le dashboard avec design épuré"""
    app.page_title.configure(text="📊 Dashboard")
    
    # ✅ Charger les préférences
    show_stats = preferences_manager.get('show_stats_cards', True)
    stats_style = preferences_manager.get('stats_card_style', 'detailed')
    show_actions = preferences_manager.get('show_quick_actions', True)
    accent_color = preferences_manager.get_accent_color_hex()
    title_font_size = preferences_manager.get('title_font_size', 20)
    
    print(f"📊 Dashboard - Stats: {show_stats}, Style: {stats_style}, Actions: {show_actions}")
    
    # ✅ NOUVEAU : Frame sans scroll (design épuré)
    main_container = ctk.CTkFrame(app.content_frame, fg_color="transparent")
    main_container.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Section Bienvenue - Design épuré
    if show_stats:  # Seulement si activé dans préférences
        welcome_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        welcome_frame.pack(fill="x", pady=(0, 20))
        
        welcome_title = ctk.CTkLabel(
            welcome_frame,
            text="Système de gestion automatisée des carrières DGSS",
            font=ctk.CTkFont(size=title_font_size, weight="bold")
        )
        welcome_title.pack(pady=(10, 5))
        
        if stats_style == "detailed":
            welcome_text = ctk.CTkLabel(
                welcome_frame,
                text="\nVersion 1.0.0 - Dashboard opérationnel",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            welcome_text.pack(pady=(0, 10))
    
    # ✅ Stats cards - Design moderne et responsive
    if show_stats:
        create_stats_section(main_container, stats_style, accent_color)
    
    # ✅ Actions rapides - Design épuré
    if show_actions:
        create_actions_section(main_container, accent_color, app)
    
    # ✅ Statut système - Compact
    create_status_section(main_container, stats_style)

def create_stats_section(parent, style, accent_color):
    """✅ NOUVEAU : Section stats moderne et responsive"""
    stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
    stats_frame.pack(fill="x", pady=(0, 20))
    
    if style == "detailed":
        stats_title = ctk.CTkLabel(
            stats_frame,
            text="📈 Statistiques Générales",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        stats_title.pack(pady=(0, 15))
    
    # Grid responsive pour les stats
    stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
    stats_grid.pack(fill="x", padx=10)
    
    # Récupérer les stats
    try:
        from core.database import db_manager
        agents_data = db_manager.get_all_agents()
        total_agents = len(agents_data)
        proposables = len([a for a in agents_data if 'Proposable' in str(a.get('resultat_evaluation', '')) and 'Non' not in str(a.get('resultat_evaluation', ''))])
        bientot = len([a for a in agents_data if 'Bientot' in str(a.get('resultat_evaluation', ''))])
        non_proposables = total_agents - proposables - bientot
    except:
        total_agents = proposables = bientot = non_proposables = 0
    
    # ✅ Stats cards avec design moderne
    stats_data = [
        ("👥 Total Agents", str(total_agents), accent_color, "Nombre total d'agents"),
        ("🟢 Proposables", str(proposables), "#16a34a", "Agents éligibles"),
        ("🟡 Bientôt", str(bientot), "#eab308", "Bientôt éligibles"),
        ("🔴 Non proposables", str(non_proposables), "#dc2626", "Non éligibles")
    ]
    
    # ✅ Layout responsive (2 colonnes sur petits écrans, 4 sur grands)
    for i, (label, value, color, desc) in enumerate(stats_data):
        stat_card = create_modern_stat_card(
            stats_grid, 
            label, 
            value, 
            color, 
            desc if style == "detailed" else None
        )
        
        # Grid layout responsive
        row = i // 2
        col = i % 2
        stat_card.grid(row=row, column=col, padx=15, pady=10, sticky="nsew")
        
        # Configurer les colonnes pour être responsive
        stats_grid.grid_columnconfigure(col, weight=1, uniform="stats")

def create_modern_stat_card(parent, label, value, color, description=None):
    """✅ NOUVEAU : Carte statistique moderne et épurée"""
    card = ctk.CTkFrame(
        parent,
        corner_radius=12,
        border_width=2,
        border_color=color
    )
    
    # Container interne avec padding
    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(fill="both", expand=True, padx=20, pady=15)
    
    # Label
    label_widget = ctk.CTkLabel(
        inner,
        text=label,
        font=ctk.CTkFont(size=13, weight="bold"),
        anchor="w"
    )
    label_widget.pack(fill="x", pady=(0, 5))
    
    # Valeur (grand chiffre)
    value_widget = ctk.CTkLabel(
        inner,
        text=value,
        font=ctk.CTkFont(size=32, weight="bold"),
        text_color=color
    )
    value_widget.pack(fill="x", pady=(0, 5))
    
    # Description (si mode détaillé)
    if description:
        desc_widget = ctk.CTkLabel(
            inner,
            text=description,
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        desc_widget.pack(fill="x")
    
    return card

def create_actions_section(parent, accent_color, app):
    """✅ NOUVEAU : Actions rapides - Design épuré et responsive"""
    actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
    actions_frame.pack(fill="x", pady=(0, 20))
    
    actions_title = ctk.CTkLabel(
        actions_frame,
        text="⚡ Actions Rapides",
        font=ctk.CTkFont(size=16, weight="bold")
    )
    actions_title.pack(pady=(0, 15))
    
    # Grid responsive pour les actions
    actions_grid = ctk.CTkFrame(actions_frame, fg_color="transparent")
    actions_grid.pack(fill="x", padx=10)
    
    # ✅ Boutons d'actions avec design moderne
    actions = [
        ("➕ Nouvel Agent", app.quick_add_agent, accent_color),
        ("🎯 Évaluer Tous", app.quick_evaluate_all, "#16a34a"),
        ("📊 Générer Rapport", app.quick_generate_report, "#eab308"),
        ("📥 Importer Excel", app.quick_import_excel, "#8b5cf6")
    ]
    
    for i, (text, command_func, color) in enumerate(actions):
        btn = ctk.CTkButton(
            actions_grid,
            text=text,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=50,
            corner_radius=10,
            fg_color=color,
            hover_color=darken_color(color),
            command=command_func  # ✅ CORRIGÉ : Passer directement la fonction
        )
        
        # Grid layout responsive (2 colonnes)
        row = i // 2
        col = i % 2
        btn.grid(row=row, column=col, padx=15, pady=10, sticky="ew")
        
        # Configurer les colonnes
        actions_grid.grid_columnconfigure(col, weight=1, uniform="actions")

def create_status_section(parent, style):
    """✅ NOUVEAU : Statut système - Version compacte"""
    
    # Seulement en mode détaillé
    if style != "detailed":
        return
    
    status_frame = ctk.CTkFrame(parent, fg_color="transparent")
    status_frame.pack(fill="x", pady=(0, 10))
    
    status_title = ctk.CTkLabel(
        status_frame,
        text="🔧 Statut du Système",
        font=ctk.CTkFont(size=14, weight="bold")
    )
    status_title.pack(pady=(0, 10))
    
    # ✅ Grid compact pour le statut
    status_grid = ctk.CTkFrame(status_frame, fg_color="transparent")
    status_grid.pack(fill="x", padx=10)
    
    statuses = [
        ("Base de données", "✅ Opérationnelle", "#16a34a"),
        ("Interface", "✅ Fonctionnelle", "#16a34a"),
        ("Moteur de règles", "✅ Opérationnel", "#16a34a"),
        ("Import/Export", "🚧 En développement", "#eab308")
    ]
    
    for i, (component, status, color) in enumerate(statuses):
        status_item = ctk.CTkFrame(
            status_grid,
            corner_radius=8,
            border_width=1,
            border_color=("gray70", "gray30")
        )
        
        # Layout 2 colonnes
        row = i // 2
        col = i % 2
        status_item.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        status_grid.grid_columnconfigure(col, weight=1, uniform="status")
        
        # Contenu compact
        inner = ctk.CTkFrame(status_item, fg_color="transparent")
        inner.pack(fill="both", padx=15, pady=8)
        
        ctk.CTkLabel(
            inner,
            text=component,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        ).pack(fill="x")
        
        ctk.CTkLabel(
            inner,
            text=status,
            font=ctk.CTkFont(size=10),
            text_color=color,
            anchor="w"
        ).pack(fill="x")

def darken_color(hex_color):
    """Assombrir une couleur hexadécimale pour l'effet hover"""
    # Enlever le #
    hex_color = hex_color.lstrip('#')
    
    # Convertir en RGB
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Assombrir de 20%
    r = max(0, int(r * 0.8))
    g = max(0, int(g * 0.8))
    b = max(0, int(b * 0.8))
    
    # Reconvertir en hex
    return f'#{r:02x}{g:02x}{b:02x}'