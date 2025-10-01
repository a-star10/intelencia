"""
Popup details agent - VERSION MISE À JOUR
gui/components/agent_popup.py
"""
import customtkinter as ctk

def show_agent_popup(app, agent):
    """Afficher une popup avec les détails de l'agent"""
    popup = ctk.CTkToplevel(app.root)
    popup.title(f"Détails - {agent.get('nom', '')} {agent.get('prenom', '')}")
    popup.geometry("600x700")
    popup.transient(app.root)
    popup.grab_set()
    
    # Centrer la popup
    popup.update_idletasks()
    x = (popup.winfo_screenwidth() - popup.winfo_width()) // 2
    y = (popup.winfo_screenheight() - popup.winfo_height()) // 2
    popup.geometry(f"+{x}+{y}")
    
    # Contenu scrollable
    scroll_frame = ctk.CTkScrollableFrame(popup)
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Titre
    title_label = ctk.CTkLabel(
        scroll_frame,
        text=f"👤 {agent.get('nom', '')} {agent.get('prenom', '')}",
        font=ctk.CTkFont(size=20, weight="bold")
    )
    title_label.pack(pady=(0, 20))
    
    # Résultat d'évaluation en haut
    if agent.get('resultat_evaluation'):
        eval_frame = ctk.CTkFrame(scroll_frame)
        eval_frame.pack(fill="x", pady=(0, 20))
        
        eval_title = ctk.CTkLabel(
            eval_frame,
            text="🎯 Résultat d'Évaluation",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        eval_title.pack(pady=(15, 5))
        
        # Coloration selon le résultat
        eval_text = agent.get('resultat_evaluation', 'Non évalué')
        if 'Proposable' in eval_text and 'Non' not in eval_text:
            eval_color = "#16a34a"
        elif 'Bientot' in eval_text:
            eval_color = "#eab308"
        elif 'Non proposable' in eval_text:
            eval_color = "#dc2626"
        else:
            eval_color = "gray"
        
        eval_label = ctk.CTkLabel(
            eval_frame,
            text=eval_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=eval_color
        )
        eval_label.pack(pady=(0, 15))
    
    # Informations organisées par section
    sections = [
        ("📋 Informations Générales", [
            ("Matricule", agent.get('matricule', '')),
            ("Statut", agent.get('statut', '')),
            ("Date de naissance", agent.get('date_naissance', '')),
            ("Âge", f"{agent.get('age') or 0} ans"),
            ("École", agent.get('ecole', ''))
        ]),
        ("🎖️ Carrière Militaire", [
            ("Grade actuel", agent.get('grade_actuel', '')),
            ("Date d'incorporation", agent.get('date_incorporation', '')),
            ("Date entrée grade", agent.get('date_entree_grade', '')),
            ("Ancienneté service", f"{agent.get('anciennete_service') or 0:.1f} années"),
            ("Ancienneté grade", f"{agent.get('anciennete_grade') or 0:.1f} années"),
            ("Unité de provenance", agent.get('unite_provenance', ''))
        ]),
        ("📊 Évaluations", [
            ("Note année -2", agent.get('note_annee_moins_2', '')),
            ("Note année -1", agent.get('note_annee_moins_1', '')),
            ("Note année courante", agent.get('note_annee_courante', '')),
            ("Statut disciplinaire", agent.get('statut_disciplinaire', ''))
        ])
    ]
    
    for section_title, section_data in sections:
        # Titre de section
        section_frame = ctk.CTkFrame(scroll_frame)
        section_frame.pack(fill="x", pady=(10, 5))
        
        ctk.CTkLabel(
            section_frame,
            text=section_title,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        # Données de la section
        for label, value in section_data:
            info_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
            info_frame.pack(fill="x", padx=20, pady=2)
            
            ctk.CTkLabel(
                info_frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                info_frame,
                text=str(value) if value else "Non renseigné",
                font=ctk.CTkFont(size=12),
                anchor="w"
            ).pack(side="right")
    
    # Diplômes si disponibles
    if agent.get('diplomes'):
        diplomes_frame = ctk.CTkFrame(scroll_frame)
        diplomes_frame.pack(fill="x", pady=(10, 5))
        
        ctk.CTkLabel(
            diplomes_frame,
            text="🎓 Diplômes",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        for diplome in agent['diplomes']:
            diplome_info = ctk.CTkFrame(diplomes_frame, fg_color="transparent")
            diplome_info.pack(fill="x", padx=20, pady=2)
            
            ctk.CTkLabel(
                diplome_info,
                text=f"• {diplome.get('diplome', '')} ({diplome.get('date_obtention', '')})",
                font=ctk.CTkFont(size=11),
                anchor="w"
            ).pack(side="left")
    
    # Boutons d'action
    buttons_frame = ctk.CTkFrame(scroll_frame)
    buttons_frame.pack(fill="x", pady=20)
    
    buttons_grid = ctk.CTkFrame(buttons_frame)
    buttons_grid.pack(pady=10)
    
    # Bouton Modifier - CONNECTÉ AU FORMULAIRE
    modify_btn = ctk.CTkButton(
        buttons_grid,
        text="✏️ Modifier",
        command=lambda: modify_agent(app, popup, agent),
        width=120
    )
    modify_btn.grid(row=0, column=0, padx=10, pady=10)
    
    # Bouton Évaluer
    evaluate_btn = ctk.CTkButton(
        buttons_grid,
        text="🎯 Re-évaluer",
        command=lambda: reevaluate_agent(popup, agent),
        width=120
    )
    evaluate_btn.grid(row=0, column=1, padx=10, pady=10)
    
    # Bouton Fermer
    close_btn = ctk.CTkButton(
        buttons_grid,
        text="Fermer",
        command=popup.destroy,
        width=120
    )
    close_btn.grid(row=0, column=2, padx=10, pady=10)

def modify_agent(app, popup, agent):
    """Modifier un agent - NOUVELLE VERSION"""
    try:
        from gui.components.agent_form import show_agent_form
        
        # Fermer la popup actuelle
        popup.destroy()
        
        # Ouvrir le formulaire en mode édition
        show_agent_form(app, agent_data=agent, mode="edit")
        
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du formulaire: {e}")

def reevaluate_agent(popup, agent):
    """Re-évaluer un agent"""
    try:
        from core.evaluator import evaluator
        from core.models import Agent
        from core.database import db_manager
        from tkinter import messagebox
        
        # Convertir et évaluer
        agent_obj = Agent.from_dict(agent)
        resultat = evaluator.evaluer_agent(agent_obj)
        
        # Sauvegarder
        if resultat.statut == "proposable":
            status_text = "Proposable"
        elif resultat.statut == "bientot":
            status_text = "Bientot proposable"
        else:
            status_text = "Non proposable"
        
        resultat_text = f"{status_text} {resultat.type_avancement} -> {resultat.grade_cible}"
        
        db_manager.update_agent(agent['id'], {
            'resultat_evaluation': resultat_text
        })
        
        messagebox.showinfo("Succès", f"Agent ré-évalué:\n{resultat_text}")
        popup.destroy()
        
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Erreur", f"Erreur lors de la ré-évaluation: {e}")