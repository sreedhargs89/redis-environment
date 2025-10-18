#!/usr/bin/env python3
"""
Simple Redis operations demonstration
Shows basic string operations, counters, and expiration
"""

import redis
import time
import json

def connect_to_redis():
    """Connect to Redis server"""
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        print("✅ Connected to Redis successfully!")
        return r
    except redis.ConnectionError:
        print("❌ Could not connect to Redis. Make sure it's running on localhost:6379")
        return None

def simple_string_operations(r):
    """Demonstrate basic string operations"""
    print("\n🔤 Simple String Operations:")
    
    # Basic set/get
    r.set("user:name", "John Doe")
    r.set("user:email", "john@example.com")
    r.set("user:age", 30)
    
    print(f"Name: {r.get('user:name')}")
    print(f"Email: {r.get('user:email')}")
    print(f"Age: {r.get('user:age')}")
    
    # String with expiration (TTL)
    r.setex("session:abc123", 60, "user_session_data")
    ttl = r.ttl("session:abc123")
    print(f"Session TTL: {ttl} seconds")

def counter_operations(r):
    """Demonstrate counter operations"""
    print("\n🔢 Counter Operations:")
    
    # Initialize counters
    r.set("page_views", 0)
    r.set("user_logins", 0)
    
    # Increment operations
    for i in range(5):
        r.incr("page_views")
        r.incr("user_logins", 2)  # increment by 2
    
    print(f"Page views: {r.get('page_views')}")
    print(f"User logins: {r.get('user_logins')}")

def json_like_storage(r):
    """Store JSON-like data as strings"""
    print("\n📄 JSON Data Storage:")
    
    user_data = {
        "id": 1001,
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "preferences": {
            "theme": "dark",
            "language": "en",
            "notifications": True
        }
    }
    
    # Store as JSON string
    r.set("user:1001", json.dumps(user_data))
    
    # Retrieve and parse
    retrieved = json.loads(r.get("user:1001"))
    print(f"Retrieved user: {retrieved['name']}")
    print(f"Theme preference: {retrieved['preferences']['theme']}")

def main():
    r = connect_to_redis()
    if not r:
        return
    
    # Clear any existing data for clean demo
    r.flushdb()
    print("🧹 Cleared database for clean demo")
    
    # Run demonstrations
    simple_string_operations(r)
    counter_operations(r)
    json_like_storage(r)
    
    # Show all keys
    print(f"\n🔑 All keys in database: {r.keys('*')}")
    print(f"📊 Total keys: {r.dbsize()}")

if __name__ == "__main__":
    main()