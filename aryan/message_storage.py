from wezaxy.json_storage import JSONMessageStorage

class MessageStorage:
    def __init__(self):
        self.db = JSONMessageStorage()
    
    def save_message(self, thread_id, sender_id, user_message, ai_reply, sender_username=None):
        """Save a message and its AI reply"""
        return self.db.save_message(thread_id, sender_id, user_message, ai_reply, sender_username)
    
    def get_thread_messages(self, thread_id):
        """Get all messages for a specific thread"""
        return self.db.get_thread_messages(thread_id)
    
    def get_all_threads(self):
        """Get all thread IDs"""
        return self.db.get_all_threads()
    
    def get_thread_info(self, thread_id):
        """Get thread information"""
        return self.db.get_thread_info(thread_id)
    
    def search_messages(self, query):
        """Search messages by content"""
        return self.db.search_messages(query)
    
    def get_all_messages(self, limit=100):
        """Get all messages (admin only)"""
        return self.db.get_all_messages(limit)
    
    def delete_thread(self, thread_id):
        """Delete all messages in a thread"""
        return self.db.delete_thread(thread_id)
