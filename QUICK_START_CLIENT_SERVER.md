# Quick Start Guide: Klar Client-Server Setup

## For Users Who Just Want to Search

### Step 1: Ask Your Administrator for the Server URL
Your organization should provide you with a server URL, such as:
- `http://192.168.1.100:5000` (local network)
- `https://search.company.com` (public internet)

### Step 2: Download and Run Klar Browser
```bash
python start_klar_browser.py
```

### Step 3: Configure Server Connection
1. Click **File** → **Settings**
2. Enter the server URL your administrator gave you
3. Click **Test Connection** - you should see "✓ Connection successful"
4. Click **Save**

### Step 4: Start Searching!
Just type naturally in Swedish:
- "Var hittar jag svenska universitet?"
- "restauranger i Stockholm"
- "hur fungerar sökmotorer"

The search engine understands natural language - no need to think in keywords!

---

## For Administrators Setting Up the Server

### Step 1: Configure Server for Remote Access
Edit `config/kse_default_config.yaml`:
```yaml
server:
  host: "0.0.0.0"  # Accept connections from all network interfaces
  port: 5000
```

### Step 2: Start the Server
```bash
cd /path/to/klar
python -m kse.server.kse_server
```

### Step 3: Note the Network Information
The server will display:
```
============================================================
KSE Server Network Information
============================================================
Local Network:   http://192.168.1.100:5000
Public Access:   http://203.0.113.45:5000
  (Use this URL for remote clients)
Hostname:        my-server
============================================================

👉 For remote clients, use: http://203.0.113.45:5000
```

### Step 4: Share the URL with Your Users
- **Local network users:** Give them `http://192.168.1.100:5000`
- **Internet users:** Give them `http://203.0.113.45:5000`
  - ⚠️ **Important:** For production, use HTTPS with a reverse proxy (see REMOTE_CLIENT_GUIDE.md)

### Step 5: Configure Firewall (if needed)
```bash
# Allow port 5000
sudo ufw allow 5000/tcp
```

---

## Troubleshooting

### "Unable to connect to KSE server"

**For Users:**
1. Check that you entered the correct server URL
2. Make sure the URL starts with `http://` or `https://`
3. Ask your administrator if the server is running
4. Test from command line: `curl http://SERVER_URL/api/health`

**For Administrators:**
1. Verify server is running: `curl http://localhost:5000/api/health`
2. Check firewall: `sudo ufw status`
3. Ensure server is listening on `0.0.0.0`: `netstat -an | grep 5000`

### "Configuration not saving"

**Solution:**
- Check that you have write permissions to your home directory
- Look for error dialogs when clicking Save
- Try setting environment variable instead:
  ```bash
  export KSE_SERVER_URL=http://SERVER_IP:5000
  python start_klar_browser.py
  ```

### "Text is too small/large in GUI"

**Solution:**
The GUI now uses configurable font sizes. Edit `gui/kse_gui_config.py`:
```python
FONTS = {
    'size': {
        'small': 10,    # Increase these numbers
        'normal': 12,   # to make text larger
        'medium': 13,
        'large': 14,
        'title': 16,
        'header': 18,
    }
}
```

---

## Environment Variables

You can use environment variables to configure the system:

### Set Server URL (Highest Priority)
```bash
# Linux/Mac
export KSE_SERVER_URL=http://192.168.1.100:5000

# Windows
set KSE_SERVER_URL=http://192.168.1.100:5000
```

This overrides any saved configuration and is useful for:
- Testing different servers
- Shared computers
- Automated deployments

---

## Configuration Files

### Client Configuration
**Location:** `~/.kse/klar_browser_config.json`

**Contents:**
```json
{
  "server_url": "http://192.168.1.100:5000"
}
```

**Priority:**
1. Environment variable `KSE_SERVER_URL` (highest)
2. Config file `~/.kse/klar_browser_config.json`
3. Default `http://localhost:5000` (lowest)

---

## API Testing

You can test the server using curl:

```bash
# Check server health
curl http://SERVER_URL/api/health

# Get network information
curl http://SERVER_URL/api/server/info

# Perform a search
curl "http://SERVER_URL/api/search?q=svenska+universitet"

# Get statistics
curl http://SERVER_URL/api/stats
```

---

## Production Deployment Checklist

For deploying to production (public internet):

- [ ] **Use HTTPS** - Never use HTTP over public internet
- [ ] **Reverse Proxy** - Use nginx/Apache, not direct Flask exposure
- [ ] **Firewall** - Block direct access to port 5000
- [ ] **Authentication** - Add API keys or user authentication
- [ ] **Monitoring** - Set up logging and alerts
- [ ] **SSL Certificate** - Use Let's Encrypt for free HTTPS
- [ ] **Rate Limiting** - Prevent abuse
- [ ] **Backups** - Regular backups of index and config

See `REMOTE_CLIENT_GUIDE.md` for detailed production setup.

---

## Need More Help?

- **Remote Setup:** See `REMOTE_CLIENT_GUIDE.md`
- **NLP Examples:** See `NLP_EXAMPLES.md`
- **Full Documentation:** See `README.md`
- **Deployment:** See `KSE-DEPLOYMENT.md`
- **Security:** See `SECURITY.md`

---

## Summary

**Client Setup:**
```bash
# Set server URL
export KSE_SERVER_URL=http://SERVER_IP:5000

# Start client
python start_klar_browser.py

# Or use Settings dialog (File → Settings)
```

**Server Setup:**
```bash
# Edit config: set host to "0.0.0.0"
# Start server
python -m kse.server.kse_server

# Note the public IP displayed
# Share with clients
```

**That's it!** You now have a working client-server search engine with natural language support.
