#!/usr/bin/env python3
"""
E-commerce Redis Patterns - Amazon-like use cases
Demonstrates real-world Redis usage in e-commerce platforms
"""

import redis
import json
import time
from datetime import datetime, timedelta
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

def session_management(r):
    """1. SESSION MANAGEMENT - User sessions, shopping carts"""
    print("\n🛒 1. SESSION MANAGEMENT (Shopping Cart & User Sessions)")
    
    # User session data
    session_id = "sess_abc123def456"
    user_data = {
        "user_id": "12345",
        "username": "john_doe",
        "email": "john@example.com",
        "login_time": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat(),
        "preferences": json.dumps({"theme": "dark", "language": "en"})
    }
    
    # Store session with 30 minutes expiry
    r.hset(f"session:{session_id}", mapping=user_data)
    r.expire(f"session:{session_id}", 1800)  # 30 minutes
    
    # Shopping cart - stores product IDs and quantities
    cart_items = {
        "product_123": "2",  # 2 units of product 123
        "product_456": "1",  # 1 unit of product 456
        "product_789": "3"   # 3 units of product 789
    }
    r.hset(f"cart:{session_id}", mapping=cart_items)
    r.expire(f"cart:{session_id}", 86400)  # 24 hours
    
    print(f"Session stored: {r.hgetall(f'session:{session_id}')}")
    print(f"Cart items: {r.hgetall(f'cart:{session_id}')}")

def caching_layer(r):
    """2. CACHING - Product details, search results, API responses"""
    print("\n⚡ 2. CACHING LAYER (Product Details & Search Results)")
    
    # Product details cache
    product_data = {
        "id": "PROD_123",
        "name": "iPhone 15 Pro",
        "price": 999.99,
        "description": "Latest iPhone with amazing features",
        "category": "Electronics",
        "brand": "Apple",
        "stock": 50,
        "rating": 4.8,
        "reviews_count": 1250
    }
    
    # Cache product for 1 hour
    r.setex(f"product:PROD_123", 3600, json.dumps(product_data))
    
    # Search results cache
    search_results = {
        "query": "iphone",
        "total_results": 156,
        "products": ["PROD_123", "PROD_124", "PROD_125"],
        "filters": {"brand": ["Apple", "Samsung"], "price_range": [100, 2000]},
        "cached_at": datetime.now().isoformat()
    }
    
    # Cache search results for 15 minutes
    r.setex("search:iphone:page:1", 900, json.dumps(search_results))
    
    # API response cache (e.g., payment gateway response)
    api_response = {"status": "success", "payment_methods": ["card", "paypal", "apple_pay"]}
    r.setex("api:payment_methods:v1", 7200, json.dumps(api_response))
    
    print(f"Cached product: {json.loads(r.get('product:PROD_123'))['name']}")
    print(f"Search cache TTL: {r.ttl('search:iphone:page:1')} seconds")

def real_time_inventory(r):
    """3. REAL-TIME INVENTORY - Stock tracking, reservation"""
    print("\n📦 3. REAL-TIME INVENTORY TRACKING")
    
    # Product inventory tracking
    products = ["PROD_123", "PROD_456", "PROD_789", "PROD_101", "PROD_202"]
    
    for product_id in products:
        initial_stock = random.randint(10, 100)
        r.set(f"inventory:{product_id}", initial_stock)
    
    # Simulate real-time stock updates
    print("Initial inventory:")
    for product_id in products[:3]:
        stock = r.get(f"inventory:{product_id}")
        print(f"  {product_id}: {stock} units")
    
    # Simulate purchase - atomic decrement
    product_to_buy = "PROD_123"
    quantity = 3
    
    # Use Lua script for atomic inventory check and decrement
    lua_script = """
    local key = KEYS[1]
    local quantity = tonumber(ARGV[1])
    local current_stock = tonumber(redis.call('GET', key) or 0)
    
    if current_stock >= quantity then
        redis.call('DECRBY', key, quantity)
        return {1, current_stock - quantity}
    else
        return {0, current_stock}
    end
    """
    
    result = r.eval(lua_script, 1, f"inventory:{product_to_buy}", quantity)
    if result[0] == 1:
        print(f"✅ Purchase successful! {product_to_buy}: {result[1]} units remaining")
    else:
        print(f"❌ Insufficient stock! Only {result[1]} units available")
    
    # Low stock alerts using sorted sets
    for product_id in products:
        stock = int(r.get(f"inventory:{product_id}"))
        if stock < 20:
            r.zadd("low_stock_alerts", {product_id: stock})
    
    low_stock = r.zrange("low_stock_alerts", 0, -1, withscores=True)
    if low_stock:
        print("⚠️  Low stock alerts:")
        for product, stock in low_stock:
            print(f"  {product}: {int(stock)} units left")

def recommendations_and_analytics(r):
    """4. RECOMMENDATIONS & ANALYTICS - User behavior, product recommendations"""
    print("\n🎯 4. RECOMMENDATIONS & USER ANALYTICS")
    
    # User behavior tracking
    user_id = "user_12345"
    
    # Recently viewed products (List - FIFO with max length)
    recently_viewed = ["PROD_123", "PROD_456", "PROD_789", "PROD_101"]
    for product in recently_viewed:
        r.lpush(f"recent_views:{user_id}", product)
        r.ltrim(f"recent_views:{user_id}", 0, 9)  # Keep only last 10 items
    
    # User interests/categories (Set for unique values)
    interests = ["Electronics", "Books", "Clothing", "Sports"]
    for interest in interests:
        r.sadd(f"interests:{user_id}", interest)
    
    # Product popularity tracking (Sorted Set)
    popular_products = [
        ("PROD_123", 1500), ("PROD_456", 1200), ("PROD_789", 900),
        ("PROD_101", 800), ("PROD_202", 600)
    ]
    for product, views in popular_products:
        r.zadd("popular_products", {product: views})
    
    # Collaborative filtering - users who bought this also bought
    # Using sets for fast intersections
    r.sadd("bought:PROD_123", "user_1", "user_2", "user_3", "user_100")
    r.sadd("bought:PROD_456", "user_2", "user_3", "user_4", "user_200")
    
    # Find similar users
    similar_users = r.sinter("bought:PROD_123", "bought:PROD_456")
    
    print(f"Recently viewed: {r.lrange(f'recent_views:{user_id}', 0, 4)}")
    print(f"User interests: {r.smembers(f'interests:{user_id}')}")
    print(f"Top products: {r.zrevrange('popular_products', 0, 2, withscores=True)}")
    print(f"Users who bought both products: {similar_users}")

def rate_limiting_and_security(r):
    """5. RATE LIMITING & SECURITY - API throttling, fraud detection"""
    print("\n🔒 5. RATE LIMITING & SECURITY")
    
    # API rate limiting - sliding window
    api_key = "api_key_abc123"
    current_minute = int(time.time() / 60)
    
    # Allow 100 requests per minute per API key
    rate_limit_key = f"rate_limit:{api_key}:{current_minute}"
    current_count = r.incr(rate_limit_key)
    r.expire(rate_limit_key, 60)  # Expire after 60 seconds
    
    if current_count <= 100:
        print(f"✅ API request allowed ({current_count}/100 this minute)")
    else:
        print(f"❌ Rate limit exceeded ({current_count}/100)")
    
    # Failed login attempts tracking
    user_ip = "192.168.1.100"
    failed_attempts = r.incr(f"failed_login:{user_ip}")
    r.expire(f"failed_login:{user_ip}", 3600)  # Reset after 1 hour
    
    if failed_attempts >= 5:
        r.setex(f"blocked_ip:{user_ip}", 7200, "blocked")  # Block for 2 hours
        print(f"🚫 IP {user_ip} blocked after {failed_attempts} failed attempts")
    
    # Fraud detection - unusual activity patterns
    user_id = "user_12345"
    
    # Track rapid purchases
    purchase_key = f"purchases:{user_id}:{int(time.time() / 300)}"  # 5-minute windows
    purchase_count = r.incr(purchase_key)
    r.expire(purchase_key, 300)
    
    if purchase_count > 10:  # More than 10 purchases in 5 minutes
        r.sadd("fraud_alerts", user_id)
        print(f"🚨 Fraud alert: User {user_id} made {purchase_count} purchases in 5 minutes")

def real_time_features(r):
    """6. REAL-TIME FEATURES - Live inventory, flash sales, notifications"""
    print("\n🔴 6. REAL-TIME FEATURES")
    
    # Flash sale countdown
    flash_sale = {
        "product_id": "PROD_FLASH_001",
        "original_price": 199.99,
        "sale_price": 99.99,
        "quantity_available": 50,
        "sale_end_time": (datetime.now() + timedelta(hours=2)).isoformat()
    }
    
    r.hset("flash_sale:current", mapping=flash_sale)
    r.expire("flash_sale:current", 7200)  # 2 hours
    
    # Live inventory updates using pub/sub pattern (simulated with lists)
    inventory_updates = [
        {"product": "PROD_123", "stock": 45, "action": "purchase"},
        {"product": "PROD_456", "stock": 78, "action": "restock"},
        {"product": "PROD_789", "stock": 12, "action": "purchase"}
    ]
    
    for update in inventory_updates:
        r.lpush("inventory_updates", json.dumps(update))
    
    # User notifications queue
    notifications = [
        {"user_id": "user_123", "type": "price_drop", "message": "Item in your wishlist is now 20% off!"},
        {"user_id": "user_456", "type": "back_in_stock", "message": "iPhone 15 is back in stock!"},
        {"user_id": "user_789", "type": "order_shipped", "message": "Your order has been shipped!"}
    ]
    
    for notification in notifications:
        user_id = notification["user_id"]
        r.lpush(f"notifications:{user_id}", json.dumps(notification))
        r.ltrim(f"notifications:{user_id}", 0, 49)  # Keep only last 50 notifications
    
    # Geographic data for shipping/delivery
    try:
        r.geoadd("warehouses", (-74.0059, 40.7128, "NYC_WAREHOUSE"))  # New York
        r.geoadd("warehouses", (-118.2437, 34.0522, "LA_WAREHOUSE"))   # Los Angeles
        r.geoadd("warehouses", (-87.6298, 41.8781, "CHI_WAREHOUSE"))   # Chicago
    except Exception as e:
        print(f"Geographic data setup failed: {e}")
        # Use simpler approach
        r.hset("warehouses", "NYC", "New York")
        r.hset("warehouses", "LA", "Los Angeles")
        r.hset("warehouses", "CHI", "Chicago")
    
    # Find nearest warehouse to customer location
    customer_location = (-73.9857, 40.7484)  # Customer in Manhattan
    try:
        nearest = r.georadius("warehouses", customer_location[0], customer_location[1], 500, "mi", withdist=True, count=1)
    except Exception as e:
        print(f"Geographic search not available: {e}")
        nearest = None
    
    print(f"Flash sale: {r.hget('flash_sale:current', 'product_id')} - ${r.hget('flash_sale:current', 'sale_price')}")
    print(f"Inventory updates in queue: {r.llen('inventory_updates')}")
    print(f"Notifications for user_123: {r.llen('notifications:user_123')}")
    if nearest:
        print(f"Nearest warehouse: {nearest[0][0]} ({nearest[0][1]:.1f} miles away)")

def search_and_filters(r):
    """7. SEARCH & FILTERING - Auto-complete, faceted search"""
    print("\n🔍 7. SEARCH & FILTERING")
    
    # Auto-complete suggestions using sorted sets
    search_terms = [
        "iphone", "iphone 15", "iphone 15 pro", "iphone case", "iphone charger",
        "samsung", "samsung galaxy", "samsung s24", "laptop", "laptop bag",
        "headphones", "wireless headphones", "bluetooth headphones"
    ]
    
    # Build auto-complete index
    for term in search_terms:
        # Add prefixes for auto-complete
        for i in range(1, len(term) + 1):
            prefix = term[:i].lower()
            r.zadd("autocomplete", {f"{prefix}*{term}": 0})
    
    # Search for auto-complete suggestions
    search_query = "iph"
    suggestions = []
    results = r.zrange("autocomplete", 0, -1)
    for result in results:
        if result.startswith(search_query.lower()):
            suggestion = result.split('*')[1]
            if suggestion not in suggestions:
                suggestions.append(suggestion)
            if len(suggestions) >= 5:
                break
    
    print(f"Auto-complete for '{search_query}': {suggestions}")
    
    # Product filters using sets
    # Category filter
    r.sadd("category:Electronics", "PROD_123", "PROD_456", "PROD_789")
    r.sadd("category:Books", "PROD_201", "PROD_202", "PROD_203")
    r.sadd("category:Clothing", "PROD_301", "PROD_302", "PROD_303")
    
    # Brand filter
    r.sadd("brand:Apple", "PROD_123", "PROD_124", "PROD_125")
    r.sadd("brand:Samsung", "PROD_456", "PROD_457", "PROD_458")
    
    # Price range filter using sorted sets
    r.zadd("price_range", {"PROD_123": 999, "PROD_456": 799, "PROD_789": 299, "PROD_124": 1199})
    
    # Complex filter query: Electronics AND Apple AND price between 500-1000
    electronics_products = r.smembers("category:Electronics")
    apple_products = r.smembers("brand:Apple")
    
    # Find intersection
    filtered_products = electronics_products.intersection(apple_products)
    
    # Apply price filter
    price_filtered = []
    for product in filtered_products:
        price = r.zscore("price_range", product)
        if price and 500 <= price <= 1000:
            price_filtered.append(product)
    
    print(f"Filtered products (Electronics + Apple + $500-1000): {price_filtered}")

def analytics_and_reporting(r):
    """8. ANALYTICS & REPORTING - Daily metrics, user behavior"""
    print("\n📊 8. ANALYTICS & REPORTING")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Daily metrics
    daily_metrics = {
        "page_views": 15420,
        "unique_visitors": 8930,
        "orders": 234,
        "revenue": 45670.50,
        "bounce_rate": 0.32
    }
    
    for metric, value in daily_metrics.items():
        r.hset(f"daily_metrics:{today}", metric, value)
        # Also add to time series for trending
        r.zadd(f"timeseries:{metric}", {today: value})
    
    # User behavior funnel
    funnel_data = {
        "visitors": 10000,
        "product_views": 7500,
        "add_to_cart": 2000,
        "checkout": 500,
        "purchase": 234
    }
    
    r.hset("funnel:today", mapping=funnel_data)
    
    # Top performing products (by revenue)
    top_products = [
        ("PROD_123", 12500.00),
        ("PROD_456", 8900.00),
        ("PROD_789", 6700.00),
        ("PROD_101", 5400.00),
        ("PROD_202", 4200.00)
    ]
    
    for product, revenue in top_products:
        r.zadd(f"top_products:{today}", {product: revenue})
    
    print(f"Daily metrics: {r.hgetall(f'daily_metrics:{today}')}")
    print(f"Conversion funnel: {funnel_data['purchase']}/{funnel_data['visitors']} = {(funnel_data['purchase']/funnel_data['visitors']*100):.1f}%")
    print(f"Top product today: {r.zrevrange(f'top_products:{today}', 0, 0, withscores=True)}")

def main():
    r = connect_to_redis()
    if not r:
        return
    
    print("🛍️  E-COMMERCE REDIS PATTERNS - AMAZON-LIKE USE CASES")
    print("=" * 60)
    
    # Clear database for clean demo
    r.flushdb()
    print("🧹 Cleared database for clean demo")
    
    # Run all demonstrations
    session_management(r)
    caching_layer(r)
    real_time_inventory(r)
    recommendations_and_analytics(r)
    rate_limiting_and_security(r)
    real_time_features(r)
    search_and_filters(r)
    analytics_and_reporting(r)
    
    # Final statistics
    print(f"\n📊 Final Database Statistics:")
    print(f"Total keys created: {r.dbsize()}")
    
    # Show memory usage
    info = r.info("memory")
    print(f"Memory used: {info.get('used_memory_human', 'N/A')}")
    
    print(f"\n✨ Demo complete! Check Redis Insight at http://localhost:8001")

if __name__ == "__main__":
    main()