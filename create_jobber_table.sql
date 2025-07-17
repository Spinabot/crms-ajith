-- Create JobberAuth table for storing OAuth tokens
CREATE TABLE IF NOT EXISTS jobber_auth (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expiration_time BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_jobber_auth_user_id ON jobber_auth(user_id);

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON TABLE jobber_auth TO your_user;
-- GRANT USAGE, SELECT ON SEQUENCE jobber_auth_id_seq TO your_user;