import json
import bcrypt
from datetime import datetime
import os

class JSONAuthorizationStorage:
    def __init__(self, filepath="Authorization.json"):
        self.filepath = filepath
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the JSON file exists"""
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump({}, f)
    
    def _load_data(self):
        """Load data from JSON file"""
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, data):
        """Save data to JSON file"""
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def save_authorization(self, user_id, auth_token):
        """Save authorization token to JSON file"""
        try:
            data = self._load_data()
            data[user_id] = {
                "auth_token": auth_token,
                "updated_at": datetime.now().isoformat()
            }
            self._save_data(data)
            print(f"✅ Authorization saved for user {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error saving authorization: {e}")
            return False
    
    def get_authorization(self, user_id):
        """Get authorization token from JSON file"""
        try:
            data = self._load_data()
            user_data = data.get(user_id)
            if user_data:
                return user_data.get('auth_token')
            return None
        except Exception as e:
            print(f"❌ Error getting authorization: {e}")
            return None
    
    def delete_authorization(self, user_id):
        """Delete authorization token from JSON file"""
        try:
            data = self._load_data()
            if user_id in data:
                del data[user_id]
                self._save_data(data)
                print(f"✅ Authorization deleted for user {user_id}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error deleting authorization: {e}")
            return False

class JSONUserStorage:
    def __init__(self, filepath="users.json"):
        self.filepath = filepath
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the JSON file exists"""
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump({}, f)
    
    def _load_data(self):
        """Load data from JSON file"""
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, data):
        """Save data to JSON file"""
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def create_user(self, username, password, email=None):
        """Create a new user"""
        try:
            data = self._load_data()
            
            # Check if user exists
            if username in data:
                return {"success": False, "message": "Username already exists"}
            
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Create user object
            user = {
                "username": username,
                "password": hashed_password.decode('utf-8'),
                "email": email,
                "created_at": datetime.now().isoformat(),
                "instagram_username": None,
                "instagram_password": None,
                "groq_api_key": None,
                "language": "english",
                "default_message": None,
                "auto_reply": True,
                "group_messages": False,
                "assistant_name": "Arcavan",
                "assistant_personality": "friendly",
                "assistant_greeting": None,
                "history": []
            }
            
            # Save user
            data[username] = user
            self._save_data(data)
            
            return {"success": True, "message": "User created successfully"}
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return {"success": False, "message": f"Failed to create user: {str(e)}"}
    
    def authenticate_user(self, username, password):
        """Authenticate a user"""
        try:
            data = self._load_data()
            
            if username not in data:
                return {"success": False, "message": "User not found"}
            
            user = data[username]
            stored_password = user['password'].encode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                return {"success": True, "message": "Authentication successful", "user": user}
            else:
                return {"success": False, "message": "Invalid password"}
                
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return {"success": False, "message": f"Authentication error: {str(e)}"}
    
    def get_user(self, username):
        """Get user information"""
        try:
            data = self._load_data()
            return data.get(username)
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user(self, username, updates):
        """Update user information"""
        try:
            data = self._load_data()
            
            if username not in data:
                return {"success": False, "message": "User not found"}
            
            # Update user fields
            for key, value in updates.items():
                data[username][key] = value
            
            self._save_data(data)
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
        # Note: personal_info field not used in current implementation
        return {"success": True, "message": "Personal info update not supported"}
    
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
            data = self._load_data()
            
            if username not in data:
                return {"success": False, "message": "User not found"}
            
            entry["timestamp"] = datetime.now().isoformat()
            data[username]["history"].append(entry)
            
            self._save_data(data)
            return {"success": True, "message": "History entry added successfully"}
            
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
            data = self._load_data()
            
            if username in data:
                del data[username]
                self._save_data(data)
                return {"success": True, "message": "User deleted successfully"}
            else:
                return {"success": False, "message": "User not found"}
            
        except Exception as e:
            print(f"Error deleting user: {e}")
            return {"success": False, "message": f"Failed to delete user: {str(e)}"}
    
    def get_all_users(self):
        """Get all users (admin only)"""
        try:
            data = self._load_data()
            users = []
            for username, user in data.items():
                users.append({
                    "username": username,
                    "email": user.get("email"),
                    "created_at": user.get("created_at"),
                    "instagram_username": user.get("instagram_username"),
                    "language": user.get("language"),
                    "auto_reply": user.get("auto_reply"),
                    "assistant_name": user.get("assistant_name")
                })
            return users
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def authenticate_admin(self, username, password):
        """Authenticate admin user"""
        # Default admin credentials
        if username == "aryankali1" and password == "aryankali1":
            return True
        return False


class JSONMessageStorage:
    def __init__(self, filepath="chat.json"):
        self.filepath = filepath
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the JSON file exists"""
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump({}, f)
    
    def _load_data(self):
        """Load data from JSON file"""
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, data):
        """Save data to JSON file"""
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def save_message(self, thread_id, sender_id, user_message, ai_reply, sender_username=None):
        """Save a message and its AI reply"""
        try:
            data = self._load_data()
            
            # Initialize thread if it doesn't exist
            if thread_id not in data:
                data[thread_id] = []
            
            # Create message object
            message = {
                "id": len(data[thread_id]) + 1,
                "thread_id": thread_id,
                "sender_id": sender_id,
                "sender_username": sender_username,
                "user_message": user_message,
                "ai_reply": ai_reply,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add message to thread
            data[thread_id].append(message)
            self._save_data(data)
            
            return True
        except Exception as e:
            print(f"Error saving message: {e}")
            return False
    
    def get_thread_messages(self, thread_id):
        """Get all messages for a specific thread"""
        try:
            data = self._load_data()
            return data.get(thread_id, [])
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    def get_all_threads(self):
        """Get all thread IDs"""
        try:
            data = self._load_data()
            return list(data.keys())
        except Exception as e:
            print(f"Error getting threads: {e}")
            return []
    
    def get_thread_info(self, thread_id):
        """Get thread information"""
        try:
            messages = self.get_thread_messages(thread_id)
            return {
                "thread_id": thread_id,
                "messages": messages
            }
        except Exception as e:
            print(f"Error getting thread info: {e}")
            return {}
    
    def search_messages(self, query):
        """Search messages by content"""
        try:
            data = self._load_data()
            results = []
            
            for thread_id, messages in data.items():
                for message in messages:
                    if (query.lower() in message.get('user_message', '').lower() or 
                        query.lower() in message.get('ai_reply', '').lower()):
                        results.append(message)
            
            # Sort by timestamp descending
            results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return results
        except Exception as e:
            print(f"Error searching messages: {e}")
            return []
    
    def get_all_messages(self, limit=100):
        """Get all messages (admin only)"""
        try:
            data = self._load_data()
            all_messages = []
            
            for thread_id, messages in data.items():
                all_messages.extend(messages)
            
            # Sort by timestamp descending
            all_messages.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return all_messages[:limit]
        except Exception as e:
            print(f"Error getting all messages: {e}")
            return []
    
    def delete_thread(self, thread_id):
        """Delete all messages in a thread"""
        try:
            data = self._load_data()
            
            if thread_id in data:
                del data[thread_id]
                self._save_data(data)
                return True
            return False
        except Exception as e:
            print(f"Error deleting thread: {e}")
            return False
