"""
Vue Agents UX OPTIMISÉE - VERSION FINALE
gui/agents_view.py
Corrections: Loading complet + Fix défilement + Design épuré
"""
import customtkinter as ctk
import sys
from pathlib import Path
from tkinter import Canvas, Scrollbar, Frame, messagebox
import threading
import time

sys.path.append(str(Path(__file__).parent.parent))
from core.preferences_manager import preferences_manager
from gui.components.agent_popup import show_agent_popup

# ==================== VARIABLES GLOBALES ====================
loading_window = None
search_state = {}

# ==================== LOADING SCREEN ====================

class LoadingScreen:
    """Écran de chargement moderne et élégant"""
    
    def __init__(self, parent):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Chargement...")
        self.window.geometry("400x250")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Centrer
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 400) // 2
        y = (self.window.winfo_screenheight() - 250) // 2
        self.window.geometry(f"+{x}+{y}")
        
        # Désactiver le redimensionnement
        self.window.resizable(False, False)
        
        # Supprimer la barre de titre
        self.window.overrideredirect(True)
        
        # Frame principal avec bords arrondis simulés
        main_frame = ctk.CTkFrame(
            self.window,
            corner_radius=15,
            border_width=2,
            border_color=("gray70", "gray30")
        )
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Container interne
        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Icône
        icon_label = ctk.CTkLabel(
            content,
            text="👥",
            font=ctk.CTkFont(size=50)
        )
        icon_label.pack(pady=(0, 15))
        
        # Titre
        title_label = ctk.CTkLabel(
            content,
            text="Chargement des agents",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Barre de progression
        self.progress = ctk.CTkProgressBar(
            content,
            width=300,
            height=8,
            mode="indeterminate"
        )
        self.progress.pack(pady=(10, 15))
        self.progress.start()
        
        # Message de statut
        self.status_label = ctk.CTkLabel(
            content,
            text="Chargement des données...",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_label.pack()
        
        self.window.update()
    
    def update_status(self, message):
        """Mettre à jour le message de statut"""
        try:
            self.status_label.configure(text=message)
            self.window.update()
        except:
            pass
    
    def destroy(self):
        """Fermer l'écran de chargement"""
        try:
            self.progress.stop()
            self.window.grab_release()
            self.window.destroy()
        except:
            pass

# ==================== FONCTION PRINCIPALE ====================

def show_agents(app):
    """Afficher la gestion des agents avec loading complet"""
    global loading_window
    
    # Nettoyer le contenu actuel immédiatement
    for widget in app.content_frame.winfo_children():
        widget.destroy()
    
    # Afficher l'écran de chargement
    loading_window = LoadingScreen(app.root)
    
    # Charger les données en arrière-plan
    def load_data_async():
        global loading_window
        
        try:
            # Étape 1: Charger les préférences
            loading_window.update_status("Chargement des préférences...")
            time.sleep(0.1)
            
            table_font_size = preferences_manager.get('table_font_size', 9)
            rows_per_page = preferences_manager.get('rows_per_page', 100)
            alternate_colors = preferences_manager.get('alternate_row_colors', True)
            row_spacing = preferences_manager.get('row_spacing', 'normal')
            accent_color = preferences_manager.get_accent_color_hex()
            
            # Étape 2: Charger les données
            loading_window.update_status("Chargement des agents...")
            time.sleep(0.1)
            
            from core.database import db_manager
            agents_data = db_manager.get_all_agents()
            
            # Étape 3: Préparer les statistiques
            loading_window.update_status("Calcul des statistiques...")
            time.sleep(0.1)
            
            total = len(agents_data)
            proposables = len([a for a in agents_data if 'Proposable' in str(a.get('resultat_evaluation', '')) and 'Non' not in str(a.get('resultat_evaluation', ''))])
            bientot = len([a for a in agents_data if 'Bientot' in str(a.get('resultat_evaluation', ''))])
            non_prop = total - proposables - bientot
            
            stats = {
                'total': total,
                'proposables': proposables,
                'bientot': bientot,
                'non_prop': non_prop
            }
            
            # Étape 4: Construire l'interface (dans le thread principal)
            loading_window.update_status("Construction de l'interface...")
            time.sleep(0.1)
            
            def build_ui():
                global loading_window
                
                try:
                    # Titre de la page
                    app.page_title.configure(text="👥 Gestion des Agents")
                    
                    # Container principal
                    main_container = ctk.CTkFrame(app.content_frame, fg_color="transparent")
                    main_container.pack(fill="both", expand=True, padx=20, pady=10)
                    
                    # Stats épurées
                    create_minimal_stats(main_container, stats, accent_color)
                    
                    # Barre de recherche épurée
                    create_search_bar(main_container, app, agents_data, accent_color, 
                                    table_font_size, rows_per_page, alternate_colors, row_spacing)
                    
                    # Tableau initial
                    create_agents_table(main_container, agents_data, table_font_size, 
                                      rows_per_page, alternate_colors, row_spacing, accent_color, app)
                    
                finally:
                    # Fermer le loading
                    if loading_window:
                        loading_window.destroy()
                        loading_window = None
            
            # Exécuter dans le thread principal
            app.root.after(0, build_ui)
            
        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            import traceback
            traceback.print_exc()
            
            # Fermer le loading en cas d'erreur
            if loading_window:
                app.root.after(0, loading_window.destroy)
                loading_window = None
            
            # Afficher l'erreur
            app.root.after(0, lambda: messagebox.showerror("Erreur", f"Erreur de chargement: {e}"))
    
    # Lancer le chargement en arrière-plan
    threading.Thread(target=load_data_async, daemon=True).start()

# ==================== STATS ÉPURÉES ====================

def create_minimal_stats(parent, stats, accent_color):
    """Stats minimalistes et élégantes"""
    stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
    stats_frame.pack(fill="x", pady=(0, 20))
    
    # Container horizontal
    stats_container = ctk.CTkFrame(stats_frame, fg_color="transparent")
    stats_container.pack(fill="x")
    
    stats_items = [
        ("👥", stats['total'], "Total", accent_color),
        ("🟢", stats['proposables'], "Proposables", "#16a34a"),
        ("🟡", stats['bientot'], "Bientôt", "#eab308"),
        ("🔴", stats['non_prop'], "Non prop.", "#dc2626")
    ]
    
    for i, (emoji, value, label, color) in enumerate(stats_items):
        card = ctk.CTkFrame(
            stats_container,
            corner_radius=12,
            border_width=1,
            border_color=("gray80", "gray30")
        )
        card.grid(row=0, column=i, padx=10, pady=0, sticky="ew")
        stats_container.grid_columnconfigure(i, weight=1, uniform="stat")
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", padx=20, pady=15)
        
        # Emoji + Valeur sur la même ligne
        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x")
        
        ctk.CTkLabel(
            top_row,
            text=emoji,
            font=ctk.CTkFont(size=24)
        ).pack(side="left")
        
        ctk.CTkLabel(
            top_row,
            text=str(value),
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=color
        ).pack(side="left", padx=(10, 0))
        
        # Label en dessous
        ctk.CTkLabel(
            inner,
            text=label,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(anchor="w", pady=(5, 0))

# ==================== BARRE DE RECHERCHE ÉPURÉE ====================

def create_search_bar(parent, app, agents_data, accent_color, font_size, rows_per_page, alternate_colors, row_spacing):
    """Barre de recherche minimaliste et moderne"""
    global search_state
    
    # Container principal
    search_container = ctk.CTkFrame(parent, corner_radius=12)
    search_container.pack(fill="x", pady=(0, 20))
    
    # Header avec titre et boutons d'action
    header_frame = ctk.CTkFrame(search_container, fg_color="transparent")
    header_frame.pack(fill="x", padx=20, pady=(15, 10))
    
    # Titre
    ctk.CTkLabel(
        header_frame,
        text="🔍 Recherche et filtres",
        font=ctk.CTkFont(size=14, weight="bold")
    ).pack(side="left")
    
    # Boutons d'action à droite
    actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    actions_frame.pack(side="right")
    
    ctk.CTkButton(
        actions_frame,
        text="➕ Nouvel Agent",
        height=32,
        width=140,
        fg_color=accent_color,
        command=app.add_new_agent
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        actions_frame,
        text="🔄",
        height=32,
        width=40,
        command=lambda: app.navigate_to("agents")
    ).pack(side="left", padx=5)
    
    # Séparateur
    separator = ctk.CTkFrame(search_container, height=1, fg_color=("gray80", "gray30"))
    separator.pack(fill="x", padx=20, pady=10)
    
    # Zone de recherche
    search_frame = ctk.CTkFrame(search_container, fg_color="transparent")
    search_frame.pack(fill="x", padx=20, pady=(0, 15))
    
    # Ligne 1: Recherche texte + Checkbox floue
    row1 = ctk.CTkFrame(search_frame, fg_color="transparent")
    row1.pack(fill="x", pady=5)
    
    ctk.CTkLabel(row1, text="Texte:", width=70, anchor="w").pack(side="left", padx=(0, 10))
    
    search_entry = ctk.CTkEntry(row1, placeholder_text="Nom, prénom, matricule...", width=300, height=36)
    search_entry.pack(side="left", padx=5)
    
    fuzzy_var = ctk.BooleanVar(value=True)
    ctk.CTkCheckBox(row1, text="Recherche floue", variable=fuzzy_var, width=120).pack(side="left", padx=15)
    
    # Ligne 2: Filtres
    row2 = ctk.CTkFrame(search_frame, fg_color="transparent")
    row2.pack(fill="x", pady=5)
    
    ctk.CTkLabel(row2, text="Grade:", width=70, anchor="w").pack(side="left", padx=(0, 10))
    
    grade_combo = ctk.CTkComboBox(
        row2,
        values=["Tous", "Caporal", "Sergent", "Adjudant", "Lieutenant", "Capitaine", "Commandant"],
        width=180,
        height=36
    )
    grade_combo.set("Tous")
    grade_combo.pack(side="left", padx=5)
    
    ctk.CTkLabel(row2, text="Unité:", width=70, anchor="w").pack(side="left", padx=(20, 10))
    
    unites = ["Toutes"] + sorted(list(set([a.get('unite_provenance', '') for a in agents_data if a.get('unite_provenance')])))
    unite_combo = ctk.CTkComboBox(row2, values=unites, width=200, height=36)
    unite_combo.set("Toutes")
    unite_combo.pack(side="left", padx=5)
    
    ctk.CTkLabel(row2, text="Statut:", width=70, anchor="w").pack(side="left", padx=(20, 10))
    
    statut_combo = ctk.CTkComboBox(
        row2,
        values=["Tous", "Proposable", "Bientôt proposable", "Non proposable"],
        width=180,
        height=36
    )
    statut_combo.set("Tous")
    statut_combo.pack(side="left", padx=5)
    
    # Boutons de recherche
    btn_frame = ctk.CTkFrame(search_container, fg_color="transparent")
    btn_frame.pack(fill="x", padx=20, pady=(0, 15))
    
    def do_search():
        """Effectuer la recherche avec loading"""
        # Mini loading
        search_btn.configure(state="disabled", text="⏳ Recherche...")
        
        def search_async():
            time.sleep(0.1)  # Petit délai pour l'UX
            
            query = search_entry.get().lower()
            use_fuzzy = fuzzy_var.get()
            grade_filter = grade_combo.get()
            unite_filter = unite_combo.get()
            statut_filter = statut_combo.get()
            
            filtered = agents_data.copy()
            
            # Filtre texte
            if query:
                if use_fuzzy:
                    from difflib import SequenceMatcher
                    filtered = [a for a in filtered if 
                        any(SequenceMatcher(None, query, str(a.get(field, '')).lower()).ratio() >= 0.6
                            for field in ['nom', 'prenom', 'matricule'])
                    ]
                else:
                    filtered = [a for a in filtered if 
                        query in a.get('nom', '').lower() or 
                        query in a.get('prenom', '').lower() or 
                        query in a.get('matricule', '').lower()
                    ]
            
            # Filtre grade
            if grade_filter != "Tous":
                filtered = [a for a in filtered if a.get('grade_actuel') == grade_filter]
            
            # Filtre unité
            if unite_filter != "Toutes":
                filtered = [a for a in filtered if a.get('unite_provenance') == unite_filter]
            
            # Filtre statut
            if statut_filter != "Tous":
                if statut_filter == "Proposable":
                    filtered = [a for a in filtered if 'Proposable' in str(a.get('resultat_evaluation', '')) 
                               and 'Non' not in str(a.get('resultat_evaluation', ''))]
                elif statut_filter == "Bientôt proposable":
                    filtered = [a for a in filtered if 'Bientot' in str(a.get('resultat_evaluation', ''))]
                elif statut_filter == "Non proposable":
                    filtered = [a for a in filtered if 'Non proposable' in str(a.get('resultat_evaluation', ''))]
            
            # Mettre à jour le tableau dans le thread principal
            def update_table():
                create_agents_table(parent, filtered, font_size, rows_per_page, 
                                  alternate_colors, row_spacing, accent_color, app)
                search_btn.configure(state="normal", text="🔍 Rechercher")
            
            app.root.after(0, update_table)
        
        threading.Thread(target=search_async, daemon=True).start()
    
    def reset_search():
        """Réinitialiser la recherche"""
        search_entry.delete(0, 'end')
        grade_combo.set("Tous")
        unite_combo.set("Toutes")
        statut_combo.set("Tous")
        fuzzy_var.set(True)
        create_agents_table(parent, agents_data, font_size, rows_per_page, 
                          alternate_colors, row_spacing, accent_color, app)
    
    search_btn = ctk.CTkButton(
        btn_frame,
        text="🔍 Rechercher",
        width=140,
        height=38,
        fg_color=accent_color,
        font=ctk.CTkFont(size=13, weight="bold"),
        command=do_search
    )
    search_btn.pack(side="left", padx=5)
    
    ctk.CTkButton(
        btn_frame,
        text="🔄 Réinitialiser",
        width=140,
        height=38,
        command=reset_search
    ).pack(side="left", padx=5)
    
    # Bind Enter pour rechercher
    search_entry.bind('<Return>', lambda e: do_search())

# ==================== TABLEAU OPTIMISÉ ====================

def create_agents_table(parent, agents_data, font_size, rows_per_page, alternate_colors, row_spacing, accent_color, app):
    """Tableau optimisé avec fix du défilement"""
    
    # Nettoyer l'ancien tableau
    for widget in parent.winfo_children():
        if isinstance(widget, ctk.CTkFrame) and hasattr(widget, '_is_table'):
            widget.destroy()
    
    if not agents_data:
        no_data = ctk.CTkLabel(
            parent,
            text="❌ Aucun agent trouvé",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        no_data.pack(pady=40)
        return
    
    # Frame tableau
    table_frame = ctk.CTkFrame(parent, corner_radius=12)
    table_frame._is_table = True
    table_frame.pack(fill="both", expand=True, pady=(0, 10))
    
    # Header
    header_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
    header_frame.pack(fill="x", padx=20, pady=15)
    
    ctk.CTkLabel(
        header_frame,
        text=f"📋 {len(agents_data)} agent(s)",
        font=ctk.CTkFont(size=14, weight="bold")
    ).pack(side="left")
    
    if len(agents_data) > rows_per_page:
        ctk.CTkLabel(
            header_frame,
            text=f"Affichage des {rows_per_page} premiers • Modifiez dans Paramètres",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(side="right")
    
    # Container avec scrollbars - FIX DÉFILEMENT
    canvas_frame = ctk.CTkFrame(table_frame)
    canvas_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    # Canvas avec taille fixe
    canvas = Canvas(
        canvas_frame,
        bg="#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#ffffff",
        highlightthickness=0,
        height=450  # Hauteur fixe pour éviter les problèmes
    )
    
    v_scroll = Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    h_scroll = Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
    
    v_scroll.pack(side="right", fill="y")
    h_scroll.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)
    
    canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    
    inner = Frame(canvas, bg="#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#ffffff")
    canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")
    
    # Espacement
    pady_val = {"compact": 1, "large": 4}.get(row_spacing, 2)
    cell_h = {"compact": 24, "large": 38}.get(row_spacing, 30)
    
    # Headers
    headers = [
        ("Matricule", 100),
        ("Nom", 160),
        ("Grade", 120),
        ("Age", 50),
        ("A.Serv", 70),
        ("A.Grad", 70),
        ("N", 40),
        ("N-1", 40),
        ("N-2", 40),
        ("Disc", 80),
        ("Unité", 150),
        ("Évaluation", 150),
        ("Action", 80)
    ]
    
    hdr_frame = ctk.CTkFrame(inner)
    hdr_frame.grid(row=0, column=0, sticky="ew", pady=(0, 3))
    
    for i, (h, w) in enumerate(headers):
        ctk.CTkLabel(
            hdr_frame,
            text=h,
            font=ctk.CTkFont(size=font_size+1, weight="bold"),
            width=w
        ).grid(row=0, column=i, padx=2, pady=5)
    
    # Lignes - Limiter pour la performance
    display_agents = agents_data[:rows_per_page]
    
    for idx, agent in enumerate(display_agents):
        bg = ("gray92", "gray17") if (alternate_colors and idx % 2 == 0) else ("gray97", "gray21") if alternate_colors else ("gray95", "gray19")
        hover_bg = ("gray85", "gray25")
        
        row = ctk.CTkFrame(inner, fg_color=bg)
        row.grid(row=idx+1, column=0, sticky="ew", pady=pady_val)
        
        # Effet hover - FIX: Utiliser configure au lieu de rebind
        def make_hover_handler(r, original_bg, hover_bg):
            def on_enter(e):
                r.configure(fg_color=hover_bg)
            def on_leave(e):
                r.configure(fg_color=original_bg)
            return on_enter, on_leave
        
        on_enter, on_leave = make_hover_handler(row, bg, hover_bg)
        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)
        
        # Données
        nom = f"{agent.get('nom', '')} {agent.get('prenom', '')}"[:22]
        unite = agent.get('unite_provenance', '')[:18]
        result = agent.get('resultat_evaluation', 'Non évalué')
        
        if 'Proposable' in result and 'Non' not in result:
            res_txt, res_col = "🟢 Proposable", "#16a34a"
        elif 'Bientot' in result:
            res_txt, res_col = "🟡 Bientôt", "#eab308"
        elif 'Non proposable' in result:
            res_txt, res_col = "🔴 Non prop.", "#dc2626"
        else:
            res_txt, res_col = "⚪ Non éval.", "gray"
        
        data = [
            agent.get('matricule', ''),
            nom,
            agent.get('grade_actuel', ''),
            str(agent.get('age', '')),
            f"{agent.get('anciennete_service', 0):.1f}",
            f"{agent.get('anciennete_grade', 0):.1f}",
            agent.get('note_annee_courante', ''),
            agent.get('note_annee_moins_1', ''),
            agent.get('note_annee_moins_2', ''),
            agent.get('statut_disciplinaire', '')[:10],
            unite,
            res_txt
        ]
        
        for i, (val, (h, w)) in enumerate(zip(data, headers[:-1])):
            col = res_col if i == 11 else ("gray10", "gray90")
            wgt = "bold" if i == 11 else "normal"
            
            lbl = ctk.CTkLabel(
                row,
                text=str(val),
                font=ctk.CTkFont(size=font_size, weight=wgt),
                width=w,
                anchor="w",
                text_color=col,
                height=cell_h
            )
            lbl.grid(row=0, column=i, padx=2, pady=2)
            
            # Propager les événements hover
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
        
        # Bouton action
        btn = ctk.CTkButton(
            row,
            text="👁️",
            width=75,
            height=cell_h-4,
            font=ctk.CTkFont(size=font_size),
            fg_color=accent_color,
            command=lambda aid=agent.get('id'): view_details(app, aid)
        )
        btn.grid(row=0, column=12, padx=2, pady=2)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
    
    # ✅ FIX DÉFILEMENT: Configuration optimisée
    def on_frame_configure(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Forcer la mise à jour de la position
        canvas.update_idletasks()
    
    inner.bind("<Configure>", on_frame_configure)
    
    # ✅ FIX: Défilement avec debouncing
    scroll_after_id = None
    
    def on_mousewheel(event):
        nonlocal scroll_after_id
        
        # Annuler le défilement précédent s'il existe
        if scroll_after_id:
            canvas.after_cancel(scroll_after_id)
        
        # Programmer le défilement avec un léger délai
        scroll_after_id = canvas.after(10, lambda: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
    
    # Lier uniquement au canvas, pas à all
    canvas.bind("<MouseWheel>", on_mousewheel, add="+")
    
    # Footer
    footer = ctk.CTkLabel(
        table_frame,
        text=f"💡 Défilement optimisé • {len(display_agents)} agents affichés",
        font=ctk.CTkFont(size=9),
        text_color="gray"
    )
    footer.pack(pady=(0, 10))

# ==================== DÉTAILS AGENT ====================

def view_details(app, agent_id):
    """Voir détails agent"""
    try:
        from core.database import db_manager
        agent = db_manager.get_agent_by_id(agent_id)
        if agent:
            show_agent_popup(app, agent)
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur: {e}")