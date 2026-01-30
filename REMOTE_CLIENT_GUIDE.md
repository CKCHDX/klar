# Klar Remote Client Connection Guide

This guide explains how to connect the Klar Browser client to a remote KSE server.

## Overview

Klar has two main components:
1. **KSE Server** - The backend search engine that indexes and serves search results
2. **Klar Browser** - The client application that users interact with to perform searches

By default, both run on the same machine (`localhost`). However, you can run the server on one machine and connect to it from client browsers on different machines across your network or the internet.

## Architecture

```
┌─────────────────────┐
│  Klar Browser       │  ← User's computer
│  (Client)           │
└──────────┬──────────┘
           │
           │ HTTP/HTTPS Request
           │ (Search queries)
           │
           ↓
┌─────────────────────┐
│  KSE Server         │  ← Your server
│  (Backend)          │
│  • Crawls websites  │
│  • Indexes content  │
│  • Ranks results    │
│  • Serves API       │
└─────────────────────┘
```

## Step 1: Configure the Server for Remote Access

### 1.1 Update Server Host Configuration

By default, the server binds to `127.0.0.1` (localhost only). To accept remote connections, you need to bind to `0.0.0.0` (all interfaces) or your specific network IP.

Edit `config/kse_default_config.yaml`:

```yaml
server:
  host: "0.0.0.0"  # Listen on all network interfaces
  port: 5000
  debug: false
  enable_cors: true
```

**Security Note:** When exposing the server to the network:
- **Use HTTPS in production** (not HTTP) - Configure SSL/TLS certificates
- Consider adding authentication to sensitive endpoints
- Use a firewall to restrict access to trusted IPs/networks
- Keep the server software updated
- Disable or restrict `/api/server/info` endpoint in production if exposing internal network details is a concern

### 1.2 Start the Server

```bash
cd /path/to/klar
python -m kse.server.kse_server
```

You should see output like:

```
============================================================
KSE Server Network Information
============================================================
Local Network:   http://192.168.1.100:5000
Listening on:    http://0.0.0.0:5000
Public Access:   http://203.0.113.45:5000
  (Use this URL for remote clients)
Hostname:        my-kse-server
============================================================

API endpoints:
  - GET  http://0.0.0.0:5000/api/search?q=<query>
  - GET  http://0.0.0.0:5000/api/server/info
  - GET  http://0.0.0.0:5000/api/health
  ...

👉 For remote clients, use: http://203.0.113.45:5000
```

**Important:** Note the IP addresses shown:
- **Local Network IP** (e.g., 192.168.1.100) - Use this for clients on the same local network
- **Public IP** (e.g., 203.0.113.45) - Use this for clients connecting from the internet

### 1.3 Test Server Accessibility

From another machine on your network, test the connection:

```bash
# Replace with your server's IP address
curl http://192.168.1.100:5000/api/health
```

You should get a JSON response:

```json
{
  "status": "healthy",
  "version": "3.0.0",
  "index_stats": {...},
  "network_info": {
    "public_ip": "203.0.113.45",
    "local_ip": "192.168.1.100",
    "hostname": "my-kse-server"
  }
}
```

## Step 2: Configure the Client (Klar Browser)

### 2.1 Using Environment Variable (Recommended)

Set the `KSE_SERVER_URL` environment variable before starting Klar Browser:

**Linux/Mac:**
```bash
export KSE_SERVER_URL=http://192.168.1.100:5000
python klar_browser.py
```

**Windows:**
```cmd
set KSE_SERVER_URL=http://192.168.1.100:5000
python klar_browser.py
```

### 2.2 Using Settings Dialog (User-Friendly)

1. Launch Klar Browser:
   ```bash
   python klar_browser.py
   ```

2. Open Settings:
   - Click **File** → **Settings**
   - Or press `Ctrl+,` (Cmd+, on Mac)

3. Configure Server URL:
   - Enter your server URL in the "KSE Server URL" field
   - Examples:
     - Local network: `http://192.168.1.100:5000`
     - Public internet: `http://203.0.113.45:5000`
     - Hostname: `http://my-kse-server.com:5000`

4. Test Connection:
   - Click "Test Connection" button
   - You should see "✓ Connection successful"

5. Save:
   - Click "Save" button
   - Configuration is saved to `~/.kse/klar_browser_config.json`
   - Settings persist across restarts

### 2.3 Using Configuration File (Advanced)

Create or edit `~/.kse/klar_browser_config.json`:

```json
{
  "server_url": "http://192.168.1.100:5000"
}
```

## Step 3: Configure the Control Center (Admin GUI)

For the Control Center admin interface, use the environment variable:

**Linux/Mac:**
```bash
export KSE_SERVER_URL=http://192.168.1.100:5000
python scripts/start_gui.py
```

**Windows:**
```cmd
set KSE_SERVER_URL=http://192.168.1.100:5000
python scripts/start_gui.py
```

Or edit the configuration directly in:
```python
gui/control_center/control_center_config.py
```

Change line:
```python
API_BASE_URL = os.getenv("KSE_SERVER_URL", "http://localhost:5000")
```

## Common Connection Scenarios

### Scenario 1: Same Local Network

**Use Case:** Server on one computer, clients on other computers in your home/office.

**Server Setup:**
- Server listens on: `0.0.0.0:5000`
- Local IP: `192.168.1.100` (example)

**Client Setup:**
- Server URL: `http://192.168.1.100:5000`

**Note:** HTTP is acceptable for local networks, but HTTPS is still recommended for sensitive data.

### Scenario 2: Public Internet Access

**Use Case:** Server in a data center, clients connecting from anywhere.

**⚠️ IMPORTANT: Do NOT expose port 5000 directly to the internet. Use a reverse proxy with HTTPS.**

**Server Setup:**
- Server listens on: `127.0.0.1:5000` (localhost only, not exposed)
- Nginx/Apache reverse proxy handles HTTPS on port 443
- Public domain: `search.example.com`

**Client Setup:**
- Server URL: `https://search.example.com` (no port needed, uses default 443)

**Critical Security Checklist:**
- [ ] **MUST** use HTTPS (not HTTP) - Get SSL certificate from Let's Encrypt
- [ ] **MUST** use reverse proxy (nginx/Apache) - Never expose Flask directly
- [ ] Add authentication (JWT, API keys, or user login)
- [ ] Configure firewall rules - Block direct access to port 5000
- [ ] Use rate limiting to prevent abuse
- [ ] Monitor logs for suspicious activity
- [ ] Keep all software updated

### Scenario 3: Development Team

**Use Case:** Development server shared by team members.

**Server Setup:**
- Server on development machine: `192.168.10.50:5000`
- Or use hostname: `dev-server:5000`

**Client Setup:**
- Team members set: `http://dev-server:5000`
- Or: `http://192.168.10.50:5000`

## Troubleshooting

### Connection Refused

**Symptoms:** 
- Error: "Unable to connect to KSE server"
- Connection refused or timeout

**Solutions:**
1. Verify server is running:
   ```bash
   curl http://localhost:5000/api/health
   ```

2. Check firewall:
   ```bash
   # Linux
   sudo ufw status
   sudo ufw allow 5000/tcp
   
   # Windows
   # Check Windows Firewall settings
   ```

3. Verify server is listening on correct interface:
   ```bash
   netstat -an | grep 5000
   # Should show: 0.0.0.0:5000 or *:5000
   ```

### Wrong IP Address

**Symptoms:**
- Server shows wrong public IP
- Can't connect from internet

**Solutions:**
1. Check actual public IP:
   ```bash
   curl https://api.ipify.org
   ```

2. Verify port forwarding (if behind router):
   - Router must forward port 5000 to server's local IP
   - Example: Forward 203.0.113.45:5000 → 192.168.1.100:5000

### CORS Errors

**Symptoms:**
- Browser console shows CORS errors
- Search works from curl but not browser

**Solutions:**
1. Ensure CORS is enabled in `config/kse_default_config.yaml`:
   ```yaml
   server:
     enable_cors: true
   ```

2. Restart server after changing config

### Slow Searches from Remote

**Symptoms:**
- Searches take >2 seconds from remote clients
- Local searches are fast

**Solutions:**
1. Check network latency:
   ```bash
   ping 192.168.1.100
   ```

2. Consider deploying server closer to users

3. Enable caching on server:
   ```yaml
   cache:
     enabled: true
   ```

## Security Best Practices

When exposing KSE server to remote clients:

1. **Use HTTPS:** Never use HTTP over public internet
   - Use Let's Encrypt for free SSL certificates
   - Configure nginx/Apache as reverse proxy

2. **Authentication:** Add API authentication
   - Consider API keys
   - JWT tokens for user sessions
   - Rate limiting per IP

3. **Firewall:** Restrict access
   - Only allow necessary ports
   - Whitelist known client IPs if possible

4. **Monitoring:** Track usage
   - Monitor search logs
   - Set up alerts for unusual activity
   - Track failed connection attempts

5. **Updates:** Keep software current
   - Regularly update KSE server
   - Monitor security advisories
   - Use automated security scanning

## Production Deployment

For production deployment with remote clients:

1. **Use a reverse proxy (nginx):**

```nginx
server {
    listen 443 ssl;
    server_name search.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

2. **Use systemd service:**

```ini
[Unit]
Description=KSE Server
After=network.target

[Service]
Type=simple
User=kse
WorkingDirectory=/opt/kse
Environment="KSE_SERVER_HOST=127.0.0.1"
Environment="KSE_SERVER_PORT=5000"
ExecStart=/opt/kse/venv/bin/python -m kse.server.kse_server
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

3. **Configure clients:**
   - All clients use: `https://search.example.com`
   - No port numbers needed (default HTTPS port 443)
   - SSL certificate verified automatically

## Summary

- **Server:** Configure host as `0.0.0.0` to accept remote connections
- **Client:** Set server URL via environment variable, settings dialog, or config file
- **Network:** Ensure firewall allows connections to server port
- **Security:** Use HTTPS and authentication for production deployments

For more information:
- See `README.md` for general KSE documentation
- See `KSE-DEPLOYMENT.md` for server deployment details
- See `SECURITY.md` for security considerations
