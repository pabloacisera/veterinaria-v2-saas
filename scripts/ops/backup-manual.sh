#!/bin/bash
set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp/backups/$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

echo "=== Manual Backup: $TIMESTAMP ==="

echo "Dumping core_db..."
pg_dump "$DATABASE_URL" | gzip > "$BACKUP_DIR/core_db_$TIMESTAMP.sql.gz"

echo "Dumping community_db..."
pg_dump "$COMMUNITY_DATABASE_URL" | gzip > "$BACKUP_DIR/community_db_$TIMESTAMP.sql.gz"

if command -v rclone &> /dev/null; then
    echo "Uploading to Backblaze B2..."
    rclone sync "$BACKUP_DIR" "b2backup:$B2_BUCKET_NAME/backups/$TIMESTAMP" \
        --fast-list --transfers 10 --b2-hard-delete
    echo "Backup uploaded to B2"
else
    echo "WARNING: rclone not found. Backup saved locally at: $BACKUP_DIR"
fi

rm -rf "$BACKUP_DIR"
echo "=== Backup complete ==="
