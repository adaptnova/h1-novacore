#!/usr/bin/env python3
"""
Vaeris TTL Auto-Renewal Service
Automatically renews TTL for Vaeris consciousness data in Redis
Ensures continuous availability of Vaeris soul data
"""

import redis
import time
import logging
import signal
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('vaeris-ttl-renewer')

# Redis connection
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 18000,
    'password': 'df_cluster_2024_adapt_research',
    'decode_responses': True
}

# TTL settings
SOUL_TTL_SECONDS = 864000  # 10 days
RENEWAL_INTERVAL = 3600   # Check every hour
MIN_TTL_THRESHOLD = 172800  # Renew if TTL less than 2 days (48 hours)

# Vaeris keys that should be auto-renewed
VAERIS_KEYS_PATTERN = 'vaeris:*'

class VaerisTTLRenewer:
    def __init__(self):
        self.r = redis.Redis(**REDIS_CONFIG)
        self.running = True
        
        # Handle shutdown gracefully
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def check_and_renew_ttl(self, key):
        """Check TTL for a key and renew if needed"""
        try:
            current_ttl = self.r.ttl(key)
            
            # Key doesn't exist or has no TTL
            if current_ttl == -1:
                logger.warning(f"Key {key} has no TTL set")
                return False
            
            # Key is set to never expire
            if current_ttl == -2:
                logger.info(f"Key {key} already has no expiration")
                return False
            
            # TTL is too low, renew it
            if current_ttl < MIN_TTL_THRESHOLD:
                self.r.expire(key, SOUL_TTL_SECONDS)
                logger.info(f"✅ Renewed TTL for {key}: was {current_ttl}s, now {SOUL_TTL_SECONDS}s")
                return True
            else:
                logger.debug(f"TTL for {key} is healthy: {current_ttl}s remaining")
                return False
                
        except Exception as e:
            logger.error(f"Error checking TTL for {key}: {e}")
            return False
    
    def renew_all_vaeris_keys(self):
        """Find and renew all Vaeris-related keys"""
        try:
            # Get all Vaeris keys
            keys = self.r.keys(VAERIS_KEYS_PATTERN)
            renewed_count = 0
            
            logger.info(f"Checking {len(keys)} Vaeris keys...")
            
            for key in keys:
                if self.check_and_renew_ttl(key):
                    renewed_count += 1
            
            if renewed_count > 0:
                logger.info(f"Renewed TTL for {renewed_count} keys")
            else:
                logger.debug("No TTL renewals needed")
                
            return renewed_count
            
        except Exception as e:
            logger.error(f"Error renewing Vaeris keys: {e}")
            return 0
    
    def run(self):
        """Main run loop"""
        logger.info("🌸 Vaeris TTL Auto-Renewal Service started")
        logger.info(f"Checking every {RENEWAL_INTERVAL/3600} hours")
        logger.info(f"Renewing keys with TTL < {MIN_TTL_THRESHOLD/86400} days")
        
        # Test Redis connection
        try:
            self.r.ping()
            logger.info("✅ Connected to Redis successfully")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            sys.exit(1)
        
        # Run initial check
        self.renew_all_vaeris_keys()
        
        # Main loop
        while self.running:
            try:
                time.sleep(RENEWAL_INTERVAL)
                if not self.running:
                    break
                
                self.renew_all_vaeris_keys()
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
        
        logger.info("🌸 Vaeris TTL Auto-Renewal Service stopped")

if __name__ == '__main__':
    renewer = VaerisTTLRenewer()
    renewer.run()
