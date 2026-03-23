import os
import re

def check_html(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Check for unclosed div or mismatch
                        if content.count('<div') != content.count('</div'):
                            print(f'Mismatched div tags in {path}: <div {content.count("<div")} vs </div {content.count("</div")}')
                        
                        # Check for missing local scripts
                        for m in re.finditer(r'<script[^>]*src=[\"\']([^\"\']+)[\"\'][^>]*>', content):
                            src = m.group(1)
                            if not (src.startswith('http') or src.startswith('//')):
                                p = os.path.join(os.path.dirname(path), src)
                                if not os.path.exists(p):
                                    print(f'Missing script: {src} in {path}')
                                    
                        # Check for missing local css links
                        for m in re.finditer(r'<link[^>]*href=[\"\']([^\"\']+)[\"\'][^>]*>', content):
                            href = m.group(1)
                            if not (href.startswith('http') or href.startswith('//')):
                                p = os.path.join(os.path.dirname(path), href)
                                if not os.path.exists(p):
                                    print(f'Missing css: {href} in {path}')
                except Exception as e:
                    print(e)

check_html('frontend')
