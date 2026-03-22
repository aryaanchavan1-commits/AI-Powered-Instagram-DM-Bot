import json
from datetime import datetime
from aryan_core.tidb_connection import TiDBConnection

class MessageStorage:
    def __init__(self):
        self.db = TiDBConnection()
    
    def save_message(self, thread_id, sender_id, user_message, ai_reply, sender_username=None):
        """Save a message and its AI reply"""
        try:
            self.db.execute_query(
                """INSERT INTO messages (thread_id, sender_id, sender_username, user_message, ai_reply, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (thread_id, sender_id, sender_username, user_message, ai_reply, datetime.now())
            )
            return True
        except Exception as e:
            print(f"Error saving message: {e}")
            return False
    
    def get_thread_messages(self, thread_id):
        """Get all messages for a specific thread"""
        try:
            results = self.db.execute_query(
                "SELECT * FROM messages WHERE thread_id = %s ORDER BY timestamp ASC",
                (thread_id,),
                fetch=True
            )
            return results or []
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    def get_all_threads(self):
        """Get all thread IDs"""
        try:
            results = self.db.execute_query(
                "SELECT DISTINCT thread_id FROM messages ORDER BY timestamp DESC",
                fetch=True
            )
            return [r['thread_id'] for r in results] if results else []
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
            results = self.db.execute_query(
                """SELECT * FROM messages 
                WHERE user_message LIKE %s OR ai_reply LIKE %s 
                ORDER BY timestamp DESC""",
                (f"%{query}%", f"%{query}%"),
                fetch=True
            )
            return results or []
        except Exception as e:
            print(f"Error searching messages: {e}")
            return []
    
    def get_all_messages(self, limit=100):
        """Get all messages (admin only)"""
        try:
            results = self.db.execute_query(
                "SELECT * FROM messages ORDER BY timestamp DESC LIMIT %s",
                (limit,),
                fetch=True
            )
            return results or []
        except Exception as e:
            print(f"Error getting all messages: {e}")
            return []
    
    def delete_thread(self, thread_id):
        """Delete all messages in a thread"""
        try:
            self.db.execute_query(
                "DELETE FROM messages WHERE thread_id = %s",
                (thread_id,)
            )
            return True
        except Exception as e:
            print(f"Error deleting thread: {e}")
            return False
