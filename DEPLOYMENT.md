# 🚀 RAG竞技场部署指南

本文档提供了在不同环境中部署RAG竞技场游戏的详细指南。

## 📋 部署前检查清单

### 系统要求
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python版本**: 3.8 或更高版本
- **内存**: 最少 4GB RAM（推荐 8GB+）
- **存储**: 至少 1GB 可用空间
- **网络**: 稳定的网络连接（用于依赖包安装）

### 必需软件
- Python 3.8+
- pip（Python包管理器）
- Git（可选，用于版本控制）

## 🏠 本地开发环境部署

### 1. 环境准备

```bash
# 检查Python版本
python --version
# 或者
python3 --version

# 检查pip版本
pip --version
```

### 2. 项目设置

```bash
# 创建项目目录
mkdir rag_xiaoyouxi
cd rag_xiaoyouxi

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 安装项目依赖
pip install -r requirements.txt

# 验证安装
pip list | grep streamlit
```

### 4. 生成游戏文档

```bash
# 生成所有游戏文档
python generate_documents.py

# 验证文档生成
ls documents/real/
ls documents/fake/
```

### 5. 启动游戏

```bash
# 方法1：使用启动脚本（Windows）
start_game.bat

# 方法2：直接启动
streamlit run app.py

# 方法3：指定端口启动
streamlit run app.py --server.port 8501
```

## 🌐 网络部署

### 局域网部署

适用于办公室内部或小型团队使用。

```bash
# 启动时绑定到所有网络接口
streamlit run app.py --server.address 0.0.0.0 --server.port 8501

# 查看本机IP地址
# Windows:
ipconfig
# macOS/Linux:
ifconfig
```

访问地址：`http://[你的IP地址]:8501`

### 云服务器部署

#### 使用 AWS EC2

1. **创建EC2实例**
   - 选择Ubuntu 20.04 LTS
   - 实例类型：t3.medium 或更高
   - 安全组开放端口：22, 8501

2. **连接并配置服务器**

```bash
# 连接到服务器
ssh -i your-key.pem ubuntu@your-ec2-ip

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和pip
sudo apt install python3 python3-pip python3-venv -y

# 克隆项目（如果使用Git）
git clone your-repository-url
cd rag_xiaoyouxi

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 生成文档
python generate_documents.py
```

3. **使用systemd管理服务**

创建服务文件：

```bash
sudo nano /etc/systemd/system/rag-game.service
```

服务文件内容：

```ini
[Unit]
Description=RAG Competition Game
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/rag_xiaoyouxi
Environment=PATH=/home/ubuntu/rag_xiaoyouxi/venv/bin
ExecStart=/home/ubuntu/rag_xiaoyouxi/venv/bin/streamlit run app.py --server.address 0.0.0.0 --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start rag-game

# 设置开机自启
sudo systemctl enable rag-game

# 查看服务状态
sudo systemctl status rag-game
```

#### 使用 Docker 部署

1. **创建 Dockerfile**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 生成游戏文档
RUN python generate_documents.py

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
```

2. **构建和运行容器**

```bash
# 构建镜像
docker build -t rag-game .

# 运行容器
docker run -p 8501:8501 rag-game

# 后台运行
docker run -d -p 8501:8501 --name rag-game-container rag-game
```

3. **使用 docker-compose**

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  rag-game:
    build: .
    ports:
      - "8501:8501"
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

启动：

```bash
docker-compose up -d
```

## 🔧 高级配置

### 反向代理配置（Nginx）

适用于生产环境，提供更好的性能和安全性。

1. **安装Nginx**

```bash
sudo apt install nginx -y
```

2. **配置Nginx**

创建配置文件：

```bash
sudo nano /etc/nginx/sites-available/rag-game
```

配置内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/rag-game /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL证书配置（Let's Encrypt）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 设置自动续期
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 负载均衡配置

对于大型活动，可以部署多个实例：

```nginx
upstream rag_game {
    server localhost:8501;
    server localhost:8502;
    server localhost:8503;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://rag_game;
        # ... 其他配置
    }
}
```

## 📊 监控和日志

### 应用监控

1. **系统资源监控**

```bash
# 安装htop
sudo apt install htop -y

# 监控系统资源
htop

# 监控磁盘使用
df -h

# 监控内存使用
free -h
```

2. **应用日志**

```bash
# 查看Streamlit日志
journalctl -u rag-game -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 性能优化

1. **Streamlit配置优化**

创建 `.streamlit/config.toml`：

```toml
[server]
port = 8501
address = "0.0.0.0"
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
base = "light"
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

2. **缓存配置**

在代码中使用Streamlit缓存：

```python
@st.cache_data
def load_documents():
    # 缓存文档加载
    pass

@st.cache_resource
def init_rag_system():
    # 缓存RAG系统初始化
    pass
```

## 🔒 安全配置

### 防火墙设置

```bash
# Ubuntu UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8501

# CentOS firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
```

### 访问控制

在Nginx中添加IP白名单：

```nginx
location / {
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    
    proxy_pass http://localhost:8501;
    # ... 其他配置
}
```

## 🚨 故障排除

### 常见问题

1. **端口被占用**

```bash
# 查看端口占用
netstat -tulpn | grep 8501
# 或
lsof -i :8501

# 杀死占用进程
sudo kill -9 <PID>
```

2. **权限问题**

```bash
# 修改文件权限
chmod +x start_game.bat
chown -R $USER:$USER .
```

3. **依赖包问题**

```bash
# 清理pip缓存
pip cache purge

# 重新安装依赖
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

4. **内存不足**

```bash
# 创建swap文件
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 日志分析

```bash
# 查看应用错误
grep -i error /var/log/rag-game.log

# 查看访问统计
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr

# 监控实时访问
tail -f /var/log/nginx/access.log | grep -v "static"
```

## 📈 扩展和维护

### 定期维护任务

创建维护脚本 `maintenance.sh`：

```bash
#!/bin/bash

# 系统更新
sudo apt update && sudo apt upgrade -y

# 清理日志
sudo journalctl --vacuum-time=30d

# 清理临时文件
sudo apt autoremove -y
sudo apt autoclean

# 备份配置
tar -czf backup-$(date +%Y%m%d).tar.gz .

# 重启服务
sudo systemctl restart rag-game
sudo systemctl restart nginx

echo "维护完成：$(date)"
```

设置定期执行：

```bash
# 添加到crontab
0 2 * * 0 /path/to/maintenance.sh
```

### 备份策略

1. **配置备份**

```bash
# 备份应用配置
tar -czf config-backup-$(date +%Y%m%d).tar.gz config.py game_settings.json

# 备份文档
tar -czf docs-backup-$(date +%Y%m%d).tar.gz documents/
```

2. **自动备份脚本**

```bash
#!/bin/bash
BACKUP_DIR="/backup/rag-game"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份应用文件
tar -czf $BACKUP_DIR/app-$DATE.tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.log' \
    .

# 保留最近7天的备份
find $BACKUP_DIR -name "app-*.tar.gz" -mtime +7 -delete

echo "备份完成：$BACKUP_DIR/app-$DATE.tar.gz"
```

---

## 📞 技术支持

如果在部署过程中遇到问题，请：

1. 检查系统日志：`journalctl -u rag-game`
2. 查看应用日志：`tail -f game.log`
3. 验证网络连接：`curl http://localhost:8501`
4. 检查端口状态：`netstat -tulpn | grep 8501`

更多技术支持，请参考项目README或提交Issue。