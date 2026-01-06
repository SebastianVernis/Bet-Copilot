#!/bin/bash
# Generate self-signed SSL certificates for development/alpha testing

set -e

echo "🔐 Generating Self-Signed SSL Certificates"
echo "=========================================="
echo ""

# Create SSL directory
SSL_DIR="docker/ssl"
mkdir -p "$SSL_DIR"

# Certificate details
DOMAIN="${1:-localhost}"
DAYS=365

echo "📝 Certificate Details:"
echo "   Domain: $DOMAIN"
echo "   Valid for: $DAYS days"
echo ""

# Generate private key
echo "🔑 Generating private key..."
openssl genrsa -out "$SSL_DIR/key.pem" 2048

# Generate certificate
echo "📜 Generating certificate..."
openssl req -new -x509 \
    -key "$SSL_DIR/key.pem" \
    -out "$SSL_DIR/cert.pem" \
    -days "$DAYS" \
    -subj "/C=US/ST=State/L=City/O=BetCopilot/OU=Alpha/CN=$DOMAIN"

# Set permissions
chmod 600 "$SSL_DIR/key.pem"
chmod 644 "$SSL_DIR/cert.pem"

echo ""
echo "✅ SSL certificates generated successfully!"
echo ""
echo "📁 Location: $SSL_DIR/"
echo "   - Certificate: cert.pem"
echo "   - Private Key: key.pem"
echo ""
echo "⚠️  Note: These are self-signed certificates for development."
echo "   Browsers will show a security warning (click 'Advanced' → 'Proceed')"
echo ""
echo "🚀 For production, use Let's Encrypt:"
echo "   certbot certonly --standalone -d your-domain.com"
