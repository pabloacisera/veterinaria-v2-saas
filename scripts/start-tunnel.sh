#!/bin/bash
set -e

echo "=== Starting Cloudflare Tunnel ==="

if ! command -v cloudflared &> /dev/null; then
    echo "ERROR: cloudflared not found. Install it first."
    echo "  https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
    exit 1
fi

CONFIG_PATH="$HOME/.cloudflared/config.yml"
TUNNEL_ID=$(grep -oP 'tunnel:\s*\K\S+' "$CONFIG_PATH" 2>/dev/null || echo "")

if [ -z "$TUNNEL_ID" ]; then
    echo "ERROR: Could not find tunnel ID in $CONFIG_PATH"
    exit 1
fi

echo "Using tunnel: $TUNNEL_ID"
echo "Dashboard: https://dash.cloudflare.com/"
echo "Tunnel URL: https://dev-api.artisandevs.site"
echo ""
echo "Validating ingress configuration..."
cloudflared tunnel ingress validate

echo ""
echo "Starting tunnel..."
cloudflared tunnel --config "$CONFIG_PATH" run "$TUNNEL_ID"
