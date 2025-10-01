"""
Design System Unifié pour Military Career Manager
gui/design_system.py

Centralise TOUS les styles, couleurs, et composants réutilisables
"""

import customtkinter as ctk
from typing import Literal, Optional, Callable
from dataclasses import dataclass


# ==================== SYSTÈME DE COULEURS ====================

@dataclass
class ColorPalette:
    """Palette de couleurs avec modes clair/sombre"""
    
    # Couleurs principales
    PRIMARY: tuple = ("#3B8ED0", "#1F6AA5")
    SUCCESS: tuple = ("#16a34a", "#15803d")
    WARNING: tuple = ("#eab308", "#ca8a04")
    DANGER: tuple = ("#dc2626", "#991b1b")
    INFO: tuple = ("#3b82f6", "#2563eb")
    
    # Couleurs neutres (light, dark)
    BG_PRIMARY: tuple = ("#ffffff", "#2b2b2b")
    BG_SECONDARY: tuple = ("#f5f5f5", "#1e1e1e")
    BG_TERTIARY: tuple = ("#e5e5e5", "#3b3b3b")
    
    TEXT_PRIMARY: tuple = ("#1f2937", "#f9fafb")
    TEXT_SECONDARY: tuple = ("#6b7280", "#9ca3af")
    TEXT_DISABLED: tuple = ("#d1d5db", "#4b5563")
    
    BORDER_DEFAULT: tuple = ("#d1d5db", "#374151")
    BORDER_FOCUS: tuple = ("#3B8ED0", "#60a5fa")
    
    # Couleurs de statut
    STATUS_ACTIVE: tuple = ("#16a34a", "#22c55e")
    STATUS_INACTIVE: tuple = ("#6b7280", "#9ca3af")
    STATUS_PENDING: tuple = ("#eab308", "#fbbf24")
    
    @staticmethod
    def get_color(color: tuple, mode: Optional[str] = None) -> str:
        """Obtenir la couleur selon le mode"""
        if mode is None:
            mode = ctk.get_appearance_mode()
        return color[0] if mode == "Light" else color[1]


# ==================== TYPOGRAPHIE ====================

@dataclass
class Typography:
    """Système typographique unifié"""
    
    # Tailles de base
    XS: int = 9
    SM: int = 10
    BASE: int = 11
    MD: int = 12
    LG: int = 14
    XL: int = 16
    XXL: int = 18
    XXXL: int = 24
    
    # Styles prédéfinis
    @staticmethod
    def get_font(
        size: int = 11,
        weight: Literal["normal", "bold"] = "normal",
        family: str = "Segoe UI"
    ) -> ctk.CTkFont:
        """Créer une police personnalisée"""
        return ctk.CTkFont(family=family, size=size, weight=weight)
    
    @staticmethod
    def heading_1() -> ctk.CTkFont:
        return ctk.CTkFont(size=24, weight="bold")
    
    @staticmethod
    def heading_2() -> ctk.CTkFont:
        return ctk.CTkFont(size=18, weight="bold")
    
    @staticmethod
    def heading_3() -> ctk.CTkFont:
        return ctk.CTkFont(size=16, weight="bold")
    
    @staticmethod
    def body_large() -> ctk.CTkFont:
        return ctk.CTkFont(size=14)
    
    @staticmethod
    def body_regular() -> ctk.CTkFont:
        return ctk.CTkFont(size=11)
    
    @staticmethod
    def body_small() -> ctk.CTkFont:
        return ctk.CTkFont(size=10)
    
    @staticmethod
    def caption() -> ctk.CTkFont:
        return ctk.CTkFont(size=9)


# ==================== ESPACEMENTS ====================

class Spacing:
    """Système d'espacement cohérent"""
    
    XS: int = 4
    SM: int = 8
    MD: int = 12
    LG: int = 16
    XL: int = 20
    XXL: int = 24
    XXXL: int = 32


# ==================== COMPOSANTS RÉUTILISABLES ====================

class DSButton(ctk.CTkButton):
    """Bouton avec variants prédéfinis"""
    
    VARIANTS = {
        "primary": ColorPalette.PRIMARY,
        "success": ColorPalette.SUCCESS,
        "warning": ColorPalette.WARNING,
        "danger": ColorPalette.DANGER,
        "ghost": ("transparent", "transparent"),
    }
    
    SIZES = {
        "sm": {"height": 28, "font_size": Typography.SM},
        "md": {"height": 36, "font_size": Typography.BASE},
        "lg": {"height": 45, "font_size": Typography.MD},
    }
    
    def __init__(
        self,
        master,
        text: str = "",
        variant: Literal["primary", "success", "warning", "danger", "ghost"] = "primary",
        size: Literal["sm", "md", "lg"] = "md",
        icon: str = "",
        **kwargs
    ):
        # Récupérer les couleurs et tailles
        colors = self.VARIANTS[variant]
        size_config = self.SIZES[size]
        
        # Ajouter l'icône si présent
        display_text = f"{icon} {text}" if icon else text
        
        # Couleur de hover
        hover_color = self._darken_color(colors[0])
        
        super().__init__(
            master,
            text=display_text,
            fg_color=colors,
            hover_color=hover_color,
            height=size_config["height"],
            font=Typography.get_font(size=size_config["font_size"]),
            corner_radius=8,
            **kwargs
        )
    
    @staticmethod
    def _darken_color(hex_color: str, factor: float = 0.8) -> str:
        """Assombrir une couleur"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * factor))
        g = max(0, int(g * factor))
        b = max(0, int(b * factor))
        return f'#{r:02x}{g:02x}{b:02x}'


class DSCard(ctk.CTkFrame):
    """Carte avec style unifié"""
    
    def __init__(
        self,
        master,
        title: Optional[str] = None,
        padding: int = Spacing.LG,
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=12,
            border_width=1,
            border_color=ColorPalette.BORDER_DEFAULT,
            **kwargs
        )
        
        # Container interne avec padding
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=padding, pady=padding)
        
        # Titre optionnel
        if title:
            title_label = ctk.CTkLabel(
                self.content,
                text=title,
                font=Typography.heading_3(),
                anchor="w"
            )
            title_label.pack(fill="x", pady=(0, Spacing.MD))


class DSBadge(ctk.CTkFrame):
    """Badge de statut"""
    
    VARIANTS = {
        "success": ColorPalette.SUCCESS,
        "warning": ColorPalette.WARNING,
        "danger": ColorPalette.DANGER,
        "info": ColorPalette.INFO,
        "neutral": ColorPalette.BG_TERTIARY,
    }
    
    def __init__(
        self,
        master,
        text: str,
        variant: Literal["success", "warning", "danger", "info", "neutral"] = "neutral",
        icon: str = "",
        **kwargs
    ):
        colors = self.VARIANTS[variant]
        
        super().__init__(
            master,
            fg_color=colors,
            corner_radius=6,
            **kwargs
        )
        
        display_text = f"{icon} {text}" if icon else text
        
        label = ctk.CTkLabel(
            self,
            text=display_text,
            font=Typography.body_small(),
            text_color=("white", "white")
        )
        label.pack(padx=Spacing.SM, pady=Spacing.XS)


class DSInput(ctk.CTkEntry):
    """Input avec style unifié"""
    
    def __init__(
        self,
        master,
        placeholder: str = "",
        height: int = 40,
        **kwargs
    ):
        super().__init__(
            master,
            placeholder_text=placeholder,
            height=height,
            corner_radius=8,
            border_width=1,
            border_color=ColorPalette.BORDER_DEFAULT,
            font=Typography.body_regular(),
            **kwargs
        )


class DSSectionHeader(ctk.CTkFrame):
    """En-tête de section"""
    
    def __init__(
        self,
        master,
        title: str,
        subtitle: Optional[str] = None,
        icon: str = "",
        action_button: Optional[dict] = None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Layout horizontal
        self.pack(fill="x", pady=Spacing.MD)
        
        # Partie gauche: Titre + Sous-titre
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True)
        
        title_text = f"{icon} {title}" if icon else title
        title_label = ctk.CTkLabel(
            left_frame,
            text=title_text,
            font=Typography.heading_2(),
            anchor="w"
        )
        title_label.pack(fill="x")
        
        if subtitle:
            subtitle_label = ctk.CTkLabel(
                left_frame,
                text=subtitle,
                font=Typography.body_small(),
                text_color=ColorPalette.TEXT_SECONDARY,
                anchor="w"
            )
            subtitle_label.pack(fill="x", pady=(Spacing.XS, 0))
        
        # Partie droite: Bouton d'action optionnel
        if action_button:
            DSButton(
                self,
                text=action_button.get("text", "Action"),
                variant=action_button.get("variant", "primary"),
                size=action_button.get("size", "md"),
                icon=action_button.get("icon", ""),
                command=action_button.get("command")
            ).pack(side="right")


class DSLoadingOverlay(ctk.CTkToplevel):
    """Overlay de chargement réutilisable"""
    
    def __init__(self, parent, message: str = "Chargement..."):
        super().__init__(parent)
        
        # Configuration
        self.title("")
        self.geometry("400x200")
        self.transient(parent)
        self.grab_set()
        self.overrideredirect(True)
        
        # Centrer
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 200) // 2
        self.geometry(f"+{x}+{y}")
        
        # Contenu
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Icône
        icon_label = ctk.CTkLabel(content, text="⏳", font=ctk.CTkFont(size=50))
        icon_label.pack(pady=(0, Spacing.MD))
        
        # Message
        message_label = ctk.CTkLabel(
            content,
            text=message,
            font=Typography.heading_3()
        )
        message_label.pack()
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(content, width=300, height=8, mode="indeterminate")
        self.progress.pack(pady=Spacing.LG)
        self.progress.start()
    
    def update_message(self, message: str):
        """Mettre à jour le message"""
        # Trouver le label et le modifier
        # (Implementation simplifiée)
        pass
    
    def close(self):
        """Fermer l'overlay"""
        self.progress.stop()
        self.grab_release()
        self.destroy()


class DSUserBadge(ctk.CTkFrame):
    """Badge utilisateur connecté"""
    
    ROLE_EMOJIS = {
        'admin': '👑',
        'manager': '👔',
        'operator': '💼',
        'viewer': '👁️'
    }
    
    def __init__(self, master, user_data: dict, **kwargs):
        super().__init__(
            master,
            corner_radius=10,
            border_width=1,
            border_color=ColorPalette.BORDER_DEFAULT,
            **kwargs
        )
        
        # Container interne
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", padx=Spacing.MD, pady=Spacing.SM)
        
        # Emoji rôle
        emoji = self.ROLE_EMOJIS.get(user_data.get('role', 'viewer'), '👤')
        
        # Nom utilisateur
        name_label = ctk.CTkLabel(
            inner,
            text=f"{emoji} {user_data.get('full_name', 'Utilisateur')}",
            font=Typography.get_font(size=11, weight="bold")
        )
        name_label.pack(anchor="w")
        
        # Rôle
        from core.auth_manager import auth_manager
        role_name = auth_manager.ROLES.get(
            user_data.get('role', 'viewer'), {}
        ).get('name', 'Utilisateur')
        
        role_label = ctk.CTkLabel(
            inner,
            text=role_name,
            font=Typography.caption(),
            text_color=ColorPalette.TEXT_SECONDARY
        )
        role_label.pack(anchor="w")


# ==================== UTILITAIRES ====================

class DSUtils:
    """Utilitaires du Design System"""
    
    @staticmethod
    def create_stat_card(
        parent,
        label: str,
        value: str,
        icon: str = "",
        color: tuple = ColorPalette.PRIMARY
    ) -> ctk.CTkFrame:
        """Créer une carte statistique"""
        card = ctk.CTkFrame(
            parent,
            corner_radius=12,
            border_width=2,
            border_color=color
        )
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.MD)
        
        # Label + Icon
        label_text = f"{icon} {label}" if icon else label
        label_widget = ctk.CTkLabel(
            inner,
            text=label_text,
            font=Typography.get_font(size=13, weight="bold"),
            anchor="w"
        )
        label_widget.pack(fill="x", pady=(0, Spacing.XS))
        
        # Valeur
        value_widget = ctk.CTkLabel(
            inner,
            text=value,
            font=Typography.get_font(size=28, weight="bold"),
            text_color=ColorPalette.get_color(color)
        )
        value_widget.pack(fill="x")
        
        return card
    
    @staticmethod
    def create_info_row(
        parent,
        label: str,
        value: str
    ) -> ctk.CTkFrame:
        """Créer une ligne d'information"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=Spacing.XS)
        
        label_widget = ctk.CTkLabel(
            row,
            text=f"{label}:",
            font=Typography.get_font(size=12, weight="bold"),
            anchor="w",
            width=150
        )
        label_widget.pack(side="left", padx=Spacing.SM)
        
        value_widget = ctk.CTkLabel(
            row,
            text=str(value),
            font=Typography.body_regular(),
            anchor="w"
        )
        value_widget.pack(side="left", padx=Spacing.SM)
        
        return row


# ==================== EXPORT ====================

__all__ = [
    'ColorPalette',
    'Typography',
    'Spacing',
    'DSButton',
    'DSCard',
    'DSBadge',
    'DSInput',
    'DSSectionHeader',
    'DSLoadingOverlay',
    'DSUserBadge',
    'DSUtils'
]