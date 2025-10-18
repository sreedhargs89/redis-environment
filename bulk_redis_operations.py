#!/usr/bin/env python3
"""
Bulk Redis operations and performance demonstration
Loads thousands of records and shows query patterns
"""

import redis
import json
import time
from faker import Faker
import random

fake = Faker()

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

def generate_sample_users(count=1000):
    """Generate sample user data"""
    users = []
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
    departments = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Support"]
    
    for i in range(count):
        user = {
            "id": i + 1,
            "name": fake.name(),
            "email": fake.email(),
            "age": random.randint(22, 65),
            "city": random.choice(cities),
            "department": random.choice(departments),
            "salary": random.randint(40000, 150000),
            "join_date": fake.date_between(start_date='-5y', end_date='today').isoformat(),
            "active": str(random.choice([True, False]))
        }
        users.append(user)
    return users

def bulk_insert_users(r, users, method="pipeline"):
    """Bulk insert users using different methods"""
    print(f"\n📦 Bulk Inserting {len(users)} users using {method}...")
    
    start_time = time.time()
    
    if method == "pipeline":
        # Using pipeline for batch operations
        pipe = r.pipeline()
        for user in users:
            user_key = f"user:{user['id']}"
            # Store as hash
            pipe.hset(user_key, mapping=user)
            # Add to city index
            pipe.sadd(f"city:{user['city']}:users", user['id'])
            # Add to department index
            pipe.sadd(f"dept:{user['department']}:users", user['id'])
            # Add to salary sorted set
            pipe.zadd("users_by_salary", {user['id']: user['salary']})
            # Add to age sorted set
            pipe.zadd("users_by_age", {user['id']: user['age']})
        
        pipe.execute()
        
    elif method == "individual":
        # Individual operations (slower)
        for user in users:
            user_key = f"user:{user['id']}"
            r.hset(user_key, mapping=user)
            r.sadd(f"city:{user['city']}:users", user['id'])
            r.sadd(f"dept:{user['department']}:users", user['id'])
            r.zadd("users_by_salary", {user['id']: user['salary']})
            r.zadd("users_by_age", {user['id']: user['age']})
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Inserted {len(users)} users in {duration:.2f} seconds")
    print(f"📊 Rate: {len(users)/duration:.0f} users/second")
    
    return duration

def query_performance_tests(r):
    """Demonstrate various query patterns and their performance"""
    print("\n🔍 Query Performance Tests:")
    
    # Test 1: Get single user
    start = time.time()
    user = r.hgetall("user:500")
    duration = time.time() - start
    print(f"1. Single user lookup: {duration*1000:.2f}ms - {user['name']} ({user['department']})")
    
    # Test 2: Get users from specific city
    start = time.time()
    ny_users = r.smembers("city:New York:users")
    duration = time.time() - start
    print(f"2. Users in New York: {len(ny_users)} users in {duration*1000:.2f}ms")
    
    # Test 3: Get top earners
    start = time.time()
    top_earners = r.zrevrange("users_by_salary", 0, 9, withscores=True)
    duration = time.time() - start
    print(f"3. Top 10 earners query: {duration*1000:.2f}ms")
    for i, (user_id, salary) in enumerate(top_earners[:3], 1):
        name = r.hget(f"user:{user_id}", "name")
        print(f"   {i}. {name}: ${int(salary):,}")
    
    # Test 4: Age range query
    start = time.time()
    young_professionals = r.zrangebyscore("users_by_age", 25, 35)
    duration = time.time() - start
    print(f"4. Users aged 25-35: {len(young_professionals)} users in {duration*1000:.2f}ms")
    
    # Test 5: Department statistics
    start = time.time()
    dept_stats = {}
    departments = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Support"]
    
    for dept in departments:
        count = r.scard(f"dept:{dept}:users")
        dept_stats[dept] = count
    
    duration = time.time() - start
    print(f"5. Department statistics: {duration*1000:.2f}ms")
    for dept, count in dept_stats.items():
        print(f"   {dept}: {count} users")

def pattern_matching_queries(r):
    """Demonstrate pattern matching and complex queries"""
    print("\n🎯 Pattern Matching & Complex Queries:")
    
    # Find all user keys
    start = time.time()
    user_keys = r.keys("user:*")
    duration = time.time() - start
    print(f"1. Pattern matching (user:*): {len(user_keys)} keys in {duration*1000:.2f}ms")
    
    # Find all city indexes
    city_keys = r.keys("city:*:users")
    cities = [key.split(":")[1] for key in city_keys]
    print(f"2. Cities with users: {cities}")
    
    # Complex query: High earners in specific city
    start = time.time()
    # Get users in San Francisco
    sf_users = r.smembers("city:San Francisco:users")
    # Get high earners (top 20%)
    total_users = r.zcard("users_by_salary")
    high_earner_threshold = int(total_users * 0.8)
    high_earners = r.zrevrange("users_by_salary", 0, high_earner_threshold)
    
    # Find intersection
    sf_high_earners = set(sf_users).intersection(set(high_earners))
    duration = time.time() - start
    
    print(f"3. High earners in San Francisco: {len(sf_high_earners)} users in {duration*1000:.2f}ms")
    
    # Show details for a few
    for user_id in list(sf_high_earners)[:3]:
        user = r.hgetall(f"user:{user_id}")
        salary = r.zscore("users_by_salary", user_id)
        print(f"   {user['name']}: ${int(salary):,} ({user['department']})")

def memory_and_stats(r):
    """Show Redis memory usage and statistics"""
    print("\n📊 Redis Statistics & Memory Usage:")
    
    # Basic stats
    info = r.info()
    print(f"Redis version: {info['redis_version']}")
    print(f"Connected clients: {info['connected_clients']}")
    print(f"Total keys: {r.dbsize()}")
    
    # Memory info
    memory_info = r.info("memory")
    print(f"Used memory: {memory_info['used_memory_human']}")
    print(f"Peak memory: {memory_info['used_memory_peak_human']}")
    
    # Key statistics by type
    key_types = {}
    sample_keys = r.keys("*")[:100]  # Sample for performance
    for key in sample_keys:
        key_type = r.type(key)
        key_types[key_type] = key_types.get(key_type, 0) + 1
    
    print("Key types (sample):")
    for key_type, count in key_types.items():
        print(f"  {key_type}: {count}")

def cleanup_demo_data(r):
    """Clean up demo data"""
    print("\n🧹 Cleaning up demo data...")
    
    # Delete all user-related keys
    keys_to_delete = []
    keys_to_delete.extend(r.keys("user:*"))
    keys_to_delete.extend(r.keys("city:*"))
    keys_to_delete.extend(r.keys("dept:*"))
    keys_to_delete.extend(r.keys("users_by_*"))
    
    if keys_to_delete:
        deleted = r.delete(*keys_to_delete)
        print(f"Deleted {deleted} keys")
    else:
        print("No demo data found to delete")

def main():
    r = connect_to_redis()
    if not r:
        return
    
    print("🚀 Redis Bulk Operations & Performance Demo")
    print("=" * 50)
    
    # Ask user for data size
    try:
        user_count = int(input("Enter number of users to generate (default 2000): ") or "2000")
    except ValueError:
        user_count = 2000
    
    # Generate sample data
    print(f"\n📋 Generating {user_count} sample users...")
    users = generate_sample_users(user_count)
    print(f"✅ Generated {len(users)} users")
    
    # Compare insertion methods
    print("\n⚡ Comparing insertion methods:")
    
    # Test pipeline method
    r.flushdb()
    pipeline_time = bulk_insert_users(r, users, "pipeline")
    
    # Show current state
    print(f"\n📊 Database now contains {r.dbsize()} keys")
    
    # Run query performance tests
    query_performance_tests(r)
    pattern_matching_queries(r)
    memory_and_stats(r)
    
    print("\n✨ Demo complete! Check Redis Insight at http://localhost:8001")
    print("\n📌 Data remains in Redis for exploration in Redis Insight")

if __name__ == "__main__":
    main()