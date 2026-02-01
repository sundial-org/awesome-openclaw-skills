#!/usr/bin/env node
// Database initialization script

const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const schemaPath = path.join(__dirname, '../migrations/001_initial_schema.sql');

async function initDatabase() {
  console.log('🗄️  Initializing LifePath Database...\n');
  
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL || 'postgresql://localhost:5432/lifepath'
  });
  
  try {
    // Read schema
    const schema = fs.readFileSync(schemaPath, 'utf8');
    
    // Execute schema
    await pool.query(schema);
    
    console.log('✅ Database schema created successfully');
    console.log('✅ Tables created: users, lives, life_events, payments, referral_codes');
    
    // Verify connection
    const result = await pool.query('SELECT NOW() as time');
    console.log(`✅ Database connected: ${result.rows[0].time}`);
    
    console.log('\n🎭 LifePath database is ready!');
    
  } catch (error) {
    console.error('❌ Database initialization failed:', error.message);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

initDatabase();
