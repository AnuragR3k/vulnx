#!/usr/bin/env python3
import requests
import re
import phonenumbers
from phonenumbers import carrier, geocoder
from colorama import init, Fore, Style
import sys

# Initialize colorama for colored output
init(autoreset=True)

class PrivacyCheckerCLI:
    """Terminal-based privacy checker for email and phone"""
    
    def __init__(self):
        self.banner()
    
    def banner(self):
        """Display banner"""
        print(Fore.CYAN + "="*60)
        print(Fore.CYAN + "🔍  PRIVACY FOOTPRINT CHECKER")
        print(Fore.CYAN + "    Check where your email/phone appears online")
        print(Fore.CYAN + "="*60)
        print()
    
    def check_email(self, email):
        """Check email privacy"""
        print(Fore.YELLOW + f"\n[*] Checking email: {email}")
        print("-" * 60)
        
        # 1. Validate format
        if self.validate_email(email):
            print(Fore.GREEN + "✓ Valid email format")
        else:
            print(Fore.RED + "✗ Invalid email format")
            return
        
        # 2. Domain info
        domain = email.split('@')[1]
        print(Fore.CYAN + f"\n[+] Domain: {domain}")
        common_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        if domain in common_domains:
            print(Fore.GREEN + "    → Common email provider")
        else:
            print(Fore.YELLOW + "    → Custom/Organization domain")
        
        # 3. Data breach check
        print(Fore.CYAN + "\n[+] Data Breach Check:")
        print(Fore.YELLOW + f"    → Manual check: https://haveibeenpwned.com/account/{email}")
        
        # 4. Social media accounts
        print(Fore.CYAN + "\n[+] Checking Social Media Accounts...")
        username = email.split('@')[0]
        self.check_social_accounts(username)
        
        # 5. Additional checks
        print(Fore.CYAN + "\n[+] Additional Resources:")
        print(f"    → Google Search: https://www.google.com/search?q={email}")
        print(f"    → Social Searcher: https://www.social-searcher.com/search-users/?q6={email}")
    
    def check_phone(self, phone):
        """Check phone number privacy"""
        print(Fore.YELLOW + f"\n[*] Checking phone: {phone}")
        print("-" * 60)
        
        try:
            # Parse phone number (default to India)
            parsed = phonenumbers.parse(phone, "IN")
            
            if phonenumbers.is_valid_number(parsed):
                print(Fore.GREEN + "✓ Valid phone number")
                
                # Country info
                country = geocoder.description_for_number(parsed, "en")
                print(Fore.CYAN + f"\n[+] Country: {country}")
                
                # Carrier info
                carrier_name = carrier.name_for_number(parsed, "en")
                if carrier_name:
                    print(Fore.CYAN + f"[+] Carrier: {carrier_name}")
                
                # Formats
                intl_format = phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                )
                nat_format = phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.NATIONAL
                )
                print(Fore.CYAN + f"[+] International Format: {intl_format}")
                print(Fore.CYAN + f"[+] National Format: {nat_format}")
                
                # Additional checks
                print(Fore.CYAN + "\n[+] Additional Resources:")
                clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
                print(f"    → Truecaller: https://www.truecaller.com/search/in/{clean_phone}")
                print(f"    → Google Search: https://www.google.com/search?q={phone}")
                
            else:
                print(Fore.RED + "✗ Invalid phone number")
        
        except Exception as e:
            print(Fore.RED + f"✗ Error: {str(e)}")
            print(Fore.YELLOW + "    Try including country code (e.g., +91 for India)")
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def check_social_accounts(self, username):
        """Check for social media accounts"""
        platforms = {
            'GitHub': f'https://github.com/{username}',
            'Twitter': f'https://twitter.com/{username}',
            'Instagram': f'https://instagram.com/{username}',
            'Reddit': f'https://reddit.com/user/{username}',
            'LinkedIn': f'https://linkedin.com/in/{username}'
        }
        
        found = []
        for platform, url in platforms.items():
            try:
                response = requests.head(url, timeout=2, allow_redirects=True)
                if response.status_code == 200:
                    found.append(f"{platform}: {url}")
                    print(Fore.GREEN + f"    ✓ Found on {platform}: {url}")
            except:
                pass
        
        if not found:
            print(Fore.YELLOW + "    → No accounts found on common platforms")
    
    def interactive_mode(self):
        """Interactive terminal interface"""
        while True:
            print(Fore.CYAN + "\n" + "="*60)
            print(Fore.WHITE + "Choose an option:")
            print("  1. Check Email")
            print("  2. Check Phone Number")
            print("  3. Exit")
            print(Fore.CYAN + "="*60)
            
            choice = input(Fore.WHITE + "\nEnter choice (1/2/3): ").strip()
            
            if choice == '1':
                email = input(Fore.WHITE + "Enter email address: ").strip()
                if email:
                    self.check_email(email)
            
            elif choice == '2':
                phone = input(Fore.WHITE + "Enter phone number (with country code): ").strip()
                if phone:
                    self.check_phone(phone)
            
            elif choice == '3':
                print(Fore.GREEN + "\n✓ Thank you for using Privacy Checker!")
                sys.exit(0)
            
            else:
                print(Fore.RED + "✗ Invalid choice. Please select 1, 2, or 3.")

def main():
    """Main function"""
    checker = PrivacyCheckerCLI()
    
    # Check if arguments provided
    if len(sys.argv) > 1:
        # Command-line mode
        identifier = sys.argv[1]
        
        # Detect type
        if '@' in identifier:
            checker.check_email(identifier)
        elif identifier.startswith('+') or identifier.isdigit():
            checker.check_phone(identifier)
        else:
            print(Fore.RED + "✗ Invalid input. Provide email or phone number.")
    else:
        # Interactive mode
        checker.interactive_mode()

if __name__ == "__main__":
    main()
