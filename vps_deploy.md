# VPS Deployment Guide

## Setup on Ubuntu/Debian VPS

1. **Update system**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install dependencies**:
   ```bash
   sudo apt install python3-pip nginx certbot python3-certbot-nginx
   pip3 install -r requirements.txt
   ```

3. **Setup systemd service**:
   ```bash
   sudo nano /etc/systemd/system/food-analyzer.service
   ```
   
   ```ini
   [Unit]
   Description=Food Quality Analyzer
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/food-analyzer
   Environment=PATH=/var/www/food-analyzer/venv/bin
   ExecStart=/var/www/food-analyzer/venv/bin/streamlit run food_quality_analyzer.py --server.port=8501
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. **Configure Nginx**:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Enable SSL**:
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

**Pros**: Full control, cost-effective
**Cons**: Requires server management skills