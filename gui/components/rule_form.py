"""
Formulaire de création/modification de règle d'avancement
gui/components/rule_form.py
"""
import customtkinter as ctk
from tkinter import messagebox
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import GRADES_HIERARCHY

class RuleForm:
    """Formulaire complet pour créer/modifier une règle d'avancement"""
    
    def __init__(self, parent_app, rule_data=None, mode="create"):
        self.app = parent_app
        self.rule_data = rule_data
        self.mode = mode  # "create" ou "edit"
        
        # Liste des diplômes possibles
        self.diplomes_disponibles = [
            "C.M.E", "C.T.E", "FCB",
            "C.M.1", "C.T.1", "B.M.P.E", "B.M.P.1",
            "C.M.2", "C.T.2", "B.M.P.2", "CPOS",
            "Diplôme de sortie d'école",
            "Brevet enseignement militaire supérieur 1er degré",
            "Brevet enseignement militaire supérieur 2ème degré"
        ]
        
        # Notes disponibles
        self.notes_disponibles = ["TB", "B", "AB", "P", "I"]
        
        # Types d'avancement
        self.types_avancement = ["Normal", "Ancienneté", "Choix"]
        
        # Catégories
        self.categories = ["Militaires du rang", "Sous-officiers", "Officiers"]
        
        # Diplômes sélectionnés
        self.diplomes_selectionnes = []
        
        self.create_form_window()
        self.setup_form()
        
        if mode == "edit" and rule_data:
            self.populate_form()
    
    def create_form_window(self):
        """Créer la fenêtre de formulaire"""
        title = "Modifier la règle" if self.mode == "edit" else "Nouvelle Règle d'Avancement"
        
        self.window = ctk.CTkToplevel(self.app.root)
        self.window.title(title)
        self.window.geometry("900x950")
        self.window.transient(self.app.root)
        self.window.grab_set()
        
        # Centrer la fenêtre
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - self.window.winfo_width()) // 2
        y = (self.window.winfo_screenheight() - self.window.winfo_height()) // 2
        self.window.geometry(f"+{x}+{y}")
        
        self.window.resizable(False, False)
    
    def setup_form(self):
        """Configurer le formulaire avec tous les champs"""
        # Frame principal scrollable
        self.main_frame = ctk.CTkScrollableFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titre
        title_text = "✏️ Modifier la règle" if self.mode == "edit" else "➕ Nouvelle Règle d'Avancement"
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text=title_text,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(0, 30))
        
        # Sections du formulaire
        self.create_basic_info_section()
        self.create_conditions_section()
        self.create_diplomes_section()
        self.create_notes_section()
        self.create_special_conditions_section()
        self.create_buttons_section()
    
    def create_basic_info_section(self):
        """Section Informations de base"""
        section_frame = ctk.CTkFrame(self.main_frame)
        section_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section_frame,
            text="📋 Informations de Base",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        fields_frame = ctk.CTkFrame(section_frame)
        fields_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Catégorie
        self.create_dropdown_field(fields_frame, 0, "Catégorie *", "categorie", self.categories)
        
        # Grade source
        self.create_dropdown_field(fields_frame, 1, "Grade source *", "grade_source", GRADES_HIERARCHY)
        
        # Grade cible
        self.create_dropdown_field(fields_frame, 2, "Grade cible *", "grade_cible", GRADES_HIERARCHY)
        
        # Type d'avancement
        self.create_dropdown_field(fields_frame, 3, "Type d'avancement *", "type_avancement", self.types_avancement)
        
        # Statut
        self.create_dropdown_field(fields_frame, 4, "Statut", "statut", ["Actif", "Inactif", "Test"])
    
    def create_conditions_section(self):
        """Section Conditions d'ancienneté"""
        section_frame = ctk.CTkFrame(self.main_frame)
        section_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section_frame,
            text="⏱️ Conditions d'Ancienneté",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        fields_frame = ctk.CTkFrame(section_frame)
        fields_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Ancienneté service
        self.create_slider_field(fields_frame, 0, "Ancienneté service (années)", "anciennete_service", 0, 30)
        
        # Ancienneté grade
        self.create_slider_field(fields_frame, 1, "Ancienneté grade (années)", "anciennete_grade", 0, 15)
        
        # Ancienneté dans grade spécifique
        ctk.CTkLabel(fields_frame, text="Grade spécifique (optionnel):", width=200).grid(row=2, column=0, padx=10, pady=8, sticky="w")
        self.field_grade_specifique = ctk.CTkComboBox(
            fields_frame, 
            values=["Aucun"] + GRADES_HIERARCHY, 
            width=250
        )
        self.field_grade_specifique.set("Aucun")
        self.field_grade_specifique.grid(row=2, column=1, padx=10, pady=8, sticky="w")
        
        # Ancienneté dans ce grade spécifique
        self.create_slider_field(fields_frame, 3, "Ancienneté dans grade spécifique (années)", "anciennete_grade_specifique", 0, 15)
    
    def create_diplomes_section(self):
        """Section Diplômes requis"""
        section_frame = ctk.CTkFrame(self.main_frame)
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Header
        header_frame = ctk.CTkFrame(section_frame)
        header_frame.pack(fill="x", pady=15, padx=20)
        
        ctk.CTkLabel(
            header_frame,
            text="🎓 Diplômes Requis",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Container pour la sélection
        diplomes_frame = ctk.CTkFrame(section_frame)
        diplomes_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Liste déroulante pour ajouter des diplômes
        selection_frame = ctk.CTkFrame(diplomes_frame)
        selection_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(selection_frame, text="Ajouter un diplôme:", width=150).pack(side="left", padx=10)
        
        self.diplome_combo = ctk.CTkComboBox(
            selection_frame,
            values=self.diplomes_disponibles,
            width=300
        )
        self.diplome_combo.pack(side="left", padx=5)
        
        add_diplome_btn = ctk.CTkButton(
            selection_frame,
            text="➕ Ajouter",
            width=100,
            command=self.add_diplome
        )
        add_diplome_btn.pack(side="left", padx=5)
        
        # Frame pour afficher les diplômes sélectionnés
        self.diplomes_list_frame = ctk.CTkFrame(diplomes_frame)
        self.diplomes_list_frame.pack(fill="x", pady=10, padx=10)
        
        self.update_diplomes_display()
    
    def add_diplome(self):
        """Ajouter un diplôme à la liste"""
        diplome = self.diplome_combo.get()
        if diplome and diplome not in self.diplomes_selectionnes:
            self.diplomes_selectionnes.append(diplome)
            self.update_diplomes_display()
    
    def remove_diplome(self, diplome):
        """Retirer un diplôme de la liste"""
        if diplome in self.diplomes_selectionnes:
            self.diplomes_selectionnes.remove(diplome)
            self.update_diplomes_display()
    
    def update_diplomes_display(self):
        """Mettre à jour l'affichage des diplômes sélectionnés"""
        # Nettoyer le frame
        for widget in self.diplomes_list_frame.winfo_children():
            widget.destroy()
        
        if not self.diplomes_selectionnes:
            ctk.CTkLabel(
                self.diplomes_list_frame,
                text="Aucun diplôme requis",
                text_color="gray"
            ).pack(pady=10)
        else:
            for diplome in self.diplomes_selectionnes:
                diplome_row = ctk.CTkFrame(self.diplomes_list_frame)
                diplome_row.pack(fill="x", pady=3)
                
                ctk.CTkLabel(
                    diplome_row,
                    text=f"✓ {diplome}",
                    font=ctk.CTkFont(size=12)
                ).pack(side="left", padx=10)
                
                remove_btn = ctk.CTkButton(
                    diplome_row,
                    text="❌",
                    width=30,
                    height=25,
                    command=lambda d=diplome: self.remove_diplome(d)
                )
                remove_btn.pack(side="right", padx=10)
    
    def create_notes_section(self):
        """Section Notes requises"""
        section_frame = ctk.CTkFrame(self.main_frame)
        section_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section_frame,
            text="📊 Conditions de Notes",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        fields_frame = ctk.CTkFrame(section_frame)
        fields_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Note minimum année courante
        self.create_dropdown_field(fields_frame, 0, "Note minimum année courante", "note_min_courante", ["Aucune"] + self.notes_disponibles)
        
        # Interdiction notes N-1 et N-2
        ctk.CTkLabel(fields_frame, text="Notes interdites N-1, N-2:", width=200).grid(row=1, column=0, padx=10, pady=8, sticky="w")
        
        notes_frame = ctk.CTkFrame(fields_frame)
        notes_frame.grid(row=1, column=1, padx=10, pady=8, sticky="w")
        
        # Checkboxes pour notes interdites
        self.interdiction_checkboxes = {}
        for i, note in enumerate(self.notes_disponibles):
            var = ctk.BooleanVar(value=False)
            checkbox = ctk.CTkCheckBox(notes_frame, text=note, variable=var, width=60)
            checkbox.grid(row=0, column=i, padx=5)
            self.interdiction_checkboxes[note] = var
    
    def create_special_conditions_section(self):
        """Section Conditions spéciales"""
        section_frame = ctk.CTkFrame(self.main_frame)
        section_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section_frame,
            text="📝 Conditions Spéciales",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        fields_frame = ctk.CTkFrame(section_frame)
        fields_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Zone de texte pour conditions spéciales
        ctk.CTkLabel(
            fields_frame,
            text="Conditions additionnelles (optionnel):",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.field_conditions_speciales = ctk.CTkTextbox(
            fields_frame,
            height=100,
            width=800
        )
        self.field_conditions_speciales.pack(padx=10, pady=(0, 10))
        
        # Exemples
        exemples_text = "Exemples: Pratique langue étrangère, Commandement effectif, Bonne conduite, etc."
        ctk.CTkLabel(
            fields_frame,
            text=exemples_text,
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(anchor="w", padx=10, pady=(0, 10))
    
    def create_buttons_section(self):
        """Section des boutons d'action"""
        buttons_frame = ctk.CTkFrame(self.main_frame)
        buttons_frame.pack(fill="x", pady=20)
        
        buttons_grid = ctk.CTkFrame(buttons_frame)
        buttons_grid.pack(pady=15)
        
        # Bouton Sauvegarder
        save_text = "💾 Modifier" if self.mode == "edit" else "💾 Créer Règle"
        save_btn = ctk.CTkButton(
            buttons_grid,
            text=save_text,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.save_rule
        )
        save_btn.grid(row=0, column=0, padx=15)
        
        # Bouton Annuler
        cancel_btn = ctk.CTkButton(
            buttons_grid,
            text="❌ Annuler",
            width=150,
            height=40,
            command=self.window.destroy
        )
        cancel_btn.grid(row=0, column=1, padx=15)
    
    def create_dropdown_field(self, parent, row, label, field_name, options):
        """Créer un champ dropdown"""
        ctk.CTkLabel(parent, text=label, width=200).grid(row=row, column=0, padx=10, pady=8, sticky="w")
        
        combo = ctk.CTkComboBox(parent, values=options, width=250)
        if options:
            combo.set(options[0])
        combo.grid(row=row, column=1, padx=10, pady=8, sticky="w")
        
        setattr(self, f"field_{field_name}", combo)
        return combo
    
    def create_slider_field(self, parent, row, label, field_name, min_val, max_val):
        """Créer un champ avec slider"""
        ctk.CTkLabel(parent, text=label, width=200).grid(row=row, column=0, padx=10, pady=8, sticky="w")
        
        slider_frame = ctk.CTkFrame(parent)
        slider_frame.grid(row=row, column=1, padx=10, pady=8, sticky="w")
        
        slider = ctk.CTkSlider(slider_frame, from_=min_val, to=max_val, width=200)
        slider.set(0)
        slider.pack(side="left", padx=5)
        
        value_label = ctk.CTkLabel(slider_frame, text="0 ans", width=60)
        value_label.pack(side="left", padx=5)
        
        def update_label(value):
            value_label.configure(text=f"{int(value)} ans")
        
        slider.configure(command=update_label)
        
        setattr(self, f"field_{field_name}", slider)
        setattr(self, f"label_{field_name}", value_label)
        
        return slider
    
    def populate_form(self):
        """Remplir le formulaire avec les données existantes (mode édition)"""
        if not self.rule_data:
            return
        
        # Champs simples
        simple_fields = [
            'categorie', 'grade_source', 'grade_cible', 
            'type_avancement', 'statut'
        ]
        
        for field in simple_fields:
            widget = getattr(self, f"field_{field}", None)
            if widget and field in self.rule_data:
                value = self.rule_data[field]
                if hasattr(widget, 'set'):
                    widget.set(str(value))
        
        # Sliders d'ancienneté
        if self.rule_data.get('anciennete_service_min'):
            self.field_anciennete_service.set(self.rule_data['anciennete_service_min'])
            self.label_anciennete_service.configure(text=f"{self.rule_data['anciennete_service_min']} ans")
        
        if self.rule_data.get('anciennete_grade_min'):
            self.field_anciennete_grade.set(self.rule_data['anciennete_grade_min'])
            self.label_anciennete_grade.configure(text=f"{self.rule_data['anciennete_grade_min']} ans")
        
        if self.rule_data.get('anciennete_grade_specifique'):
            self.field_anciennete_grade_specifique.set(self.rule_data['anciennete_grade_specifique'])
            self.label_anciennete_grade_specifique.configure(text=f"{self.rule_data['anciennete_grade_specifique']} ans")
        
        # Grade spécifique
        if self.rule_data.get('grade_specifique'):
            self.field_grade_specifique.set(self.rule_data['grade_specifique'])
        
        # Diplômes requis
        if self.rule_data.get('diplomes_requis'):
            self.diplomes_selectionnes = self.rule_data['diplomes_requis'].copy()
            self.update_diplomes_display()
        
        # Note minimum courante
        if self.rule_data.get('note_min_courante'):
            self.field_note_min_courante.set(self.rule_data['note_min_courante'])
        else:
            self.field_note_min_courante.set("Aucune")
        
        # Notes interdites
        if self.rule_data.get('notes_interdites_n1_n2'):
            for note in self.rule_data['notes_interdites_n1_n2']:
                if note in self.interdiction_checkboxes:
                    self.interdiction_checkboxes[note].set(True)
        
        # Conditions spéciales
        if self.rule_data.get('conditions_speciales'):
            self.field_conditions_speciales.delete("1.0", "end")
            self.field_conditions_speciales.insert("1.0", self.rule_data['conditions_speciales'])
    
    def validate_form(self):
        """Valider les données du formulaire"""
        errors = []
        
        # Champs obligatoires
        if not self.field_categorie.get():
            errors.append("La catégorie est obligatoire")
        
        if not self.field_grade_source.get():
            errors.append("Le grade source est obligatoire")
        
        if not self.field_grade_cible.get():
            errors.append("Le grade cible est obligatoire")
        
        # Vérifier que grade source != grade cible
        if self.field_grade_source.get() == self.field_grade_cible.get():
            errors.append("Le grade source et cible doivent être différents")
        
        return errors
    
    def collect_form_data(self):
        """Collecter toutes les données du formulaire"""
        # Notes interdites
        notes_interdites = [note for note, var in self.interdiction_checkboxes.items() if var.get()]
        
        data = {
            'categorie': self.field_categorie.get(),
            'grade_source': self.field_grade_source.get(),
            'grade_cible': self.field_grade_cible.get(),
            'type_avancement': self.field_type_avancement.get(),
            'statut': self.field_statut.get(),
            'anciennete_service_min': int(self.field_anciennete_service.get()),
            'anciennete_grade_min': int(self.field_anciennete_grade.get()),
            'grade_specifique': self.field_grade_specifique.get() if self.field_grade_specifique.get() != "Aucun" else None,
            'anciennete_grade_specifique': int(self.field_anciennete_grade_specifique.get()),
            'diplomes_requis': self.diplomes_selectionnes,
            'note_min_courante': self.field_note_min_courante.get() if self.field_note_min_courante.get() != "Aucune" else None,
            'notes_interdites_n1_n2': notes_interdites,
            'conditions_speciales': self.field_conditions_speciales.get("1.0", "end-1c").strip()
        }
        
        return data
    
    def save_rule(self):
        """Sauvegarder la règle"""
        # Validation
        errors = self.validate_form()
        if errors:
            error_message = "Erreurs de validation :\n\n" + "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("Erreurs de validation", error_message)
            return
        
        # Collecter les données
        form_data = self.collect_form_data()
        
        try:
            from core.database import db_manager
            
            if self.mode == "create":
                # Créer une nouvelle règle
                rule_id = db_manager.create_rule(form_data)
                
                if rule_id:
                    messagebox.showinfo(
                        "Succès",
                        f"Règle créée avec succès !\n\n"
                        f"ID: {rule_id}\n"
                        f"Grade: {form_data['grade_source']} → {form_data['grade_cible']}\n"
                        f"Type: {form_data['type_avancement']}\n"
                        f"Catégorie: {form_data['categorie']}\n"
                        f"Ancienneté service: {form_data['anciennete_service_min']} ans\n"
                        f"Diplômes requis: {', '.join(form_data['diplomes_requis']) if form_data['diplomes_requis'] else 'Aucun'}"
                    )
                    self.window.destroy()
                    
                    # Rafraîchir la vue des règles
                    if hasattr(self.app, 'current_page') and self.app.current_page == "rules":
                        self.app.navigate_to("rules")
                else:
                    messagebox.showerror("Erreur", "Erreur lors de la création de la règle")
            
            else:  # mode edit
                # Modifier la règle existante
                success = db_manager.update_rule(self.rule_data['id'], form_data)
                if success:
                    messagebox.showinfo("Succès", "Règle modifiée avec succès !")
                    self.window.destroy()
                    
                    # Rafraîchir la vue
                    if hasattr(self.app, 'current_page') and self.app.current_page == "rules":
                        self.app.navigate_to("rules")
                else:
                    messagebox.showerror("Erreur", "Erreur lors de la modification")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {str(e)}")

def show_rule_form(app, rule_data=None, mode="create"):
    """Fonction utilitaire pour afficher le formulaire"""
    return RuleForm(app, rule_data, mode)