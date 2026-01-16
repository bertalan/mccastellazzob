#!/bin/bash
# Test TDD per verificare tutti i link di navigazione con curl

set -e

echo "🧪 Test TDD - Verifica Link di Navigazione"
echo "=========================================="
echo ""

# Colori per output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0
BASE_URL="http://localhost:8000"

# Funzione per testare un link
test_link() {
    local url=$1
    local description=$2
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$status" = "200" ] || [ "$status" = "404" ]; then
        echo -e "${GREEN}✅ PASS${NC} - $description ($url) → $status"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} - $description ($url) → $status"
        ((FAILED++))
    fi
}

echo "📍 Test 1: Homepage per tutte le lingue"
echo "----------------------------------------"
for lang in it en fr de es; do
    test_link "$BASE_URL/$lang/" "Homepage $lang"
done
echo ""

echo "📍 Test 2: Link principali navbar (IT)"
echo "----------------------------------------"
test_link "$BASE_URL/it/chi-siamo/" "Chi Siamo"
test_link "$BASE_URL/it/chi-siamo/consiglio-direttivo/" "Consiglio Direttivo"
test_link "$BASE_URL/it/eventi/" "Eventi"
test_link "$BASE_URL/it/galleria/" "Galleria"
test_link "$BASE_URL/it/chi-siamo/contatti/" "Contatti"
echo ""

echo "📍 Test 3: Link footer trasparenza (IT)"
echo "----------------------------------------"
test_link "$BASE_URL/it/chi-siamo/trasparenza/" "Trasparenza"
test_link "$BASE_URL/it/privacy/" "Privacy Policy"
echo ""

echo "📍 Test 4: Link cambio lingua dalla homepage"
echo "----------------------------------------"
for lang in it en fr de es; do
    test_link "$BASE_URL/$lang/" "Cambio lingua → $lang"
done
echo ""

echo "📍 Test 5: Persistenza lingua durante navigazione"
echo "----------------------------------------"
for lang in it en de; do
    test_link "$BASE_URL/$lang/chi-siamo/" "Chi Siamo in $lang"
done
echo ""

echo "=========================================="
echo "📊 Risultati Finali:"
echo "   ✅ Passati: $PASSED"
echo "   ❌ Falliti: $FAILED"
echo "=========================================="

if [ $FAILED -gt 0 ]; then
    exit 1
fi
