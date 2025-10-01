"""
Formulaire d'ajout/modification d'agent - VERSION CORRIGÉE
gui/components/agent_form.py
"""
import customtkinter as ctk
from datetime import date, datetime
from tkinter import messagebox
import re
import sys
from pathlib import Path

# Imports du projet
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import GRADES_HIERARCHY, STATUTS_AGENT
from core.database import db_manager
from core.models import Agent, Diplome

class AgentForm:
    """Formulaire complet pour créer/modifier un agent"""
    
    def __init__(self, parent_app, agent_data=None, mode="create"):
        self.app = parent_app
        self.agent_data = agent_data
        self.mode = mode  # "create" ou "edit"
        self.diplomes_list = []  # Liste des diplômes temporaires
        
        self.create_form_window()
        self.setup_form()
        
        if mode == "edit" and agent_data:
            self.populate_form()
    
    def create_form_window(self):
        """Créer la fenêtre de formulaire"""
        title = "Modifier l'agent" if self.mode == "edit" else "Nouvel Agent"
        
        self.window = ctk.CTkToplevel(self.app.root)
        self.window.title(title)
        self.window.geometry("800x900")
        self.window.transient(self.app.root)
        self.window.grab_set()
        
        # Centrer la fenêtre
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - self.window.winfo_width()) // 2
        y = (self.window.winfo_screenheight() - self.window.winfo_height()) // 2
        self.window.geometry(f"+{x}+{y}")
        
        # Empêcher le redimensionnement
        self.window.resizable(False, False)
    
    def setup_form(self):
        """Configurer le formulaire avec tous les champs"""
        # Frame principal scrollable
        self.main_frame = ctk.CTkScrollableFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titre
        title_text = "✏️ Modifier l'agent" if self.mode == "edit" else "➕ Nouvel Agent"
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text=title_text,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(0, 30))
        
        # Sections du formulaire
        self.create_identity_section()
        self.create_career_section()
        self.create_evaluation_section()
        self.create_diplomes_section()
        self.create_buttons_section()
    
    def create_identity_section(self):
        """Section Identité"""
        section_frame = ctk.CTkFrame(self.main_frame)
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Titre de section
        ctk.CTkLabel(
            section_frame,
            text="👤 Informations Personnelles",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        # Grid pour les champs
        fields_frame = ctk.CTkFrame(section_frame)
        fields_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Matricule (obligatoire)
        self.create_field_row(fields_frame, 0, "Matricule *", "matricule", placeholder="MT123456")
        
        # Nom et Prénom
        self.create_field_row(fields_frame, 1, "Nom *", "nom", placeholder="Dupont")
        self.create_field_row(fields_frame, 2, "Prénom *", "prenom", placeholder="Jean")
        
        # Date de naissance
        self.create_date_field(fields_frame, 3, "Date de naissance *", "date_naissance")
        
        # Statut
        self.create_dropdown_field(fields_frame, 4, "Statut", "statut", STATUTS_AGENT)
    
    def create_career_section(self):
        """Section Carrière"""
        section_frame = ctk.CTkFrame(self.main_frame)
        section_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section_frame,
            text="🎖️ Carrière Militaire",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        fields_frame = ctk.CTkFrame(section_frame)
        fields_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Grade actuel
        self.create_dropdown_field(fields_frame, 0, "Grade actuel *", "grade_actuel", GRADES_HIERARCHY)
        
        # Dates importantes
        self.create_date_field(fields_frame, 1, "Date d'incorporation *", "date_incorporation")
        self.create_date_field(fields_frame, 2, "Date d'entrée dans le grade *", "date_entree_grade")
        
        # École et unité
        self.create_field_row(fields_frame, 3, "École de formation", "ecole", placeholder="École Militaire de Saint-Cyr")
        self.create_field_row(fields_frame, 4, "Unité de provenance", "unite_provenance", placeholder="1er Régiment d'Infanterie")
    
    def create_evaluation_section(self):
        """Section Évaluations"""
        section_frame = ctk.CTkFrame(self.main_frame)
        section_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section_frame,
            text="📊 Évaluations",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        fields_frame = ctk.CTkFrame(section_frame)
        fields_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        notes_options = ["TB", "B", "AB", "P", "I"]
        
        # Notes des 3 dernières années
        self.create_dropdown_field(fields_frame, 0, "Note année N-2", "note_annee_moins_2", notes_options)
        self.create_dropdown_field(fields_frame, 1, "Note année N-1", "note_annee_moins_1", notes_options)
        self.create_dropdown_field(fields_frame, 2, "Note année courante", "note_annee_courante", notes_options)
        
        # Statut disciplinaire
        statuts_disciplinaires = ["RAS", "Avertissement", "Blâme", "Punition", "En observation"]
        self.create_dropdown_field(fields_frame, 3, "Statut disciplinaire", "statut_disciplinaire", statuts_disciplinaires)
    
    def create_diplomes_section(self):
        """Section Diplômes avec gestion dynamique"""
        self.diplomes_section = ctk.CTkFrame(self.main_frame)
        self.diplomes_section.pack(fill="x", pady=(0, 20))
        
        # Header avec bouton d'ajout
        header_frame = ctk.CTkFrame(self.diplomes_section)
        header_frame.pack(fill="x", pady=15, padx=20)
        
        ctk.CTkLabel(
            header_frame,
            text="🎓 Diplômes",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        add_diplome_btn = ctk.CTkButton(
            header_frame,
            text="➕ Ajouter diplôme",
            width=120,
            height=28,
            command=self.add_diplome_entry
        )
        add_diplome_btn.pack(side="right")
        
        # Container pour la liste des diplômes
        self.diplomes_container = ctk.CTkFrame(self.diplomes_section)
        self.diplomes_container.pack(fill="x", padx=20, pady=(0, 20))
        
        # Ajouter un diplôme par défaut
        self.add_diplome_entry()
    
    def add_diplome_entry(self):
        """Ajouter une ligne de diplôme"""
        diplome_frame = ctk.CTkFrame(self.diplomes_container)
        diplome_frame.pack(fill="x", pady=5)
        
        # Index du diplôme
        diplome_index = len(self.diplomes_list)
        
        # Champs du diplôme
        fields_grid = ctk.CTkFrame(diplome_frame)
        fields_grid.pack(fill="x", padx=10, pady=10)
        
        # Nom du diplôme
        ctk.CTkLabel(fields_grid, text="Diplôme:", width=80).grid(row=0, column=0, padx=5, sticky="w")
        diplome_nom = ctk.CTkEntry(fields_grid, placeholder_text="Ex: C.M.1", width=150)
        diplome_nom.grid(row=0, column=1, padx=5)
        
        # Date d'obtention
        ctk.CTkLabel(fields_grid, text="Date:", width=60).grid(row=0, column=2, padx=5, sticky="w")
        
        # Année
        diplome_annee = ctk.CTkEntry(fields_grid, placeholder_text="2020", width=80)
        diplome_annee.grid(row=0, column=3, padx=2)
        
        # Mois
        diplome_mois = ctk.CTkComboBox(fields_grid, values=[f"{i:02d}" for i in range(1, 13)], width=60)
        diplome_mois.set("01")
        diplome_mois.grid(row=0, column=4, padx=2)
        
        # Jour
        diplome_jour = ctk.CTkComboBox(fields_grid, values=[f"{i:02d}" for i in range(1, 32)], width=60)
        diplome_jour.set("01")
        diplome_jour.grid(row=0, column=5, padx=2)
        
        # Établissement
        ctk.CTkLabel(fields_grid, text="École:", width=60).grid(row=0, column=6, padx=5, sticky="w")
        diplome_etablissement = ctk.CTkEntry(fields_grid, placeholder_text="École Militaire", width=150)
        diplome_etablissement.grid(row=0, column=7, padx=5)
        
        # Bouton supprimer
        remove_btn = ctk.CTkButton(
            fields_grid,
            text="🗑️",
            width=30,
            height=28,
            command=lambda: self.remove_diplome_entry(diplome_frame, diplome_index)
        )
        remove_btn.grid(row=0, column=8, padx=5)
        
        # Stocker les références
        diplome_data = {
            'frame': diplome_frame,
            'nom': diplome_nom,
            'annee': diplome_annee,
            'mois': diplome_mois,
            'jour': diplome_jour,
            'etablissement': diplome_etablissement,
            'index': diplome_index
        }
        
        self.diplomes_list.append(diplome_data)
    
    def remove_diplome_entry(self, frame, index):
        """Supprimer une ligne de diplôme"""
        frame.destroy()
        # Retirer de la liste
        self.diplomes_list = [d for d in self.diplomes_list if d['index'] != index]
    
    def create_buttons_section(self):
        """Section des boutons d'action"""
        buttons_frame = ctk.CTkFrame(self.main_frame)
        buttons_frame.pack(fill="x", pady=20)
        
        buttons_grid = ctk.CTkFrame(buttons_frame)
        buttons_grid.pack(pady=15)
        
        # Bouton Sauvegarder
        save_text = "💾 Modifier" if self.mode == "edit" else "💾 Créer Agent"
        save_btn = ctk.CTkButton(
            buttons_grid,
            text=save_text,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.save_agent
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
    
    def create_field_row(self, parent, row, label, field_name, placeholder="", width=200):
        """Créer une ligne de champ standard"""
        ctk.CTkLabel(parent, text=label, width=150).grid(row=row, column=0, padx=10, pady=8, sticky="w")
        
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, width=width)
        entry.grid(row=row, column=1, padx=10, pady=8, sticky="w")
        
        # Stocker la référence
        setattr(self, f"field_{field_name}", entry)
        
        return entry
    
    def create_dropdown_field(self, parent, row, label, field_name, options):
        """Créer un champ dropdown"""
        ctk.CTkLabel(parent, text=label, width=150).grid(row=row, column=0, padx=10, pady=8, sticky="w")
        
        combo = ctk.CTkComboBox(parent, values=options, width=200)
        if options:
            combo.set(options[0])
        combo.grid(row=row, column=1, padx=10, pady=8, sticky="w")
        
        setattr(self, f"field_{field_name}", combo)
        return combo
    
    def create_date_field(self, parent, row, label, field_name):
        """Créer un champ de date avec validation et valeurs par défaut"""
        ctk.CTkLabel(parent, text=label, width=150).grid(row=row, column=0, padx=10, pady=8, sticky="w")
        
        date_frame = ctk.CTkFrame(parent)
        date_frame.grid(row=row, column=1, padx=10, pady=8, sticky="w")
        
        # Valeurs par défaut intelligentes
        current_year = date.today().year
        if field_name == 'date_naissance':
            default_year = str(current_year - 25)  # 25 ans par défaut
        elif field_name == 'date_incorporation':
            default_year = str(current_year - 5)   # Il y a 5 ans
        else:  # date_entree_grade
            default_year = str(current_year - 2)   # Il y a 2 ans
        
        # Année
        year_entry = ctk.CTkEntry(date_frame, placeholder_text=default_year, width=60)
        year_entry.pack(side="left", padx=2)
        
        ctk.CTkLabel(date_frame, text="-").pack(side="left")
        
        # Mois
        month_combo = ctk.CTkComboBox(date_frame, values=[f"{i:02d}" for i in range(1, 13)], width=60)
        month_combo.set("01")
        month_combo.pack(side="left", padx=2)
        
        ctk.CTkLabel(date_frame, text="-").pack(side="left")
        
        # Jour
        day_combo = ctk.CTkComboBox(date_frame, values=[f"{i:02d}" for i in range(1, 32)], width=60)
        day_combo.set("01")
        day_combo.pack(side="left", padx=2)
        
        # Stocker les références
        setattr(self, f"field_{field_name}_year", year_entry)
        setattr(self, f"field_{field_name}_month", month_combo)
        setattr(self, f"field_{field_name}_day", day_combo)
    
    def populate_form(self):
        """Remplir le formulaire avec les données existantes (mode édition)"""
        if not self.agent_data:
            return
        
        # Champs simples
        simple_fields = [
            'matricule', 'nom', 'prenom', 'statut', 'grade_actuel',
            'ecole', 'unite_provenance', 'note_annee_moins_2',
            'note_annee_moins_1', 'note_annee_courante', 'statut_disciplinaire'
        ]
        
        for field in simple_fields:
            widget = getattr(self, f"field_{field}", None)
            if widget and field in self.agent_data:
                value = self.agent_data[field]
                if hasattr(widget, 'set'):
                    widget.set(str(value))
                else:
                    widget.delete(0, 'end')
                    widget.insert(0, str(value))
        
        # Dates
        date_fields = ['date_naissance', 'date_incorporation', 'date_entree_grade']
        for field in date_fields:
            if field in self.agent_data and self.agent_data[field]:
                date_str = self.agent_data[field]
                if isinstance(date_str, str):
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                        year_widget = getattr(self, f"field_{field}_year")
                        month_widget = getattr(self, f"field_{field}_month")
                        day_widget = getattr(self, f"field_{field}_day")
                        
                        year_widget.delete(0, 'end')
                        year_widget.insert(0, str(date_obj.year))
                        month_widget.set(f"{date_obj.month:02d}")
                        day_widget.set(f"{date_obj.day:02d}")
                    except:
                        pass
        
        # Diplômes
        if 'diplomes' in self.agent_data and self.agent_data['diplomes']:
            # Supprimer le diplôme par défaut
            if self.diplomes_list:
                self.diplomes_list[0]['frame'].destroy()
                self.diplomes_list.clear()
            
            # Ajouter les diplômes existants
            for diplome in self.agent_data['diplomes']:
                self.add_diplome_entry()
                last_diplome = self.diplomes_list[-1]
                
                # Remplir les champs
                last_diplome['nom'].insert(0, diplome.get('diplome', diplome.get('nom', '')))
                last_diplome['etablissement'].insert(0, diplome.get('etablissement', ''))
                
                # Date
                date_str = diplome.get('date_obtention', '')
                if date_str:
                    try:
                        if isinstance(date_str, str):
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                        else:
                            date_obj = date_str
                        
                        last_diplome['annee'].insert(0, str(date_obj.year))
                        last_diplome['mois'].set(f"{date_obj.month:02d}")
                        last_diplome['jour'].set(f"{date_obj.day:02d}")
                    except:
                        pass
    
    def validate_form(self):
        """Valider les données du formulaire"""
        errors = []
        
        # Champs obligatoires
        required_fields = {
            'matricule': "Le matricule est obligatoire",
            'nom': "Le nom est obligatoire",
            'prenom': "Le prénom est obligatoire",
            'grade_actuel': "Le grade est obligatoire"
        }
        
        for field, error_msg in required_fields.items():
            widget = getattr(self, f"field_{field}")
            value = widget.get().strip()
            if not value:
                errors.append(error_msg)
        
        # Validation du matricule (format)
        matricule = self.field_matricule.get().strip()
        if matricule and not re.match(r"^MT\d{6}$", matricule):
            errors.append("Le matricule doit avoir le format MT123456")
        
        # Vérifier l'unicité du matricule (seulement en mode création)
        if self.mode == "create" and matricule:
            existing_agent = db_manager.get_agent_by_matricule(matricule)
            if existing_agent:
                errors.append("Ce matricule existe déjà")
        
        # Validation des dates OBLIGATOIRES
        required_date_fields = {
            'date_naissance': "La date de naissance est obligatoire",
            'date_incorporation': "La date d'incorporation est obligatoire", 
            'date_entree_grade': "La date d'entrée dans le grade est obligatoire"
        }
        
        for field, error_msg in required_date_fields.items():
            year_widget = getattr(self, f"field_{field}_year")
            year = year_widget.get().strip()
            
            if not year:  # Date obligatoire manquante
                errors.append(error_msg)
            else:  # Valider le format si présent
                try:
                    year_int = int(year)
                    if year_int < 1950 or year_int > date.today().year:
                        errors.append(f"Année invalide pour {field.replace('_', ' ')}")
                except ValueError:
                    errors.append(f"Année invalide pour {field.replace('_', ' ')}")
        
        return errors
    
    def collect_form_data(self):
        """Collecter toutes les données du formulaire"""
        data = {}
        
        # Champs simples
        simple_fields = [
            'matricule', 'nom', 'prenom', 'statut', 'grade_actuel',
            'ecole', 'unite_provenance', 'note_annee_moins_2',
            'note_annee_moins_1', 'note_annee_courante', 'statut_disciplinaire'
        ]
        
        for field in simple_fields:
            widget = getattr(self, f"field_{field}")
            data[field] = widget.get().strip()
        
        # Dates - TOUTES OBLIGATOIRES avec valeurs par défaut intelligentes
        date_fields = ['date_naissance', 'date_incorporation', 'date_entree_grade']
        for field in date_fields:
            year_widget = getattr(self, f"field_{field}_year")
            month_widget = getattr(self, f"field_{field}_month")
            day_widget = getattr(self, f"field_{field}_day")
            
            year = year_widget.get().strip()
            if year:
                try:
                    month = int(month_widget.get())
                    day = int(day_widget.get())
                    date_obj = date(int(year), month, day)
                    data[field] = date_obj.isoformat()
                except (ValueError, TypeError):
                    # En cas d'erreur, utiliser une date par défaut
                    if field == 'date_naissance':
                        data[field] = date(1990, 1, 1).isoformat()
                    elif field == 'date_incorporation':
                        data[field] = date(2010, 1, 1).isoformat()
                    else:  # date_entree_grade
                        data[field] = date(2015, 1, 1).isoformat()
            else:
                # Dates par défaut si vides (ne devrait pas arriver avec la validation)
                if field == 'date_naissance':
                    data[field] = date(1990, 1, 1).isoformat()
                elif field == 'date_incorporation':
                    data[field] = date(2010, 1, 1).isoformat()
                else:  # date_entree_grade
                    data[field] = date(2015, 1, 1).isoformat()
        
        # Diplômes
        diplomes = []
        for diplome_data in self.diplomes_list:
            if diplome_data['frame'].winfo_exists():  # Vérifier que le frame existe encore
                nom = diplome_data['nom'].get().strip()
                if nom:  # Seulement si un nom est saisi
                    try:
                        annee = int(diplome_data['annee'].get())
                        mois = int(diplome_data['mois'].get())
                        jour = int(diplome_data['jour'].get())
                        date_diplome = date(annee, mois, jour)
                        
                        diplomes.append({
                            'nom': nom,
                            'date_obtention': date_diplome.isoformat(),
                            'etablissement': diplome_data['etablissement'].get().strip()
                        })
                    except (ValueError, TypeError):
                        # Ignorer les diplômes avec des dates invalides
                        pass
        
        data['diplomes'] = diplomes
        
        return data
    
    def save_agent(self):
        """Sauvegarder l'agent (création ou modification)"""
        # Validation
        errors = self.validate_form()
        if errors:
            error_message = "Erreurs de validation :\n\n" + "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("Erreurs de validation", error_message)
            return
        
        # Collecter les données
        form_data = self.collect_form_data()
        
        # CALCULER LES CHAMPS AUTOMATIQUES AVANT SAUVEGARDE
        try:
            # Créer un objet Agent temporaire pour calculer les champs
            from core.models import Agent, Diplome
            
            # Convertir les diplômes
            diplomes_objects = []
            for dip_data in form_data.get('diplomes', []):
                diplome = Diplome(
                    nom=dip_data['nom'],
                    date_obtention=datetime.strptime(dip_data['date_obtention'], '%Y-%m-%d').date(),
                    etablissement=dip_data['etablissement']
                )
                diplomes_objects.append(diplome)
            
            # Créer l'agent temporaire
            temp_agent = Agent(
                matricule=form_data['matricule'],
                nom=form_data['nom'],
                prenom=form_data['prenom'],
                date_naissance=datetime.strptime(form_data['date_naissance'], '%Y-%m-%d').date(),
                grade_actuel=form_data['grade_actuel'],
                date_incorporation=datetime.strptime(form_data['date_incorporation'], '%Y-%m-%d').date(),
                date_entree_grade=datetime.strptime(form_data['date_entree_grade'], '%Y-%m-%d').date(),
                ecole=form_data['ecole'],
                note_annee_moins_2=form_data['note_annee_moins_2'],
                note_annee_moins_1=form_data['note_annee_moins_1'],
                note_annee_courante=form_data['note_annee_courante'],
                statut_disciplinaire=form_data['statut_disciplinaire'],
                unite_provenance=form_data['unite_provenance'],
                diplomes=diplomes_objects
            )
            
            # Calculer les champs automatiques
            temp_agent.update_calculated_fields()
            
            # Mettre à jour form_data avec les valeurs calculées
            form_data['age'] = temp_agent.age
            form_data['anciennete_service'] = temp_agent.anciennete_service
            form_data['anciennete_grade'] = temp_agent.anciennete_grade
            
        except Exception as e:
            print(f"Erreur calcul des champs: {e}")
            # Continuer sans les calculs si erreur
        
        try:
            if self.mode == "create":
                # Créer un nouvel agent
                agent_id = db_manager.create_agent(form_data)
                if agent_id:
                    messagebox.showinfo(
                        "Succès",
                        f"Agent {form_data['matricule']} créé avec succès !\n\n"
                        f"ID: {agent_id}\n"
                        f"Nom: {form_data['nom']} {form_data['prenom']}\n"
                        f"Grade: {form_data['grade_actuel']}\n"
                        f"Âge: {form_data.get('age', 'N/A')} ans"
                    )
                    self.window.destroy()
                    
                    # Rafraîchir la vue des agents
                    if hasattr(self.app, 'current_page') and self.app.current_page == "agents":
                        self.app.navigate_to("agents")
                else:
                    messagebox.showerror("Erreur", "Erreur lors de la création de l'agent")
            
            else:  # mode edit
                # Modifier l'agent existant
                success = db_manager.update_agent(self.agent_data['id'], form_data)
                if success:
                    messagebox.showinfo("Succès", "Agent modifié avec succès !")
                    self.window.destroy()
                    
                    # Rafraîchir la vue
                    if hasattr(self.app, 'current_page') and self.app.current_page == "agents":
                        self.app.navigate_to("agents")
                else:
                    messagebox.showerror("Erreur", "Erreur lors de la modification")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {str(e)}")

def show_agent_form(app, agent_data=None, mode="create"):
    """Fonction utilitaire pour afficher le formulaire"""
    return AgentForm(app, agent_data, mode)