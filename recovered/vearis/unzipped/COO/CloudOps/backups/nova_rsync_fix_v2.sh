#!/bin/bash

GCP_USER="x"
GCP_HOST="35.243.206.117"
RSYNC_SSH="ssh -T -o Compression=no -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

RSYNC_OPTS="-az --compress-level=0 --info=flist2,name,progress2,stats2 --progress --no-motd --partial-dir=.rsync-partial --delete"

echo -e "\n🚀 Syncing /data-nova/00 → /c/00-fix (with speed + progress)"
rsync $RSYNC_OPTS -e "$RSYNC_SSH" /data-nova/00/ "$GCP_USER@$GCP_HOST:/c/00-fix/"

echo -e "\n🚀 Syncing /data-nova/ax → /c/ax-fix (with speed + progress)"
rsync $RSYNC_OPTS -e "$RSYNC_SSH" /data-nova/ax/ "$GCP_USER@$GCP_HOST:/c/ax-fix/"

echo -e "\n✅ All done. Check du -sh /c/*-fix and we’ll snapshot it."
