import mysql.connector
from mysql.connector import Error, pooling
import streamlit as st
import json
from datetime import datetime
import os
import threading

class TiDBConnection:
    _instance = None
    _lock = threading.Lock()
    _connection_pool = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one connection pool exists"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TiDBConnection, cls).__new__(cls)
                    cls._instance.connection = None
                    cls._instance.connect()
        return cls._instance
    
    def __init__(self):
        # Initialization is done in __new__
        pass
    
    def connect(self):
        """Connect to TiDB database"""
        try:
            # Get database URL from Streamlit secrets or environment
            db_url = None
            
            # Try to get from Streamlit secrets first
            try:
                db_url = st.secrets.get("tidb", {}).get("url", "")
            except:
                pass
            
            # If not in secrets, try environment variable
            if not db_url:
                db_url = os.environ.get("TIDB_URL", "")
            
            # If still not found, use default from secrets.toml
            if not db_url:
                try:
                    with open('.streamlit/secrets.toml', 'r') as f:
                        content = f.read()
                        # Parse the URL from secrets.toml
                        for line in content.split('\n'):
                            if 'url = ' in line and 'mysql://' in line:
                                db_url = line.split('url = ')[1].strip().strip('"')
                                break
                except:
                    pass
            
            # If still not found, use hardcoded default (for development)
            if not db_url:
                db_url = "mysql://2r3q7uB1LNoB8ow.root:YOUR_PASSWORD@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/test"
                print("⚠️ Using default TiDB URL - please update .streamlit/secrets.toml with your actual password")
            
            if not db_url:
                print("❌ TiDB URL not found in secrets or environment")
                return False
            
            # Parse the connection string
            # Format: mysql://username:password@host:port/database
            if db_url.startswith("mysql://"):
                db_url = db_url[8:]  # Remove mysql://
            
            # Split into user:password@host:port/database
            if "@" in db_url:
                user_pass, host_port_db = db_url.split("@")
                if ":" in user_pass:
                    username, password = user_pass.split(":")
                else:
                    username = user_pass
                    password = ""
                
                if "/" in host_port_db:
                    host_port, database = host_port_db.split("/")
                else:
                    host_port = host_port_db
                    database = "test"
                
                if ":" in host_port:
                    host, port = host_port.split(":")
                    port = int(port)
                else:
                    host = host_port
                    port = 4000
                
                print(f"🔌 Connecting to TiDB: {host}:{port}/{database}")
                
                # Try connecting with SSL disabled first
                try:
                    self.connection = mysql.connector.connect(
                        host=host,
                        port=port,
                        user=username,
                        password=password,
                        database=database,
                        ssl_disabled=True,
                        connection_timeout=30,
                        autocommit=True
                    )
                    
                    if self.connection.is_connected():
                        print("✅ Connected to TiDB database (SSL disabled)")
                        self._create_tables()
                        return True
                except Error as e:
                    print(f"⚠️ Connection with SSL disabled failed: {e}")
                    
                    # Try with SSL enabled but verify disabled
                    try:
                        self.connection = mysql.connector.connect(
                            host=host,
                            port=port,
                            user=username,
                            password=password,
                            database=database,
                            ssl_ca=None,
                            ssl_verify_cert=False,
                            ssl_verify_identity=False,
                            connection_timeout=30,
                            autocommit=True
                        )
                        
                        if self.connection.is_connected():
                            print("✅ Connected to TiDB database (SSL verify disabled)")
                            self._create_tables()
                            return True
                    except Error as e2:
                        print(f"⚠️ Connection with SSL verify disabled failed: {e2}")
                        
                        # Try with minimal SSL
                        try:
                            self.connection = mysql.connector.connect(
                                host=host,
                                port=port,
                                user=username,
                                password=password,
                                database=database,
                                ssl_ca='',
                                ssl_cert='',
                                ssl_key='',
                                connection_timeout=30,
                                autocommit=True
                            )
                            
                            if self.connection.is_connected():
                                print("✅ Connected to TiDB database (minimal SSL)")
                                self._create_tables()
                                return True
                        except Error as e3:
                            print(f"❌ All connection attempts failed: {e3}")
                            return False
            
            return False
            
        except Error as e:
            print(f"❌ TiDB connection error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username VARCHAR(255) PRIMARY KEY,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    instagram_username VARCHAR(255),
                    instagram_password VARCHAR(255),
                    groq_api_key VARCHAR(255),
                    language VARCHAR(50) DEFAULT 'english',
                    default_message TEXT,
                    auto_reply BOOLEAN DEFAULT TRUE,
                    group_messages BOOLEAN DEFAULT FALSE,
                    personal_info JSON,
                    assistant_name VARCHAR(255) DEFAULT 'Arcavan',
                    assistant_personality VARCHAR(50) DEFAULT 'friendly',
                    assistant_greeting TEXT,
                    history JSON
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    thread_id VARCHAR(255),
                    sender_id VARCHAR(255),
                    sender_username VARCHAR(255),
                    user_message TEXT,
                    ai_reply TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_thread_id (thread_id),
                    INDEX idx_timestamp (timestamp)
                )
            """)
            
            # Admin users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    username VARCHAR(255) PRIMARY KEY,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Authorization table for Instagram auth tokens
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS authorization (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(255) UNIQUE,
                    auth_token TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            # Insert default admin user if not exists
            cursor.execute("""
                INSERT IGNORE INTO admin_users (username, password)
                VALUES ('aryankali1', 'aryankali1')
            """)
            
            self.connection.commit()
            cursor.close()
            print("✅ Tables created/verified")
            
        except Error as e:
            print(f"❌ Error creating tables: {e}")
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a query"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    print("❌ Failed to reconnect to database")
                    return None if fetch else False
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                cursor.close()
                return True
                
        except Error as e:
            print(f"❌ Query execution error: {e}")
            # Try to reconnect
            try:
                if self.connect():
                    cursor = self.connection.cursor(dictionary=True)
                    cursor.execute(query, params or ())
                    if fetch:
                        result = cursor.fetchall()
                        cursor.close()
                        return result
                    else:
                        self.connection.commit()
                        cursor.close()
                        return True
            except:
                pass
            return None if fetch else False
    
    def save_authorization(self, user_id, auth_token):
        """Save authorization token to database"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO authorization (user_id, auth_token)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE auth_token = %s, updated_at = CURRENT_TIMESTAMP
            """, (user_id, auth_token, auth_token))
            
            self.connection.commit()
            cursor.close()
            print(f"✅ Authorization saved for user {user_id}")
            return True
        except Error as e:
            print(f"❌ Error saving authorization: {e}")
            return False
    
    def get_authorization(self, user_id):
        """Get authorization token from database"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT auth_token FROM authorization WHERE user_id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return result['auth_token']
            return None
        except Error as e:
            print(f"❌ Error getting authorization: {e}")
            return None
    
    def delete_authorization(self, user_id):
        """Delete authorization token from database"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute("""
                DELETE FROM authorization WHERE user_id = %s
            """, (user_id,))
            
            self.connection.commit()
            cursor.close()
            print(f"✅ Authorization deleted for user {user_id}")
            return True
        except Error as e:
            print(f"❌ Error deleting authorization: {e}")
            return False
    
    def close(self):
        """Close the connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ TiDB connection closed")
