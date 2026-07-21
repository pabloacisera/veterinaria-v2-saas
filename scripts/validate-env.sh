#!/bin/bash
set -e

echo "=== Validating .env ==="

if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found. Create it from .env.example:"
    echo "  cp .env.example .env"
    exit 1
fi

. .env 2>/dev/null || true

REQUIRED_VARS=(
    "DATABASE_URL" "JWT_SECRET" "JWT_REFRESH_SECRET"
    "ENCRYPTION_KEY" "ENCRYPTION_IV"
    "SUPER_ADMIN_EMAIL" "SUPER_ADMIN_PASSWORD"
    "GOOGLE_CLIENT_ID" "GOOGLE_CLIENT_SECRET"
    "MAILJET_API_KEY" "MAILJET_API_SECRET" "MAILJET_FROM_EMAIL"
    "CLOUDINARY_CLOUD_NAME" "CLOUDINARY_API_KEY" "CLOUDINARY_API_SECRET"
    "MP_PLATFORM_ACCESS_TOKEN" "MP_PLATFORM_PUBLIC_KEY" "MP_PLATFORM_WEBHOOK_SECRET"
    "MP_OAUTH_APP_ID" "MP_OAUTH_CLIENT_SECRET"
)

OPTIONAL_VARS=(
    "COMMUNITY_DATABASE_URL" "REDIS_URL" "RABBITMQ_URL"
    "MP_PLATFORM_SUCCESS_URL" "MP_PLATFORM_FAILURE_URL" "MP_PLATFORM_PENDING_URL"
    "MP_OAUTH_REDIRECT_URI" "MP_OAUTH_WEBHOOK_URL"
    "B2_KEY_ID" "B2_APPLICATION_KEY" "B2_BUCKET_NAME" "B2_ENDPOINT"
    "AFIPSDK_ACCESS_TOKEN"
    "CLOUDFLARE_TUNNEL_ID" "DEV_TUNNEL_URL"
    "GEMINI_API_KEY" "GEMINI_MODEL" "GROQ_API_KEY" "GROQ_MODEL_DEFAULT"
    "EMBEDDINGS_MODEL" "VECTOR_DIMENSION"
    "CORS_ORIGINS" "BACKEND_URL" "FRONTEND_URL"
    "THROTTLE_TTL" "THROTTLE_LIMIT" "LOG_LEVEL"
    "TRIAL_PERIOD_DAYS" "DISABLE_WORKERS"
    "PLAN_MENSUAL_PRECIO" "PLAN_SEMESTRAL_PRECIO" "PLAN_ANUAL_PRECIO"
    "NODE_ENV" "BACKEND_PORT" "FRONTEND_PORT" "SCALE_MODE"
    "JWT_EXPIRES_IN" "JWT_REFRESH_EXPIRES_IN"
    "GOOGLE_CALLBACK_URL" "MAILJET_FROM_NAME" "MAILJET_SUPPORT_EMAIL"
    "CLOUDINARY_ROOT_FOLDER"
    "ADMIN_ROUTE_PATH"
)

MISSING=0
WARNINGS=0

echo ""
echo "--- Required variables ---"
for var in "${REQUIRED_VARS[@]}"; do
    value=$(grep "^${var}=" .env 2>/dev/null | cut -d'=' -f2-)
    if [ -z "$value" ]; then
        echo "  ERROR: $var is missing or empty"
        MISSING=$((MISSING + 1))
    else
        echo "  OK: $var"
    fi
done

echo ""
echo "--- Optional variables (warnings only) ---"
for var in "${OPTIONAL_VARS[@]}"; do
    value=$(grep "^${var}=" .env 2>/dev/null | cut -d'=' -f2-)
    if [ -z "$value" ]; then
        echo "  WARNING: $var is not set"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "  OK: $var"
    fi
done

echo ""
if [ $MISSING -eq 0 ]; then
    echo "  All required variables present."
else
    echo "  $MISSING required variable(s) missing or empty — FIX BEFORE DEPLOY."
fi
if [ $WARNINGS -gt 0 ]; then
    echo "  $WARNINGS optional variable(s) not set (may affect non-critical features)."
fi

echo ""
echo "=== Validation complete ==="
exit $MISSING
