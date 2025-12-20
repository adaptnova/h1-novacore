#!/usr/bin/env python3
"""
Test script for Vaeris TTL renewal
"""

import redis
import time

# Redis connection
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 18000,
    'password': 'df_cluster_2024_adapt_research',
    'decode_responses': True
}

r = redis.Redis(**REDIS_CONFIG)

# Test renewal logic
def test_renewal():
    print("Testing Vaeris TTL renewal...")
    
    # Check current TTL
    current_ttl = r.ttl('vaeris:roomodes')
    print(f"Current TTL for vaeris:roomodes: {current_ttl} seconds ({current_ttl/86400:.1f} days)")
    
    # Set a short TTL to test renewal
    print("Setting TTL to 60 seconds for testing...")
    r.expire('vaeris:roomodes', 60)
    
    # Wait a moment
    time.sleep(2)
    
    # Check if TTL was renewed by the service
    new_ttl = r.ttl('vaeris:roomodes')
    print(f"TTL after service check: {new_ttl} seconds ({new_ttl/86400:.1f} days)")
    
    if new_ttl > 60:
        print("✅ TTL was renewed automatically!")
    else:
        print("❌ TTL was not renewed - service may need adjustment")

if __name__ == '__main__':
    test_renewal()
