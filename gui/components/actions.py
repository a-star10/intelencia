"""
Actions et callbacks - VERSION MISE À JOUR
gui/components/actions.py
"""
from tkinter import messagebox

def quick_add_agent(app):
    """Action rapide : ajouter un agent depuis le dashboard"""
    try:
        from gui.components.agent_form import show_agent_form
        show_agent_form(app, mode="create")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du formulaire: {e}")

def quick_evaluate_all(app):
    """Action rapide : evaluer tous les agents"""
    try:
        from core.evaluator import evaluator
        
        # Confirmer avec l'utilisateur
        response = messagebox.askyesno(
            "Confirmation", 
            "Voulez-vous evaluer tous les agents?\n\nCela peut prendre quelques secondes."
        )
        
        if response:
            # Lancer l'evaluation
            resultats = evaluator.evaluer_tous_agents()
            
            # Compter les resultats
            proposables = len([r for r in resultats if r.statut == "proposable"])
            bientot = len([r for r in resultats if r.statut == "bientot"])
            non_proposables = len([r for r in resultats if r.statut == "non_proposable"])
            
            messagebox.showinfo(
                "Evaluation terminee", 
                f"Evaluation de {len(resultats)} agents terminee:\n\n"
                f"• {proposables} agent(s) proposable(s)\n"
                f"• {bientot} agent(s) bientot proposable(s)\n"
                f"• {non_proposables} agent(s) non proposable(s)\n\n"
                f"Allez dans 'Agents' et cliquez 'Actualiser' pour voir les resultats."
            )
    
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'evaluation: {e}")

def quick_generate_report(app):
    """Action rapide : generer un rapport"""
    messagebox.showinfo("Info", "Prochaine etape de developpement !\n\nGeneration de rapports en cours de creation...")

def quick_import_excel(app):
    """Action rapide : importer depuis Excel"""
    messagebox.showinfo("Info", "Prochaine etape de developpement !\n\nImport/Export Excel en cours de creation...")

def add_new_agent(app):
    """Ajouter un nouvel agent - VERSION COMPLETE"""
    try:
        from gui.components.agent_form import show_agent_form
        show_agent_form(app, mode="create")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du formulaire: {e}")

def export_agents(app):
    """Exporter les agents"""
    try:
        from core.database import db_manager
        import pandas as pd
        from pathlib import Path
        
        # Recuperer les agents
        agents_data = db_manager.get_all_agents()
        
        if not agents_data:
            messagebox.showwarning("Attention", "Aucun agent a exporter")
            return
        
        # Convertir en DataFrame pandas
        df_data = []
        for agent in agents_data:
            df_data.append({
                'Matricule': agent.get('matricule', ''),
                'Nom': agent.get('nom', ''),
                'Prenom': agent.get('prenom', ''),
                'Grade': agent.get('grade_actuel', ''),
                'Age': agent.get('age', ''),
                'Anciennete_Service': agent.get('anciennete_service', ''),
                'Anciennete_Grade': agent.get('anciennete_grade', ''),
                'Note_Courante': agent.get('note_annee_courante', ''),
                'Note_N-1': agent.get('note_annee_moins_1', ''),
                'Note_N-2': agent.get('note_annee_moins_2', ''),
                'Statut_Disciplinaire': agent.get('statut_disciplinaire', ''),
                'Unite': agent.get('unite_provenance', ''),
                'Resultat_Evaluation': agent.get('resultat_evaluation', '')
            })
        
        df = pd.DataFrame(df_data)
        
        # Sauvegarder en Excel
        export_path = Path("data/exports/agents_export.xlsx")
        export_path.parent.mkdir(exist_ok=True)
        
        df.to_excel(export_path, index=False, sheet_name="Agents")
        
        messagebox.showinfo(
            "Export reussi", 
            f"Export Excel termine !\n\nFichier sauvegarde :\n{export_path.absolute()}\n\n{len(agents_data)} agents exportes"
        )
    
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")

def import_agents(app):
    """Importer des agents"""
    messagebox.showinfo("Info", "Fonctionnalite en developpement\n\nImport Excel bientot disponible!")

def modify_agent(app, agent_data):
    """Modifier un agent existant"""
    try:
        from gui.components.agent_form import show_agent_form
        show_agent_form(app, agent_data=agent_data, mode="edit")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du formulaire: {e}")