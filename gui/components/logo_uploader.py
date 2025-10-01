"""
Composant d'upload de logo personnalisé
gui/components/logo_uploader.py
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from core.preferences_manager import preferences_manager

class LogoUploader:
    """Composant pour uploader et gérer le logo"""
    
    def __init__(self, parent_frame, callback=None):
        self.parent = parent_frame
        self.callback = callback  # Fonction à appeler après changement
        self.current_logo_path = None
        self.preview_image = None
        
        self.create_ui()
        self.load_current_logo()
    
    def create_ui(self):
        """Créer l'interface du composant"""
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="x", padx=20, pady=10)
        
        # Titre
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="🖼️ Gestion du Logo",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(15, 10))
        
        # Description
        desc_label = ctk.CTkLabel(
            self.main_frame,
            text="Personnalisez le logo de l'application (PNG, JPG, GIF)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        desc_label.pack(pady=(0, 15))
        
        # Container pour prévisualisation et contrôles
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Zone de prévisualisation
        preview_frame = ctk.CTkFrame(content_frame)
        preview_frame.pack(side="left", padx=10, pady=10)
        
        preview_title = ctk.CTkLabel(
            preview_frame,
            text="Aperçu",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        preview_title.pack(pady=(10, 5))
        
        # Label pour afficher le logo
        self.logo_preview = ctk.CTkLabel(
            preview_frame,
            text="",
            width=200,
            height=200
        )
        self.logo_preview.pack(pady=10, padx=10)
        
        # Info sur le logo actuel
        self.logo_info = ctk.CTkLabel(
            preview_frame,
            text="Aucun logo",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.logo_info.pack(pady=(0, 10))
        
        # Contrôles
        controls_frame = ctk.CTkFrame(content_frame)
        controls_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Taille du logo
        size_label = ctk.CTkLabel(
            controls_frame,
            text="Taille du logo :",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        size_label.pack(pady=(20, 5), anchor="w", padx=20)
        
        size_frame = ctk.CTkFrame(controls_frame)
        size_frame.pack(pady=5, padx=20, fill="x")
        
        self.size_var = ctk.StringVar(value="180")
        
        for size in ["120", "180", "240"]:
            radio = ctk.CTkRadioButton(
                size_frame,
                text=f"{size}x{size} px",
                variable=self.size_var,
                value=size,
                command=self.on_size_change
            )
            radio.pack(side="left", padx=10)
        
        # Boutons d'action
        buttons_frame = ctk.CTkFrame(controls_frame)
        buttons_frame.pack(pady=20, padx=20, fill="x")
        
        # Bouton Parcourir
        browse_btn = ctk.CTkButton(
            buttons_frame,
            text="📁 Parcourir...",
            width=180,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.browse_logo
        )
        browse_btn.pack(pady=5)
        
        # Bouton Restaurer défaut
        restore_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Restaurer logo par défaut",
            width=180,
            height=35,
            command=self.restore_default
        )
        restore_btn.pack(pady=5)
        
        # Bouton Supprimer
        delete_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Supprimer le logo personnalisé",
            width=180,
            height=35,
            fg_color="#dc2626",
            hover_color="#991b1b",
            command=self.delete_custom_logo
        )
        delete_btn.pack(pady=5)
        
        # Note d'information
        info_label = ctk.CTkLabel(
            controls_frame,
            text="💡 Le logo sera redimensionné automatiquement.\nFormats supportés: PNG, JPG, JPEG, GIF, BMP",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            justify="center"
        )
        info_label.pack(pady=10)
    
    def load_current_logo(self):
        """Charger le logo actuel"""
        logo_path = preferences_manager.get('logo_path', 'assets/logo.png')
        logo_size = preferences_manager.get('logo_size', 180)
        
        self.size_var.set(str(logo_size))
        self.display_logo(logo_path, logo_size)
    
    def display_logo(self, logo_path: str, size: int = 180):
        """Afficher le logo dans la prévisualisation"""
        try:
            logo_file = Path(logo_path)
            
            if logo_file.exists():
                # Charger l'image
                logo_image = Image.open(logo_file)
                
                # Redimensionner
                logo_image = logo_image.resize((size, size), Image.Resampling.LANCZOS)
                
                # Convertir pour CustomTkinter
                logo_ctk = ctk.CTkImage(
                    light_image=logo_image,
                    dark_image=logo_image,
                    size=(size, size)
                )
                
                # Afficher
                self.logo_preview.configure(image=logo_ctk, text="")
                self.preview_image = logo_ctk  # Garder référence
                
                # Info
                use_custom = preferences_manager.get('use_custom_logo', False)
                logo_type = "Logo personnalisé" if use_custom else "Logo par défaut"
                self.logo_info.configure(text=f"{logo_type}\n{logo_file.name}")
                
                self.current_logo_path = logo_path
                
            else:
                # Logo non trouvé
                self.logo_preview.configure(
                    image=None,
                    text="❌\nLogo introuvable"
                )
                self.logo_info.configure(text=f"Fichier: {logo_path}\n(Non trouvé)")
        
        except Exception as e:
            print(f"❌ Erreur affichage logo: {e}")
            self.logo_preview.configure(
                image=None,
                text="❌\nErreur de chargement"
            )
            self.logo_info.configure(text=f"Erreur: {str(e)}")
    
    def browse_logo(self):
        """Ouvrir le dialogue de sélection de fichier"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner un logo",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("GIF", "*.gif"),
                ("BMP", "*.bmp"),
                ("Tous les fichiers", "*.*")
            ]
        )
        
        if file_path:
            # Uploader le logo
            success = preferences_manager.upload_custom_logo(file_path)
            
            if success:
                # Recharger l'affichage
                logo_size = int(self.size_var.get())
                new_logo_path = preferences_manager.get('logo_path')
                self.display_logo(new_logo_path, logo_size)
                
                messagebox.showinfo(
                    "Succès",
                    f"✅ Logo personnalisé uploadé avec succès !\n\n"
                    f"Fichier: {Path(file_path).name}\n"
                    f"Taille: {logo_size}x{logo_size} px\n\n"
                    f"Le nouveau logo sera visible au prochain redémarrage."
                )
                
                # Callback si défini
                if self.callback:
                    self.callback()
            else:
                messagebox.showerror(
                    "Erreur",
                    "❌ Erreur lors de l'upload du logo.\n\n"
                    "Vérifiez que le fichier est une image valide."
                )
    
    def restore_default(self):
        """Restaurer le logo par défaut"""
        response = messagebox.askyesno(
            "Confirmer",
            "Voulez-vous restaurer le logo par défaut ?\n\n"
            "Le logo personnalisé sera conservé mais n'est plus utilisé."
        )
        
        if response:
            success = preferences_manager.restore_default_logo()
            
            if success:
                logo_size = int(self.size_var.get())
                self.display_logo('assets/logo.png', logo_size)
                
                messagebox.showinfo(
                    "Succès",
                    "✅ Logo par défaut restauré !\n\n"
                    "Les changements seront visibles au prochain redémarrage."
                )
                
                if self.callback:
                    self.callback()
    
    def delete_custom_logo(self):
        """Supprimer le logo personnalisé"""
        if not preferences_manager.get('use_custom_logo', False):
            messagebox.showinfo(
                "Information",
                "Aucun logo personnalisé n'est actuellement utilisé."
            )
            return
        
        response = messagebox.askyesno(
            "Confirmer la suppression",
            "Voulez-vous supprimer définitivement le logo personnalisé ?\n\n"
            "Cette action est irréversible.\n"
            "Le logo par défaut sera restauré."
        )
        
        if response:
            try:
                # Supprimer le fichier custom_logo
                custom_logos = Path("assets").glob("custom_logo.*")
                for logo_file in custom_logos:
                    logo_file.unlink()
                    print(f"🗑️ Fichier supprimé: {logo_file}")
                
                # Restaurer le logo par défaut
                preferences_manager.restore_default_logo()
                
                # Recharger l'affichage
                logo_size = int(self.size_var.get())
                self.display_logo('assets/logo.png', logo_size)
                
                messagebox.showinfo(
                    "Succès",
                    "✅ Logo personnalisé supprimé !\n\n"
                    "Le logo par défaut a été restauré."
                )
                
                if self.callback:
                    self.callback()
            
            except Exception as e:
                messagebox.showerror(
                    "Erreur",
                    f"❌ Erreur lors de la suppression:\n\n{str(e)}"
                )
    
    def on_size_change(self):
        """Changement de taille du logo"""
        new_size = int(self.size_var.get())
        preferences_manager.set('logo_size', new_size)
        
        # Recharger avec la nouvelle taille
        if self.current_logo_path:
            self.display_logo(self.current_logo_path, new_size)

def show_logo_uploader(parent_frame, callback=None):
    """Fonction utilitaire pour afficher le composant"""
    return LogoUploader(parent_frame, callback)