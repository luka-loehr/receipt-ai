#!/usr/bin/env python3
"""
Printer Configuration
Easy setup for different thermal printer connections
"""

from .thermal_printer import PrinterConfig
import os

# ============== PRINTER CONFIGURATIONS ==============

# Common thermal printer configurations
PRINTER_CONFIGS = {
    # USB Connection Examples
    'usb_generic': PrinterConfig(
        connection_type='usb',
        device_id='USB001',
        vendor_id=0x0483,      # Generic thermal printer
        product_id=0x5740,     # Adjust for your printer
        in_ep=0x81,            # Adjust for your printer
        out_ep=0x03            # Adjust for your printer
    ),
    
    # Network Connection Examples
    'network_ethernet': PrinterConfig(
        connection_type='network',
        device_id='192.168.1.100',  # Your printer's IP address
        host='192.168.1.100',
        port=9100                    # Standard ESC/POS port
    ),
    
    'network_wifi': PrinterConfig(
        connection_type='network',
        device_id='192.168.1.101',   # Your WiFi printer's IP
        host='192.168.1.101',
        port=9100
    ),
    
    # Serial Connection Example
    'serial_rs232': PrinterConfig(
        connection_type='serial',
        device_id='/dev/ttyUSB0',    # Linux serial port
        timeout=30
    ),
    
    # File-based (for testing without hardware)
    'file_test': PrinterConfig(
        connection_type='file',
        device_id='outputs/escpos/test_print.txt'
    )
}

# ============== PRINTER DETECTION ==============

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
    return PrinterConfig(
        connection_type='usb',
        device_id=f"USB_{hex(printer_info['vendor_id'])}_{hex(printer_info['product_id'])}",
        vendor_id=printer_info['vendor_id'],
        product_id=printer_info['product_id'],
        in_ep=printer_info['in_ep'],
        out_ep=printer_info['out_ep']
    )

# ============== CONFIGURATION HELPERS ==============

def print_available_configs():
    """Print all available printer configurations"""
    print("🖨️  Available Printer Configurations:")
    print("=" * 50)
    
    for name, config in PRINTER_CONFIGS.items():
        print(f"\n📋 {name.upper()}")
        print(f"   Type: {config.connection_type}")
        print(f"   Device: {config.device_id}")
        
        if config.connection_type == 'usb':
            print(f"   Vendor ID: {hex(config.vendor_id) if config.vendor_id else 'Not set'}")
            print(f"   Product ID: {hex(config.product_id) if config.product_id else 'Not set'}")
        elif config.connection_type == 'network':
            print(f"   Host: {config.host}")
            print(f"   Port: {config.port}")
        elif config.connection_type == 'serial':
            print(f"   Port: {config.device_id}")
    
    print("\n💡 To use a configuration:")
    print("   from printer_config import PRINTER_CONFIGS")
    print("   from thermal_printer import ThermalPrinter")
    print("   printer = ThermalPrinter(PRINTER_CONFIGS['usb_generic'])")

def setup_printer_interactive():
    """Interactive printer setup"""
    print("🖨️  Interactive Printer Setup")
    print("=" * 40)
    
    # Detect USB printers
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
            print(f"   Config: {config}")
            
            # Test the connection
            from thermal_printer import ThermalPrinter
            printer = ThermalPrinter(config)
            
            if printer.is_connected():
                print("✅ Printer connected successfully!")
                test = input("Run test print? (y/n): ").lower().strip()
                if test == 'y':
                    printer.test_print()
                printer.disconnect()
            else:
                print("❌ Could not connect to printer")
    
    # Network printer setup
    print("\n🌐 Network Printer Setup")
    setup_network = input("Setup network printer? (y/n): ").lower().strip()
    
    if setup_network == 'y':
        ip = input("Enter printer IP address: ").strip()
        port = input("Enter port (default 9100): ").strip() or "9100"
        
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
        from thermal_printer import ThermalPrinter
        printer = ThermalPrinter(config)
        
        if printer.is_connected():
            print("✅ Network printer connected successfully!")
            test = input("Run test print? (y/n): ").lower().strip()
            if test == 'y':
                printer.test_print()
            printer.disconnect()
        else:
            print("❌ Could not connect to network printer")

if __name__ == "__main__":
    print_available_configs()
    print("\n" + "="*50)
    setup_printer_interactive()
