#!/bin/bash

# --- SOURCE AND TARGET CONFIG ---
SRC_DIRS=("/data-nova/ax" "/data-nova/00")
TARGET_DIR="/c"
GCP_HOST="35.243.206.117"
GCP_USER="x"

# --- Performance Config ---
TOTAL_THREADS=64
TOTAL_CORES=96

# --- Rsync Runner ---
run_rsync_parallel() {
  local src_dir="$1"
  echo -e "\n🔄 Syncing directory: $src_dir"

  find "$src_dir" -mindepth 1 -maxdepth 1 -print0 | \
  parallel -0 -j "$TOTAL_THREADS" --eta --bar '
    FILE="{}"
    INDEX={#}
    CPU_CORE=$(( INDEX % '"$TOTAL_CORES"' ))

    echo "→ Syncing $FILE (CPU $CPU_CORE)"

    taskset -c $CPU_CORE \
    rsync -az --info=progress2 --inplace --no-whole-file \
      -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
      "$FILE" '"$GCP_USER"'@'"$GCP_HOST"':'"$TARGET_DIR"'/ 
  '
}

# --- EXECUTE SYNC ---
START=$(date +%s)
for dir in "${SRC_DIRS[@]}"; do
  run_rsync_parallel "$dir"
done
END=$(date +%s)

echo -e "\n✅ Sync complete. Duration: $((END - START)) seconds."
