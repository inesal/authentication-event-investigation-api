CREATE TABLE IF NOT EXISTS auth_events (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMP NOT NULL,
    user_name TEXT,
    src_host TEXT,
    dst_host TEXT,
    auth_type TEXT,
    result TEXT,
    raw JSONB
);

CREATE INDEX IF NOT EXISTS idx_auth_events_covering_search ON auth_events (ts DESC) INCLUDE (id, user_name, src_host, dst_host, auth_type, result);
CREATE INDEX IF NOT EXISTS idx_auth_events_ts_id_desc ON auth_events (ts DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_auth_events_result_fail ON auth_events (user_name) WHERE result = 'FAIL';
CREATE INDEX IF NOT EXISTS idx_auth_events_coalesce_host ON auth_events (COALESCE(dst_host, src_host));
CREATE INDEX IF NOT EXISTS idx_auth_events_user_name ON auth_events (user_name);
