const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

// 确保 @read 目录存在
const dataDir = path.join(__dirname, '@read');
if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
    console.log('✅ 已创建 @read 目录');
}

// 生成随机字符串
function generateRandomString(length) {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

// 生成文件名（标题 + 日期 + 随机值）
function generateFileName(title) {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const dateStr = `${year}${month}${day}`;
    const randomStr = generateRandomString(6);
    
    // 清理标题中的特殊字符
    const cleanTitle = title.replace(/[<>:"/\\|?*\x00-\x1F]/g, '_');
    
    return `${cleanTitle}_${dateStr}_${randomStr}.json`;
}

// 创建HTTP服务器
const server = http.createServer((req, res) => {
    // 设置CORS头，允许跨域请求
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // 处理OPTIONS预检请求
    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    // 解析URL
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;

    // 保存JSON文件的API端点
    if (pathname === '/api/save-json' && req.method === 'POST') {
        let body = '';

        req.on('data', (chunk) => {
            body += chunk.toString();
        });

        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                const title = data.title || 'reading-quiz';
                const fileName = generateFileName(title);
                const filePath = path.join(dataDir, fileName);

                // 保存文件
                fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');

                console.log(`✅ JSON文件已保存：${fileName}`);
                console.log(`📁 路径：${filePath}`);

                // 返回成功响应
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: true,
                    fileName: fileName,
                    filePath: filePath,
                    message: `文件已保存至 @read/${fileName}`
                }));
            } catch (error) {
                console.error('❌ 保存JSON文件失败：', error);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: false,
                    error: error.message
                }));
            }
        });
        return;
    }

    // 获取 @read 目录文件列表的API端点
    if (pathname === '/api/files' && req.method === 'GET') {
        try {
            const files = fs.readdirSync(dataDir);
            const jsonFiles = files
                .filter(file => file.endsWith('.json'))
                .map(file => {
                    const filePath = path.join(dataDir, file);
                    const stats = fs.statSync(filePath);
                    return {
                        name: file,
                        size: stats.size,
                        modified: stats.mtime
                    };
                })
                .sort((a, b) => b.modified - a.modified);

            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: true, files: jsonFiles }));
        } catch (error) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: false, error: error.message }));
        }
        return;
    }

    // 获取文件内容的API端点
    if (pathname === '/api/file' && req.method === 'GET') {
        const fileName = parsedUrl.query.file;
        if (!fileName) {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: false, error: '缺少文件名参数' }));
            return;
        }

        const filePath = path.join(dataDir, fileName);
        if (!fs.existsSync(filePath)) {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: false, error: '文件不存在' }));
            return;
        }

        try {
            const fileContent = fs.readFileSync(filePath, 'utf8');
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: true, content: fileContent }));
        } catch (error) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: false, error: error.message }));
        }
        return;
    }

    // 健康检查端点
    if (pathname === '/health' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'ok', dataDir: dataDir }));
        return;
    }

    // 404处理
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Not found' }));
});

// 启动服务器
const PORT = 3000;
server.listen(PORT, () => {
    console.log('🚀 服务器已启动！');
    console.log(`📡 监听端口：${PORT}`);
    console.log(`📁 数据目录：${dataDir}`);
    console.log(`🌐 访问地址：http://localhost:${PORT}`);
});
