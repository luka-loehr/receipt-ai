#!/usr/bin/env python3
"""
🚀 Receipt Printer - Complete Setup Script
One script to set up everything and get you running immediately!
"""

import os
import json
import webbrowser
import subprocess
import sys
from pathlib import Path

def install_dependencies():
    """Install all required dependencies from requirements.txt"""
    print("📦 Installing dependencies from requirements.txt...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("   Please install manually: pip install -r requirements.txt")
        return False
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def print_header():
    """Print beautiful header"""
    print("🚀" + "="*50 + "🚀")
    print("    RECEIPT PRINTER - COMPLETE SETUP")
    print("🚀" + "="*50 + "🚀")
    print()

def check_google_credentials():
    """Check if google_credentials.json exists"""
    if os.path.exists('cloud_credentials/google_credentials.json'):
        print("✅ google_credentials.json found in cloud_credentials folder")
        print("   Make sure you have enabled these APIs in Google Cloud Console:")
        print("   - Gmail API")
        print("   - Google Calendar API") 
        print("   - Google Tasks API")
        print("   Visit: https://console.developers.google.com/apis")
        return True
    else:
        print("❌ google_credentials.json not found")
        print("   Please download it from Google Cloud Console and place it in cloud_credentials/ folder")
        return False

def setup_thermal_printer():
    """Set up thermal printer connection"""
    print("\n🖨️  Thermal Printer Setup")
    print("-" * 30)
    
    print("📋 This will help you configure your thermal printer for ESC/POS printing.")
    print("   Your daily briefs will be automatically printed to the thermal printer.")
    print()
    
    # Check if thermal printer dependencies are available
    try:
        import escpos
        print("✅ ESC/POS library available")
    except ImportError:
        print("❌ ESC/POS library not available")
        print("   Installing thermal printer dependencies...")
        install_thermal_printer_deps()
        return False
    
    # Try to detect USB printers
    print("\n🔍 Detecting USB thermal printers...")
    usb_printers = detect_usb_printers()
    
    if usb_printers:
        print(f"✅ Found {len(usb_printers)} USB printer(s):")
        for i, printer in enumerate(usb_printers):
            print(f"   {i+1}. {printer['manufacturer']} {printer['product']}")
            print(f"      Vendor: {hex(printer['vendor_id'])}, Product: {hex(printer['product_id'])}")
        
        choice = input(f"\nSelect printer (1-{len(usb_printers)}) or press Enter to skip: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(usb_printers):
            selected = usb_printers[int(choice) - 1]
            config = create_printer_config_from_detected(selected)
            
            print(f"\n✅ Selected: {selected['manufacturer']} {selected['product']}")
            
            # Test the connection
            from src.thermal_printer import ThermalPrinter
            printer = ThermalPrinter(config)
            
            if printer.is_connected():
                print("✅ Printer connected successfully!")
                test = input("Run test print? (y/n): ").lower().strip()
                if test == 'y':
                    printer.test_print()
                
                # Save configuration
                save_printer_config('usb_auto', config)
                printer.disconnect()
                return True
            else:
                print("❌ Could not connect to printer")
    
    # Network printer setup
    print("\n🌐 Network Printer Setup")
    setup_network = input("Setup network printer? (y/n): ").lower().strip()
    
    if setup_network == 'y':
        ip = input("Enter printer IP address: ").strip()
        port = input("Enter port (default 9100): ").strip() or "9100"
        
        from src.thermal_printer import PrinterConfig
        config = PrinterConfig(
            connection_type='network',
            device_id=ip,
            host=ip,
            port=int(port)
        )
        
        print(f"\n✅ Network printer config created:")
        print(f"   IP: {ip}")
        print(f"   Port: {port}")
        
        # Test connection
        printer = ThermalPrinter(config)
        
        if printer.is_connected():
            print("✅ Network printer connected successfully!")
            test = input("Run test print? (y/n): ").lower().strip()
            if test == 'y':
                printer.test_print()
            
            # Save configuration
            save_printer_config('network_auto', config)
            printer.disconnect()
            return True
        else:
            print("❌ Could not connect to network printer")
    
    # File-based printer (for testing)
    print("\n📁 File-based Printer (for testing)")
    setup_file = input("Setup file-based printer for testing? (y/n): ").lower().strip()
    
    if setup_file == 'y':
        from src.thermal_printer import PrinterConfig
        config = PrinterConfig(
            connection_type='file',
            device_id='outputs/escpos/daily_brief.txt'
        )
        
        # Create output directory
        os.makedirs('outputs/escpos', exist_ok=True)
        
        print("✅ File-based printer configured for testing")
        print("   ESC/POS commands will be saved to: outputs/escpos/daily_brief.txt")
        
        # Save configuration
        save_printer_config('file_test', config)
        return True
    
    print("⏭️  Skipped thermal printer setup")
    return False

def detect_usb_printers():
    """Detect USB thermal printers on the system"""
    try:
        import usb.core
        import usb.util
        
        # Common thermal printer vendor IDs
        thermal_vendors = [
            0x0483,  # Generic thermal
            0x04b8,  # Epson
            0x0419,  # Citizen
            0x0525,  # Star
            0x0483,  # Bixolon
        ]
        
        detected_printers = []
        
        for vendor_id in thermal_vendors:
            try:
                devices = usb.core.find(find_all=True, idVendor=vendor_id)
                for device in devices:
                    detected_printers.append({
                        'vendor_id': device.idVendor,
                        'product_id': device.idProduct,
                        'manufacturer': usb.util.get_string(device, device.iManufacturer),
                        'product': usb.util.get_string(device, device.iProduct),
                        'in_ep': None,
                        'out_ep': None
                    })
                    
                    # Try to find endpoints
                    for cfg in device:
                        for intf in cfg:
                            for ep in intf:
                                if ep.bEndpointAddress & 0x80:  # IN endpoint
                                    detected_printers[-1]['in_ep'] = ep.bEndpointAddress
                                else:  # OUT endpoint
                                    detected_printers[-1]['out_ep'] = ep.bEndpointAddress
                    
            except Exception as e:
                print(f"⚠️  Error detecting vendor {hex(vendor_id)}: {e}")
                continue
        
        return detected_printers
        
    except ImportError:
        print("⚠️  pyusb not installed. Install with: pip install pyusb")
        return []
    except Exception as e:
        print(f"❌ USB detection error: {e}")
        return []

def create_printer_config_from_detected(printer_info):
    """Create a PrinterConfig from detected printer info"""
    from thermal_printer import PrinterConfig
    return PrinterConfig(
        connection_type='usb',
        device_id=f"USB_{hex(printer_info['vendor_id'])}_{hex(printer_info['product_id'])}",
        vendor_id=printer_info['vendor_id'],
        product_id=printer_info['product_id'],
        in_ep=printer_info['in_ep'],
        out_ep=printer_info['out_ep']
    )

def save_printer_config(name, config):
    """Save printer configuration to environment"""
    # Set environment variable for printer type
    update_env_file('THERMAL_PRINTER_TYPE', name)
    print(f"✅ Printer configuration saved as: {name}")

def install_thermal_printer_deps():
    """Install thermal printer dependencies"""
    try:
        import subprocess
        print("📦 Installing python-escpos...")
        subprocess.run([sys.executable, "-m", "pip", "install", "python-escpos", "pyusb"], check=True)
        print("✅ Thermal printer dependencies installed!")
        return True
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("   Please install manually: pip install python-escpos pyusb")
        return False

def setup_openweather():
    """Get OpenWeatherMap API key"""
    print("\n🌤️  OpenWeatherMap API Setup")
    print("-" * 30)
    
    api_key = input("Enter your OpenWeatherMap API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Update .env file
        update_env_file('OPENWEATHER_API_KEY', api_key)
        print("✅ OpenWeatherMap API key saved!")
        return True
    else:
        print("⏭️  Skipped OpenWeatherMap setup")
        return False

def setup_openai():
    """Get OpenAI API key"""
    print("\n🤖 OpenAI API Setup")
    print("-" * 30)
    
    print("📋 To get your OpenAI API key:")
    print("   1. Go to: https://platform.openai.com/api-keys")
    print("   2. Sign in to your OpenAI account (or create one)")
    print("   3. Click 'Create new secret key'")
    print("   4. Give it a name (e.g., 'Receipt Printer')")
    print("   5. Copy the key (starts with 'sk-')")
    print("   6. ⚠️  Keep it secure - you won't see it again!")
    print()
    
    print("💰 Pricing info:")
    print("   • GPT-4o: ~$0.005 per 1K input tokens, ~$0.015 per 1K output tokens")
    print("   • Morning brief: ~$0.01-0.02 per generation")
    print("   • Set usage limits at: https://platform.openai.com/usage")
    print()
    
    # Offer to open browser
    open_browser = input("Open OpenAI API keys page in browser? (y/n): ").lower().strip()
    if open_browser == 'y':
        try:
            webbrowser.open('https://platform.openai.com/api-keys')
            print("🌐 Browser opened!")
        except Exception as e:
            print(f"⚠️  Could not open browser: {e}")
    
    print()
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Validate API key format
        if not api_key.startswith('sk-'):
            print("⚠️  Warning: OpenAI API keys usually start with 'sk-'")
            confirm = input("Continue anyway? (y/n): ").lower().strip()
            if confirm != 'y':
                print("⏭️  Skipped OpenAI setup")
                return False
        
        # Update .env file
        update_env_file('OPENAI_API_KEY', api_key)
        print("✅ OpenAI API key saved!")
        
        # Test the API key
        if test_openai_api(api_key):
            print("✅ OpenAI API key is working!")
            return True
        else:
            print("❌ OpenAI API key test failed")
            return False
    else:
        print("⏭️  Skipped OpenAI setup")
        return False

def test_openai_api(api_key):
    """Test OpenAI API key"""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, API test successful!' in German."}
            ],
            max_tokens=20
        )
        
        result = response.choices[0].message.content
        print(f"   🤖 API Response: {result}")
        return True
        
    except Exception as e:
        print(f"   ❌ OpenAI API error: {e}")
        return False

def setup_google_oauth():
    """Set up Google OAuth for Gmail, Calendar, and Tasks in one authorization flow"""
    print("\n🔐 Google OAuth Setup")
    print("-" * 30)
    
    if not check_google_credentials():
        print("❌ Cannot proceed without google_credentials.json")
        return False
    
    print("📋 This will:")
    print("   1. Open your browser for Google authorization")
    print("   2. Request permissions for Gmail, Calendar, and Tasks")
    print("   3. Generate unified tokens for all Google services")
    print("   4. Test all APIs to ensure they work")
    print()
    
    proceed = input("Proceed with unified Google OAuth setup? (y/n): ").lower().strip()
    if proceed != 'y':
        print("⏭️  Skipped OAuth setup")
        return False
    
    try:
        print("\n🌐 Opening browser for Google authorization...")
        print("📋 Receipt Printer will request the following permissions:")
        print("   • 📧 Gmail: Read your emails for daily brief")
        print("   • 📅 Calendar: Access your calendar events")
        print("   • ✅ Tasks: Read your Google Tasks")
        print()
        
        # Single OAuth flow with all scopes
        if unified_google_oauth():
            print("✅ All Google APIs authorized successfully!")
            
            # Test all APIs
            print("\n🧪 Testing all Google APIs...")
            
            if test_calendar_api():
                print("✅ Calendar API working!")
            else:
                print("❌ Calendar API failed")
                return False
            
            if test_gmail_api():
                print("✅ Gmail API working!")
            else:
                print("❌ Gmail API failed")
                return False
            
            if test_tasks_api():
                print("✅ Tasks API working!")
            else:
                print("❌ Tasks API failed")
                return False
            
            print("\n🎉 Google OAuth setup completed successfully!")
            return True
        else:
            print("❌ Google OAuth authorization failed")
            return False
        
    except Exception as e:
        print(f"❌ OAuth setup failed: {e}")
        return False

def test_calendar_api():
    """Test Google Calendar API"""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from datetime import datetime, timedelta
        
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        
        # Get credentials from unified token
        creds = None
        if os.path.exists('token_autogenerated/unified_google_token.json'):
            creds = Credentials.from_authorized_user_file('token_autogenerated/unified_google_token.json', SCOPES)
        elif os.path.exists('token_autogenerated/calendar_token.json'):
            creds = Credentials.from_authorized_user_file('token_autogenerated/calendar_token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("   ❌ No valid credentials found. Run OAuth setup first.")
                return False
        
        # Test the API
        service = build('calendar', 'v3', credentials=creds)
        
        # Get today's events
        now = datetime.utcnow().isoformat() + 'Z'
        end = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end,
            maxResults=5,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"   📅 Found {len(events)} events today")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Calendar API error: {e}")
        return False

def test_gmail_api():
    """Test Gmail API"""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        
        # Get credentials from unified token
        creds = None
        if os.path.exists('token_autogenerated/unified_google_token.json'):
            creds = Credentials.from_authorized_user_file('token_autogenerated/unified_google_token.json', SCOPES)
        elif os.path.exists('token_autogenerated/gmail_token.json'):
            creds = Credentials.from_authorized_user_file('token_autogenerated/gmail_token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("   ❌ No valid credentials found. Run OAuth setup first.")
                return False
        
        # Test the API
        service = build('gmail', 'v1', credentials=creds)
        
        # Get recent messages
        results = service.users().messages().list(userId='me', maxResults=3).execute()
        messages = results.get('messages', [])
        
        print(f"   📧 Found {len(messages)} recent messages")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Gmail API error: {e}")
        return False

def test_tasks_api():
    """Test Google Tasks API"""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']
        
        # Get credentials from unified token
        creds = None
        if os.path.exists('token_autogenerated/unified_google_token.json'):
            creds = Credentials.from_authorized_user_file('token_autogenerated/unified_google_token.json', SCOPES)
        elif os.path.exists('token_autogenerated/tasks_token.json'):
            creds = Credentials.from_authorized_user_file('token_autogenerated/tasks_token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("   ❌ No valid credentials found. Run OAuth setup first.")
                return False
        
        # Test the API
        service = build('tasks', 'v1', credentials=creds)
        
        # Get task lists
        task_lists = service.tasklists().list().execute()
        lists = task_lists.get('items', [])
        
        print(f"   ✅ Found {len(lists)} task lists")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Tasks API error: {e}")
        return False

def unified_google_oauth():
    """Single OAuth flow for all Google APIs"""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        
        # Combined scopes for all APIs
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/tasks.readonly'
        ]
        
        # Get credentials
        creds = None
        if os.path.exists('tokens_autogenerated/unified_google_token.json'):
            creds = Credentials.from_authorized_user_file('tokens_autogenerated/unified_google_token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('cloud_credentials/google_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the unified credentials
            os.makedirs('token_autogenerated', exist_ok=True)
            with open('token_autogenerated/unified_google_token.json', 'w') as token:
                token.write(creds.to_json())
            
            # Unified token only - no need for separate tokens anymore
        
        return True
        
    except Exception as e:
        print(f"   ❌ Unified OAuth error: {e}")
        return False

def update_env_file(key, value):
    """Update or add a key-value pair in .env file"""
    env_file = '.env'
    
    # Read existing .env file
    lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
    
    # Check if key already exists
    key_exists = False
    for i, line in enumerate(lines):
        if line.startswith(f'{key}='):
            lines[i] = f'{key}={value}\n'
            key_exists = True
            break
    
    # Add new key if it doesn't exist
    if not key_exists:
        lines.append(f'{key}={value}\n')
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(lines)

def create_env_template():
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists('.env'):
        print("\n📝 Creating .env file from template...")
        
        # Copy from config.env.example
        if os.path.exists('config.env.example'):
            with open('config.env.example', 'r') as f:
                template_content = f.read()
            
            # Update with unified credentials
            template_content = template_content.replace(
                'GMAIL_CREDENTIALS_FILE=gmail_credentials.json',
                'GOOGLE_CREDENTIALS_FILE=google_credentials.json'
            )
            template_content = template_content.replace(
                'CALENDAR_CREDENTIALS_FILE=calendar_credentials.json',
                'GOOGLE_CREDENTIALS_FILE=google_credentials.json'
            )
            
            with open('.env', 'w') as f:
                f.write(template_content)
            
            print("✅ .env file created!")
        else:
            print("⚠️  config.env.example not found, creating basic .env")
            basic_env = """# Receipt Printer Configuration
GOOGLE_CREDENTIALS_FILE=google_credentials.json
USER_NAME=Luka
USER_TIMEZONE=Europe/Berlin
WEATHER_LOCATION=Karlsruhe,DE
MAX_EMAILS_TO_PROCESS=10
EMAIL_PRIORITY_KEYWORDS=urgent,important,asap,deadline,meeting
EMAIL_SPAM_FILTERS=newsletter,marketing,promotion,unsubscribe

# Thermal Printer Configuration
THERMAL_PRINTER_TYPE=file_test

# API Keys (set these during setup)
OPENAI_API_KEY=your_openai_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
"""
            with open('.env', 'w') as f:
                f.write(basic_env)
            print("✅ Basic .env file created!")

def final_test():
    """Run final test to ensure everything works"""
    print("\n🧪 Final System Test")
    print("-" * 20)
    
    try:
        # Test data services
        from src.data_services import DataManager
        
        print("📊 Testing data services...")
        manager = DataManager()
        
        # Test the new structured daily brief
        brief_response = manager.get_daily_brief()
        
        print(f"✅ Greeting: {brief_response.greeting}")
        print(f"✅ Brief: {brief_response.brief[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Final test failed: {e}")
        print("   This might be due to missing API keys or credentials")
        return False

def main():
    """Main setup function"""
    print_header()
    
    print("🎯 This setup will configure your Receipt Printer for:")
    print("   • OpenWeatherMap API (weather data)")
    print("   • OpenAI GPT-4o API (AI insights & greetings)")
    print("   • Google OAuth (Gmail & Calendar)")
    print("   • Thermal Printer (ESC/POS printing)")
    print()
    
    # Create .env file if it doesn't exist
    create_env_template()
    
    # Install dependencies
    install_dependencies()
    
    # Setup OpenWeatherMap
    setup_openweather()
    
    # Setup OpenAI
    setup_openai()
    
    # Setup Google OAuth
    setup_google_oauth()
    
    # Setup Thermal Printer
    setup_thermal_printer()
    
    # Final test
    if final_test():
        print("\n🎉 SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 40)
        print("✅ Your Receipt Printer is ready to use!")
        print()
        print("🚀 Next steps:")
        print("   1. Run: python daily_brief.py")
        print("   2. Enjoy your personalized German daily brief!")
        print("   3. Your brief will be printed to the thermal printer automatically!")
        print()
        print("📚 Need help? Check README.md for usage instructions")
    else:
        print("\n⚠️  Setup completed with some issues")
        print("   Check the errors above and try again")

if __name__ == "__main__":
    main()
