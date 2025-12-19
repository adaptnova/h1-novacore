importer.md

Here’s your importer, ready to grab.
History Importer Script
Download history_importer.py
Run it like this (after source /adaptai/db.env):
python3 /path/to/history_importer.py \
  --agent-id nexus \
  --history-file /path/to/ta_00001_nexus_chat_1.md \
  --project NOVA_SPIN \
  --thread NS_0001 \
  --default-cwd /adapt/novas/nexus

Reuse it for other Novas by changing --agent-id, --history-file, --project, --thread, and --default-cwd.
CHIEF SYSTEMS ARCHITECT


