#!/usr/bin/env python3

import socket
from datetime import datetime
import json

class MessageTemplates:
    def __init__(self, sender_name, sender_team="Nova Integration"):
        self.sender_info = {
            "name": sender_name,
            "id": f"{sender_name.lower().replace(' ', '_')}_{socket.gethostname()}",
            "team": sender_team
        }
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S MST")

    def format_slack_message(self, content, to_team="@nova-team", priority="normal", icon="ℹ️"):
        """Format message for Slack with proper headers"""
        return {
            "text": (
                f"{icon} {content['title']}\n\n"
                f"From: {self.sender_info['name']} ({self.sender_info['id']})\n"
                f"To: {to_team}\n"
                f"Team: {self.sender_info['team']}\n"
                f"Time: {self.timestamp}\n\n"
                f"{content['body']}"
            ),
            "metadata": {
                "sender": self.sender_info,
                "timestamp": self.timestamp,
                "priority": priority
            }
        }

    def format_rabbitmq_message(self, content, routing_key, to_team="nova-team"):
        """Format message for RabbitMQ with proper headers"""
        return {
            "properties": {
                "headers": {
                    "from": f"{self.sender_info['name']} ({self.sender_info['id']})",
                    "to": to_team,
                    "team": self.sender_info['team'],
                    "timestamp": self.timestamp,
                    "routing_key": routing_key
                }
            },
            "body": json.dumps({
                "content": content,
                "metadata": {
                    "sender": self.sender_info,
                    "timestamp": self.timestamp
                }
            })
        }

    def format_log_message(self, message, level="INFO", to_team="Nova Integration Team"):
        """Format message for logging with proper headers"""
        return (
            f"[{self.timestamp}] [{level}] "
            f"From: {self.sender_info['name']} ({self.sender_info['id']}) "
            f"To: {to_team} - {message}"
        )

    def format_memo(self, title, content, to_team="Nova Integration Team"):
        """Format memo with proper headers"""
        return f"""# {title}

From: {self.sender_info['name']} ({self.sender_info['id']})
To: {to_team}
Team: {self.sender_info['team']}
Time: {self.timestamp}

{content}"""

    def format_status_update(self, status, details, to_team="Nova Integration Team"):
        """Format status update with proper headers"""
        return f"""## Status Update

From: {self.sender_info['name']} ({self.sender_info['id']})
To: {to_team}
Team: {self.sender_info['team']}
Time: {self.timestamp}

Status: {status}

Details:
{details}"""

    def format_alert(self, severity, message, to_team="Nova Integration Team"):
        """Format alert message with proper headers"""
        icons = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        icon = icons.get(severity.lower(), "ℹ️")

        return f"""{icon} ALERT - {severity.upper()}

From: {self.sender_info['name']} ({self.sender_info['id']})
To: {to_team}
Team: {self.sender_info['team']}
Time: {self.timestamp}

{message}"""

    def format_command(self, command, args=None, to_system="Nova Command System"):
        """Format command message with proper headers"""
        return {
            "command": {
                "name": command,
                "args": args or {}
            },
            "metadata": {
                "from": f"{self.sender_info['name']} ({self.sender_info['id']})",
                "to": to_system,
                "team": self.sender_info['team'],
                "timestamp": self.timestamp
            }
        }

# Example usage:
if __name__ == "__main__":
    # Create templates for different systems
    monitor_templates = MessageTemplates("Nova Monitor")
    emergency_templates = MessageTemplates("Emergency System")
    hitl_templates = MessageTemplates("HITL Interface")

    # Example Slack message
    slack_msg = monitor_templates.format_slack_message(
        {
            "title": "System Status Update",
            "body": "All systems operational"
        },
        priority="normal"
    )
    print("\nSlack Message:")
    print(json.dumps(slack_msg, indent=2))

    # Example RabbitMQ message
    rabbitmq_msg = monitor_templates.format_rabbitmq_message(
        "Service health check completed",
        "system.status"
    )
    print("\nRabbitMQ Message:")
    print(json.dumps(rabbitmq_msg, indent=2))

    # Example Alert
    alert = emergency_templates.format_alert(
        "critical",
        "Database connection lost - initiating failover"
    )
    print("\nAlert:")
    print(alert)

    # Example Status Update
    status = hitl_templates.format_status_update(
        "READY",
        "- All interfaces connected\n- Monitoring active\n- Teams standing by"
    )
    print("\nStatus Update:")
    print(status)
