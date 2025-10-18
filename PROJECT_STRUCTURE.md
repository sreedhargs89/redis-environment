# Project Structure 📁

## Overview
This Redis learning environment provides a comprehensive setup for understanding Redis from basic concepts to advanced e-commerce implementations.

## File Structure

```
redis-learning-environment/
├── README.md                     # Main project documentation
├── REDIS_INTERVIEW_GUIDE.md      # Comprehensive interview preparation
├── PROJECT_STRUCTURE.md          # This file - project organization
├── requirements.txt               # Python dependencies
├── docker-compose.yml            # Docker setup for Redis + Redis Insight
├── .gitignore                    # Git ignore patterns
│
├── simple_redis_operations.py    # Basic Redis operations demo
├── complex_redis_operations.py   # Advanced data structures demo  
├── bulk_redis_operations.py      # Performance testing with bulk data
└── ecommerce_redis_patterns.py   # Real-world e-commerce patterns
```

## File Descriptions

### Configuration Files
- **`docker-compose.yml`**: Sets up Redis server (port 6379) and Redis Insight dashboard (port 8001)
- **`requirements.txt`**: Python dependencies (redis, faker)
- **`.gitignore`**: Excludes temporary files, Python cache, and Redis data files

### Documentation
- **`README.md`**: Quick start guide and feature overview
- **`REDIS_INTERVIEW_GUIDE.md`**: In-depth interview preparation with 60+ questions and practical examples
- **`PROJECT_STRUCTURE.md`**: This file explaining the project organization

### Demo Scripts

#### 1. `simple_redis_operations.py`
**Purpose**: Introduction to basic Redis operations
**Features**:
- String operations (SET, GET, INCR)
- TTL (Time To Live) examples
- Counter implementations
- JSON data storage patterns

**Run**: `python3 simple_redis_operations.py`

#### 2. `complex_redis_operations.py`
**Purpose**: Advanced Redis data structures
**Features**:
- **Hashes**: User profiles, object storage
- **Lists**: Activity feeds, task queues, FIFO/LIFO operations
- **Sets**: Tags, unique collections, intersections
- **Sorted Sets**: Leaderboards, rankings, score-based queries
- **Pipeline operations**: Batch processing for performance

**Run**: `python3 complex_redis_operations.py`

#### 3. `bulk_redis_operations.py`
**Purpose**: Performance testing and scalability demonstration
**Features**:
- Bulk data insertion (thousands of records)
- Performance benchmarking
- Query optimization techniques
- Memory usage analysis
- Complex query patterns

**Run**: `python3 bulk_redis_operations.py`

#### 4. `ecommerce_redis_patterns.py`
**Purpose**: Real-world e-commerce applications (Amazon-like patterns)
**Features**:
- **Session Management**: User sessions, shopping carts
- **Caching Layer**: Product details, search results, API responses
- **Real-time Inventory**: Stock tracking, atomic operations
- **Recommendations**: User behavior, collaborative filtering
- **Rate Limiting**: API throttling, security measures
- **Real-time Features**: Flash sales, notifications, geographic data
- **Search & Filtering**: Auto-complete, faceted search
- **Analytics**: Metrics, reporting, conversion funnels

**Run**: `python3 ecommerce_redis_patterns.py`

## Usage Scenarios

### Learning Path
1. **Beginner**: Start with `simple_redis_operations.py`
2. **Intermediate**: Progress to `complex_redis_operations.py`
3. **Advanced**: Explore `bulk_redis_operations.py` for performance
4. **Expert**: Study `ecommerce_redis_patterns.py` for real-world applications

### Interview Preparation
1. **Read**: `REDIS_INTERVIEW_GUIDE.md` for comprehensive Q&A
2. **Practice**: Run demo scripts to understand practical implementations
3. **Experiment**: Modify scripts to test different scenarios
4. **Explore**: Use Redis Insight dashboard to visualize data structures

### Development Reference
- **Patterns**: Copy and adapt patterns from `ecommerce_redis_patterns.py`
- **Performance**: Reference bulk operations for optimization techniques
- **Architecture**: Use as a foundation for Redis-based system design

## Data Patterns Demonstrated

### E-commerce Platform (Amazon-style)
```
Sessions & Cart:
session:abc123        -> Hash (user data, preferences)
cart:abc123          -> Hash (product_id -> quantity)

Product Catalog:
product:123          -> JSON string (cached product details)
search:query:page:1  -> JSON string (cached search results)

Inventory Management:
inventory:PROD123    -> String (stock count)
low_stock_alerts     -> Sorted Set (product_id -> stock_level)

User Behavior:
recent_views:user123 -> List (recently viewed products)
interests:user123    -> Set (user interest categories)
popular_products     -> Sorted Set (product_id -> view_count)

Security & Rate Limiting:
rate_limit:api_key:minute -> String (request counter)
failed_login:ip           -> String (failed attempt counter)
blocked_ip:ip            -> String (block status)

Real-time Features:
flash_sale:current       -> Hash (sale details)
notifications:user123    -> List (user notifications queue)
inventory_updates        -> List (real-time inventory changes)

Analytics:
daily_metrics:2024-01-01 -> Hash (page views, orders, revenue)
funnel:today            -> Hash (conversion funnel data)
top_products:2024-01-01 -> Sorted Set (product_id -> revenue)
```

### Performance Benchmarks
- **Insertion Rate**: 25,000+ records/second using pipelines
- **Query Performance**: Sub-millisecond response times
- **Memory Efficiency**: ~2.18MB for 2,000 user records
- **Scalability**: Handles thousands of concurrent operations

## Redis Insight Dashboard
Access at `http://localhost:8001` after running `docker-compose up -d`

### Features to Explore
1. **Browser**: Visual exploration of all keys and data types
2. **Workbench**: Interactive Redis command execution
3. **Analysis**: Memory usage breakdown and key statistics
4. **Profiler**: Real-time command monitoring

### Sample Queries to Try
```bash
# User data exploration
HGETALL user:1
LRANGE recent_views:user_12345 0 9
SMEMBERS interests:user_12345

# E-commerce patterns
ZREVRANGE popular_products 0 9 WITHSCORES
ZREVRANGE users_by_salary 0 9 WITHSCORES
SMEMBERS "city:New York:users"

# Performance testing
INFO memory
DBSIZE
KEYS pattern*
```

## Extension Ideas

### Add New Patterns
- **Message Queues**: Implement pub/sub patterns
- **Distributed Locks**: Add mutex implementations
- **Time Series**: Add metric collection patterns
- **Graph Data**: Implement social network patterns

### Performance Enhancements
- **Clustering**: Add Redis Cluster examples
- **Replication**: Demonstrate master-slave setup
- **Persistence**: Add RDB and AOF configuration examples
- **Memory Optimization**: Add compression and eviction examples

### Production Readiness
- **Monitoring**: Add Redis metrics collection
- **Security**: Implement authentication and SSL
- **Backup**: Add data backup and recovery scripts
- **High Availability**: Add Sentinel configuration

## Contributing
Feel free to add new patterns, optimize existing code, or enhance documentation. This project is designed to be a comprehensive learning resource for the Redis community.

## Resources
- [Redis Official Documentation](https://redis.io/docs/)
- [Redis Commands Reference](https://redis.io/commands/)
- [Redis Best Practices](https://redis.io/docs/management/optimization/)
- [Redis Design Patterns](https://redis.com/redis-best-practices/)