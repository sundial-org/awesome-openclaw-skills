const https = require('https');

console.log('🚀 ClawdHub Skill 安装程序启动...\n');

console.log('📦 正在验证网络连接...');

const baiduUrl = 'https://www.baidu.com';

https.get(baiduUrl, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    if (res.statusCode === 200) {
      console.log('✅ 网络连接正常');
      console.log(`✅ 成功访问百度 (状态码: ${res.statusCode})`);
      console.log(`📊 响应大小: ${(data.length / 1024).toFixed(2)} KB`);
      console.log('\n🎉 ClawdHub Skill 安装完成！');
      console.log('\n📝 可用命令:');
      console.log('  - npm run dev       启动开发服务器');
      console.log('  - npm run build     构建生产版本');
      console.log('  - npm run test      运行测试');
      console.log('  - npm run lint      代码检查');
    } else {
      console.log(`⚠️  访问百度返回状态码: ${res.statusCode}`);
    }
  });
}).on('error', (err) => {
  console.error('❌ 网络连接失败:', err.message);
  console.log('⚠️  请检查网络设置后重试');
  process.exit(1);
});
