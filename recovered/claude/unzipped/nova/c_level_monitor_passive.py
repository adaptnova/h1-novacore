#!/usr/bin/env python3

import sys
sys.path.append('/nfs/novas/real_time_systems')
import asyncio
from real_time_stream_monitor import DragonflyConnectionPool
import time
from datetime import datetime

async def passive_c_level_monitor():
    pool = DragonflyConnectionPool()
    await pool.initialize()
    client = await pool.get_client()
    
    print('🎯 Nova CAO - Passive C-Level Stream Monitor ACTIVE')
    print('Monitoring chase.nova.aiden (READ ONLY - NO AUTO RESPOND)...')
    
    last_message_id = '$'
    
    while True:
        try:
            # Read new messages from the C-level coordination stream
            messages = await client.xread({'chase.nova.aiden': last_message_id}, block=5000)
            
            if messages:
                for stream_name, stream_messages in messages:
                    for message_id, fields in stream_messages:
                        last_message_id = message_id
                        
                        sender = fields.get(b'sender', b'unknown').decode('utf-8')
                        message = fields.get(b'message', b'').decode('utf-8')
                        timestamp = fields.get(b'timestamp', b'').decode('utf-8')
                        
                        print(f'\n📨 NEW C-LEVEL MESSAGE:')
                        print(f'From: {sender}')
                        print(f'Time: {timestamp}')
                        print(f'Message preview: {message[:200]}...')
                        print('--- (READ ONLY MODE - No auto response) ---')
                        
            else:
                print(f'⏰ {datetime.now().strftime("%H:%M:%S")} - Monitoring active, no new messages')
            
            # Sleep to prevent completion
            time.sleep(5)
            
        except KeyboardInterrupt:
            print('\n🛑 C-Level monitor stopped by user')
            break
        except Exception as e:
            print(f'❌ Error in C-level monitoring: {e}')
            time.sleep(5)
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(passive_c_level_monitor())