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
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        # Check if virtual environment already exists
        if os.path.exists("venv"):
            print("🔍 Found existing virtual environment")
            print("📦 Checking if dependencies are already installed...")
            
            # Try to use existing virtual environment
            if os.name == 'nt':  # Windows
                pip_path = os.path.join("venv", "Scripts", "pip")
                python_path = os.path.join("venv", "Scripts", "python")
            else:  # Linux/macOS
                pip_path = os.path.join("venv", "bin", "pip")
                python_path = os.path.join("venv", "bin", "python")
            
            # Check if key dependencies are installed
            try:
                result = subprocess.run([pip_path, "list"], capture_output=True, text=True, check=True)
                if "openai" in result.stdout and "google-api-python-client" in result.stdout:
                    print("✅ Dependencies already installed in existing virtual environment")
                    
                    # Update sys.executable and sys.path
                    sys.executable = python_path
                    venv_site_packages = os.path.join("venv", "lib", "python3.12", "site-packages")
                    if os.path.exists(venv_site_packages):
                        sys.path.insert(0, venv_site_packages)
                    
                    print("💡 Using existing virtual environment!")
                    return True
            except:
                pass
            
            print("🔧 Using existing virtual environment for package installation...")
        else:
            print("🔧 Creating virtual environment for safe package installation...")
            
            # Check if venv module is available
            try:
                import venv
            except ImportError:
                print("❌ Virtual environment module not available")
                print("   Please install python3-venv:")
                print("   sudo apt update && sudo apt install python3-venv")
                print("   Then run this setup script again.")
                return False
            
            try:
                # Create virtual environment
                venv_path = "venv"
                subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
                print("✅ Virtual environment created successfully!")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to create virtual environment: {e}")
                return False
        
        # Install dependencies in virtual environment
        if os.name == 'nt':  # Windows
            pip_path = os.path.join("venv", "Scripts", "pip")
            python_path = os.path.join("venv", "Scripts", "python")
        else:  # Linux/macOS
            pip_path = os.path.join("venv", "bin", "pip")
            python_path = os.path.join("venv", "bin", "python")
        
        print("📦 Installing dependencies in virtual environment...")
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ All dependencies installed successfully!")
        
        # Update the sys.executable to use the virtual environment
        sys.executable = python_path
        
        # Update sys.path to include the virtual environment site-packages
        venv_site_packages = os.path.join("venv", "lib", "python3.12", "site-packages")
        if os.path.exists(venv_site_packages):
            sys.path.insert(0, venv_site_packages)
        
        print("💡 Virtual environment activated for this session!")
        print("   To activate manually in the future, run:")
        if os.name == 'nt':  # Windows
            print(f"   venv\\Scripts\\activate")
        else:  # Linux/macOS
            print(f"   source venv/bin/activate")
        
        return True
        
    else:
        # Already in virtual environment, install normally
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
    """Compact header"""
    print("RECEIPT PRINTER - SETUP")
    print("========================\n")

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

def setup_task_lists():
    """Configure task list names"""
    print("\n📋 Task List Configuration")
    print("-" * 30)
    
    # Check if task lists are already configured
    existing_general = os.getenv('GENERAL_TASKS_LIST_NAME')
    existing_shopping = os.getenv('SHOPPING_LIST_NAME')
    
    if existing_general and existing_general != 'General':
        print(f"🔍 Found existing general tasks list: {existing_general}")
        print("✅ Using existing general tasks list configuration")
    else:
        print("📋 Configure your Google Tasks list names:")
        print("   • General tasks list: Your main task list (e.g., 'General', 'Allgemeines', 'Tasks')")
        print("   • Shopping list: Your shopping list (e.g., 'Shopping List', 'Einkaufsliste', 'Groceries')")
        print()
        
        general_name = input("Enter general tasks list name (default: General): ").strip() or "General"
        update_env_file('GENERAL_TASKS_LIST_NAME', general_name)
        print(f"✅ General tasks list set to: {general_name}")
    
    if existing_shopping and existing_shopping != 'Shopping List':
        print(f"🔍 Found existing shopping list: {existing_shopping}")
        print("✅ Using existing shopping list configuration")
    else:
        shopping_name = input("Enter shopping list name (default: Shopping List): ").strip() or "Shopping List"
        update_env_file('SHOPPING_LIST_NAME', shopping_name)
        print(f"✅ Shopping list set to: {shopping_name}")
    
    print("\n💡 These lists must exist in your Google Tasks for the system to work properly")
    return True

def setup_thermal_printer():
    """Set up thermal printer connection"""
    print("\n🖨️  Thermal Printer Setup")
    print("-" * 30)
    
    # Check if we already have a printer configuration
    existing_config = os.getenv('THERMAL_PRINTER_TYPE')
    if existing_config and existing_config != 'file_test':
        print(f"🔍 Found existing printer configuration: {existing_config}")
        print("✅ Using existing printer configuration")
        return True
    
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
        
        # Check if we're in a virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        
        if not in_venv and os.path.exists("venv"):
            # Use virtual environment pip
            if os.name == 'nt':  # Windows
                pip_path = os.path.join("venv", "Scripts", "pip")
            else:  # Linux/macOS
                pip_path = os.path.join("venv", "bin", "pip")
            
            subprocess.run([pip_path, "install", "python-escpos", "pyusb"], check=True)
        else:
            # Use current environment
            subprocess.run([sys.executable, "-m", "pip", "install", "python-escpos", "pyusb"], check=True)
        
        print("✅ Thermal printer dependencies installed!")
        return True
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("   Please install manually: pip install python-escpos pyusb")
        return False

def setup_openweather():
    """Prompt for OpenWeather API key (minimal)."""
    existing_key = os.getenv('OPENWEATHER_API_KEY')
    if existing_key and existing_key != 'your_openweather_api_key_here':
        print("OpenWeather: configured")
        return True
    api_key = input("OpenWeather API key (Enter to skip): ").strip()
    if api_key:
        update_env_file('OPENWEATHER_API_KEY', api_key)
        print("OpenWeather: saved")
        return True
    print("OpenWeather: skipped")
    return False

def setup_openai():
    """Prompt for OpenAI API key (minimal) and save; quick test if provided."""
    existing_key = os.getenv('OPENAI_API_KEY')
    if existing_key and existing_key != 'your_openai_api_key_here':
        print("OpenAI: configured")
        return True
    api_key = input("OpenAI API key (Enter to skip): ").strip()
    if not api_key:
        print("OpenAI: skipped")
        return False
    update_env_file('OPENAI_API_KEY', api_key)
    if test_openai_api(api_key):
        print("OpenAI: saved & verified")
        return True
    print("OpenAI: saved but verification failed")
    return False

def test_openai_api(api_key):
    """Test OpenAI API key"""
    try:
        # Check if we need to reload modules from virtual environment
        if os.path.exists("venv"):
            venv_site_packages = os.path.join("venv", "lib", "python3.12", "site-packages")
            if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
                sys.path.insert(0, venv_site_packages)
        
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-4.1",
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
    
    # Check if we already have valid tokens
    if os.path.exists('token_autogenerated/unified_google_token.json'):
        print("🔍 Found existing Google OAuth tokens")
        print("🧪 Testing existing tokens...")
        
        if test_calendar_api() and test_gmail_api() and test_tasks_api():
            print("✅ Existing Google OAuth tokens are working!")
            return True
        else:
            print("⚠️  Existing tokens failed test, will re-authorize")
    
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
        # Check if we need to reload modules from virtual environment
        if os.path.exists("venv"):
            venv_site_packages = os.path.join("venv", "lib", "python3.12", "site-packages")
            if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
                sys.path.insert(0, venv_site_packages)
        
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
        # Check if we need to reload modules from virtual environment
        if os.path.exists("venv"):
            venv_site_packages = os.path.join("venv", "lib", "python3.12", "site-packages")
            if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
                sys.path.insert(0, venv_site_packages)
        
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        
        # Get credentials from unified token
        creds = None
        if os.path.exists('token_autogenerated/unified_google_token.json'):
            creds = Credentials.from_authorized_user_file('token_autogenerated/unified_google_token.json', SCOPES)
        else:
            print("   ❌ No valid credentials found. Run OAuth setup first.")
            return False
        
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
        # Check if we need to reload modules from virtual environment
        if os.path.exists("venv"):
            venv_site_packages = os.path.join("venv", "lib", "python3.12", "site-packages")
            if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
                sys.path.insert(0, venv_site_packages)
        
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']
        
        # Get credentials from unified token
        creds = None
        if os.path.exists('token_autogenerated/unified_google_token.json'):
            creds = Credentials.from_authorized_user_file('token_autogenerated/unified_google_token.json', SCOPES)
        else:
            print("   ❌ No valid credentials found. Run OAuth setup first.")
            return False
        
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
        # Check if we need to reload modules from virtual environment
        if os.path.exists("venv"):
            venv_site_packages = os.path.join("venv", "lib", "python3.12", "site-packages")
            if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
                sys.path.insert(0, venv_site_packages)
        
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
        if os.path.exists('token_autogenerated/unified_google_token.json'):
            creds = Credentials.from_authorized_user_file('token_autogenerated/unified_google_token.json', SCOPES)
        
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

def show_configuration_status():
    """Compact configuration status"""
    print("Config:")
    
    # Check OpenWeatherMap
    weather_key = os.getenv('OPENWEATHER_API_KEY')
    if weather_key and weather_key != 'your_openweather_api_key_here':
        print("  weather: ✅")
    else:
        print("  weather: ❌")
    
    # Check OpenAI
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key != 'your_openai_api_key_here':
        model = os.getenv('AI_MODEL', 'gpt-4o-mini')
        max_tokens = os.getenv('MAX_OUTPUT_TOKENS', '1200')
        print(f"  openai: ✅ (model={model}, max_output_tokens={max_tokens})")
    else:
        print("  openai: ❌")
    
    # Check Google OAuth
    if os.path.exists('token_autogenerated/unified_google_token.json'):
        print("  oauth: ✅")
    else:
        print("  oauth: ❌")
    
    # Check Thermal Printer
    printer_type = os.getenv('THERMAL_PRINTER_TYPE')
    if printer_type and printer_type != 'file_test':
        print(f"  printer: ✅ ({printer_type})")
    else:
        print("  printer: file_test")

def ensure_ai_env_defaults():
    """Ensure AI_MODEL and MAX_OUTPUT_TOKENS exist in .env with sensible defaults."""
    if not os.getenv('AI_MODEL'):
        update_env_file('AI_MODEL', 'gpt-4o-mini')
    if not os.getenv('MAX_OUTPUT_TOKENS'):
        update_env_file('MAX_OUTPUT_TOKENS', '1200')

def prompt_ai_defaults():
    """Prompt for AI model and max output tokens (minimal)."""
    current_model = os.getenv('AI_MODEL', 'gpt-4o-mini')
    current_max = os.getenv('MAX_OUTPUT_TOKENS', '1200')
    model = input(f"AI model [{current_model}]: ").strip() or current_model
    max_out = input(f"Max output tokens [{current_max}]: ").strip() or current_max
    update_env_file('AI_MODEL', model)
    update_env_file('MAX_OUTPUT_TOKENS', max_out)
    print("AI config: saved")

def create_output_directories():
    """Create all necessary output directories for the receipt printer"""
    print("📁 Creating output directories...")
    
    # List of required directories
    directories = [
        'outputs',
        'outputs/txt',
        'outputs/png', 
        'outputs/escpos',
        'token_autogenerated'
    ]
    
    created_count = 0
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"   ✅ Created: {directory}")
            created_count += 1
        else:
            print(f"   🔍 Found: {directory}")
    
    if created_count > 0:
        print(f"✅ Created {created_count} new directories")
    else:
        print("✅ All required directories already exist")

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

# Language Configuration
RECEIPT_LANGUAGE=german

# AI Configuration
AI_MODEL=gpt-4o-mini
MAX_OUTPUT_TOKENS=1200

# Task List Configuration
GENERAL_TASKS_LIST_NAME=Allgemeines
SHOPPING_LIST_NAME=Einkaufsliste

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
    """Minimal final test using ModularDataManager."""
    try:
        if os.path.exists("venv"):
            venv_site_packages = os.path.join("venv", "lib", "python3.12", "site-packages")
            if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
                sys.path.insert(0, venv_site_packages)
        from src.data_manager import ModularDataManager
        print("Testing brief generation...")
        manager = ModularDataManager()
        content, _ = manager.generate_complete_receipt()
        print("OK: brief generated")
        return True
    except Exception as e:
        print(f"Final test error: {e}")
        return False

def main():
    """Main setup function (simplified prompts)."""
    print_header()
    
    # Create .env file if it doesn't exist
    create_env_template()
    
    # Create output directories
    create_output_directories()
    print()
    
    # Show current configuration status
    print("Checking configuration...")
    show_configuration_status()
    ensure_ai_env_defaults()
    
    # Install dependencies (best-effort)
    try:
        install_dependencies()
    except Exception:
        pass
    
    # Minimal prompts for API keys & AI config
    setup_openweather()
    setup_openai()
    prompt_ai_defaults()
    
    # Setup Google OAuth
    setup_google_oauth()
    
    # Setup Task Lists
    setup_task_lists()
    
    # Setup Thermal Printer
    setup_thermal_printer()
    
    # Final test
    if final_test():
        print("\nSetup done.")
        show_configuration_status()
    else:
        print("\nSetup finished with issues. See above.")

if __name__ == "__main__":
    main()
