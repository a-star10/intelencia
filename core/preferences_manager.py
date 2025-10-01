"""
Gestionnaire des préférences utilisateur
core/preferences_manager.py
"""
import json
from pathlib import Path
from typing import Dict, Any
import shutil

class PreferencesManager:
    """Gestionnaire centralisé des préférences utilisateur"""
    
    def __init__(self):
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        
        self.preferences_file = self.config_dir / "user_preferences.json"
        self.logo_dir = Path("assets")
        self.logo_dir.mkdir(exist_ok=True)
        
        # Préférences par défaut
        self.default_preferences = {
            # Apparence
            "theme": "light",  # light, dark
            "accent_color": "blue",  # blue, green, red, orange, purple
            "display_mode": "normal",  # compact, normal, comfortable
            
            # Typographie
            "global_font_size": "normal",  # very_small, small, normal, large, very_large
            "table_font_size": 9,  # 7-12
            "title_font_size": 20,  # 18-26
            
            # Logo
            "logo_path": "assets/logo.png",
            "logo_size": 180,  # 120, 180, 240
            "use_custom_logo": False,
            
            # Tableaux
            "rows_per_page": 30,  # 10, 20, 30, 50, 100, -1 (tout)
            "alternate_row_colors": True,
            "row_spacing": "normal",  # compact, normal, large
            
            # Dashboard
            "show_stats_cards": True,
            "stats_card_style": "detailed",  # minimalist, detailed
            "show_quick_actions": True,
            
            # Général
            "auto_save": True,
            "show_tooltips": True
        }
        
        self.preferences = self.load_preferences()
    
    def load_preferences(self) -> Dict[str, Any]:
        """Charger les préférences depuis le fichier JSON"""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    loaded_prefs = json.load(f)
                    # Fusionner avec les valeurs par défaut pour les nouvelles clés
                    preferences = self.default_preferences.copy()
                    preferences.update(loaded_prefs)
                    return preferences
            except Exception as e:
                print(f"⚠️ Erreur chargement préférences: {e}")
                return self.default_preferences.copy()
        else:
            # Première utilisation : créer le fichier
            self.save_preferences(self.default_preferences)
            return self.default_preferences.copy()
    
    def save_preferences(self, preferences: Dict[str, Any] = None) -> bool:
        """Sauvegarder les préférences dans le fichier JSON"""
        try:
            prefs_to_save = preferences if preferences else self.preferences
            
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(prefs_to_save, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Préférences sauvegardées dans {self.preferences_file}")
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde préférences: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Récupérer une préférence"""
        return self.preferences.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True):
        """Définir une préférence"""
        self.preferences[key] = value
        if save and self.preferences.get('auto_save', True):
            self.save_preferences()
    
    def reset_to_defaults(self) -> bool:
        """Réinitialiser aux valeurs par défaut"""
        try:
            self.preferences = self.default_preferences.copy()
            self.save_preferences()
            print("✅ Préférences réinitialisées aux valeurs par défaut")
            return True
        except Exception as e:
            print(f"❌ Erreur réinitialisation: {e}")
            return False
    
    def export_preferences(self, export_path: str) -> bool:
        """Exporter les préférences vers un fichier"""
        try:
            export_file = Path(export_path)
            shutil.copy(self.preferences_file, export_file)
            print(f"✅ Préférences exportées vers {export_file}")
            return True
        except Exception as e:
            print(f"❌ Erreur export: {e}")
            return False
    
    def import_preferences(self, import_path: str) -> bool:
        """Importer les préférences depuis un fichier"""
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                print(f"❌ Fichier {import_file} introuvable")
                return False
            
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_prefs = json.load(f)
            
            # Valider et fusionner
            self.preferences = self.default_preferences.copy()
            self.preferences.update(imported_prefs)
            self.save_preferences()
            
            print(f"✅ Préférences importées depuis {import_file}")
            return True
        except Exception as e:
            print(f"❌ Erreur import: {e}")
            return False
    
    def upload_custom_logo(self, source_path: str) -> bool:
        """Uploader un logo personnalisé"""
        try:
            source = Path(source_path)
            if not source.exists():
                print(f"❌ Fichier {source} introuvable")
                return False
            
            # Vérifier que c'est une image
            valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
            if source.suffix.lower() not in valid_extensions:
                print(f"❌ Format non supporté. Utilisez: {', '.join(valid_extensions)}")
                return False
            
            # Copier vers le dossier assets
            custom_logo_path = self.logo_dir / f"custom_logo{source.suffix}"
            shutil.copy(source, custom_logo_path)
            
            # Mettre à jour les préférences
            self.set('logo_path', str(custom_logo_path))
            self.set('use_custom_logo', True)
            
            print(f"✅ Logo personnalisé uploadé: {custom_logo_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur upload logo: {e}")
            return False
    
    def restore_default_logo(self) -> bool:
        """Restaurer le logo par défaut"""
        try:
            self.set('logo_path', 'assets/logo.png')
            self.set('use_custom_logo', False)
            print("✅ Logo par défaut restauré")
            return True
        except Exception as e:
            print(f"❌ Erreur restauration logo: {e}")
            return False
    
    def get_font_size_multiplier(self) -> float:
        """Obtenir le multiplicateur de taille de police globale"""
        size_map = {
            "very_small": 0.75,
            "small": 0.875,
            "normal": 1.0,
            "large": 1.125,
            "very_large": 1.25
        }
        return size_map.get(self.get('global_font_size', 'normal'), 1.0)
    
    def get_accent_color_hex(self) -> str:
        """Obtenir le code couleur hex de l'accent"""
        color_map = {
            "blue": "#3B8ED0",
            "green": "#2E8B57",
            "red": "#DC143C",
            "orange": "#FF8C00",
            "purple": "#8B5CF6"
        }
        return color_map.get(self.get('accent_color', 'blue'), "#3B8ED0")

# Instance globale
preferences_manager = PreferencesManager()

if __name__ == "__main__":
    print("🧪 Test du gestionnaire de préférences...")
    
    # Test des préférences
    print(f"Thème actuel: {preferences_manager.get('theme')}")
    print(f"Taille police tableaux: {preferences_manager.get('table_font_size')}")
    print(f"Logo: {preferences_manager.get('logo_path')}")
    
    # Test de modification
    preferences_manager.set('theme', 'dark')
    print(f"Nouveau thème: {preferences_manager.get('theme')}")
    
    print("\n✅ Gestionnaire de préférences fonctionnel !")