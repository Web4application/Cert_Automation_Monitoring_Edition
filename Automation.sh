#!/bin/bash
set -e

echo "🚀 Starting WEB4 Analytics Ultra Production Installer..."

# ------------------------------
# CONFIGURATION
# ------------------------------
PRIMARY_DOMAIN="analytics.web4.com"
ADMIN_EMAIL="admin@web4.com"
ADMIN_PASSWORD="SuperSecure123!"
SUBDOMAIN_FILE="panels.txt"  # optional additional panels, one per line

# Cloudflare API
CLOUDFLARE_TOKEN="YOUR_CLOUDFLARE_API_TOKEN"
CLOUDFLARE_ZONE="web4.com"

# SMTP provider
SMTP_HOST="smtp.mailgun.org"
SMTP_PORT=587
SMTP_USER="postmaster@web4.com"
SMTP_PASS="YOUR_MAILGUN_PASSWORD"

# PostgreSQL credentials (superuser)
PG_SUPERUSER="postgres"
PG_SUPERPASS="postgres_password"

# ------------------------------
# DEPENDENCIES
# ------------------------------
sudo apt update
sudo apt install -y docker.io docker-compose git curl certbot jq postgresql-client
sudo systemctl enable --now docker

# ------------------------------
# CLONE OPENPANEL
# ------------------------------
git clone https://github.com/openpanel-dev/openpanel.git
cd openpanel/self-hosting

# ------------------------------
# FUNCTIONS
# ------------------------------

create_env() {
    local DOMAIN=$1
    local DB_NAME=$2
    local DB_USER=$3
    local DB_PASS=$4
    cat > .env <<EOL
OPENPANEL_APP_NAME=WEB4 Analytics
OPENPANEL_DOMAIN=$DOMAIN
OPENPANEL_PORT=8080
OPENPANEL_BASE_URL=https://$DOMAIN
OPENPANEL_ADMIN_EMAIL=$ADMIN_EMAIL
OPENPANEL_ADMIN_PASSWORD=$ADMIN_PASSWORD

OPENPANEL_DB_TYPE=postgres
OPENPANEL_DB_HOST=db
OPENPANEL_DB_PORT=5432
OPENPANEL_DB_NAME=$DB_NAME
OPENPANEL_DB_USER=$DB_USER
OPENPANEL_DB_PASSWORD=$DB_PASS

# SMTP
OPENPANEL_EMAIL_FROM_NAME=WEB4 Analytics
OPENPANEL_EMAIL_FROM_ADDRESS=no-reply@$DOMAIN
OPENPANEL_EMAIL_SMTP_HOST=$SMTP_HOST
OPENPANEL_EMAIL_SMTP_PORT=$SMTP_PORT
OPENPANEL_EMAIL_SMTP_USER=$SMTP_USER
OPENPANEL_EMAIL_SMTP_PASS=$SMTP_PASS
OPENPANEL_EMAIL_USE_TLS=true

# SSL
OPENPANEL_SSL_CERT=/etc/letsencrypt/live/$DOMAIN/fullchain.pem
OPENPANEL_SSL_KEY=/etc/letsencrypt/live/$DOMAIN/privkey.pem

OPENPANEL_ENABLE_COOKIELESS=true
OPENPANEL_TRACK_RETENTION=true
OPENPANEL_ENABLE_DEMO_DATA=false
EOL
}

add_dns() {
    local DOMAIN=$1
    echo "🔹 Adding DNS A record for $DOMAIN via Cloudflare..."
    ZONE_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=$CLOUDFLARE_ZONE" \
        -H "Authorization: Bearer $CLOUDFLARE_TOKEN" \
        -H "Content-Type: application/json" | jq -r '.result[0].id')
    curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
        -H "Authorization: Bearer $CLOUDFLARE_TOKEN" \
        -H "Content-Type: application/json" \
        --data "{\"type\":\"A\",\"name\":\"$DOMAIN\",\"content\":\"$(curl -s ifconfig.me)\",\"ttl\":120,\"proxied\":false}" > /dev/null
}

wait_dns() {
    local DOMAIN=$1
    SERVER_IP=$(curl -s ifconfig.me)
    echo "⏳ Waiting for DNS to propagate for $DOMAIN..."
    while true; do
        DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)
        if [[ "$DOMAIN_IP" == "$SERVER_IP" ]]; then
            echo "✅ DNS propagated for $DOMAIN"
            break
        fi
        sleep 5
    done
}

create_db() {
    local DB_NAME=$1
    local DB_USER=$2
    local DB_PASS=$3
    echo "💾 Creating PostgreSQL database $DB_NAME and user $DB_USER..."
    PGPASSWORD=$PG_SUPERPASS psql -U $PG_SUPERUSER -h localhost -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" || true
    PGPASSWORD=$PG_SUPERPASS psql -U $PG_SUPERUSER -h localhost -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" || true
}

deploy_panel() {
    local DOMAIN=$1
    local DB_NAME="db_$(echo $DOMAIN | tr '.' '_')"
    local DB_USER="user_$(echo $DOMAIN | tr '.' '_')"
    local DB_PASS=$(openssl rand -base64 12)

    add_dns $DOMAIN
    wait_dns $DOMAIN
    create_db $DB_NAME $DB_USER $DB_PASS
    create_env $DOMAIN $DB_NAME $DB_USER $DB_PASS
    sudo certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos -m $ADMIN_EMAIL
    docker-compose up -d --build
    echo "🎉 Panel deployed: $DOMAIN (DB: $DB_NAME)"
}

# ------------------------------
# DEPLOY PRIMARY PANEL
# ------------------------------
deploy_panel $PRIMARY_DOMAIN

# ------------------------------
# DEPLOY ADDITIONAL PANELS
# ------------------------------
if [[ -f "../$SUBDOMAIN_FILE" ]]; then
    while IFS= read -r DOMAIN; do
        [[ -z "$DOMAIN" ]] && continue
        PANEL_DIR="../${DOMAIN//./_}"
        cp -r . "$PANEL_DIR"
        cd "$PANEL_DIR"
        deploy_panel $DOMAIN
        cd ..
    done < "../$SUBDOMAIN_FILE"
fi

echo "🎉 All WEB4 Analytics panels deployed with DNS + SSL + SMTP + isolated databases!"
