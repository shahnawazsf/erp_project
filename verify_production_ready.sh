#!/bin/bash

# Production Readiness Verification Script
# Usage: bash verify_production_ready.sh

echo "═══════════════════════════════════════════════════════════"
echo "  ERP Production Readiness Checker"
echo "═══════════════════════════════════════════════════════════"
echo ""

PASS=0
FAIL=0
WARN=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check() {
    local name=$1
    local condition=$2
    local critical=$3  # true if critical, false if warning

    if eval "$condition"; then
        echo -e "${GREEN}✓${NC} $name"
        ((PASS++))
    else
        if [ "$critical" = "true" ]; then
            echo -e "${RED}✗${NC} $name"
            ((FAIL++))
        else
            echo -e "${YELLOW}⚠${NC} $name"
            ((WARN++))
        fi
    fi
}

echo "📋 Checking Django Configuration..."
echo ""

# Check .env file
check "Environment file (.env) exists" "[ -f .env ]" true

# Check static files
check "Static files collected" "[ -d staticfiles ] && [ -f staticfiles/staticfiles.json ]" true

# Check key Django files
check "settings.py exists" "[ -f erp_project/settings.py ]" true
check "wsgi.py exists" "[ -f erp_project/wsgi.py ]" true
check "urls.py exists" "[ -f erp_project/urls.py ]" true

echo ""
echo "📦 Checking Python Packages..."
echo ""

# Check required packages
check "Django installed" "python -c 'import django' 2>/dev/null" true
check "Waitress installed" "python -c 'import waitress' 2>/dev/null" true
check "oracledb installed" "python -c 'import oracledb' 2>/dev/null" true
check "WhiteNoise installed" "python -c 'import whitenoise' 2>/dev/null" true

echo ""
echo "🗄️ Checking Database..."
echo ""

# Check database connection
check "Can connect to Oracle" "python manage.py dbshell 2>&1 | grep -q 'SQL>' || [ $? -eq 0 ]" false

echo ""
echo "📁 Checking Directory Structure..."
echo ""

# Check directories
check "templates/ directory exists" "[ -d templates ]" true
check "staticfiles/ directory exists" "[ -d staticfiles ]" true
check "logs/ directory exists or can be created" "[ -d logs ] || mkdir -p logs 2>/dev/null" true

echo ""
echo "🔐 Checking Security Settings..."
echo ""

# Check settings for production
DEBUG_SETTING=$(grep "^DEBUG" erp_project/settings.py | grep -i false)
check "DEBUG set to False" "[ -n '$DEBUG_SETTING' ]" false

SECRET_KEY_CHECK=$(grep "SECRET_KEY" erp_project/settings.py | grep -v "insecure")
check "SECRET_KEY is not default" "[ -n '$SECRET_KEY_CHECK' ]" false

check "ALLOWED_HOSTS configured" "grep 'ALLOWED_HOSTS' erp_project/settings.py | grep -v '\[\*\]' >/dev/null 2>&1" false

echo ""
echo "📡 Checking Server Configuration..."
echo ""

check "Port 9001 is available" "netstat -tuln 2>/dev/null | grep ':9001' || echo 'Available' | grep -q Available" false

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Summary"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${YELLOW}Warnings: $WARN${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -gt 0 ]; then
    echo -e "${RED}❌ NOT READY FOR PRODUCTION${NC}"
    echo ""
    echo "Required fixes:"
    echo "1. Ensure all failed checks are resolved"
    echo "2. Run: python manage.py collectstatic --noinput"
    echo "3. Create .env file with production settings"
    echo "4. Set DEBUG=False in settings.py"
    exit 1
else
    echo -e "${GREEN}✅ READY FOR PRODUCTION${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review PRODUCTION_DEPLOYMENT.md"
    echo "2. Start server: python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application"
    echo "3. Monitor logs: tail -f logs/django.log"
    exit 0
fi
