"""
Système d'authentification et gestion des utilisateurs
core/auth_manager.py
"""
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import json

class AuthManager:
    """Gestionnaire d'authentification et de permissions"""
    
    # Définition des rôles et permissions
    ROLES = {
        'admin': {
            'name': 'Administrateur',
            'permissions': ['*'],  # Toutes les permissions
            'description': 'Accès complet au système'
        },
        'manager': {
            'name': 'Gestionnaire RH',
            'permissions': [
                'view_agents', 'create_agent', 'edit_agent', 'delete_agent',
                'view_rules', 'edit_rules',
                'view_evaluation', 'run_evaluation',
                'view_reports', 'export_data',
                'view_settings'
            ],
            'description': 'Gestion complète des agents et évaluations'
        },
        'operator': {
            'name': 'Opérateur',
            'permissions': [
                'view_agents', 'create_agent', 'edit_agent',
                'view_rules',
                'view_evaluation',
                'view_reports'
            ],
            'description': 'Consultation et modification des agents'
        },
        'viewer': {
            'name': 'Consultant',
            'permissions': [
                'view_agents',
                'view_rules',
                'view_evaluation',
                'view_reports'
            ],
            'description': 'Consultation en lecture seule'
        }
    }
    
    def __init__(self, db_path: Path = None):
        if db_path is None:
            from config import DATABASE_PATH
            self.db_path = DATABASE_PATH
        else:
            self.db_path = db_path
        
        self.current_user = None
        self.session_token = None
        self.init_database()
        self.create_default_admin()
    
    def get_connection(self):
        """Obtenir une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialiser les tables d'authentification"""
        with self.get_connection() as conn:
            # Table utilisateurs
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    email TEXT,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'viewer',
                    is_active BOOLEAN DEFAULT 1,
                    must_change_password BOOLEAN DEFAULT 0,
                    last_login DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """)
            
            # Table sessions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Table logs d'audit
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    resource TEXT,
                    resource_id INTEGER,
                    details TEXT,
                    ip_address TEXT,
                    success BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Index pour optimisation
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_token 
                ON sessions(token, is_active)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_user 
                ON audit_logs(user_id, created_at)
            """)
            
            conn.commit()
            print("✅ Tables d'authentification initialisées")
    
    def create_default_admin(self):
        """Créer l'administrateur par défaut si aucun utilisateur n'existe"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
                
                if count == 0:
                    # Créer admin par défaut
                    password_hash, salt = self._hash_password("admin123")
                    
                    conn.execute("""
                        INSERT INTO users (username, password_hash, salt, full_name, role, must_change_password)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, ("admin", password_hash, salt, "Administrateur", "admin", 1))
                    
                    conn.commit()
                    print("✅ Utilisateur admin créé (admin/admin123)")
                    print("⚠️  Changez ce mot de passe lors de la première connexion!")
        except Exception as e:
            print(f"❌ Erreur création admin: {e}")
    
    def _hash_password(self, password: str, salt: str = None) -> tuple:
        """Hacher un mot de passe avec salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Utiliser PBKDF2 pour plus de sécurité
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # Nombre d'itérations
        ).hex()
        
        return password_hash, salt
    
    def authenticate(self, username: str, password: str, ip_address: str = None) -> Dict[str, Any]:
        """Authentifier un utilisateur"""
        try:
            with self.get_connection() as conn:
                # Récupérer l'utilisateur
                cursor = conn.execute("""
                    SELECT * FROM users 
                    WHERE username = ? AND is_active = 1
                """, (username,))
                
                user = cursor.fetchone()
                
                if not user:
                    self._log_audit(None, "login_failed", "authentication", 
                                  details=f"User not found: {username}", 
                                  ip_address=ip_address, success=False)
                    return {'success': False, 'error': 'Identifiants invalides'}
                
                # Vérifier le mot de passe
                password_hash, _ = self._hash_password(password, user['salt'])
                
                if password_hash != user['password_hash']:
                    self._log_audit(user['id'], "login_failed", "authentication",
                                  details="Invalid password", 
                                  ip_address=ip_address, success=False)
                    return {'success': False, 'error': 'Identifiants invalides'}
                
                # Créer une session
                token = secrets.token_urlsafe(32)
                expires_at = datetime.now() + timedelta(hours=8)
                
                conn.execute("""
                    INSERT INTO sessions (user_id, token, ip_address, expires_at)
                    VALUES (?, ?, ?, ?)
                """, (user['id'], token, ip_address, expires_at))
                
                # Mettre à jour last_login
                conn.execute("""
                    UPDATE users SET last_login = ? WHERE id = ?
                """, (datetime.now(), user['id']))
                
                conn.commit()
                
                # Sauvegarder l'utilisateur courant
                self.current_user = dict(user)
                self.session_token = token
                
                self._log_audit(user['id'], "login_success", "authentication",
                              ip_address=ip_address)
                
                return {
                    'success': True,
                    'user': dict(user),
                    'token': token,
                    'must_change_password': bool(user['must_change_password'])
                }
        
        except Exception as e:
            print(f"❌ Erreur authentification: {e}")
            return {'success': False, 'error': str(e)}
    
    def logout(self):
        """Déconnecter l'utilisateur courant"""
        if self.session_token:
            try:
                with self.get_connection() as conn:
                    conn.execute("""
                        UPDATE sessions SET is_active = 0 
                        WHERE token = ?
                    """, (self.session_token,))
                    conn.commit()
                    
                    if self.current_user:
                        self._log_audit(self.current_user['id'], "logout", "authentication")
            except Exception as e:
                print(f"❌ Erreur déconnexion: {e}")
        
        self.current_user = None
        self.session_token = None
    
    def verify_session(self, token: str) -> bool:
        """Vérifier si une session est valide"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT s.*, u.*
                    FROM sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE s.token = ? 
                    AND s.is_active = 1 
                    AND s.expires_at > ?
                    AND u.is_active = 1
                """, (token, datetime.now()))
                
                row = cursor.fetchone()
                
                if row:
                    self.current_user = dict(row)
                    self.session_token = token
                    return True
                
                return False
        except Exception as e:
            print(f"❌ Erreur vérification session: {e}")
            return False
    
    def has_permission(self, permission: str) -> bool:
        """Vérifier si l'utilisateur a une permission"""
        if not self.current_user:
            return False
        
        role = self.current_user.get('role', 'viewer')
        role_permissions = self.ROLES.get(role, {}).get('permissions', [])
        
        # Admin a toutes les permissions
        if '*' in role_permissions:
            return True
        
        return permission in role_permissions
    
    def require_permission(self, permission: str) -> bool:
        """Vérifier une permission et lever une exception si non autorisé"""
        if not self.has_permission(permission):
            raise PermissionError(f"Permission requise: {permission}")
        return True
    
    def create_user(self, username: str, password: str, full_name: str, 
                   role: str = 'viewer', email: str = None) -> Dict[str, Any]:
        """Créer un nouvel utilisateur"""
        try:
            # Vérifier la permission
            self.require_permission('*')  # Seul admin peut créer
            
            # Valider le rôle
            if role not in self.ROLES:
                return {'success': False, 'error': f'Rôle invalide: {role}'}
            
            # Vérifier si l'utilisateur existe
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT id FROM users WHERE username = ?
                """, (username,))
                
                if cursor.fetchone():
                    return {'success': False, 'error': 'Nom d\'utilisateur déjà utilisé'}
                
                # Créer l'utilisateur
                password_hash, salt = self._hash_password(password)
                
                cursor = conn.execute("""
                    INSERT INTO users (username, password_hash, salt, full_name, role, email, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (username, password_hash, salt, full_name, role, email, 
                     self.current_user['id'] if self.current_user else None))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                self._log_audit(self.current_user['id'], "create_user", "users", 
                              resource_id=user_id, 
                              details=f"Created user: {username} (role: {role})")
                
                return {'success': True, 'user_id': user_id}
        
        except PermissionError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            print(f"❌ Erreur création utilisateur: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_user(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """Mettre à jour un utilisateur"""
        try:
            # Vérifier la permission
            self.require_permission('*')
            
            allowed_fields = ['full_name', 'email', 'role', 'is_active']
            updates = []
            values = []
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    updates.append(f"{field} = ?")
                    values.append(value)
            
            if not updates:
                return {'success': False, 'error': 'Aucun champ à mettre à jour'}
            
            updates.append("updated_at = ?")
            values.append(datetime.now())
            values.append(user_id)
            
            with self.get_connection() as conn:
                query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
                conn.execute(query, values)
                conn.commit()
                
                self._log_audit(self.current_user['id'], "update_user", "users",
                              resource_id=user_id, details=json.dumps(kwargs))
                
                return {'success': True}
        
        except PermissionError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            print(f"❌ Erreur mise à jour utilisateur: {e}")
            return {'success': False, 'error': str(e)}
    
    def change_password(self, user_id: int, new_password: str, 
                       old_password: str = None) -> Dict[str, Any]:
        """Changer le mot de passe d'un utilisateur"""
        try:
            with self.get_connection() as conn:
                # Si pas admin, vérifier l'ancien mot de passe
                if not self.has_permission('*') and old_password:
                    cursor = conn.execute("""
                        SELECT password_hash, salt FROM users WHERE id = ?
                    """, (user_id,))
                    user = cursor.fetchone()
                    
                    if user:
                        old_hash, _ = self._hash_password(old_password, user['salt'])
                        if old_hash != user['password_hash']:
                            return {'success': False, 'error': 'Ancien mot de passe incorrect'}
                
                # Changer le mot de passe
                new_hash, salt = self._hash_password(new_password)
                
                conn.execute("""
                    UPDATE users 
                    SET password_hash = ?, salt = ?, must_change_password = 0, updated_at = ?
                    WHERE id = ?
                """, (new_hash, salt, datetime.now(), user_id))
                
                conn.commit()
                
                self._log_audit(user_id, "change_password", "users", resource_id=user_id)
                
                return {'success': True}
        
        except Exception as e:
            print(f"❌ Erreur changement mot de passe: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Supprimer (désactiver) un utilisateur"""
        try:
            self.require_permission('*')
            
            # Ne pas supprimer son propre compte
            if self.current_user and user_id == self.current_user['id']:
                return {'success': False, 'error': 'Impossible de supprimer votre propre compte'}
            
            with self.get_connection() as conn:
                conn.execute("""
                    UPDATE users SET is_active = 0, updated_at = ?
                    WHERE id = ?
                """, (datetime.now(), user_id))
                
                conn.commit()
                
                self._log_audit(self.current_user['id'], "delete_user", "users",
                              resource_id=user_id)
                
                return {'success': True}
        
        except PermissionError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            print(f"❌ Erreur suppression utilisateur: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Récupérer tous les utilisateurs"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT id, username, full_name, email, role, is_active, 
                           last_login, created_at
                    FROM users
                    ORDER BY created_at DESC
                """)
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erreur récupération utilisateurs: {e}")
            return []
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer un utilisateur par ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM users WHERE id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"❌ Erreur récupération utilisateur: {e}")
            return None
    
    def get_audit_logs(self, user_id: int = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Récupérer les logs d'audit"""
        try:
            with self.get_connection() as conn:
                if user_id:
                    cursor = conn.execute("""
                        SELECT a.*, u.username, u.full_name
                        FROM audit_logs a
                        LEFT JOIN users u ON a.user_id = u.id
                        WHERE a.user_id = ?
                        ORDER BY a.created_at DESC
                        LIMIT ?
                    """, (user_id, limit))
                else:
                    cursor = conn.execute("""
                        SELECT a.*, u.username, u.full_name
                        FROM audit_logs a
                        LEFT JOIN users u ON a.user_id = u.id
                        ORDER BY a.created_at DESC
                        LIMIT ?
                    """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erreur récupération logs: {e}")
            return []
    
    def _log_audit(self, user_id: int, action: str, resource: str, 
                  resource_id: int = None, details: str = None, 
                  ip_address: str = None, success: bool = True):
        """Enregistrer une action dans les logs d'audit"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO audit_logs 
                    (user_id, action, resource, resource_id, details, ip_address, success)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, action, resource, resource_id, details, ip_address, success))
                
                conn.commit()
        except Exception as e:
            print(f"❌ Erreur log audit: {e}")
    
    def cleanup_expired_sessions(self):
        """Nettoyer les sessions expirées"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    UPDATE sessions SET is_active = 0
                    WHERE expires_at < ? AND is_active = 1
                """, (datetime.now(),))
                
                conn.commit()
        except Exception as e:
            print(f"❌ Erreur nettoyage sessions: {e}")

# Instance globale
auth_manager = AuthManager()

if __name__ == "__main__":
    print("🔐 Test du système d'authentification...")
    
    # Test login
    result = auth_manager.authenticate("admin", "admin123")
    if result['success']:
        print(f"✅ Login réussi: {result['user']['full_name']}")
        print(f"   Rôle: {result['user']['role']}")
        print(f"   Token: {result['token'][:20]}...")
    else:
        print(f"❌ Erreur: {result['error']}")