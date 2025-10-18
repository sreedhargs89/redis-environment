#!/usr/bin/env python3
"""
Complex Redis data structures demonstration
Shows hashes, lists, sets, sorted sets with real-world examples
"""

import redis
import json
from datetime import datetime

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

def hash_operations(r):
    """Demonstrate Redis Hash operations - perfect for objects"""
    print("\n🏠 Hash Operations (User Profiles):")
    
    # User profiles as hashes
    users = [
        {"id": "user:1001", "name": "Alice Johnson", "email": "alice@example.com", "age": "28", "city": "New York"},
        {"id": "user:1002", "name": "Bob Smith", "email": "bob@example.com", "age": "35", "city": "San Francisco"},
        {"id": "user:1003", "name": "Carol Davis", "email": "carol@example.com", "age": "42", "city": "Chicago"}
    ]
    
    for user in users:
        user_id = user.pop("id")
        r.hset(user_id, mapping=user)
    
    # Retrieve hash data
    alice = r.hgetall("user:1001")
    print(f"Alice's profile: {alice}")
    
    # Get specific field
    bob_email = r.hget("user:1002", "email")
    print(f"Bob's email: {bob_email}")
    
    # Get multiple fields
    carol_info = r.hmget("user:1003", "name", "city", "age")
    print(f"Carol's info (name, city, age): {carol_info}")

def list_operations(r):
    """Demonstrate Redis List operations - queues, logs, activity feeds"""
    print("\n📋 List Operations (Activity Feed & Queue):")
    
    # Activity feed (recent activities first)
    activities = [
        "User logged in",
        "User viewed product #123",
        "User added item to cart",
        "User updated profile",
        "User logged out"
    ]
    
    # Add activities to feed (most recent first)
    for activity in activities:
        r.lpush("activity_feed", f"{datetime.now().strftime('%H:%M:%S')} - {activity}")
    
    # Get recent activities
    recent = r.lrange("activity_feed", 0, 2)
    print(f"Recent activities: {recent}")
    
    # Task queue demonstration
    tasks = ["process_payment", "send_email", "generate_report", "backup_data"]
    for task in tasks:
        r.rpush("task_queue", task)
    
    # Process tasks (FIFO)
    print("Processing tasks:")
    while r.llen("task_queue") > 0:
        task = r.lpop("task_queue")
        print(f"  Processing: {task}")

def set_operations(r):
    """Demonstrate Redis Set operations - unique collections, tags"""
    print("\n🎯 Set Operations (Tags & Unique Collections):")
    
    # Product tags
    r.sadd("product:123:tags", "electronics", "smartphone", "android", "budget")
    r.sadd("product:124:tags", "electronics", "smartphone", "ios", "premium")
    r.sadd("product:125:tags", "electronics", "laptop", "gaming", "premium")
    
    # User interests
    r.sadd("user:1001:interests", "electronics", "gaming", "photography")
    r.sadd("user:1002:interests", "electronics", "smartphone", "music")
    
    # Get all tags for a product
    tags_123 = r.smembers("product:123:tags")
    print(f"Product 123 tags: {tags_123}")
    
    # Find common tags between products
    common_tags = r.sinter("product:123:tags", "product:124:tags")
    print(f"Common tags between products 123 & 124: {common_tags}")
    
    # Find users interested in electronics
    electronics_users = []
    for user_key in r.keys("user:*:interests"):
        if r.sismember(user_key, "electronics"):
            user_id = user_key.split(":")[1]
            electronics_users.append(user_id)
    print(f"Users interested in electronics: {electronics_users}")

def sorted_set_operations(r):
    """Demonstrate Redis Sorted Set operations - leaderboards, rankings"""
    print("\n🏆 Sorted Set Operations (Leaderboards & Rankings):")
    
    # Game leaderboard (score as the sort key)
    players = [
        ("Alice", 1500),
        ("Bob", 2200),
        ("Carol", 1800),
        ("David", 2500),
        ("Eve", 1900),
        ("Frank", 2100)
    ]
    
    for player, score in players:
        r.zadd("game_leaderboard", {player: score})
    
    # Get top players
    top_players = r.zrevrange("game_leaderboard", 0, 2, withscores=True)
    print("Top 3 players:")
    for i, (player, score) in enumerate(top_players, 1):
        print(f"  {i}. {player}: {int(score)} points")
    
    # Get player rank
    alice_rank = r.zrevrank("game_leaderboard", "Alice")
    print(f"Alice's rank: #{alice_rank + 1}")
    
    # Product popularity (views as score)
    products = [
        ("product:123", 500),
        ("product:124", 1200),
        ("product:125", 300),
        ("product:126", 800),
        ("product:127", 1500)
    ]
    
    for product, views in products:
        r.zadd("popular_products", {product: views})
    
    # Most popular products
    popular = r.zrevrange("popular_products", 0, 2, withscores=True)
    print("\nMost popular products:")
    for product, views in popular:
        print(f"  {product}: {int(views)} views")

def advanced_operations(r):
    """Demonstrate advanced operations and patterns"""
    print("\n🚀 Advanced Operations:")
    
    # Pub/Sub pattern simulation (using lists for demo)
    channels = ["news", "sports", "tech"]
    for channel in channels:
        r.lpush(f"channel:{channel}", f"Latest update from {channel}")
    
    # Bulk operations with pipeline
    pipe = r.pipeline()
    for i in range(10):
        pipe.set(f"bulk_key:{i}", f"value_{i}")
    pipe.execute()
    print("Created 10 keys using pipeline")
    
    # Pattern matching
    bulk_keys = r.keys("bulk_key:*")
    print(f"Found {len(bulk_keys)} bulk keys")
    
    # Memory usage info
    info = r.info("memory")
    print(f"Redis memory usage: {info.get('used_memory_human', 'N/A')}")

def main():
    r = connect_to_redis()
    if not r:
        return
    
    # Clear any existing data for clean demo
    r.flushdb()
    print("🧹 Cleared database for clean demo")
    
    print("🏗️  Demonstrating Complex Redis Data Structures")
    
    # Run demonstrations
    hash_operations(r)
    list_operations(r)
    set_operations(r)
    sorted_set_operations(r)
    advanced_operations(r)
    
    # Show database stats
    print(f"\n📊 Database Statistics:")
    print(f"Total keys: {r.dbsize()}")
    print(f"All keys: {r.keys('*')[:10]}{'...' if r.dbsize() > 10 else ''}")

if __name__ == "__main__":
    main()