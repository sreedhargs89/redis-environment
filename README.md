

### 1. Start Redis and Redis Insight
```bash
docker-compose up -d
```

This starts:
- Redis server on `localhost:6379`
- Redis Insight dashboard on `http://localhost:8001`

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Demonstrations

#### Simple Operations (Strings, Counters, JSON)
```bash
python3 simple_redis_operations.py
```

#### Complex Data Structures (Hashes, Lists, Sets, Sorted Sets)
```bash
python3 complex_redis_operations.py
```

#### Bulk Operations (Thousands of Records)
```bash
python3 bulk_redis_operations.py
```

## What You'll Learn

### Simple Operations
- **String Operations**: Basic key-value storage, TTL (Time To Live)
- **Counters**: Atomic increment/decrement operations
- **JSON Storage**: Storing structured data as strings

### Complex Data Structures
- **Hashes**: Perfect for objects (user profiles, product details)
- **Lists**: Activity feeds, task queues, recent items
- **Sets**: Unique collections, tags, user interests
- **Sorted Sets**: Leaderboards, rankings, time-based data

### Performance & Scale
- **Pipeline Operations**: Batch processing for better performance
- **Indexing Patterns**: Secondary indexes using sets
- **Query Performance**: Sub-millisecond response times
- **Memory Efficiency**: Optimized data structures

## Redis Insight Dashboard

Access the Redis Insight dashboard at `http://localhost:8001`

### Features Demonstrated:
1. **Browser**: Explore all keys and data structures visually
2. **Workbench**: Run Redis commands interactively
3. **Analysis**: Memory usage and key statistics
4. **Monitoring**: Real-time performance metrics

### Connecting to Redis in Insight:
1. Open `http://localhost:8001`
2. Click "Add Database"
3. Enter:
   - Host: `redis-server` (or `localhost`)
   - Port: `6379`
   - Database Alias: `Redis Learning`

## Data Patterns Demonstrated

### User Management System
```
user:{id}                 -> Hash with user details
city:{city}:users        -> Set of user IDs in each city
dept:{department}:users  -> Set of user IDs in each department
users_by_salary         -> Sorted set ranked by salary
users_by_age           -> Sorted set ranked by age
```

### E-commerce Patterns
```
product:{id}:tags       -> Set of product tags
popular_products       -> Sorted set by view count
activity_feed         -> List of recent activities
task_queue           -> List used as FIFO queue
```

## Performance Results

With 5,000 user records:
- **Insertion Rate**: ~26,000 records/second (using pipeline)
- **Single Lookup**: ~0.3ms
- **Range Query**: ~1.2ms
- **Pattern Matching**: ~3.7ms
- **Memory Usage**: ~4.75MB

## Redis Commands Cheat Sheet

### Basic Operations
```bash
SET key value          # Store string
GET key               # Retrieve string
DEL key               # Delete key
EXISTS key            # Check if key exists
TTL key               # Get time to live
```

### Hashes
```bash
HSET user:1 name "John" age 30
HGET user:1 name
HGETALL user:1
```

### Lists
```bash
LPUSH queue task1     # Push to front
RPOP queue           # Pop from back
LRANGE queue 0 -1    # Get all items
```

### Sets
```bash
SADD tags:product1 electronics mobile
SMEMBERS tags:product1
SINTER tags:product1 tags:product2
```

### Sorted Sets
```bash
ZADD leaderboard 100 player1 200 player2
ZREVRANGE leaderboard 0 2 WITHSCORES
ZRANK leaderboard player1
```

## Cleanup

To stop and remove all containers:
```bash
docker-compose down
```

To also remove the data volumes:
```bash
docker-compose down -v
```

## Next Steps

1. Explore the Redis Insight dashboard
2. Try different query patterns
3. Experiment with Redis pub/sub
4. Learn about Redis modules (RedisJSON, RedisGraph, etc.)
5. Study Redis clustering and high availability

## Useful Resources

- [Redis Documentation](https://redis.io/docs/)
- [Redis Commands](https://redis.io/commands/)
- [Redis Best Practices](https://redis.io/docs/management/optimization/)
- [Redis Data Types](https://redis.io/docs/data-types/)
