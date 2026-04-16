# Vue.js Frontend Deployment Guide

Your Vue.js build is located at: `C:\Users\PMLS\OneDrive\Documents\dist\dist`

## Option 1: Manual Upload (Quick)

**From your local machine:**

```bash
# Windows PowerShell
scp -r "C:\Users\PMLS\OneDrive\Documents\dist\dist\*" root@209.74.88.53:/var/www/html/

# Or on Mac/Linux
scp -r ~/Documents/dist/dist/* root@209.74.88.53:/var/www/html/
```

Then restart Apache:
```bash
ssh root@209.74.88.53
systemctl restart httpd
```

## Option 2: Automated with CI/CD (Recommended)

**Step 1: Add Vue.js dist to your Git repo**

```bash
cd C:\Users\PMLS\OneDrive\Desktop\Hotel Maar\HotelBookingEngine

# Copy Vue.js build into repo
cp -r "C:\Users\PMLS\OneDrive\Documents\dist\dist" ./public_html

# Commit and push
git add public_html/
git commit -m "Add Vue.js frontend build"
git push origin main
```

**Step 2: Update GitHub Actions workflow**

The workflow already has frontend deployment placeholder. On server, create:

```bash
cat > /HotelBookingEngine/scripts/deploy-frontend.sh << 'EOF'
#!/bin/bash
# Copy frontend build to public_html
cp -r /HotelBookingEngine/public_html/* /var/www/html/
chmod -R 755 /var/www/html
chown -R nobody:nobody /var/www/html
systemctl restart httpd
echo "✓ Frontend deployed"
EOF

chmod +x /HotelBookingEngine/scripts/deploy-frontend.sh
```

**Step 3: Update workflow to call the script**

Edit `.github/workflows/deploy.yml` and add to deploy-frontend step:

```yaml
script: |
  cd /HotelBookingEngine
  ./scripts/deploy-frontend.sh
```

## Step 3: Configure Apache for Vue.js (Required)

**On your server**, create Apache config:

```bash
cat > /etc/httpd/conf.d/frontend.conf << 'EOF'
<VirtualHost *:80>
    ServerName marhotels.com.sa
    ServerAlias www.marhotels.com.sa
    DocumentRoot /var/www/html
    
    <Directory /var/www/html>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
        
        # Vue Router - send all requests to index.html
        <IfModule mod_rewrite.c>
            RewriteEngine On
            RewriteBase /
            RewriteRule ^index\.html$ - [L]
            RewriteCond %{REQUEST_FILENAME} !-f
            RewriteCond %{REQUEST_FILENAME} !-d
            RewriteRule . /index.html [L]
        </IfModule>
    </Directory>
    
    # Redirect API calls to backend
    ProxyPass /api http://127.0.0.1:9000/api
    ProxyPassReverse /api http://127.0.0.1:9000/api
</VirtualHost>
EOF

# Enable mod_rewrite
a2enmod rewrite
systemctl restart httpd
```

## Step 4: Remove old PHP file

```bash
# On server
rm /var/www/html/index.php
rm /var/www/html/*.php
```

## Step 5: Test

```bash
# From server
curl http://127.0.0.1/index.html

# Check Apache logs
tail -f /var/log/httpd/error_log

# Verify frontend is served
curl http://209.74.88.53/
```

## After DNS Setup

Once you point `marhotels.com.sa` → `209.74.88.53`:
- Frontend: `https://marhotels.com.sa`
- Backend API: `https://api.marhotels.com.sa` or just `/api` (proxied)

## Troubleshooting

**Frontend shows blank page:**
- Check browser console (F12) for errors
- Verify API calls go to correct endpoint
- Check Apache rewrite rules: `curl http://127.0.0.1/some-route`

**API calls failing:**
- Ensure backend is running: `docker-compose ps`
- Check ProxyPass is configured in Apache
- Verify CORS is enabled in Django settings

**Style/Script files missing:**
- Clear browser cache (Ctrl+Shift+Del)
- Check assets are in `/var/www/html/assets/`
- Verify file permissions: `ls -la /var/www/html/`

## Deployment Checklist

- [ ] Vue.js build copied to `/var/www/html`
- [ ] Apache frontend.conf created
- [ ] mod_rewrite enabled
- [ ] Apache restarted
- [ ] Old PHP files removed
- [ ] API proxy working (`curl http://127.0.0.1/api/v1/health/`)
- [ ] Frontend loads (no blank page)
- [ ] Vue Router works (navigation doesn't give 404)
