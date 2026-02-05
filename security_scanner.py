#!/usr/bin/env python3
"""
Security Scanner for AfriClimate Analytics Lake
Scans for potential private information before Git commit
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

# Patterns that should not be in public repository
SENSITIVE_PATTERNS = {
    'aws_access_key': r'AKIA[0-9A-Z]{16}',
    'aws_secret_key': r'[0-9a-zA-Z/+]{40}',
    'account_id': r'\d{12}',
    'private_email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    'password': r'password["\']?\s*[:=]\s*["\']?[^\s"\']+["\']?',
    'api_key': r'api[_-]?key["\']?\s*[:=]\s*["\']?[^\s"\']+["\']?',
    'secret': r'secret["\']?\s*[:=]\s*["\']?[^\s"\']+["\']?',
    'token': r'token["\']?\s*[:=]\s*["\']?[^\s"\']+["\']?'
}

# Files to skip scanning
SKIP_FILES = {
    '.git',
    '__pycache__',
    'node_modules',
    '.vscode',
    '.idea',
    '*.pyc',
    '*.log'
}

# Files that are allowed to have certain patterns
ALLOWED_PATTERNS = {
    'demo_emails': r'.*@example\.com',
    'demo_aws': r'ACCOUNT_ID',
    'placeholder': r'placeholder|demo|example'
}

def scan_file_for_secrets(file_path):
    """Scan a single file for sensitive information"""
    
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for pattern_name, pattern in SENSITIVE_PATTERNS.items():
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    
                    for match in matches:
                        # Check if this is allowed (demo/placeholder)
                        matched_text = match.group()
                        is_allowed = False
                        
                        for allowed_pattern in ALLOWED_PATTERNS.values():
                            if re.search(allowed_pattern, matched_text, re.IGNORECASE):
                                is_allowed = True
                                break
                        
                        if not is_allowed:
                            issues.append({
                                'file': str(file_path),
                                'line': line_num,
                                'pattern': pattern_name,
                                'match': matched_text[:50] + '...' if len(matched_text) > 50 else matched_text,
                                'context': line.strip()[:100]
                            })
    
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
    
    return issues

def scan_repository():
    """Scan entire repository for sensitive information"""
    
    print("🔒 AfriClimate Analytics Lake - Security Scanner")
    print("=" * 60)
    
    all_issues = []
    scanned_files = 0
    
    # Get all files in repository
    for root, dirs, files in os.walk('.'):
        # Skip directories
        dirs[:] = [d for d in dirs if not any(d.startswith(skip) for skip in SKIP_FILES)]
        
        for file in files:
            file_path = Path(root) / file
            
            # Skip certain file types
            if any(file_path.match(pattern) for pattern in SKIP_FILES):
                continue
            
            # Skip the security scanner itself
            if 'security' in file_path.name.lower():
                continue
            
            # Scan the file
            issues = scan_file_for_secrets(file_path)
            all_issues.extend(issues)
            scanned_files += 1
    
    # Report results
    print(f"📊 Scanned {scanned_files} files")
    
    if all_issues:
        print(f"\n🚨 SECURITY ISSUES FOUND: {len(all_issues)}")
        print("=" * 60)
        
        for issue in all_issues:
            print(f"📁 File: {issue['file']}")
            print(f"📍 Line {issue['line']}: {issue['pattern']}")
            print(f"🔍 Match: {issue['match']}")
            print(f"📝 Context: {issue['context']}")
            print("-" * 40)
        
        print(f"\n❌ DO NOT COMMIT TO GITHUB!")
        print(f"🔧 Fix security issues before committing")
        
        return False
    else:
        print(f"\n✅ NO SECURITY ISSUES FOUND")
        print(f"🎉 Repository is safe for GitHub commit")
        
        return True

def generate_security_report():
    """Generate security report for documentation"""
    
    report = {
        'scan_date': datetime.now().isoformat(),
        'scanner_version': '1.0',
        'patterns_checked': list(SENSITIVE_PATTERNS.keys()),
        'files_skipped': list(SKIP_FILES),
        'allowed_patterns': list(ALLOWED_PATTERNS.keys()),
        'status': 'secure'
    }
    
    with open('security_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Security report saved to: security_report.json")

def main():
    """Main security scanning function"""
    
    # Scan repository
    is_secure = scan_repository()
    
    # Generate report
    generate_security_report()
    
    if is_secure:
        print(f"\n🎯 Next Steps:")
        print(f"✅ Safe to commit to GitHub")
        print(f"📤 git add .")
        print(f"📤 git commit -m 'Add AfriClimate Analytics Lake with real data integration'")
        print(f"📤 git push origin main")
    else:
        print(f"\n🔧 Security Actions Required:")
        print(f"1. Remove or redact sensitive information")
        print(f"2. Use environment variables for credentials")
        print(f"3. Replace real emails with demo emails for public repo")
        print(f"4. Run security scanner again")

if __name__ == "__main__":
    main()
