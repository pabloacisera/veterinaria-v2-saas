CREATE TABLE IF NOT EXISTS admin_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash VARCHAR(64) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_admin_reset_tokens_hash ON admin_reset_tokens(token_hash);
CREATE INDEX idx_admin_reset_tokens_ip ON admin_reset_tokens(ip_address, created_at);
