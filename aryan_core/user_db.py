import json
import bcrypt
from datetime import datetime
from aryan_core.tidb_connection import TiDBConnection

class UserDatabase:
    def __init__(self):
        self.db = TiDBConnection()
    
    def create_user(self, username, password, email=None):
        """Create a new user"""
        try:
            # Check if user exists
            existing = self.db.execute_query(
                "SELECT username FROM users WHERE username = %s",
                (username,),
                fetch=True
            )
            
            if existing:
                return {"success": False, "message": "Username already exists"}
            
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Default personal info
            personal_info = json.dumps({
                "full_name": None,
                "nickname": None,
                "bio": None,
                "profession": None,
                "interests": [],
                "location": None,
                "website": None,
                "contact_email": None,
                "social_links": {}
            })
            
            # Default history
            history = json.dumps([])
            
            # Insert user
            self.db.execute_query(
                """INSERT INTO users (
                    username, password, email, created_at,
                    instagram_username, instagram_password, groq_api_key,
                    language, default_message, auto_reply, group_messages,
                    personal_info, assistant_name, assistant_personality,
                    assistant_greeting, history
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    username, hashed_password.decode('utf-8'), email, datetime.now(),
                    None, None, None, 'english', None, True, False,
                    personal_info, 'Arcavan', 'friendly', None, history
                )
            )
            
            return {"success": True, "message": "User created successfully"}
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return {"success": False, "message": f"Failed to create user: {str(e)}"}
    
    def authenticate_user(self, username, password):
        """Authenticate a user"""
        try:
            result = self.db.execute_query(
                "SELECT * FROM users WHERE username = %s",
                (username,),
                fetch=True
            )
            
            if not result:
                return {"success": False, "message": "User not found"}
            
            user = result[0]
            stored_password = user['password'].encode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                # Parse JSON fields
                if user.get('personal_info'):
                    user['personal_info'] = json.loads(user['personal_info'])
                if user.get('history'):
                    user['history'] = json.loads(user['history'])
                
                return {"success": True, "message": "Authentication successful", "user": user}
            else:
                return {"success": False, "message": "Invalid password"}
                
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return {"success": False, "message": f"Authentication error: {str(e)}"}
    
    def get_user(self, username):
        """Get user information"""
        try:
            result = self.db.execute_query(
                "SELECT * FROM users WHERE username = %s",
                (username,),
                fetch=True
            )
            
            if result:
                user = result[0]
                # Parse JSON fields
                if user.get('personal_info'):
                    user['personal_info'] = json.loads(user['personal_info'])
                if user.get('history'):
                    user['history'] = json.loads(user['history'])
                return user
            return None
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user(self, username, updates):
        """Update user information"""
        try:
            # Build update query
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key == 'personal_info' or key == 'history':
                    value = json.dumps(value)
                set_clauses.append(f"{key} = %s")
                values.append(value)
            
            values.append(username)
            
            query = f"UPDATE users SET {', '.join(set_clauses)} WHERE username = %s"
            self.db.execute_query(query, tuple(values))
            
            return {"success": True, "message": "User updated successfully"}
            
        except Exception as e:
            print(f"Error updating user: {e}")
            return {"success": False, "message": f"Failed to update user: {str(e)}"}
    
    def update_instagram_credentials(self, username, instagram_username, instagram_password):
        """Update Instagram credentials for a user"""
        return self.update_user(username, {
            "instagram_username": instagram_username,
            "instagram_password": instagram_password
        })
    
    def update_groq_api_key(self, username, api_key):
        """Update Groq API key for a user"""
        return self.update_user(username, {"groq_api_key": api_key})
    
    def update_personal_info(self, username, personal_info):
        """Update personal information for a user"""
        return self.update_user(username, {"personal_info": personal_info})
    
    def update_assistant_settings(self, username, assistant_name=None, assistant_personality=None, assistant_greeting=None):
        """Update assistant settings for a user"""
        updates = {}
        if assistant_name is not None:
            updates["assistant_name"] = assistant_name
        if assistant_personality is not None:
            updates["assistant_personality"] = assistant_personality
        if assistant_greeting is not None:
            updates["assistant_greeting"] = assistant_greeting
        
        return self.update_user(username, updates)
    
    def update_settings(self, username, language=None, default_message=None, auto_reply=None, group_messages=None):
        """Update user settings"""
        updates = {}
        if language is not None:
            updates["language"] = language
        if default_message is not None:
            updates["default_message"] = default_message
        if auto_reply is not None:
            updates["auto_reply"] = auto_reply
        if group_messages is not None:
            updates["group_messages"] = group_messages
        
        return self.update_user(username, updates)
    
    def add_history_entry(self, username, entry):
        """Add a history entry for a user"""
        try:
            user = self.get_user(username)
            if not user:
                return {"success": False, "message": "User not found"}
            
            history = user.get('history', [])
            entry["timestamp"] = datetime.now().isoformat()
            history.append(entry)
            
            return self.update_user(username, {"history": history})
            
        except Exception as e:
            print(f"Error adding history entry: {e}")
            return {"success": False, "message": f"Failed to add history entry: {str(e)}"}
    
    def get_user_history(self, username, limit=50):
        """Get user history"""
        user = self.get_user(username)
        if user:
            return user.get('history', [])[-limit:]
        return []
    
    def delete_user(self, username):
        """Delete a user"""
        try:
            self.db.execute_query(
                "DELETE FROM users WHERE username = %s",
                (username,)
            )
            return {"success": True, "message": "User deleted successfully"}
            
        except Exception as e:
            print(f"Error deleting user: {e}")
            return {"success": False, "message": f"Failed to delete user: {str(e)}"}
    
    def get_all_users(self):
        """Get all users (admin only)"""
        try:
            results = self.db.execute_query(
                "SELECT username, email, created_at, instagram_username, language, auto_reply, assistant_name FROM users",
                fetch=True
            )
            return results or []
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def authenticate_admin(self, username, password):
        """Authenticate admin user"""
        try:
            result = self.db.execute_query(
                "SELECT * FROM admin_users WHERE username = %s AND password = %s",
                (username, password),
                fetch=True
            )
            return len(result) > 0
        except Exception as e:
            print(f"Error authenticating admin: {e}")
            return False
