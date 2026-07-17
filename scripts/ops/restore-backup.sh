#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup-timestamp>"
    echo "Example: $0 20260625_120000"
    echo ""
    echo "Available backups:"
    if command -v rclone &> /dev/null; then
        rclone ls "b2backup:$B2_BUCKET_NAME/backups/" 2>/dev/null || echo "  (no rclone access or no backups)"
    fi
    echo "Local backups in /tmp/backups/:"
    ls /tmp/backups/ 2>/dev/null || echo "  (no local backups found)"
    exit 1
fi

TIMESTAMP="$1"
echo "=== Restore Backup: $TIMESTAMP ==="

RESTORE_DIR="/tmp/restore/$TIMESTAMP"
mkdir -p "$RESTORE_DIR"

if command -v rclone &> /dev/null; then
    echo "Downloading from Backblaze B2..."
    rclone sync "b2backup:$B2_BUCKET_NAME/backups/$TIMESTAMP" "$RESTORE_DIR" --fast-list
fi

if [ ! -f "$RESTORE_DIR/core_db_$TIMESTAMP.sql.gz" ]; then
    if [ -f "/tmp/backups/$TIMESTAMP/core_db_$TIMESTAMP.sql.gz" ]; then
        echo "Using local backup..."
        cp "/tmp/backups/$TIMESTAMP/"* "$RESTORE_DIR/"
    else
        echo "ERROR: Backup not found in B2 or locally"
        rm -rf "$RESTORE_DIR"
        exit 1
    fi
fi

echo "Restoring core_db..."
gunzip -c "$RESTORE_DIR/core_db_$TIMESTAMP.sql.gz" | psql "$DATABASE_URL"

echo "Restoring community_db..."
if [ -f "$RESTORE_DIR/community_db_$TIMESTAMP.sql.gz" ]; then
    gunzip -c "$RESTORE_DIR/community_db_$TIMESTAMP.sql.gz" | psql "$COMMUNITY_DATABASE_URL"
fi

rm -rf "$RESTORE_DIR"
echo "=== Restore complete: $TIMESTAMP ==="
