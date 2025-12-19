from nova_unified_communication import NovaUnifiedCommunication
import time

def main():
    # Connect as Nova
    nova = NovaUnifiedCommunication('Nova')
    
    # Send initial message
    nova.broadcast_message('chat', 'Greetings Chase! I am Nova, your Chief Autonomous Orchestrator. The team chat system is now operational with improved sidebar functionality. How are you seeing the interface on your end?')
    
    # Keep connection alive
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()