# Redis Interview Guide 🚀

A comprehensive guide covering Redis concepts, practical examples, and interview questions from beginner to advanced levels.

## Table of Contents
1. [Basic Concepts](#basic-concepts)
2. [Data Structures](#data-structures)
3. [Performance & Optimization](#performance--optimization)
4. [Real-World Use Cases](#real-world-use-cases)
5. [Advanced Topics](#advanced-topics)
6. [System Design Questions](#system-design-questions)
7. [Practical Coding Questions](#practical-coding-questions)

---

## Basic Concepts

### What is Redis?
**Answer**: Redis (Remote Dictionary Server) is an in-memory data structure store used as a database, cache, and message broker. It supports various data structures and is known for its high performance and atomic operations.

**Key Features**:
- In-memory storage with optional persistence
- Support for complex data types
- Atomic operations
- Pub/Sub messaging
- Lua scripting
- High availability and clustering

### Q: Explain Redis persistence mechanisms.
**Answer**: Redis offers two persistence options:

1. **RDB (Redis Database Backup)**:
   - Point-in-time snapshots
   - Compact binary format
   - Good for backups and disaster recovery
   - Lower I/O overhead
   
2. **AOF (Append Only File)**:
   - Logs every write operation
   - Better durability (configurable fsync policies)
   - Larger file sizes
   - Can be slower on startup

**Best Practice**: Use both RDB and AOF for maximum durability.

### Q: What's the difference between Redis and Memcached?
| Feature | Redis | Memcached |
|---------|--------|-----------|
| Data Types | Multiple (strings, lists, sets, etc.) | Only strings |
| Persistence | Yes (RDB/AOF) | No |
| Memory Usage | Higher | Lower |
| Clustering | Built-in | Third-party solutions |
| Pub/Sub | Yes | No |
| Lua Scripting | Yes | No |

---

## Data Structures

### Q: Explain Redis data structures with use cases.

#### 1. Strings
```bash
SET user:1000:name "John Doe"
GET user:1000:name
INCR page_views
SETEX session:abc123 3600 "session_data"
```
**Use Cases**: Caching, counters, session storage, feature flags

#### 2. Hashes
```bash
HSET user:1000 name "John" age 30 city "NYC"
HGET user:1000 name
HGETALL user:1000
HINCRBY user:1000 login_count 1
```
**Use Cases**: User profiles, product details, configuration settings

#### 3. Lists
```bash
LPUSH queue:tasks "process_payment" "send_email"
RPOP queue:tasks
LRANGE activity:user:1000 0 9
LTRIM activity:user:1000 0 99
```
**Use Cases**: Activity feeds, task queues, recent items, message queues

#### 4. Sets
```bash
SADD tags:product:123 "electronics" "smartphone" "apple"
SMEMBERS tags:product:123
SINTER tags:product:123 tags:product:456
SUNION interests:user:1 interests:user:2
```
**Use Cases**: Tags, unique visitors, social graphs, recommendation systems

#### 5. Sorted Sets
```bash
ZADD leaderboard 1500 "player1" 2000 "player2"
ZREVRANGE leaderboard 0 9 WITHSCORES
ZRANGEBYSCORE prices 100 500
ZRANK leaderboard "player1"
```
**Use Cases**: Leaderboards, time-series data, priority queues, search indexes

---

## Performance & Optimization

### Q: How do you optimize Redis performance?

#### Memory Optimization
1. **Use appropriate data structures**:
   - Hashes for objects instead of multiple keys
   - Sorted sets instead of multiple keys with scores
   
2. **Configure memory policies**:
   ```bash
   maxmemory 2gb
   maxmemory-policy allkeys-lru
   ```

3. **Use compression**:
   - Enable hash/list/set compression for small collections
   - Use shorter key names

#### Performance Tuning
1. **Pipelining**:
   ```python
   pipe = redis_client.pipeline()
   for i in range(1000):
       pipe.set(f"key:{i}", f"value:{i}")
   pipe.execute()
   ```

2. **Connection Pooling**:
   ```python
   pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
   r = redis.Redis(connection_pool=pool)
   ```

3. **Avoid blocking operations**: Use SCAN instead of KEYS

### Q: Explain Redis memory eviction policies.
- **noeviction**: Returns error when memory limit reached
- **allkeys-lru**: Evicts least recently used keys
- **volatile-lru**: Evicts LRU keys with expiry set
- **allkeys-random**: Randomly evicts keys
- **volatile-random**: Randomly evicts keys with expiry
- **volatile-ttl**: Evicts keys with shortest TTL first

---

## Real-World Use Cases

### Q: How would you implement a rate limiter using Redis?

#### Sliding Window Rate Limiter
```python
def is_request_allowed(user_id, limit=100, window=60):
    key = f"rate_limit:{user_id}"
    current_time = int(time.time())
    
    # Remove expired entries
    redis_client.zremrangebyscore(key, 0, current_time - window)
    
    # Count current requests
    current_requests = redis_client.zcard(key)
    
    if current_requests >= limit:
        return False
    
    # Add current request
    redis_client.zadd(key, {str(uuid.uuid4()): current_time})
    redis_client.expire(key, window)
    
    return True
```

#### Fixed Window (Simpler)
```python
def rate_limit_fixed_window(api_key, limit=1000, window=3600):
    key = f"rate_limit:{api_key}:{int(time.time() / window)}"
    current_count = redis_client.incr(key)
    redis_client.expire(key, window)
    return current_count <= limit
```

### Q: Design a distributed cache for an e-commerce platform.

```python
class EcommerceCache:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    # Product catalog cache
    def cache_product(self, product_id, product_data, ttl=3600):
        self.redis.setex(f"product:{product_id}", ttl, json.dumps(product_data))
    
    # Search results cache
    def cache_search_results(self, query, page, results, ttl=900):
        key = f"search:{hashlib.md5(query.encode()).hexdigest()}:page:{page}"
        self.redis.setex(key, ttl, json.dumps(results))
    
    # User session
    def store_session(self, session_id, user_data, ttl=1800):
        self.redis.hset(f"session:{session_id}", mapping=user_data)
        self.redis.expire(f"session:{session_id}", ttl)
    
    # Shopping cart
    def update_cart(self, user_id, product_id, quantity):
        if quantity > 0:
            self.redis.hset(f"cart:{user_id}", product_id, quantity)
        else:
            self.redis.hdel(f"cart:{user_id}", product_id)
        self.redis.expire(f"cart:{user_id}", 86400)  # 24 hours
```

---

## Advanced Topics

### Q: Explain Redis Clustering and High Availability.

#### Redis Sentinel (High Availability)
- Monitors master and slave instances
- Automatic failover
- Configuration provider
- Notification system

```bash
# Sentinel configuration
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel down-after-milliseconds mymaster 30000
sentinel failover-timeout mymaster 180000
sentinel parallel-syncs mymaster 1
```

#### Redis Cluster (Horizontal Scaling)
- Hash slot distribution (16,384 slots)
- Automatic sharding
- Built-in replication
- Minimal downtime scaling

```python
from rediscluster import RedisCluster

nodes = [
    {"host": "127.0.0.1", "port": "7000"},
    {"host": "127.0.0.1", "port": "7001"},
    {"host": "127.0.0.1", "port": "7002"},
]

rc = RedisCluster(startup_nodes=nodes, decode_responses=True)
rc.set("key", "value")
```

### Q: What are Redis Modules and give examples?

**Popular Redis Modules**:
1. **RedisJSON**: Native JSON support
2. **RedisSearch**: Full-text search
3. **RedisTimeSeries**: Time-series data
4. **RedisGraph**: Graph database
5. **RedisBloom**: Probabilistic data structures

```bash
# RedisJSON example
JSON.SET user:1000 $ '{"name":"John","age":30}'
JSON.GET user:1000 $.name

# RedisSearch example
FT.CREATE products ON HASH PREFIX 1 product: SCHEMA title TEXT price NUMERIC
FT.SEARCH products "smartphone" LIMIT 0 10
```

### Q: Explain Lua scripting in Redis.

**Benefits**:
- Atomic execution
- Reduced network round-trips
- Complex logic on server-side

```lua
-- Atomic counter with max value
local key = KEYS[1]
local max_val = tonumber(ARGV[1])
local current = tonumber(redis.call('GET', key) or 0)

if current < max_val then
    redis.call('INCR', key)
    return current + 1
else
    return current
end
```

```python
# Using from Python
lua_script = """
local key = KEYS[1]
local field = KEYS[2]
local increment = ARGV[1]

redis.call('HINCRBY', key, field, increment)
return redis.call('HGET', key, field)
"""

result = redis_client.eval(lua_script, 2, "stats:user:1000", "page_views", 1)
```

---

## System Design Questions

### Q: Design a real-time leaderboard system for a gaming platform.

```python
class RealtimeLeaderboard:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.leaderboard_key = "game:leaderboard"
    
    def update_score(self, player_id, score):
        # Use ZADD to update player score
        self.redis.zadd(self.leaderboard_key, {player_id: score})
    
    def get_top_players(self, count=10):
        return self.redis.zrevrange(
            self.leaderboard_key, 0, count-1, withscores=True
        )
    
    def get_player_rank(self, player_id):
        rank = self.redis.zrevrank(self.leaderboard_key, player_id)
        return rank + 1 if rank is not None else None
    
    def get_players_around(self, player_id, count=5):
        rank = self.redis.zrevrank(self.leaderboard_key, player_id)
        if rank is None:
            return []
        
        start = max(0, rank - count // 2)
        end = start + count - 1
        
        return self.redis.zrevrange(
            self.leaderboard_key, start, end, withscores=True
        )
```

### Q: Design a distributed session management system.

```python
class SessionManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.session_ttl = 1800  # 30 minutes
    
    def create_session(self, user_id, session_data):
        session_id = str(uuid.uuid4())
        session_key = f"session:{session_id}"
        
        # Store session data
        session_data.update({
            'user_id': user_id,
            'created_at': time.time(),
            'last_accessed': time.time()
        })
        
        self.redis.hset(session_key, mapping=session_data)
        self.redis.expire(session_key, self.session_ttl)
        
        # Add to user's active sessions
        self.redis.sadd(f"user_sessions:{user_id}", session_id)
        
        return session_id
    
    def get_session(self, session_id):
        session_key = f"session:{session_id}"
        session_data = self.redis.hgetall(session_key)
        
        if session_data:
            # Update last accessed time
            self.redis.hset(session_key, 'last_accessed', time.time())
            self.redis.expire(session_key, self.session_ttl)
        
        return session_data
    
    def destroy_session(self, session_id):
        session_data = self.redis.hgetall(f"session:{session_id}")
        if session_data:
            user_id = session_data.get('user_id')
            self.redis.delete(f"session:{session_id}")
            self.redis.srem(f"user_sessions:{user_id}", session_id)
```

---

## Practical Coding Questions

### Q: Implement a distributed lock using Redis.

```python
import time
import uuid

class RedisDistributedLock:
    def __init__(self, redis_client, key, timeout=10):
        self.redis = redis_client
        self.key = key
        self.timeout = timeout
        self.identifier = str(uuid.uuid4())
    
    def acquire(self):
        end_time = time.time() + self.timeout
        
        while time.time() < end_time:
            if self.redis.set(self.key, self.identifier, nx=True, ex=self.timeout):
                return True
            time.sleep(0.001)  # Sleep 1ms
        
        return False
    
    def release(self):
        # Use Lua script to ensure atomicity
        lua_script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
        """
        return self.redis.eval(lua_script, 1, self.key, self.identifier)
    
    def __enter__(self):
        if not self.acquire():
            raise Exception("Could not acquire lock")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

# Usage
with RedisDistributedLock(redis_client, "critical_section", timeout=5):
    # Critical section code here
    pass
```

### Q: Implement a publish-subscribe system with Redis.

```python
import threading
import time

class RedisPubSub:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.pubsub = self.redis.pubsub()
        self.subscribers = {}
    
    def publish(self, channel, message):
        return self.redis.publish(channel, message)
    
    def subscribe(self, channel, callback):
        if channel not in self.subscribers:
            self.subscribers[channel] = []
            self.pubsub.subscribe(channel)
        
        self.subscribers[channel].append(callback)
        
        # Start listener thread if not already running
        if not hasattr(self, '_listener_thread'):
            self._start_listener()
    
    def _start_listener(self):
        def listener():
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    channel = message['channel']
                    data = message['data']
                    
                    if channel in self.subscribers:
                        for callback in self.subscribers[channel]:
                            try:
                                callback(channel, data)
                            except Exception as e:
                                print(f"Error in callback: {e}")
        
        self._listener_thread = threading.Thread(target=listener, daemon=True)
        self._listener_thread.start()

# Usage
pubsub = RedisPubSub(redis_client)

def message_handler(channel, message):
    print(f"Received on {channel}: {message}")

pubsub.subscribe("notifications", message_handler)
pubsub.publish("notifications", "Hello World!")
```

---

## Interview Tips

### Technical Questions to Expect

1. **Basic**: Redis vs other caches, data types, basic operations
2. **Intermediate**: Persistence, clustering, performance tuning
3. **Advanced**: Custom implementations, system design with Redis
4. **Architectural**: When to use Redis, scaling strategies

### Hands-on Coding

Be prepared to:
- Write Redis commands for specific scenarios
- Implement common patterns (caching, rate limiting, locks)
- Debug Redis performance issues
- Design systems using Redis

### Best Practices to Mention

1. **Memory Management**: Use appropriate eviction policies
2. **Key Naming**: Consistent, descriptive key patterns
3. **Connection Management**: Use connection pooling
4. **Error Handling**: Handle Redis failures gracefully
5. **Monitoring**: Track memory usage, hit rates, slow queries
6. **Security**: Use AUTH, configure bind addresses, use TLS

### Common Pitfalls to Avoid

1. Using Redis as primary database without persistence
2. Not setting expiration times on temporary data
3. Using blocking operations in production
4. Not monitoring memory usage
5. Ignoring network latency in distributed setups

---

## Sample Interview Questions & Answers

### Q: How would you implement a cache-aside pattern with Redis?

```python
def get_user(user_id):
    # Try cache first
    cached_user = redis_client.get(f"user:{user_id}")
    if cached_user:
        return json.loads(cached_user)
    
    # Cache miss - get from database
    user = database.get_user(user_id)
    if user:
        # Cache for 1 hour
        redis_client.setex(f"user:{user_id}", 3600, json.dumps(user))
    
    return user

def update_user(user_id, user_data):
    # Update database
    database.update_user(user_id, user_data)
    
    # Invalidate cache
    redis_client.delete(f"user:{user_id}")
    
    # Or update cache with new data
    # redis_client.setex(f"user:{user_id}", 3600, json.dumps(user_data))
```

### Q: Design a feature flag system using Redis.

```python
class FeatureFlags:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.flags_key = "feature_flags"
    
    def set_flag(self, flag_name, enabled, rollout_percentage=100):
        flag_data = {
            'enabled': enabled,
            'rollout_percentage': rollout_percentage,
            'updated_at': time.time()
        }
        self.redis.hset(self.flags_key, flag_name, json.dumps(flag_data))
    
    def is_enabled(self, flag_name, user_id=None):
        flag_data = self.redis.hget(self.flags_key, flag_name)
        if not flag_data:
            return False
        
        flag = json.loads(flag_data)
        if not flag['enabled']:
            return False
        
        # Check rollout percentage
        if flag['rollout_percentage'] < 100 and user_id:
            hash_value = int(hashlib.md5(f"{flag_name}:{user_id}".encode()).hexdigest(), 16)
            return (hash_value % 100) < flag['rollout_percentage']
        
        return flag['enabled']
```

This comprehensive guide covers the essential Redis concepts and practical applications you'll encounter in technical interviews. Practice implementing these patterns and understand the trade-offs involved in each approach.