#!/usr/bin/env python3
"""
Test TDD per verificare tutti i link di navigazione.
"""

import requests
from typing import List, Tuple

BASE_URL = "http://localhost:8000"

# Emoji per output
PASS = "✅"
FAIL = "❌"
INFO = "📍"

passed = 0
failed = 0


def test_link(url: str, description: str, expected_statuses: List[int] = [200]) -> bool:
    """Test un singolo link."""
    global passed, failed
    
    try:
        response = requests.get(url, timeout=5)
        status = response.status_code
        
        if status in expected_statuses:
            print(f"{PASS} PASS - {description} ({url}) → {status}")
            passed += 1
            return True
        else:
            print(f"{FAIL} FAIL - {description} ({url}) → {status} (atteso: {expected_statuses})")
            failed += 1
            return False
    except Exception as e:
        print(f"{FAIL} FAIL - {description} ({url}) → ERROR: {str(e)}")
        failed += 1
        return False


def main():
    global passed, failed
    
    print("🧪 Test TDD - Verifica Link di Navigazione")
    print("=" * 60)
    print()

    # Test 1: Homepage per tutte le lingue
    print(f"{INFO} Test 1: Homepage per tutte le lingue")
    print("-" * 60)
    for lang in ['it', 'en', 'fr', 'de', 'es']:
        test_link(f"{BASE_URL}/{lang}/", f"Homepage {lang.upper()}")
    print()

    # Test 2: Link principali navbar (IT)
    print(f"{INFO} Test 2: Link principali navbar (IT)")
    print("-" * 60)
    navbar_links = [
        ('/', 'Home'),
        ('/chi-siamo/', 'Chi Siamo'),
        ('/chi-siamo/consiglio/', 'Consiglio Direttivo'),
        ('/eventi/', 'Eventi'),
        ('/galleria/', 'Galleria'),
        ('/chi-siamo/contatti/', 'Contatti'),
    ]
    for path, name in navbar_links:
        test_link(f"{BASE_URL}/it{path}", name, [200])
    print()

    # Test 3: Link footer trasparenza (IT)
    print(f"{INFO} Test 3: Link footer trasparenza (IT)")
    print("-" * 60)
    footer_links = [
        ('/chi-siamo/trasparenza/', 'Trasparenza'),
        ('/privacy/', 'Privacy Policy'),
    ]
    for path, name in footer_links:
        test_link(f"{BASE_URL}/it{path}", name, [200])
    print()

    # Test 4: Persistenza lingua durante navigazione
    print(f"{INFO} Test 4: Persistenza lingua durante navigazione")
    print("-" * 60)
    for lang in ['it', 'en', 'de']:
        test_link(f"{BASE_URL}/{lang}/chi-siamo/", f"Chi Siamo in {lang.upper()}", [200, 404])
    print()

    # Test 5: Verifica contenuto homepage con bandiere
    print(f"{INFO} Test 5: Verifica contenuto homepage con bandiere")
    print("-" * 60)
    try:
        response = requests.get(f"{BASE_URL}/it/", timeout=5)
        content = response.text
        
        # Verifica flag emojis
        flags = ['🇮🇹', '🇬🇧', '🇫🇷', '🇩🇪', '🇪🇸']
        all_flags_present = all(flag in content for flag in flags)
        
        if all_flags_present:
            print(f"{PASS} PASS - Tutte le bandiere presenti nel language switcher")
            passed += 1
        else:
            missing = [f for f in flags if f not in content]
            print(f"{FAIL} FAIL - Bandiere mancanti: {missing}")
            failed += 1
            
        # Verifica link cambio lingua
        lang_links_present = all(f'/{lang}/' in content for lang in ['it', 'en', 'fr', 'de', 'es'])
        
        if lang_links_present:
            print(f"{PASS} PASS - Tutti i link cambio lingua presenti")
            passed += 1
        else:
            print(f"{FAIL} FAIL - Alcuni link cambio lingua mancanti")
            failed += 1
            
    except Exception as e:
        print(f"{FAIL} FAIL - Errore nel test contenuto: {str(e)}")
        failed += 2
    print()

    # Test 6: Link social nel footer
    print(f"{INFO} Test 6: Link social nel footer")
    print("-" * 60)
    try:
        response = requests.get(f"{BASE_URL}/it/", timeout=5)
        content = response.text
        
        social_icons = ['fa-facebook-f', 'fa-instagram', 'fa-youtube']
        all_social_present = all(icon in content for icon in social_icons)
        
        if all_social_present:
            print(f"{PASS} PASS - Tutte le icone social presenti")
            passed += 1
        else:
            print(f"{FAIL} FAIL - Alcune icone social mancanti")
            failed += 1
            
    except Exception as e:
        print(f"{FAIL} FAIL - Errore nel test social: {str(e)}")
        failed += 1
    print()

    # Test 7: Email e telefono nel footer
    print(f"{INFO} Test 7: Email e telefono nel footer")
    print("-" * 60)
    try:
        response = requests.get(f"{BASE_URL}/it/", timeout=5)
        content = response.text
        
        if 'mailto:info@mccastellazzo.it' in content:
            print(f"{PASS} PASS - Link email presente")
            passed += 1
        else:
            print(f"{FAIL} FAIL - Link email mancante")
            failed += 1
            
        if 'tel:+390123456789' in content:
            print(f"{PASS} PASS - Link telefono presente")
            passed += 1
        else:
            print(f"{FAIL} FAIL - Link telefono mancante")
            failed += 1
            
    except Exception as e:
        print(f"{FAIL} FAIL - Errore nel test contatti: {str(e)}")
        failed += 2
    print()

    # Risultati finali
    print("=" * 60)
    print("📊 Risultati Finali:")
    print(f"   {PASS} Passati: {passed}")
    print(f"   {FAIL} Falliti: {failed}")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
