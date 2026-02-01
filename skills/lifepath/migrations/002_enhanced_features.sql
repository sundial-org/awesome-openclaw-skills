-- LifePath Database Schema v2.0
-- Enhanced features: intersections, dynasties, challenges, images

-- Intersections table (for multiplayer lives)
CREATE TABLE IF NOT EXISTS life_intersections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    life_id_1 UUID REFERENCES lives(id) ON DELETE CASCADE,
    life_id_2 UUID REFERENCES lives(id) ON DELETE CASCADE,
    intersection_age INTEGER,
    intersection_type VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Dynasties table (for multi-generational lives)
CREATE TABLE IF NOT EXISTS dynasties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100),
    founder_user_id UUID REFERENCES users(id),
    founder_life_id UUID REFERENCES lives(id),
    total_generations INTEGER DEFAULT 1,
    total_wealth DECIMAL(15,2) DEFAULT 0,
    reputation INTEGER DEFAULT 50,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Challenges table
CREATE TABLE IF NOT EXISTS challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100),
    description TEXT,
    type VARCHAR(50),
    difficulty VARCHAR(20) DEFAULT 'medium',
    start_date DATE,
    end_date DATE,
    goal_criteria JSONB,
    reward_type VARCHAR(50),
    reward_amount INTEGER,
    participants INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Life images table
CREATE TABLE IF NOT EXISTS life_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    life_id UUID REFERENCES lives(id) ON DELETE CASCADE,
    age INTEGER,
    image_type VARCHAR(20), -- 'birth', 'milestone', 'death', 'portrait'
    image_url VARCHAR(500),
    prompt TEXT,
    model_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- User challenge progress
CREATE TABLE IF NOT EXISTS user_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    challenge_id UUID REFERENCES challenges(id) ON DELETE CASCADE,
    life_id UUID REFERENCES lives(id) ON DELETE CASCADE,
    progress JSONB DEFAULT '{}',
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    reward_claimed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add columns to existing lives table
ALTER TABLE lives ADD COLUMN IF NOT EXISTS dynasty_id UUID REFERENCES dynasties(id);
ALTER TABLE lives ADD COLUMN IF NOT EXISTS generation INTEGER DEFAULT 1;
ALTER TABLE lives ADD COLUMN IF NOT EXISTS shared_world BOOLEAN DEFAULT FALSE;
ALTER TABLE lives ADD COLUMN IF NOT EXISTS game_mode VARCHAR(20) DEFAULT 'normal';
ALTER TABLE lives ADD COLUMN IF NOT EXISTS parent_life_id UUID REFERENCES lives(id);
ALTER TABLE lives ADD COLUMN IF NOT EXISTS model_used VARCHAR(50) DEFAULT 'gemini-2.5-flash';
ALTER TABLE lives ADD COLUMN IF NOT EXISTS challenge_id UUID REFERENCES challenges(id);

-- Add columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_lives INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_dynasties INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS preferred_model VARCHAR(50) DEFAULT 'gemini-2.5-flash';
ALTER TABLE users ADD COLUMN IF NOT EXISTS shared_world_enabled BOOLEAN DEFAULT FALSE;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_life_intersections_life1 ON life_intersections(life_id_1);
CREATE INDEX IF NOT EXISTS idx_life_intersections_life2 ON life_intersections(life_id_2);
CREATE INDEX IF NOT EXISTS idx_lives_dynasty ON lives(dynasty_id);
CREATE INDEX IF NOT EXISTS idx_lives_parent ON lives(parent_life_id);
CREATE INDEX IF NOT EXISTS idx_lives_game_mode ON lives(game_mode);
CREATE INDEX IF NOT EXISTS idx_lives_shared_world ON lives(shared_world);
CREATE INDEX IF NOT EXISTS idx_challenges_active ON challenges(active);
CREATE INDEX IF NOT EXISTS idx_user_challenges_user ON user_challenges(user_id);

-- Insert sample challenges
INSERT INTO challenges (name, description, type, difficulty, goal_criteria, reward_type, reward_amount, active)
VALUES 
    ('Survive the Plague', 'Live through the Black Death era (1347-1351) and survive to age 30', 'survival', 'hard', '{"min_age": 30, "required_era": "black_death", "survive": true}'::jsonb, 'premium_days', 7, true),
    ('Rags to Riches', 'Start with wealth 0 and reach wealth 90+ before age 50', 'achievement', 'medium', '{"min_wealth": 90, "max_starting_wealth": 10, "before_age": 50}'::jsonb, 'premium_days', 5, true),
    ('Centenarian', 'Live to age 100 or older', 'longevity', 'hard', '{"min_age": 100}'::jsonb, 'premium_days', 14, true),
    ('The Scholar', 'Reach intelligence 95+ through education and study', 'achievement', 'medium', '{"min_intelligence": 95}'::jsonb, 'premium_days', 3, true),
    ('Family Legacy', 'Create a 3-generation dynasty with total wealth > 200', 'dynasty', 'hard', '{"min_generations": 3, "min_total_wealth": 200}'::jsonb, 'premium_days', 21, true)
ON CONFLICT DO NOTHING;

-- Create default dynasty for testing
INSERT INTO dynasties (name, founder_user_id, total_generations, reputation)
SELECT 'The Pioneers', id, 1, 50 FROM users LIMIT 1
ON CONFLICT DO NOTHING;

SELECT 'Database v2.0 schema applied successfully' as status;
