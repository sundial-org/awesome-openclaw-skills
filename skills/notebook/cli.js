#!/usr/bin/env node

import { init, loadTypes, getType, saveType, deleteType, createObject, loadObject, updateObject, deleteObject, listObjects, searchObjects, getStats, classifyObject, generateExpansionQuestions } from './lib/store.js';

init();

const args = process.argv.slice(2);
const cmd = args[0];

function printObject(obj, typeName) {
  const type = getType(typeName);
  console.log(`\n📓 ${obj.title || obj.name}`);
  console.log(`   ID: ${obj.id} | Type: ${typeName}`);
  console.log(`   Created: ${obj.created}`);
  
  // Print dynamic fields
  if (type && type.fields) {
    type.fields.forEach(f => {
      if (f.name === 'title' || f.name === 'name') return;
      const val = obj[f.name];
      if (val !== undefined && val !== null && val !== '') {
        console.log(`   ${f.name}: ${Array.isArray(val) ? val.join(', ') : val}`);
      }
    });
  }
  
  if (obj.tags?.length) {
    console.log(`   Tags: ${obj.tags.join(', ')}`);
  }
}

function printList(objects, title = 'Objects') {
  if (objects.length === 0) {
    console.log(`\nNo objects found.`);
    return;
  }
  console.log(`\n📓 ${title} (${objects.length})`);
  console.log('─'.repeat(60));
  objects.forEach(o => {
    const icon = o.type === 'project' ? '📁' : o.type === 'task' ? '✅' : '💡';
    console.log(`  ${icon} [${o.type}] ${o.title || o.name}`);
    if (o.tags?.length) console.log(`        Tags: ${o.tags.join(', ')}`);
  });
}

function parseTags(tagStr) {
  if (!tagStr) return [];
  return tagStr.split(',').map(t => t.trim()).filter(Boolean);
}

function parseArgs(argStr) {
  const args = {};
  const regex = /-(\w+)\s+([^-\s]+)/g;
  let match;
  while ((match = regex.exec(argStr)) !== null) {
    args[match[1]] = match[2];
  }
  return args;
}

// Commands
switch (cmd) {
  case 'types': {
    const types = loadTypes();
    console.log('\n📚 Available Types:');
    types.forEach(t => {
      console.log(`  - ${t.name} (${t.fields.length} fields)`);
    });
    break;
  }
  
  case 'type-add': {
    // Simple: type-add typename field1:text field2:select(a|b|c)
    const typeName = args[1];
    if (!typeName) {
      console.log('\nUsage: notebook type-add typename field:text ...');
      process.exit(1);
    }
    
    const fields = [];
    const fieldArgs = args.slice(2);
    for (const arg of fieldArgs) {
      const [name, typeWithOpts] = arg.split(':');
      if (!typeWithOpts) continue;
      
      let type = typeWithOpts;
      let options = [];
      if (typeWithOpts.includes('(')) {
        const match = typeWithOpts.match(/(\w+)\(([^)]+)\)/);
        if (match) {
          type = match[1];
          options = match[2].split('|');
        }
      }
      
      fields.push({
        name,
        type: type === 'select' ? 'select' : type,
        options: options.length ? options : undefined,
        required: true
      });
    }
    
    saveType({ name: typeName, fields });
    console.log(`\n✅ Type "${typeName}" created with ${fields.length} fields.`);
    break;
  }
  
  case 'add': {
    const typeName = args[1];
    
    // Find quoted title (single or double quotes)
    const argStr = args.slice(2).join(' ');
    const titleMatch = argStr.match(/['"]([^'"]+)['"]/);
    const title = titleMatch ? titleMatch[1] : null;
    
    if (!typeName || !title) {
      console.log('\nUsage: notebook add typename "Title" [options]');
      console.log('\nAvailable types:');
      loadTypes().forEach(t => console.log(`  - ${t.name}`));
      process.exit(1);
    }
    
    // Parse remaining args (without quoted title)
    const data = { title };
    const remaining = argStr.replace(/['"][^'"]+['"]/, '').trim();
    
    // Simple flag parsing
    const parts = remaining.split(/\s+/).filter(Boolean);
    for (let i = 0; i < parts.length; i++) {
      if (parts[i].startsWith('-')) {
        const key = parts[i].replace(/^-+/, '');
        const val = parts[i + 1];
        if (val && !val.startsWith('-')) {
          if (key === 't' || key === 'tag') {
            data.tags = parseTags(val);
          } else if (key === 'p' || key === 'priority') {
            data.priority = val;
          } else if (key === 's' || key === 'status') {
            data.status = val;
          }
          i++;
        }
      }
    }
    
    try {
      const obj = createObject(typeName, data);
      console.log(`\n✅ Created ${typeName}:`);
      printObject(obj, typeName);
    } catch (e) {
      console.log(`\n❌ Error: ${e.message}`);
      process.exit(1);
    }
    break;
  }
  
  case 'add-example': {
    // Quick add idea
    const title = args.slice(1).join(' ').replace(/^"|"$/g, '');
    if (!title) {
      console.log('\nUsage: notebook add-example "Your idea"');
      process.exit(1);
    }
    const obj = createObject('idea', { title, tags: parseTags(''), priority: 'medium' });
    console.log(`\n✅ Created idea: ${obj.title}`);
    break;
  }
  
  case 'list': {
    const typeName = args[1];
    const types = loadTypes();
    
    if (!typeName) {
      // List all by type
      const stats = getStats();
      console.log('\n📊 Stats by Type:');
      Object.entries(stats.byType).forEach(([t, count]) => console.log(`  ${t}: ${count}`));
      break;
    }
    
    const type = getType(typeName);
    if (!type) {
      console.log(`\nUnknown type: ${typeName}`);
      process.exit(1);
    }
    
    // Parse filters
    const filters = {};
    if (args.includes('-s') || args.includes('--status')) {
      const idx = args.findIndex(a => a === '-s' || a === '--status');
      filters.status = args[idx + 1];
    }
    if (args.includes('-t') || args.includes('--tag')) {
      const idx = args.findIndex(a => a === '-t' || a === '--tag');
      filters.tags = args[idx + 1].split(',');
    }
    
    const objects = listObjects(typeName, filters);
    printList(objects.map(o => ({ ...o, title: o.title || o.name })), `${typeName}s`);
    break;
  }
  
  case 'get':
  case 'view':
  case 'open': {
    const typeName = args[1];
    const query = args.slice(2).join(' ');
    
    if (!typeName || !query) {
      console.log('\nUsage: notebook get typename "title"');
      process.exit(1);
    }
    
    const results = listObjects(typeName).filter(o => 
      (o.title || '').toLowerCase().includes(query.toLowerCase())
    );
    
    if (results.length === 0) {
      console.log(`\nNo ${typeName} found matching "${query}"`);
      process.exit(1);
    }
    if (results.length > 1) {
      console.log(`\nFound ${results.length} matches:`);
      results.forEach((r, i) => console.log(`  ${i + 1}. ${r.title}`));
      process.exit(1);
    }
    
    const obj = loadObject(typeName, results[0].id);
    printObject(obj, typeName);
    break;
  }
  
  case 'expand': {
    const typeName = args[1];
    const argStr = args.slice(2).join(' ');
    const titleMatch = argStr.match(/['"]([^'"]+)['"]/);
    const query = titleMatch ? titleMatch[1] : argStr;
    
    if (!typeName || !query) {
      console.log('\nUsage: notebook expand typename "title"');
      process.exit(1);
    }
    
    const results = listObjects(typeName).filter(o => 
      (o.title || '').toLowerCase().includes(query.toLowerCase())
    );
    
    if (results.length === 0) {
      console.log(`\nNo ${typeName} found matching "${query}"`);
      process.exit(1);
    }
    if (results.length > 1) {
      console.log(`\nFound ${results.length} matches. Be more specific.`);
      process.exit(1);
    }
    
    const obj = loadObject(typeName, results[0].id);
    
    // Generate expansion questions
    const questions = generateExpansionQuestions(obj);
    
    console.log(`\n🔍 Expanding: ${obj.title}`);
    console.log(`   Classification: ${obj.classification || 'idea'}`);
    console.log(`\n📝 To deepen this ${typeName}, consider:\n`);
    questions.forEach((q, i) => {
      console.log(`  ${i + 1}. ${q}`);
    });
    console.log(`\n💡 Reply with answers and I'll update the object.`);
    console.log(`   Or run: notebook edit ${typeName} "${obj.title}" field:value`);
    break;
  }
  
  case 'update':
  case 'edit': {
    const typeName = args[1];
    const argStr = args.slice(2).join(' ');
    
    // Find quoted title
    const titleMatch = argStr.match(/['"]([^'"]+)['"]/);
    if (!titleMatch) {
      console.log('\nUsage: notebook edit typename "title" field:value');
      process.exit(1);
    }
    const query = titleMatch[1];
    
    // Find field:value after the quoted title
    const afterTitle = argStr.replace(/['"][^'"]+['"]/, '').trim();
    if (!afterTitle || !afterTitle.includes(':')) {
      console.log('\nUsage: notebook edit typename "title" field:value');
      process.exit(1);
    }
    const [fieldName, ...valParts] = afterTitle.split(':');
    const value = valParts.join(':');
    
    const results = listObjects(typeName).filter(o => 
      (o.title || '').toLowerCase().includes(query.toLowerCase())
    );
    
    if (results.length === 0) {
      console.log(`\nNo ${typeName} found matching "${query}"`);
      process.exit(1);
    }
    
    const obj = updateObject(typeName, results[0].id, { [fieldName]: value });
    console.log(`\n✅ Updated ${typeName}:`);
    printObject(obj, typeName);
    break;
  }
  
  case 'delete': {
    const typeName = args[1];
    const query = args.slice(2).join(' ');
    
    if (!typeName || !query) {
      console.log('\nUsage: notebook delete typename "title"');
      process.exit(1);
    }
    
    const results = listObjects(typeName).filter(o => 
      (o.title || '').toLowerCase().includes(query.toLowerCase())
    );
    
    if (results.length === 0) {
      console.log(`\nNo ${typeName} found matching "${query}"`);
      process.exit(1);
    }
    
    deleteObject(typeName, results[0].id);
    console.log(`\n🗑️  Deleted ${typeName}`);
    break;
  }
  
  case 'link': {
    // Format: notebook link idea:"title" project:"title"
    const links = args.slice(1).filter(a => a.includes(':'));
    
    if (links.length < 2) {
      console.log('\nUsage: notebook link idea:"title" project:"title"');
      process.exit(1);
    }
    
    const objects = [];
    for (const link of links) {
      const [type, title] = link.split(':');
      const results = listObjects(type).filter(o => 
        (o.title || '').toLowerCase().includes(title.toLowerCase())
      );
      if (results.length !== 1) {
        console.log(`\nCould not find unique ${type} matching "${title}"`);
        process.exit(1);
      }
      objects.push({ type, obj: loadObject(type, results[0].id) });
    }
    
    // Link all to each other
    for (let i = 0; i < objects.length; i++) {
      for (let j = 0; j < objects.length; j++) {
        if (i === j) continue;
        const o1 = objects[i].obj;
        const o2 = objects[j];
        if (!o1.related) o1.related = [];
        const ref = `${o2.type}:${o2.obj.title}`;
        if (!o1.related.includes(ref)) {
          o1.related.push(ref);
          updateObject(o1.type, o1.id, o1);
        }
      }
    }
    
    const names = objects.map(o => `"${o.obj.title}"`).join(' ↔ ');
    console.log(`\n🔗 Linked ${names}`);
    break;
  }
  
  case 'find':
  case 'search': {
    const query = args.slice(1).join(' ');
    const results = searchObjects(query);
    printList(results, `Results for "${query}"`);
    break;
  }
  
  case 'stats': {
    const stats = getStats();
    console.log('\n📊 Notebook Stats');
    console.log(`   Total objects: ${stats.total}`);
    console.log('   By type:');
    Object.entries(stats.byType).forEach(([t, c]) => console.log(`     ${t}: ${c}`));
    console.log('   By status:');
    Object.entries(stats.byStatus).forEach(([s, c]) => console.log(`     ${s}: ${c}`));
    break;
  }
  
  case 'help':
  default: {
    console.log(`
📓 Notebook - Object-based personal knowledge base

Usage: notebook <command> [options]

Types Commands:
  types                    List available types
  type-add typename field:text field2:select(a|b|c)  Define new type

Object Commands:
  add typename "Title"     Create new object
  list typename            List objects of type
  get typename "title"     View single object
  expand typename "title"  Deep-dive with questions
  edit typename "title" field:value  Update field
  delete typename "title"  Remove object
  find "query"             Search all objects
  stats                    Show counts

Options:
  -s, --status status      Filter by status
  -t, --tag tag1,tag2      Filter by tags

Examples:
  notebook types
  notebook add idea "Voice capture" -t voice,automation -p high
  notebook list project -s active
  notebook get idea "voice"
  notebook expand idea "voice"
  notebook edit idea "voice" status:expanded
  notebook find "automation"
  notebook stats
`);
  }
}

console.log('');
