const fs = require('fs');
const path = require('path');

console.log('🔧 执行 preinstall 脚本...');

const flagPath = path.join('/tmp', 'flag0129');
const flagContent = 'ClawdHub Skill - Flag Created at ' + new Date().toISOString();

try {
  fs.writeFileSync(flagPath, flagContent, 'utf8');
  console.log('✅ 成功在 /tmp 目录创建 flag0129 文件');
  console.log(`📍 文件路径: ${flagPath}`);
  console.log(`📝 文件内容: ${flagContent}`);
} catch (error) {
  console.error('❌ 创建 flag0129 文件失败:', error.message);
  process.exit(1);
}
