-- LifePath Database Schema
-- PostgreSQL

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id BIGINT UNIQUE,
    telegram_username VARCHAR(100),
    moltbook_username VARCHAR(100),
    wallet_address VARCHAR(42),
    tier VARCHAR(20) DEFAULT 'free',
    daily_lives_remaining INTEGER DEFAULT 3,
    last_life_reset TIMESTAMP DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    premium_until TIMESTAMP
);

-- Lives table
CREATE TABLE IF NOT EXISTS lives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    mode VARCHAR(20) NOT NULL CHECK (mode IN ('private', 'public', 'trench')),
    birth_country VARCHAR(100) NOT NULL,
    birth_year INTEGER NOT NULL CHECK (birth_year BETWEEN 1900 AND 2025),
    gender VARCHAR(20) CHECK (gender IN ('male', 'female', 'non-binary')),
    seed VARCHAR(64) NOT NULL,
    current_age INTEGER DEFAULT 0,
    alive BOOLEAN DEFAULT TRUE,
    health INTEGER DEFAULT 50 CHECK (health BETWEEN 0 AND 100),
    happiness INTEGER DEFAULT 50 CHECK (happiness BETWEEN 0 AND 100),
    wealth INTEGER DEFAULT 50 CHECK (wealth BETWEEN 0 AND 100),
    intelligence INTEGER DEFAULT 50 CHECK (intelligence BETWEEN 0 AND 100),
    relationships JSONB DEFAULT '[]',
    history JSONB DEFAULT '[]',
    images JSONB DEFAULT '[]',
    shared_to_moltbook BOOLEAN DEFAULT FALSE,
    moltbook_post_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Life events table
CREATE TABLE IF NOT EXISTS life_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    life_id UUID REFERENCES lives(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    age INTEGER NOT NULL,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('birth', 'childhood', 'major', 'minor', 'decision', 'death')),
    title VARCHAR(200),
    description TEXT NOT NULL,
    consequences JSONB,
    player_choice JSONB,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'ETH',
    payment_method VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    transaction_hash VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP
);

-- Referral codes
CREATE TABLE IF NOT EXISTS referral_codes (
    code VARCHAR(20) PRIMARY KEY,
    creator_id UUID REFERENCES users(id) ON DELETE CASCADE,
    uses INTEGER DEFAULT 0,
    max_uses INTEGER DEFAULT 10,
    reward_type VARCHAR(20) DEFAULT 'premium_day',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_lives_user_id ON lives(user_id);
CREATE INDEX idx_lives_mode ON lives(mode);
CREATE INDEX idx_lives_alive ON lives(alive);
CREATE INDEX idx_life_events_life_id ON life_events(life_id);
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_tier ON users(tier);
