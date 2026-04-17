# Generate self-signed SSL certificates for development
# For production, use Let's Encrypt with Certbot

param(
    [string]$Domain = "localhost",
    [int]$Days = 365,
    [string]$CertPath = ".\certs"
)

Write-Host "Generating self-signed SSL certificates for development..." -ForegroundColor Cyan
Write-Host "Domain: $Domain" -ForegroundColor Yellow
Write-Host "Days Valid: $Days" -ForegroundColor Yellow
Write-Host "Cert Path: $CertPath" -ForegroundColor Yellow

# Create certs directory if it doesn't exist
if (-not (Test-Path $CertPath)) {
    New-Item -ItemType Directory -Path $CertPath -Force | Out-Null
}

# Create certificate using Docker (if openssl not available locally)
$containerCmd = @'
$dockerfile = @"
FROM alpine:latest
RUN apk add --no-cache openssl
WORKDIR /certs
CMD ["openssl", "req", "-x509", "-newkey", "rsa:4096", "-keyout", "privkey.pem", "-out", "cert.pem", "-days", "365", "-nodes", "-subj", "/C=PK/ST=Sindh/L=Karachi/O=HotelMaar/CN=localhost"]
"@

$dockerfile | Out-File -FilePath "Dockerfile.certs" -Encoding UTF8
docker build -t cert-generator -f Dockerfile.certs .
docker run --rm -v "$($CertPath):/certs" cert-generator
Remove-Item "Dockerfile.certs"
'@

Invoke-Expression $containerCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ Certificates generated successfully!" -ForegroundColor Green
    Write-Host "Private Key: $CertPath/privkey.pem" -ForegroundColor Green
    Write-Host "Certificate: $CertPath/cert.pem" -ForegroundColor Green
    Write-Host "`nFor production deployment:" -ForegroundColor Yellow
    Write-Host "1. Use Let's Encrypt with Certbot" -ForegroundColor Yellow
    Write-Host "2. Mount certificates in docker-compose.yml" -ForegroundColor Yellow
    Write-Host "3. Set USE_HTTPS=true in .env" -ForegroundColor Yellow
} else {
    Write-Host "✗ Failed to generate certificates" -ForegroundColor Red
    exit 1
}
