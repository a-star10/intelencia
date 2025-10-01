"""
Vue Rapports
gui/reports_view.py
"""
import customtkinter as ctk

def show_reports(app):
    """Afficher les rapports"""
    app.page_title.configure(text="📈 Rapports")
    
    placeholder_frame = ctk.CTkFrame(app.content_frame)
    placeholder_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    ctk.CTkLabel(
        placeholder_frame,
        text="🚧 Section Rapports en developpement",
        font=ctk.CTkFont(size=20, weight="bold")
    ).pack(pady=30)
    
    features_text = """
    Fonctionnalites prevues :
    
    • Graphiques statistiques interactifs
    • Rapports Excel/PDF automatises
    • Analyses par grade et categorie
    • Tendances d'avancement
    • Tableaux de bord personnalises
    • Export vers Excel
    """
    
    ctk.CTkLabel(
        placeholder_frame,
        text=features_text,
        font=ctk.CTkFont(size=14),
        justify="left"
    ).pack(pady=20)