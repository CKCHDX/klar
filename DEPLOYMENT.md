# 🚀 Deployment Guide - KSE Production Setup

## Overview

This guide walks you through deploying KSE (Klar Search Engine) to a production server.

---

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.9 or higher
- 2GB+ RAM
- 10GB+ disk space
- Internet connection for crawling

---

## Quick Deployment (Ubuntu/Debian)

### 1. Clone Repository

```bash
# SSH to your server
ssh user@your-server.com

# Clone the repository
cd /opt
sudo git clone https://github.com/CKCHDX/klar.git
cd klar

# Switch to main branch (after merging PR)
git checkout main
```

### 2. Install Dependencies

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv -y

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install KSE
pip install -e .

# Verify installation
pip list | grep -E "Flask|nltk|urllib3"
```

### 3. Configure KSE

```bash
# Edit configuration
nano config/kse_default_config.yaml
```

Update settings:
```yaml
server:
  host: "0.0.0.0"  # Listen on all interfaces
  port: 5000
  debug: false

crawler:
  crawl_delay: 2.0  # Be respectful (2 seconds between requests)
  crawl_depth: 100  # More pages per domain
```

### 4. Add Swedish Domains

```bash
# Edit domains list
nano config/swedish_domains.json
```

Add more Swedish domains to crawl.

### 5. Run Initial Test

```bash
# Test the system
python scripts/test_end_to_end.py

# Should output: ✓ END-TO-END TEST COMPLETED SUCCESSFULLY
```

### 6. Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/kse.service
```

Add:
```ini
[Unit]
Description=KSE (Klar Search Engine) API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/klar
Environment="PATH=/opt/klar/venv/bin"
ExecStart=/opt/klar/venv/bin/python -m kse.server.kse_server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable kse
sudo systemctl start kse
sudo systemctl status kse
```

### 7. Setup Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/kse
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/kse /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. Setup SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

### 9. Run Crawler

```bash
# Create crawler service
sudo nano /etc/systemd/system/kse-crawler.service
```

Add:
```ini
[Unit]
Description=KSE Web Crawler
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/klar
Environment="PATH=/opt/klar/venv/bin"
ExecStart=/opt/klar/venv/bin/python scripts/start_crawler.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Run crawler:
```bash
sudo systemctl start kse-crawler
sudo systemctl status kse-crawler
```

### 10. Monitor & Maintain

```bash
# View API logs
sudo journalctl -u kse -f

# View crawler logs
sudo journalctl -u kse-crawler -f

# Check application logs
tail -f /opt/klar/data/logs/kse.log
tail -f /opt/klar/data/logs/crawler.log
```

---

## Production Checklist

### Security
- [ ] Use HTTPS (SSL certificate via Certbot)
- [ ] Configure firewall (UFW)
- [ ] Add API authentication (if public)
- [ ] Restrict server ports (only 80, 443, SSH)
- [ ] Regular security updates

### Performance
- [ ] Configure rate limiting in Nginx
- [ ] Setup log rotation
- [ ] Monitor disk space
- [ ] Setup automated backups
- [ ] Consider using Redis for caching

### Monitoring
- [ ] Setup monitoring (Prometheus/Grafana)
- [ ] Configure alerts
- [ ] Monitor API response times
- [ ] Track crawler statistics
- [ ] Monitor server resources

---

## Firewall Configuration

```bash
# Install UFW
sudo apt install ufw -y

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

---

## Backup Strategy

```bash
# Create backup script
nano /opt/klar/backup.sh
```

Add:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/kse"
mkdir -p $BACKUP_DIR

# Backup data
tar -czf $BACKUP_DIR/kse_data_$DATE.tar.gz /opt/klar/data

# Keep only last 7 days
find $BACKUP_DIR -name "kse_data_*.tar.gz" -mtime +7 -delete
```

Make executable and schedule:
```bash
chmod +x /opt/klar/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /opt/klar/backup.sh
```

---

## Scaling (Optional)

### For High Traffic:

1. **Use Gunicorn** instead of Flask dev server:
```bash
pip install gunicorn

# Update systemd service
ExecStart=/opt/klar/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 kse.server.kse_server:app
```

2. **Setup Redis** for caching:
```bash
sudo apt install redis-server -y
pip install redis
```

3. **Load Balancer** with multiple instances:
```bash
# Setup multiple KSE instances on different ports
# Configure Nginx to load balance between them
```

---

## Health Checks

### API Health Check
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "index_stats": {
    "total_documents": 1000,
    "total_terms": 5000
  }
}
```

### System Health
```bash
# Check service status
sudo systemctl status kse

# Check disk space
df -h

# Check memory
free -h

# Check logs for errors
grep ERROR /opt/klar/data/logs/kse.log
```

---

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u kse -n 50

# Check permissions
sudo chown -R www-data:www-data /opt/klar

# Check Python path
which python
```

### Slow search responses
```bash
# Check index size
ls -lh /opt/klar/data/storage/index/

# Rebuild index if needed
cd /opt/klar
source venv/bin/activate
python scripts/rebuild_index.py
```

### Crawler not working
```bash
# Check internet connectivity
ping google.com

# Check robots.txt compliance
cat /opt/klar/data/logs/crawler.log | grep "robots.txt"

# Test crawler manually
python scripts/start_crawler.py
```

---

## Maintenance Tasks

### Weekly
- Check error logs
- Monitor disk usage
- Review crawl statistics

### Monthly
- Update dependencies (after testing)
- Review and optimize index
- Clean old logs
- Verify backups

### Quarterly
- Security audit
- Performance review
- Update Swedish domains list
- Review and update configuration

---

## Cost Estimate

### Minimum Setup
- **Server**: $5-10/month (DigitalOcean, Linode)
- **Domain**: $10-15/year
- **SSL**: Free (Let's Encrypt)
- **Total**: ~$6-11/month

### Recommended Setup
- **Server**: $20-40/month (4GB RAM, 2 CPUs)
- **Backup Storage**: $5/month
- **Domain**: $10-15/year
- **Monitoring**: Free (self-hosted)
- **Total**: ~$26-46/month

---

## Support

For deployment issues:
1. Check logs: `/opt/klar/data/logs/`
2. Review systemd status: `sudo systemctl status kse`
3. Test manually: `python -m kse.server.kse_server`
4. Verify configuration: `cat config/kse_default_config.yaml`

---

**Last Updated**: 2026-01-29  
**Tested On**: Ubuntu 20.04, 22.04
