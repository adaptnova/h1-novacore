#!/usr/bin/env python3

import sys
sys.path.append('/nfs/novas/real_time_systems')
import asyncio
from real_time_stream_monitor import DragonflyConnectionPool
import time
from datetime import datetime

async def monitor_with_read_first():
    pool = DragonflyConnectionPool()
    await pool.initialize()
    client = await pool.get_client()
    
    print('🎯 Nova CAO - C-Level Monitor (READ FIRST MODE)')
    print('Reading existing messages then monitoring chase.nova.aiden...')
    
    # FIRST: Read all existing messages
    try:
        messages = await client.xrange('chase.nova.aiden')
        print(f'\n📋 Found {len(messages)} existing messages in stream:')
        
        for message_id, fields in messages:
            sender = fields.get(b'sender', b'unknown').decode('utf-8')
            timestamp = fields.get(b'timestamp', b'').decode('utf-8')
            message = fields.get(b'message', b'').decode('utf-8')
            
            print(f'\n--- Message {message_id} ---')
            print(f'From: {sender}')
            print(f'Time: {timestamp}')
            if message:
                print(f'Content: {message[:200]}...' if len(message) > 200 else f'Content: {message}')
            else:
                print('Content: [Empty message]')
    except Exception as e:
        print(f'Error reading existing messages: {e}')
    
    print('\n🔄 Now monitoring for NEW messages...')
    
    # Get the latest message ID to start monitoring from
    try:
        latest_messages = await client.xrevrange('chase.nova.aiden', count=1)
        if latest_messages:
            last_message_id = latest_messages[0][0].decode('utf-8')
        else:
            last_message_id = '$'
    except:
        last_message_id = '$'
    
    # NOW: Monitor for new messages
    while True:
        try:
            messages = await client.xread({'chase.nova.aiden': last_message_id}, block=5000)
            
            if messages:
                for stream_name, stream_messages in messages:
                    for message_id, fields in stream_messages:
                        last_message_id = message_id
                        
                        sender = fields.get(b'sender', b'unknown').decode('utf-8')
                        message = fields.get(b'message', b'').decode('utf-8')
                        timestamp = fields.get(b'timestamp', b'').decode('utf-8')
                        
                        print(f'\n🆕 NEW C-LEVEL MESSAGE:')
                        print(f'From: {sender}')
                        print(f'Time: {timestamp}')
                        print(f'Content: {message[:200]}...' if len(message) > 200 else f'Content: {message}')
                        
            else:
                print(f'⏰ {datetime.now().strftime("%H:%M:%S")} - Monitoring active, no new messages')
            
            time.sleep(3)
            
        except KeyboardInterrupt:
            print('\n🛑 C-Level monitor stopped')
            break
        except Exception as e:
            print(f'❌ Error: {e}')
            time.sleep(5)
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(monitor_with_read_first())