#!/bin/bash
kill $(pgrep -f "python3 nova_web_chat.py")
kill $(pgrep -f "python3 nova_chat_gui.py")
echo "Nova chat system stopped"
