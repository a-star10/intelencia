"""
Section Gestion des Équivalences Diplômes
gui/components/equivalences_section.py
"""
import customtkinter as ctk
from tkinter import messagebox
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from core.database import db_manager

def show_equivalences_section(parent, app):
    """Afficher la section des équivalences diplômes"""
    
    # Frame principale pour les équivalences
    equiv_main_frame = ctk.CTkFrame(parent)
    equiv_main_frame.pack(fill="x", padx=20, pady=20)
    
    # Titre
    title_label = ctk.CTkLabel(
        equiv_main_frame,
        text="🔄 Gestion des Équivalences Diplômes",
        font=ctk.CTkFont(size=18, weight="bold")
    )
    title_label.pack(pady=15)
    
    # Description
    desc_label = ctk.CTkLabel(
        equiv_main_frame,
        text="Les équivalences permettent au système de reconnaître des diplômes alternatifs\n"
             "Exemple: Un agent avec C.T.E peut satisfaire une condition qui demande C.M.E",
        font=ctk.CTkFont(size=11),
        text_color="gray"
    )
    desc_label.pack(pady=(0, 15))
    
    # Formulaire d'ajout d'équivalence
    create_add_equivalence_form(equiv_main_frame, app)
    
    # Tableau des équivalences existantes
    create_equivalences_table(equiv_main_frame, app)

def create_add_equivalence_form(parent, app):
    """Créer le formulaire d'ajout d'équivalence"""
    
    form_frame = ctk.CTkFrame(parent)
    form_frame.pack(fill="x", padx=20, pady=(0, 20))
    
    # Titre du formulaire
    form_title = ctk.CTkLabel(
        form_frame,
        text="➕ Ajouter une Équivalence",
        font=ctk.CTkFont(size=14, weight="bold")
    )
    form_title.pack(pady=10)
    
    # Grid pour les champs
    fields_grid = ctk.CTkFrame(form_frame)
    fields_grid.pack(fill="x", padx=20, pady=10)
    
    # Liste des diplômes disponibles
    diplomes_list = [
        "C.M.E", "C.T.E", "FCB",
        "C.M.1", "C.T.1", "B.M.P.E", "B.M.P.1",
        "C.M.2", "C.T.2", "B.M.P.2", "CPOS",
        "Diplôme de sortie d'école",
        "Brevet enseignement militaire supérieur 1er degré",
        "Brevet enseignement militaire supérieur 2ème degré"
    ]
    
    # Diplôme principal
    ctk.CTkLabel(fields_grid, text="Diplôme principal:", width=150).grid(row=0, column=0, padx=10, pady=10, sticky="w")
    diplome_principal = ctk.CTkComboBox(fields_grid, values=diplomes_list, width=300)
    diplome_principal.grid(row=0, column=1, padx=10, pady=10, sticky="w")
    
    # Label explicatif
    ctk.CTkLabel(
        fields_grid, 
        text="↔️", 
        font=ctk.CTkFont(size=20)
    ).grid(row=0, column=2, padx=5)
    
    # Diplôme équivalent
    ctk.CTkLabel(fields_grid, text="Est équivalent à:", width=150).grid(row=0, column=3, padx=10, pady=10, sticky="w")
    diplome_equivalent = ctk.CTkComboBox(fields_grid, values=diplomes_list, width=300)
    diplome_equivalent.grid(row=0, column=4, padx=10, pady=10, sticky="w")
    
    # Bouton Ajouter
    add_button = ctk.CTkButton(
        fields_grid,
        text="✅ Ajouter",
        width=120,
        height=35,
        font=ctk.CTkFont(size=13, weight="bold"),
        command=lambda: add_equivalence(app, diplome_principal.get(), diplome_equivalent.get())
    )
    add_button.grid(row=0, column=5, padx=15, pady=10)
    
    # Note d'information
    info_label = ctk.CTkLabel(
        form_frame,
        text="💡 L'équivalence fonctionne dans les deux sens automatiquement",
        font=ctk.CTkFont(size=10),
        text_color="#3B8ED0"
    )
    info_label.pack(pady=(0, 10))

# ==================== FONCTIONS DE GESTION ====================

def add_equivalence(app, diplome_principal, diplome_equivalent):
    """Ajouter une nouvelle équivalence"""
    
    # Validation
    if not diplome_principal or not diplome_equivalent:
        messagebox.showerror("Erreur", "Veuillez sélectionner les deux diplômes")
        return
    
    if diplome_principal == diplome_equivalent:
        messagebox.showerror("Erreur", "Les deux diplômes doivent être différents")
        return
    
    # Vérifier si l'équivalence existe déjà
    existing = db_manager.get_equivalence(diplome_principal, diplome_equivalent)
    if existing:
        messagebox.showwarning("Attention", "Cette équivalence existe déjà")
        return
    
    # Créer l'équivalence
    try:
        equiv_id = db_manager.create_equivalence(diplome_principal, diplome_equivalent)
        
        if equiv_id:
            messagebox.showinfo(
                "Succès",
                f"Équivalence créée avec succès !\n\n"
                f"{diplome_principal} ↔️ {diplome_equivalent}\n\n"
                f"ID: {equiv_id}"
            )
            
            # Rafraîchir la vue
            app.navigate_to("rules")
        else:
            messagebox.showerror("Erreur", "Erreur lors de la création de l'équivalence")
    
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création : {str(e)}")

def delete_equivalence(app, equiv_id):
    """Supprimer une équivalence"""
    
    try:
        # Récupérer l'équivalence
        equiv = db_manager.get_equivalence_by_id(equiv_id)
        
        if not equiv:
            messagebox.showerror("Erreur", "Équivalence non trouvée")
            return
        
        # Confirmation
        response = messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous vraiment supprimer cette équivalence ?\n\n"
            f"{equiv['diplome_principal']} ↔️ {equiv['diplome_equivalent']}\n\n"
            f"Cette action est irréversible."
        )
        
        if response:
            success = db_manager.delete_equivalence(equiv_id)
            
            if success:
                messagebox.showinfo("Succès", "Équivalence supprimée avec succès !")
                app.navigate_to("rules")
            else:
                messagebox.showerror("Erreur", "Erreur lors de la suppression")
    
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression : {str(e)}")

def edit_equivalence(app, equiv_id):
    """Modifier une équivalence"""
    
    try:
        # Récupérer l'équivalence
        equiv = db_manager.get_equivalence_by_id(equiv_id)
        
        if not equiv:
            messagebox.showerror("Erreur", "Équivalence non trouvée")
            return
        
        # Ouvrir la popup de modification
        show_edit_equivalence_popup(app, equiv)
    
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ouverture : {str(e)}")

def show_edit_equivalence_popup(app, equiv):
    """Afficher la popup de modification d'équivalence"""
    
    popup = ctk.CTkToplevel(app.root)
    popup.title("Modifier l'équivalence")
    popup.geometry("600x300")
    popup.transient(app.root)
    popup.grab_set()
    
    # Centrer
    popup.update_idletasks()
    x = (popup.winfo_screenwidth() - popup.winfo_width()) // 2
    y = (popup.winfo_screenheight() - popup.winfo_height()) // 2
    popup.geometry(f"+{x}+{y}")
    
    # Contenu
    main_frame = ctk.CTkFrame(popup)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Titre
    title_label = ctk.CTkLabel(
        main_frame,
        text="✏️ Modifier l'Équivalence",
        font=ctk.CTkFont(size=18, weight="bold")
    )
    title_label.pack(pady=(0, 20))
    
    # Liste des diplômes
    diplomes_list = [
        "C.M.E", "C.T.E", "FCB",
        "C.M.1", "C.T.1", "B.M.P.E", "B.M.P.1",
        "C.M.2", "C.T.2", "B.M.P.2", "CPOS",
        "Diplôme de sortie d'école",
        "Brevet enseignement militaire supérieur 1er degré",
        "Brevet enseignement militaire supérieur 2ème degré"
    ]
    
    # Formulaire
    fields_frame = ctk.CTkFrame(main_frame)
    fields_frame.pack(fill="x", pady=20)
    
    # Diplôme principal
    ctk.CTkLabel(fields_frame, text="Diplôme principal:", width=150).grid(row=0, column=0, padx=10, pady=10, sticky="w")
    diplome_principal = ctk.CTkComboBox(fields_frame, values=diplomes_list, width=250)
    diplome_principal.set(equiv['diplome_principal'])
    diplome_principal.grid(row=0, column=1, padx=10, pady=10, sticky="w")
    
    # Flèche
    ctk.CTkLabel(fields_frame, text="↔️", font=ctk.CTkFont(size=20)).grid(row=1, column=0, columnspan=2, pady=5)
    
    # Diplôme équivalent
    ctk.CTkLabel(fields_frame, text="Diplôme équivalent:", width=150).grid(row=2, column=0, padx=10, pady=10, sticky="w")
    diplome_equivalent = ctk.CTkComboBox(fields_frame, values=diplomes_list, width=250)
    diplome_equivalent.set(equiv['diplome_equivalent'])
    diplome_equivalent.grid(row=2, column=1, padx=10, pady=10, sticky="w")
    
    # Boutons
    buttons_frame = ctk.CTkFrame(main_frame)
    buttons_frame.pack(pady=20)
    
    def save_changes():
        new_principal = diplome_principal.get()
        new_equivalent = diplome_equivalent.get()
        
        # Validation
        if not new_principal or not new_equivalent:
            messagebox.showerror("Erreur", "Veuillez sélectionner les deux diplômes")
            return
        
        if new_principal == new_equivalent:
            messagebox.showerror("Erreur", "Les deux diplômes doivent être différents")
            return
        
        # Mettre à jour
        try:
            success = db_manager.update_equivalence(equiv['id'], new_principal, new_equivalent)
            
            if success:
                messagebox.showinfo("Succès", "Équivalence modifiée avec succès !")
                popup.destroy()
                app.navigate_to("rules")
            else:
                messagebox.showerror("Erreur", "Erreur lors de la modification")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {str(e)}")
    
    # Bouton Sauvegarder
    save_btn = ctk.CTkButton(
        buttons_frame,
        text="💾 Sauvegarder",
        width=150,
        height=35,
        command=save_changes
    )
    save_btn.pack(side="left", padx=10)
    
    # Bouton Annuler
    cancel_btn = ctk.CTkButton(
        buttons_frame,
        text="❌ Annuler",
        width=150,
        height=35,
        command=popup.destroy
    )
    cancel_btn.pack(side="left", padx=10)

def create_equivalences_table(parent, app):
    """Créer le tableau des équivalences existantes"""
    
    table_frame = ctk.CTkFrame(parent)
    table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    # Titre du tableau
    table_title = ctk.CTkLabel(
        table_frame,
        text="📋 Équivalences Existantes",
        font=ctk.CTkFont(size=14, weight="bold")
    )
    table_title.pack(pady=15)
    
    # Container scrollable
    table_container = ctk.CTkScrollableFrame(table_frame, height=250)
    table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    # Récupérer les équivalences
    equivalences = db_manager.get_all_equivalences()
    
    if not equivalences:
        no_data_label = ctk.CTkLabel(
            table_container,
            text="Aucune équivalence définie\n\nUtilisez le formulaire ci-dessus pour ajouter des équivalences",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        no_data_label.pack(pady=30)
        return
    
    # Headers
    headers = [
        ("Diplôme Principal", 300),
        ("↔️", 50),
        ("Diplôme Équivalent", 300),
        ("Statut", 100),
        ("Actions", 100)
    ]
    
    header_frame = ctk.CTkFrame(table_container)
    header_frame.pack(fill="x", pady=(0, 5))
    
    for i, (header, width) in enumerate(headers):
        header_label = ctk.CTkLabel(
            header_frame,
            text=header,
            font=ctk.CTkFont(size=11, weight="bold"),
            width=width
        )
        header_label.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
    
    # Lignes des équivalences
    for idx, equiv in enumerate(equivalences):
        bg_color = ("gray92", "gray17") if idx % 2 == 0 else ("gray97", "gray21")
        
        row_frame = ctk.CTkFrame(table_container, fg_color=bg_color)
        row_frame.pack(fill="x", pady=2)
        
        # Diplôme principal
        ctk.CTkLabel(
            row_frame,
            text=equiv['diplome_principal'],
            font=ctk.CTkFont(size=11),
            width=300,
            anchor="w"
        ).grid(row=0, column=0, padx=5, pady=8, sticky="ew")
        
        # Flèche
        ctk.CTkLabel(
            row_frame,
            text="↔️",
            font=ctk.CTkFont(size=14),
            width=50
        ).grid(row=0, column=1, padx=5, pady=8)
        
        # Diplôme équivalent
        ctk.CTkLabel(
            row_frame,
            text=equiv['diplome_equivalent'],
            font=ctk.CTkFont(size=11),
            width=300,
            anchor="w"
        ).grid(row=0, column=2, padx=5, pady=8, sticky="ew")
        
        # Statut
        statut_text = "✅ Actif" if equiv['actif'] else "❌ Inactif"
        statut_color = "#16a34a" if equiv['actif'] else "#dc2626"
        
        ctk.CTkLabel(
            row_frame,
            text=statut_text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=statut_color,
            width=100
        ).grid(row=0, column=3, padx=5, pady=8)
        
        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=4, padx=5, pady=8)
        
        # Bouton Modifier
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=35,
            height=25,
            font=ctk.CTkFont(size=10),
            command=lambda equiv_id=equiv['id']: edit_equivalence(app, equiv_id)
        )
        edit_btn.pack(side="left", padx=2)
        
        # Bouton Supprimer
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=35,
            height=25,
            font=ctk.CTkFont(size=10),
            fg_color="#dc2626",
            hover_color="#991b1b",
            command=lambda equiv_id=equiv['id']: delete_equivalence(app, equiv_id)
        )
        delete_btn.pack(side="left", padx=2)
    
    # Footer
    footer_label = ctk.CTkLabel(
        table_container,
        text=f"📊 {len(equivalences)} équivalence(s) définie(s)",
        font=ctk.CTkFont(size=10),
        text_color="gray"
    )
    footer_label.pack(pady=10)