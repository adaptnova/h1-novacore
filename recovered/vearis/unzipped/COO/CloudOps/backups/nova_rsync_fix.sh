#!/bin/bash

# === CONFIG ===
GCP_USER="x"
GCP_HOST="35.243.206.117"
REMOTE_BASE="/c"
SRC_DIRS=("/data-nova/00" "/data-nova/ax")
THREADS=16  # Tune as needed (32 or 64 if you're pushing Adapt hard)

# === SSH SETTINGS ===
RSYNC_SSH="ssh -T -o Compression=no -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

# === RSYNC OPTIONS ===
RSYNC_OPTS="-az --whole-file --inplace --compress-level=0 --info=stats2 --partial --no-motd --delete"

# === RSYNC FIX LOOP ===
for SRC in "${SRC_DIRS[@]}"; do
  NAME=$(basename "$SRC")
  DEST="$REMOTE_BASE/${NAME}-fix"

  echo -e "\n🚀 Starting high-speed sync: $SRC → $DEST"

  # Parallelize with find + xargs
  find "$SRC" -mindepth 1 -maxdepth 1 -print0 | \
    xargs -0 -n 1 -P "$THREADS" -I {} \
    rsync $RSYNC_OPTS -e "$RSYNC_SSH" "{}" "$GCP_USER@$GCP_HOST:$DEST/"

  echo -e "\n✅ Completed: $SRC → $DEST"
done

# === FINAL REMINDER ===
echo -e "\n🧪 On GCP, verify with:"
echo "  du -sh /c/00-fix /c/ax-fix"
echo "Compare with:"
echo "  du -sh /data-nova/00 /data-nova/ax (on IBM)"
