#!/usr/bin/env python3
"""
Script per correggere i tag di traduzione da {% trans %}...{% endtrans %}
al formato corretto per Jinja2: {{ _("...") }}
"""
import re
from pathlib import Path

# Template files to fix
TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "website" / "pages"

FILES_TO_FIX = [
    "about_page.jinja2",
    "contact_page.jinja2",
    "privacy_page.jinja2",
]

def fix_trans_tags(content: str) -> str:
    """Replace {% trans %}...{% endtrans %} with {{ _("...") }}"""
    # Pattern to match {% trans %}...{% endtrans %}
    pattern = r'\{%\s*trans\s*%\}(.*?)\{%\s*endtrans\s*%\}'
    
    def replace_match(match):
        text = match.group(1)
        # Escape any double quotes in the text
        text = text.replace('"', '\\"')
        return f'{{{{ _("{text}") }}}}'
    
    return re.sub(pattern, replace_match, content, flags=re.DOTALL)


def main():
    for filename in FILES_TO_FIX:
        filepath = TEMPLATE_DIR / filename
        if not filepath.exists():
            print(f"⚠️  File not found: {filepath}")
            continue
        
        content = filepath.read_text(encoding="utf-8")
        
        # Count matches before
        pattern = r'\{%\s*trans\s*%\}.*?\{%\s*endtrans\s*%\}'
        matches = re.findall(pattern, content, flags=re.DOTALL)
        
        if not matches:
            print(f"✓  {filename}: No trans tags found")
            continue
        
        # Fix the content
        new_content = fix_trans_tags(content)
        
        # Write back
        filepath.write_text(new_content, encoding="utf-8")
        print(f"✅ {filename}: Fixed {len(matches)} trans tags")


if __name__ == "__main__":
    main()
