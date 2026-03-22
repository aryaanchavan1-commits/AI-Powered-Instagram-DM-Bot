from aryan.json_storage import JSONUserStorage

class UserDatabase:
    def __init__(self):
        self.db = JSONUserStorage()
    
    def create_user(self, username, password, email=None):
        """Create a new user"""
        return self.db.create_user(username, password, email)
    
    def authenticate_user(self, username, password):
        """Authenticate a user"""
        return self.db.authenticate_user(username, password)
    
    def get_user(self, username):
        """Get user information"""
        return self.db.get_user(username)
    
    def update_user(self, username, updates):
        """Update user information"""
        return self.db.update_user(username, updates)
    
    def update_instagram_credentials(self, username, instagram_username, instagram_password):
        """Update Instagram credentials for a user"""
        return self.db.update_instagram_credentials(username, instagram_username, instagram_password)
    
    def update_groq_api_key(self, username, api_key):
        """Update Groq API key for a user"""
        return self.db.update_groq_api_key(username, api_key)
    
    def update_personal_info(self, username, personal_info):
        """Update personal information for a user"""
        return self.db.update_personal_info(username, personal_info)
    
    def update_assistant_settings(self, username, assistant_name=None, assistant_personality=None, assistant_greeting=None):
        """Update assistant settings for a user"""
        return self.db.update_assistant_settings(username, assistant_name, assistant_personality, assistant_greeting)
    
    def update_settings(self, username, language=None, default_message=None, auto_reply=None, group_messages=None):
        """Update user settings"""
        return self.db.update_settings(username, language, default_message, auto_reply, group_messages)
    
    def add_history_entry(self, username, entry):
        """Add a history entry for a user"""
        return self.db.add_history_entry(username, entry)
    
    def get_user_history(self, username, limit=50):
        """Get user history"""
        return self.db.get_user_history(username, limit)
    
    def delete_user(self, username):
        """Delete a user"""
        return self.db.delete_user(username)
    
    def get_all_users(self):
        """Get all users (admin only)"""
        return self.db.get_all_users()
    
    def authenticate_admin(self, username, password):
        """Authenticate admin user"""
        return self.db.authenticate_admin(username, password)
