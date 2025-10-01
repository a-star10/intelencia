"""
Système d'historique des connexions
core/connection_history.py
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import platform
import socket

class ConnectionHistoryManager:
    """Gestionnaire de l'historique des connexions"""
    
    def __init__(self, db_path: Path = None):
        if db_path is None:
            from config import DATABASE_PATH
            self.db_path = DATABASE_PATH
        else:
            self.db_path = db_path
        
        self.init_database()
    
    def get_connection(self):
        """Obtenir une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialiser la table d'historique des connexions"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS connection_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    full_name TEXT,
                    login_time DATETIME NOT NULL,
                    logout_time DATETIME,
                    session_duration INTEGER,
                    ip_address TEXT,
                    hostname TEXT,
                    os_info TEXT,
                    browser_info TEXT,
                    success BOOLEAN DEFAULT 1,
                    failure_reason TEXT,
                    location TEXT,
                    device_info TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Index pour optimisation
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_connection_history_user 
                ON connection_history(user_id, login_time DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_connection_history_time 
                ON connection_history(login_time DESC)
            """)
            
            conn.commit()
    
    def get_system_info(self) -> Dict[str, str]:
        """Récupérer les informations système"""
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
        except:
            hostname = "Unknown"
            ip_address = "0.0.0.0"
        
        os_info = f"{platform.system()} {platform.release()}"
        device_info = f"{platform.machine()} - {platform.processor()}"
        
        return {
            'hostname': hostname,
            'ip_address': ip_address,
            'os_info': os_info,
            'device_info': device_info
        }
    
    def record_login(self, user: Dict[str, Any], success: bool = True, 
                    failure_reason: str = None) -> int:
        """Enregistrer une tentative de connexion"""
        try:
            system_info = self.get_system_info()
            
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO connection_history (
                        user_id, username, full_name, login_time,
                        ip_address, hostname, os_info, device_info,
                        success, failure_reason
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user.get('id'),
                    user.get('username'),
                    user.get('full_name'),
                    datetime.now(),
                    system_info['ip_address'],
                    system_info['hostname'],
                    system_info['os_info'],
                    system_info['device_info'],
                    success,
                    failure_reason
                ))
                
                connection_id = cursor.lastrowid
                conn.commit()
                
                return connection_id
        
        except Exception as e:
            print(f"❌ Erreur enregistrement connexion: {e}")
            return None
    
    def record_logout(self, user_id: int):
        """Enregistrer une déconnexion"""
        try:
            with self.get_connection() as conn:
                # Trouver la dernière connexion active
                cursor = conn.execute("""
                    SELECT id, login_time 
                    FROM connection_history
                    WHERE user_id = ? AND logout_time IS NULL
                    ORDER BY login_time DESC
                    LIMIT 1
                """, (user_id,))
                
                row = cursor.fetchone()
                
                if row:
                    logout_time = datetime.now()
                    login_time = datetime.fromisoformat(row['login_time'])
                    duration = int((logout_time - login_time).total_seconds())
                    
                    conn.execute("""
                        UPDATE connection_history
                        SET logout_time = ?, session_duration = ?
                        WHERE id = ?
                    """, (logout_time, duration, row['id']))
                    
                    conn.commit()
                    return True
                
                return False
        
        except Exception as e:
            print(f"❌ Erreur enregistrement déconnexion: {e}")
            return False
    
    def get_user_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupérer l'historique d'un utilisateur"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM connection_history
                    WHERE user_id = ?
                    ORDER BY login_time DESC
                    LIMIT ?
                """, (user_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            print(f"❌ Erreur récupération historique: {e}")
            return []
    
    def get_all_history(self, limit: int = 100, 
                       days: int = None) -> List[Dict[str, Any]]:
        """Récupérer tout l'historique"""
        try:
            with self.get_connection() as conn:
                if days:
                    since_date = datetime.now() - timedelta(days=days)
                    cursor = conn.execute("""
                        SELECT * FROM connection_history
                        WHERE login_time >= ?
                        ORDER BY login_time DESC
                        LIMIT ?
                    """, (since_date, limit))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM connection_history
                        ORDER BY login_time DESC
                        LIMIT ?
                    """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            print(f"❌ Erreur récupération historique: {e}")
            return []
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Récupérer les sessions actuellement actives"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM connection_history
                    WHERE logout_time IS NULL AND success = 1
                    ORDER BY login_time DESC
                """)
                
                return [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            print(f"❌ Erreur récupération sessions actives: {e}")
            return []
    
    def get_failed_attempts(self, hours: int = 24, 
                          user_id: int = None) -> List[Dict[str, Any]]:
        """Récupérer les tentatives de connexion échouées"""
        try:
            since_time = datetime.now() - timedelta(hours=hours)
            
            with self.get_connection() as conn:
                if user_id:
                    cursor = conn.execute("""
                        SELECT * FROM connection_history
                        WHERE success = 0 AND login_time >= ? AND user_id = ?
                        ORDER BY login_time DESC
                    """, (since_time, user_id))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM connection_history
                        WHERE success = 0 AND login_time >= ?
                        ORDER BY login_time DESC
                    """, (since_time,))
                
                return [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            print(f"❌ Erreur récupération échecs: {e}")
            return []
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Récupérer les statistiques de connexion"""
        try:
            since_date = datetime.now() - timedelta(days=days)
            
            with self.get_connection() as conn:
                # Total connexions
                cursor = conn.execute("""
                    SELECT COUNT(*) as total FROM connection_history
                    WHERE login_time >= ? AND success = 1
                """, (since_date,))
                total = cursor.fetchone()['total']
                
                # Échecs
                cursor = conn.execute("""
                    SELECT COUNT(*) as failed FROM connection_history
                    WHERE login_time >= ? AND success = 0
                """, (since_date,))
                failed = cursor.fetchone()['failed']
                
                # Utilisateurs uniques
                cursor = conn.execute("""
                    SELECT COUNT(DISTINCT user_id) as unique_users 
                    FROM connection_history
                    WHERE login_time >= ? AND success = 1
                """, (since_date,))
                unique_users = cursor.fetchone()['unique_users']
                
                # Durée moyenne des sessions
                cursor = conn.execute("""
                    SELECT AVG(session_duration) as avg_duration 
                    FROM connection_history
                    WHERE login_time >= ? AND session_duration IS NOT NULL
                """, (since_date,))
                avg_duration = cursor.fetchone()['avg_duration'] or 0
                
                # Top utilisateurs
                cursor = conn.execute("""
                    SELECT username, full_name, COUNT(*) as login_count
                    FROM connection_history
                    WHERE login_time >= ? AND success = 1
                    GROUP BY user_id
                    ORDER BY login_count DESC
                    LIMIT 5
                """, (since_date,))
                top_users = [dict(row) for row in cursor.fetchall()]
                
                # Connexions par jour
                cursor = conn.execute("""
                    SELECT 
                        DATE(login_time) as date,
                        COUNT(*) as count
                    FROM connection_history
                    WHERE login_time >= ? AND success = 1
                    GROUP BY DATE(login_time)
                    ORDER BY date DESC
                """, (since_date,))
                daily_logins = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'total_connections': total,
                    'failed_attempts': failed,
                    'unique_users': unique_users,
                    'avg_session_duration': int(avg_duration),
                    'success_rate': round((total / (total + failed) * 100) if (total + failed) > 0 else 0, 2),
                    'top_users': top_users,
                    'daily_logins': daily_logins
                }
        
        except Exception as e:
            print(f"❌ Erreur calcul statistiques: {e}")
            return {
                'total_connections': 0,
                'failed_attempts': 0,
                'unique_users': 0,
                'avg_session_duration': 0,
                'success_rate': 0,
                'top_users': [],
                'daily_logins': []
            }
    
    def cleanup_old_records(self, days: int = 90):
        """Nettoyer les anciens enregistrements"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    DELETE FROM connection_history
                    WHERE login_time < ?
                """, (cutoff_date,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                print(f"✅ {deleted_count} enregistrement(s) supprimé(s)")
                return deleted_count
        
        except Exception as e:
            print(f"❌ Erreur nettoyage: {e}")
            return 0

# Instance globale
connection_history = ConnectionHistoryManager()

# ============================================================================
# Intégration dans auth_manager.py
# ============================================================================

"""
AJOUTER CES MODIFICATIONS DANS core/auth_manager.py :

1. Import en haut du fichier:
from core.connection_history import connection_history

2. Dans la méthode authenticate(), après une connexion réussie:
# Enregistrer la connexion dans l'historique
connection_history.record_login(dict(user), success=True)

3. Dans la méthode authenticate(), après un échec:
# Enregistrer l'échec dans l'historique
connection_history.record_login(
    {'id': None, 'username': username, 'full_name': 'Unknown'},
    success=False,
    failure_reason="Invalid credentials"
)

4. Dans la méthode logout():
# Enregistrer la déconnexion
if self.current_user:
    connection_history.record_logout(self.current_user['id'])
"""

if __name__ == "__main__":
    print("🔍 Test du système d'historique de connexion...")
    
    # Test d'initialisation
    connection_history.init_database()
    print("✅ Base de données initialisée")
    
    # Test statistiques
    stats = connection_history.get_statistics(days=30)
    print(f"\n📊 Statistiques (30 derniers jours):")
    print(f"   Total connexions : {stats['total_connections']}")
    print(f"   Échecs           : {stats['failed_attempts']}")
    print(f"   Taux de succès   : {stats['success_rate']}%")
    print(f"   Durée moyenne    : {stats['avg_session_duration']}s")