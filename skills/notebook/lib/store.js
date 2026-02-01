import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import yaml from 'js-yaml';

// Always resolve skill folder from import.meta.url, not __dirname (which varies by CWD)
const SKILL_FOLDER = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
// CLAWD_WORKSPACE env var takes precedence, otherwise walk up from skills folder
// The workspace is typically the parent of the 'skills' directory
const SKILLS_FOLDER = path.dirname(SKILL_FOLDER);
const WORKSPACE_DIR = process.env.CLAWD_WORKSPACE || path.dirname(SKILLS_FOLDER);
const DATA_DIR = path.join(WORKSPACE_DIR, 'notebook');
const OBJECTS_DIR = path.join(DATA_DIR, 'objects');
const TYPES_FILE = path.join(DATA_DIR, 'types.yaml');
const INDEX_FILE = path.join(DATA_DIR, 'index.json');

// Debug logging
// console.error('DEBUG: SKILL_FOLDER =', SKILL_FOLDER);
// console.error('DEBUG: SKILLS_FOLDER =', SKILLS_FOLDER);
// console.error('DEBUG: WORKSPACE_DIR =', WORKSPACE_DIR);
// console.error('DEBUG: DATA_DIR =', DATA_DIR);
// console.error('DEBUG: TYPES_FILE =', TYPES_FILE);

// Ensure directories exist
function init() {
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
  if (!fs.existsSync(OBJECTS_DIR)) fs.mkdirSync(OBJECTS_DIR, { recursive: true });
  if (!fs.existsSync(TYPES_FILE)) {
    // No default types - user defines their own
    fs.writeFileSync(TYPES_FILE, 'types: []');
  }
  if (!fs.existsSync(INDEX_FILE)) saveIndex({ objects: [] });
}

// Load types
function loadTypes() {
  try {
    const content = fs.readFileSync(TYPES_FILE, 'utf-8');
    const data = yaml.load(content);
    return data.types || [];
  } catch {
    return [];
  }
}

function getType(typeName) {
  const types = loadTypes();
  return types.find(t => t.name === typeName);
}

function saveType(type) {
  const types = loadTypes();
  const existingIdx = types.findIndex(t => t.name === type.name);
  if (existingIdx >= 0) {
    types[existingIdx] = type;
  } else {
    types.push(type);
  }
  fs.writeFileSync(TYPES_FILE, yaml.dump({ types }));
}

function deleteType(typeName) {
  const types = loadTypes();
  const filtered = types.filter(t => t.name !== typeName);
  fs.writeFileSync(TYPES_FILE, yaml.dump({ types: filtered }));
}

// Load/save index
function loadIndex() {
  try {
    return JSON.parse(fs.readFileSync(INDEX_FILE, 'utf-8'));
  } catch {
    return { objects: [] };
  }
}

function saveIndex(index) {
  fs.writeFileSync(INDEX_FILE, JSON.stringify(index, null, 2));
}

// Get today's date
function today() {
  return new Date().toISOString().split('T')[0];
}

// Generate object ID
function generateId() {
  return `${Date.now().toString(36)}`;
}

// Classify object for expansion routing
function classifyObject(data) {
  const text = (data.title || '') + ' ' + (data.notes || '') + ' ' + (data.notes || '');
  const lower = text.toLowerCase();
  
  if (lower.includes('problem') || lower.includes('bug') || lower.includes('error') || 
      lower.includes('fail') || lower.includes('issue') || lower.includes('broken')) {
    return 'problem';
  }
  if (lower.includes('how to') || lower.includes('documentation') || lower.includes('guide') ||
      lower.includes('explain') || lower.includes('process')) {
    return 'documentation';
  }
  return 'idea'; // default
}

// Expansion question generators
function generateExpansionQuestions(object) {
  const type = object.type;
  const classification = object.classification || 'idea';
  
  const questions = [];
  
  // Core questions for all types
  if (type === 'idea' || type === 'project') {
    questions.push(
      `What problem does this solve?`,
      `Who is this for?`,
      `What are the success criteria?`,
      `What could go wrong?`
    );
  }
  
  if (type === 'task') {
    questions.push(
      `What is the Definition of Done?`,
      `What dependencies exist?`,
      `What is the deadline?`,
      `What does "done" look like?`
    );
  }
  
  // Classification-specific
  if (classification === 'problem') {
    questions.push(
      `What is the root cause?`,
      `How did this manifest?`,
      `What have you already tried?`,
      `What is the minimal reproduction?`
    );
  } else if (classification === 'documentation') {
    questions.push(
      `What audience is this for?`,
      `What prerequisites are needed?`,
      `What examples would help?`,
      `What common mistakes should be noted?`
    );
  }
  
  // SCAMPER questions (random 3)
  const scamper = [
    `What could you substitute to simplify this?`,
    `What could you combine to reduce complexity?`,
    `How would an expert adapt this?`,
    `What modification would make this 10x better?`,
    `What other use cases exist?`,
    `What could you eliminate entirely?`,
    `What if you reversed the approach?`
  ];
  
  // Add 2-3 SCAMPER questions randomly
  const shuffled = scamper.sort(() => 0.5 - Math.random()).slice(0, 2);
  questions.push(...shuffled);
  
  return questions.slice(0, 5); // Max 5 questions
}

function getExpansionMethod(answerCount, complexity) {
  if (answerCount <= 2) return 'annotation';
  if (complexity === 'high' || answerCount >= 5) return 'rewrite';
  return 'annotation'; // default
}

// Get object path
function getObjectPath(type, id) {
  const typeDir = path.join(OBJECTS_DIR, type);
  if (!fs.existsSync(typeDir)) fs.mkdirSync(typeDir, { recursive: true });
  return path.join(typeDir, `${id}.yaml`);
}

// Create object
function createObject(typeName, data) {
  const type = getType(typeName);
  if (!type) throw new Error(`Type "${typeName}" not found`);
  
  const id = generateId();
  const object = {
    id,
    type: typeName,
    created: today(),
    updated: new Date().toISOString(),
    classification: classifyObject(data),
    ...data
  };
  
  // Validate required fields
  for (const field of type.fields) {
    if (field.required && !object[field.name]) {
      throw new Error(`Field "${field.name}" is required for ${typeName}`);
    }
  }
  
  // Save object file
  const filePath = getObjectPath(typeName, id);
  fs.writeFileSync(filePath, yaml.dump(object));
  
  // Update index
  const index = loadIndex();
  if (!index.objects) index.objects = [];
  index.objects.push({
    id,
    type: typeName,
    title: object.title || object.name || `Untitled ${typeName}`,
    tags: object.tags || []
  });
  saveIndex(index);
  
  return object;
}

// Load object
function loadObject(typeName, id) {
  const filePath = getObjectPath(typeName, id);
  if (!fs.existsSync(filePath)) return null;
  const content = fs.readFileSync(filePath, 'utf-8');
  return yaml.load(content);
}

// Update object
function updateObject(typeName, id, updates) {
  const object = loadObject(typeName, id);
  if (!object) throw new Error('Object not found');
  
  const updated = {
    ...object,
    ...updates,
    updated: new Date().toISOString()
  };
  
  const filePath = getObjectPath(typeName, id);
  fs.writeFileSync(filePath, yaml.dump(updated));
  
  return updated;
}

// Delete object
function deleteObject(typeName, id) {
  const filePath = getObjectPath(typeName, id);
  if (!fs.existsSync(filePath)) throw new Error('Object not found');
  
  fs.unlinkSync(filePath);
  
  // Update index
  const index = loadIndex();
  index.objects = index.objects.filter(o => o.id !== id || o.type !== typeName);
  saveIndex(index);
  
  return true;
}

// List objects by type
function listObjects(typeName, filters = {}) {
  const index = loadIndex();
  let objects = index.objects.filter(o => o.type === typeName);
  
  if (filters.status) {
    objects = objects.filter(o => o.status === filters.status);
  }
  if (filters.tags) {
    const tagFilters = Array.isArray(filters.tags) ? filters.tags : [filters.tags];
    objects = objects.filter(o => 
      tagFilters.some(t => o.tags?.includes(t))
    );
  }
  
  return objects;
}

// Search all objects
function searchObjects(query) {
  const index = loadIndex();
  const q = query.toLowerCase();
  
  return index.objects.filter(o => {
    // Check title
    if (o.title?.toLowerCase().includes(q)) return true;
    // Check tags
    if (o.tags?.some(t => t.toLowerCase().includes(q))) return true;
    return false;
  });
}

// Get stats
function getStats() {
  const index = loadIndex();
  const byType = {};
  const byStatus = {};
  
  index.objects.forEach(o => {
    byType[o.type] = (byType[o.type] || 0) + 1;
    if (o.status) {
      byStatus[o.status] = (byStatus[o.status] || 0) + 1;
    }
  });
  
  return { total: index.objects.length, byType, byStatus };
}

export {
  init,
  loadTypes,
  getType,
  saveType,
  deleteType,
  createObject,
  loadObject,
  updateObject,
  deleteObject,
  listObjects,
  searchObjects,
  getStats,
  classifyObject,
  generateExpansionQuestions,
  getExpansionMethod
};
