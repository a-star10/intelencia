"""
Interface de gestion des utilisateurs (onglet dans Paramètres)
gui/components/users_management.py
"""
import customtkinter as ctk
from tkinter import messagebox, Canvas, Scrollbar, Frame
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from core.auth_manager import auth_manager

def create_users_tab(parent, app):
    """Créer l'onglet de gestion des utilisateurs"""
    
    # Vérifier les permissions
    if not auth_manager.has_permission('*'):
        no_perm = ctk.CTkFrame(parent)
        no_perm.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            no_perm,
            text="🔒 Accès refusé",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=30)
        
        ctk.CTkLabel(
            no_perm,
            text="Vous n'avez pas les permissions nécessaires\npour gérer les utilisateurs.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack()
        
        return
    
    scroll_frame = ctk.CTkScrollableFrame(parent)
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Header
    create_users_header(scroll_frame, app)
    
    # Liste des utilisateurs
    create_users_list(scroll_frame, app)
    
    # Logs d'audit
    create_audit_logs_section(scroll_frame)

def create_users_header(parent, app):
    """Créer le header avec statistiques et boutons"""
    header_frame = ctk.CTkFrame(parent)
    header_frame.pack(fill="x", padx=20, pady=(0, 20))
    
    # Titre et stats
    title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    title_frame.pack(fill="x", padx=20, pady=15)
    
    # Gauche: Titre
    left_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
    left_frame.pack(side="left")
    
    ctk.CTkLabel(
        left_frame,
        text="👥 Gestion des Utilisateurs",
        font=ctk.CTkFont(size=18, weight="bold")
    ).pack(anchor="w")
    
    # Stats
    users = auth_manager.get_all_users()
    active_users = len([u for u in users if u['is_active']])
    
    stats_text = f"{active_users} utilisateur(s) actif(s) • {len(users)} total"
    ctk.CTkLabel(
        left_frame,
        text=stats_text,
        font=ctk.CTkFont(size=11),
        text_color="gray"
    ).pack(anchor="w", pady=(5, 0))
    
    # Droite: Boutons
    right_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
    right_frame.pack(side="right")
    
    ctk.CTkButton(
        right_frame,
        text="➕ Nouvel utilisateur",
        width=160,
        height=38,
        command=lambda: show_create_user_dialog(app)
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        right_frame,
        text="🔄 Actualiser",
        width=120,
        height=38,
        command=lambda: app.navigate_to("settings")
    ).pack(side="left", padx=5)

def create_users_list(parent, app):
    """Créer la liste des utilisateurs"""
    users_frame = ctk.CTkFrame(parent)
    users_frame.pack(fill="x", padx=20, pady=(0, 20))
    
    # Header
    header = ctk.CTkFrame(users_frame, fg_color="transparent")
    header.pack(fill="x", padx=20, pady=15)
    
    ctk.CTkLabel(
        header,
        text="📋 Liste des utilisateurs",
        font=ctk.CTkFont(size=14, weight="bold")
    ).pack(side="left")
    
    # Tableau avec scroll
    canvas_frame = ctk.CTkFrame(users_frame)
    canvas_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    canvas = Canvas(
        canvas_frame,
        bg="#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#ffffff",
        highlightthickness=0,
        height=350
    )
    
    v_scroll = Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    v_scroll.pack(side="right", fill="y")
    
    canvas.pack(side="left", fill="both", expand=True)
    canvas.configure(yscrollcommand=v_scroll.set)
    
    inner = Frame(canvas, bg="#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#ffffff")
    canvas.create_window((0, 0), window=inner, anchor="nw")
    
    # Headers
    headers = [
        ("👤", 50),
        ("Nom d'utilisateur", 150),
        ("Nom complet", 200),
        ("Rôle", 150),
        ("Email", 200),
        ("Dernière connexion", 150),
        ("Statut", 100),
        ("Actions", 150)
    ]
    
    hdr_frame = ctk.CTkFrame(inner)
    hdr_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
    
    for i, (h, w) in enumerate(headers):
        ctk.CTkLabel(
            hdr_frame,
            text=h,
            font=ctk.CTkFont(size=10, weight="bold"),
            width=w
        ).grid(row=0, column=i, padx=2, pady=5)
    
    # Lignes
    users = auth_manager.get_all_users()
    
    for idx, user in enumerate(users):
        bg = ("gray92", "gray17") if idx % 2 == 0 else ("gray97", "gray21")
        
        row = ctk.CTkFrame(inner, fg_color=bg)
        row.grid(row=idx+1, column=0, sticky="ew", pady=2)
        
        # Emoji selon le rôle
        role_emojis = {
            'admin': '👑',
            'manager': '👔',
            'operator': '💼',
            'viewer': '👁️'
        }
        emoji = role_emojis.get(user['role'], '👤')
        
        # Rôle avec couleur
        role_colors = {
            'admin': '#dc2626',
            'manager': '#3b82f6',
            'operator': '#16a34a',
            'viewer': '#6b7280'
        }
        role_color = role_colors.get(user['role'], 'gray')
        
        # Statut
        if user['is_active']:
            status_text = "✅ Actif"
            status_color = "#16a34a"
        else:
            status_text = "❌ Inactif"
            status_color = "#dc2626"
        
        # Dernière connexion
        if user['last_login']:
            try:
                dt = datetime.fromisoformat(user['last_login'])
                last_login = dt.strftime("%d/%m/%Y %H:%M")
            except:
                last_login = user['last_login'][:16]
        else:
            last_login = "Jamais"
        
        data = [
            (emoji, 50, "normal", "gray"),
            (user['username'], 150, "bold", ("gray10", "gray90")),
            (user['full_name'], 200, "normal", ("gray10", "gray90")),
            (auth_manager.ROLES[user['role']]['name'], 150, "bold", role_color),
            (user['email'] or "-", 200, "normal", ("gray10", "gray90")),
            (last_login, 150, "normal", "gray"),
            (status_text, 100, "bold", status_color)
        ]
        
        for i, (val, w, weight, color) in enumerate(data):
            ctk.CTkLabel(
                row,
                text=str(val),
                font=ctk.CTkFont(size=10, weight=weight),
                width=w,
                anchor="w",
                text_color=color,
                height=32
            ).grid(row=0, column=i, padx=2, pady=2)
        
        # Actions
        actions_frame = ctk.CTkFrame(row, fg_color="transparent")
        actions_frame.grid(row=0, column=7, padx=2, pady=2)
        
        ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=35,
            height=28,
            command=lambda u=user: show_edit_user_dialog(app, u)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            actions_frame,
            text="🔑",
            width=35,
            height=28,
            command=lambda u=user: show_reset_password_dialog(u)
        ).pack(side="left", padx=2)
        
        # Ne pas permettre de supprimer son propre compte
        if auth_manager.current_user['id'] != user['id']:
            ctk.CTkButton(
                actions_frame,
                text="🗑️",
                width=35,
                height=28,
                fg_color="#dc2626",
                hover_color="#991b1b",
                command=lambda u=user: delete_user(app, u)
            ).pack(side="left", padx=2)
    
    # Config scroll
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

def create_audit_logs_section(parent):
    """Créer la section des logs d'audit"""
    logs_frame = ctk.CTkFrame(parent)
    logs_frame.pack(fill="x", padx=20, pady=(0, 20))
    
    # Header
    header = ctk.CTkFrame(logs_frame, fg_color="transparent")
    header.pack(fill="x", padx=20, pady=15)
    
    ctk.CTkLabel(
        header,
        text="📜 Logs d'audit (50 dernières actions)",
        font=ctk.CTkFont(size=14, weight="bold")
    ).pack(side="left")
    
    # Liste des logs
    logs_container = ctk.CTkScrollableFrame(logs_frame, height=200)
    logs_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    logs = auth_manager.get_audit_logs(limit=50)
    
    for log in logs:
        log_item = ctk.CTkFrame(logs_container, fg_color=("gray90", "gray25"))
        log_item.pack(fill="x", pady=3)
        
        # Icône selon l'action
        action_emojis = {
            'login_success': '🔓',
            'login_failed': '🔒',
            'logout': '🚪',
            'create_user': '➕',
            'update_user': '✏️',
            'delete_user': '🗑️',
            'change_password': '🔑'
        }
        emoji = action_emojis.get(log['action'], '📝')
        
        # Couleur selon succès
        if log['success']:
            color = "#16a34a" if 'login_success' in log['action'] else ("gray10", "gray90")
        else:
            color = "#dc2626"
        
        # Date
        try:
            dt = datetime.fromisoformat(log['created_at'])
            date_str = dt.strftime("%d/%m/%Y %H:%M:%S")
        except:
            date_str = log['created_at'][:19]
        
        # Texte
        user_name = log.get('username', 'Système')
        action_text = log['action'].replace('_', ' ').title()
        
        text = f"{emoji} {date_str} • {user_name} • {action_text}"
        if log['details']:
            text += f" • {log['details'][:50]}"
        
        ctk.CTkLabel(
            log_item,
            text=text,
            font=ctk.CTkFont(size=10),
            text_color=color,
            anchor="w"
        ).pack(fill="x", padx=10, pady=8)

# ==================== DIALOGUES ====================

def show_create_user_dialog(app):
    """Dialogue de création d'utilisateur"""
    dialog = ctk.CTkToplevel(app.root)
    dialog.title("Nouvel utilisateur")
    dialog.geometry("500x600")
    dialog.transient(app.root)
    dialog.grab_set()
    
    # Centrer
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() - 500) // 2
    y = (dialog.winfo_screenheight() - 600) // 2
    dialog.geometry(f"+{x}+{y}")
    
    main = ctk.CTkFrame(dialog, fg_color="transparent")
    main.pack(fill="both", expand=True, padx=30, pady=30)
    
    # Titre
    ctk.CTkLabel(
        main,
        text="➕ Créer un nouvel utilisateur",
        font=ctk.CTkFont(size=18, weight="bold")
    ).pack(pady=(0, 20))
    
    # Formulaire
    form = ctk.CTkFrame(main)
    form.pack(fill="both", expand=True)
    
    # Username
    ctk.CTkLabel(form, text="Nom d'utilisateur *", anchor="w").pack(fill="x", padx=20, pady=(15, 5))
    username_entry = ctk.CTkEntry(form, height=40)
    username_entry.pack(fill="x", padx=20)
    
    # Nom complet
    ctk.CTkLabel(form, text="Nom complet *", anchor="w").pack(fill="x", padx=20, pady=(15, 5))
    fullname_entry = ctk.CTkEntry(form, height=40)
    fullname_entry.pack(fill="x", padx=20)
    
    # Email
    ctk.CTkLabel(form, text="Email", anchor="w").pack(fill="x", padx=20, pady=(15, 5))
    email_entry = ctk.CTkEntry(form, height=40)
    email_entry.pack(fill="x", padx=20)
    
    # Rôle
    ctk.CTkLabel(form, text="Rôle *", anchor="w").pack(fill="x", padx=20, pady=(15, 5))
    
    role_frame = ctk.CTkFrame(form, fg_color="transparent")
    role_frame.pack(fill="x", padx=20, pady=5)
    
    role_var = ctk.StringVar(value="viewer")
    
    for role_id, role_info in auth_manager.ROLES.items():
        radio_frame = ctk.CTkFrame(role_frame, fg_color=("gray85", "gray25"), corner_radius=8)
        radio_frame.pack(fill="x", pady=3)
        
        ctk.CTkRadioButton(
            radio_frame,
            text=f"{role_info['name']} - {role_info['description']}",
            variable=role_var,
            value=role_id
        ).pack(anchor="w", padx=10, pady=8)
    
    # Mot de passe
    ctk.CTkLabel(form, text="Mot de passe initial *", anchor="w").pack(fill="x", padx=20, pady=(15, 5))
    password_entry = ctk.CTkEntry(form, show="•", height=40)
    password_entry.pack(fill="x", padx=20)
    
    ctk.CTkLabel(
        form,
        text="L'utilisateur devra changer ce mot de passe à la première connexion",
        font=ctk.CTkFont(size=10),
        text_color="gray"
    ).pack(padx=20, pady=5)
    
    # Message d'erreur
    error_label = ctk.CTkLabel(form, text="", text_color="#dc2626")
    error_label.pack(pady=10)
    
    # Boutons
    btn_frame = ctk.CTkFrame(main, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(20, 0))
    
    def create():
        username = username_entry.get().strip()
        fullname = fullname_entry.get().strip()
        email = email_entry.get().strip()
        role = role_var.get()
        password = password_entry.get()
        
        if not username or not fullname or not password:
            error_label.configure(text="Veuillez remplir tous les champs obligatoires (*)")
            return
        
        if len(password) < 6:
            error_label.configure(text="Le mot de passe doit contenir au moins 6 caractères")
            return
        
        result = auth_manager.create_user(username, password, fullname, role, email)
        
        if result['success']:
            messagebox.showinfo("Succès", f"Utilisateur '{username}' créé avec succès!")
            dialog.destroy()
            app.navigate_to("settings")
        else:
            error_label.configure(text=result.get('error', 'Erreur'))
    
    ctk.CTkButton(
        btn_frame,
        text="✅ Créer l'utilisateur",
        width=180,
        height=45,
        command=create
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        btn_frame,
        text="❌ Annuler",
        width=120,
        height=45,
        command=dialog.destroy
    ).pack(side="left", padx=5)

def show_edit_user_dialog(app, user):
    """Dialogue de modification d'utilisateur"""
    dialog = ctk.CTkToplevel(app.root)
    dialog.title(f"Modifier - {user['username']}")
    dialog.geometry("500x500")
    dialog.transient(app.root)
    dialog.grab_set()
    
    # Centrer
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() - 500) // 2
    y = (dialog.winfo_screenheight() - 500) // 2
    dialog.geometry(f"+{x}+{y}")
    
    main = ctk.CTkFrame(dialog, fg_color="transparent")
    main.pack(fill="both", expand=True, padx=30, pady=30)
    
    # Titre
    ctk.CTkLabel(
        main,
        text=f"✏️ Modifier {user['username']}",
        font=ctk.CTkFont(size=18, weight="bold")
    ).pack(pady=(0, 20))
    
    # Formulaire
    form = ctk.CTkFrame(main)
    form.pack(fill="both", expand=True)
    
    # Nom complet
    ctk.CTkLabel(form, text="Nom complet", anchor="w").pack(fill="x", padx=20, pady=(15, 5))
    fullname_entry = ctk.CTkEntry(form, height=40)
    fullname_entry.insert(0, user['full_name'])
    fullname_entry.pack(fill="x", padx=20)
    
    # Email
    ctk.CTkLabel(form, text="Email", anchor="w").pack(fill="x", padx=20, pady=(15, 5))
    email_entry = ctk.CTkEntry(form, height=40)
    if user['email']:
        email_entry.insert(0, user['email'])
    email_entry.pack(fill="x", padx=20)
    
    # Rôle
    ctk.CTkLabel(form, text="Rôle", anchor="w").pack(fill="x", padx=20, pady=(15, 5))
    role_combo = ctk.CTkComboBox(
        form,
        values=[info['name'] for info in auth_manager.ROLES.values()],
        height=40
    )
    role_combo.set(auth_manager.ROLES[user['role']]['name'])
    role_combo.pack(fill="x", padx=20)
    
    # Statut
    ctk.CTkLabel(form, text="Statut", anchor="w").pack(fill="x", padx=20, pady=(15, 5))
    
    status_var = ctk.BooleanVar(value=user['is_active'])
    ctk.CTkCheckBox(
        form,
        text="Utilisateur actif",
        variable=status_var
    ).pack(anchor="w", padx=20)
    
    # Message d'erreur
    error_label = ctk.CTkLabel(form, text="", text_color="#dc2626")
    error_label.pack(pady=10)
    
    # Boutons
    btn_frame = ctk.CTkFrame(main, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(20, 0))
    
    def update():
        fullname = fullname_entry.get().strip()
        email = email_entry.get().strip()
        role_name = role_combo.get()
        
        # Trouver le role_id
        role_id = None
        for rid, rinfo in auth_manager.ROLES.items():
            if rinfo['name'] == role_name:
                role_id = rid
                break
        
        if not fullname:
            error_label.configure(text="Le nom complet est obligatoire")
            return
        
        result = auth_manager.update_user(
            user['id'],
            full_name=fullname,
            email=email or None,
            role=role_id,
            is_active=status_var.get()
        )
        
        if result['success']:
            messagebox.showinfo("Succès", "Utilisateur modifié avec succès!")
            dialog.destroy()
            app.navigate_to("settings")
        else:
            error_label.configure(text=result.get('error', 'Erreur'))
    
    ctk.CTkButton(
        btn_frame,
        text="💾 Sauvegarder",
        width=150,
        height=45,
        command=update
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        btn_frame,
        text="❌ Annuler",
        width=120,
        height=45,
        command=dialog.destroy
    ).pack(side="left", padx=5)

def show_reset_password_dialog(user):
    """Dialogue de réinitialisation de mot de passe"""
    dialog = ctk.CTkToplevel()
    dialog.title("Réinitialiser le mot de passe")
    dialog.geometry("400x300")
    dialog.grab_set()
    
    # Centrer
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() - 400) // 2
    y = (dialog.winfo_screenheight() - 300) // 2
    dialog.geometry(f"+{x}+{y}")
    
    main = ctk.CTkFrame(dialog, fg_color="transparent")
    main.pack(fill="both", expand=True, padx=30, pady=30)
    
    ctk.CTkLabel(
        main,
        text=f"🔑 Réinitialiser le mot de passe",
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=(0, 10))
    
    ctk.CTkLabel(
        main,
        text=f"Utilisateur: {user['username']}",
        font=ctk.CTkFont(size=12)
    ).pack(pady=(0, 20))
    
    ctk.CTkLabel(main, text="Nouveau mot de passe", anchor="w").pack(fill="x", pady=(0, 5))
    password_entry = ctk.CTkEntry(main, show="•", height=40)
    password_entry.pack(fill="x")
    
    error_label = ctk.CTkLabel(main, text="", text_color="#dc2626")
    error_label.pack(pady=10)
    
    def reset():
        password = password_entry.get()
        
        if len(password) < 6:
            error_label.configure(text="Le mot de passe doit contenir au moins 6 caractères")
            return
        
        result = auth_manager.change_password(user['id'], password)
        
        if result['success']:
            messagebox.showinfo("Succès", "Mot de passe réinitialisé avec succès!")
            dialog.destroy()
        else:
            error_label.configure(text=result.get('error', 'Erreur'))
    
    btn_frame = ctk.CTkFrame(main, fg_color="transparent")
    btn_frame.pack(pady=(20, 0))
    
    ctk.CTkButton(
        btn_frame,
        text="🔑 Réinitialiser",
        width=140,
        height=40,
        command=reset
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        btn_frame,
        text="Annuler",
        width=100,
        height=40,
        command=dialog.destroy
    ).pack(side="left", padx=5)

def delete_user(app, user):
    """Supprimer un utilisateur"""
    response = messagebox.askyesno(
        "Confirmation",
        f"Voulez-vous vraiment désactiver l'utilisateur '{user['username']}' ?\n\n"
        f"Cette action peut être annulée en réactivant l'utilisateur."
    )
    
    if response:
        result = auth_manager.delete_user(user['id'])
        
        if result['success']:
            messagebox.showinfo("Succès", "Utilisateur désactivé avec succès!")
            app.navigate_to("settings")
        else:
            messagebox.showerror("Erreur", result.get('error', 'Erreur'))