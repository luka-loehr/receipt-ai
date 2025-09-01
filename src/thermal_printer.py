#!/usr/bin/env python3
"""
Thermal Printer Service - ESC/POS Commands
Handles direct printing to thermal printers using ESC/POS protocol
"""

import os
from typing import List, Optional
from dataclasses import dataclass
from escpos import printer
from escpos.exceptions import Error as ESCPOSError

@dataclass
class PrinterConfig:
    """Printer configuration"""
    connection_type: str  # 'usb', 'network', 'serial', 'file'
    device_id: str        # USB device ID, IP address, serial port, or file path
    vendor_id: Optional[int] = None  # USB vendor ID
    product_id: Optional[int] = None # USB product ID
    in_ep: Optional[int] = None     # USB in endpoint
    out_ep: Optional[int] = None    # USB out endpoint
    host: Optional[str] = None      # Network printer IP
    port: Optional[int] = 9100      # Network printer port
    timeout: int = 30               # Connection timeout

class ThermalPrinter:
    """ESC/POS thermal printer interface"""
    
    def __init__(self, config: PrinterConfig):
        self.config = config
        self.printer = None
        self._connect()
    
    def _connect(self):
        """Establish connection to printer"""
        try:
            if self.config.connection_type == 'usb':
                self.printer = printer.Usb(
                    idVendor=self.config.vendor_id,
                    idProduct=self.config.product_id,
                    in_ep=self.config.in_ep,
                    out_ep=self.config.out_ep,
                    timeout=self.config.timeout
                )
            elif self.config.connection_type == 'network':
                self.printer = printer.Network(
                    host=self.config.host,
                    port=self.config.port,
                    timeout=self.config.timeout
                )
            elif self.config.connection_type == 'serial':
                self.printer = printer.Serial(
                    devfile=self.config.device_id,
                    baudrate=9600,
                    timeout=self.config.timeout
                )
            elif self.config.connection_type == 'file':
                self.printer = printer.File(self.config.device_id)
            else:
                raise ValueError(f"Unsupported connection type: {self.config.connection_type}")
            
            print(f"✅ Connected to {self.config.connection_type} printer")
            
        except ESCPOSError as e:
            print(f"❌ Printer connection failed: {e}")
            self.printer = None
        except Exception as e:
            print(f"❌ Unexpected error connecting to printer: {e}")
            self.printer = None
    
    def is_connected(self) -> bool:
        """Check if printer is connected"""
        return self.printer is not None
    
    def print_daily_brief(self, greeting: str, brief: str, tasks: List[str] = None, shopping_list: List[str] = None):
        """Print daily brief in German using ESC/POS commands"""
        if not self.is_connected():
            print("❌ Printer not connected")
            return False
        
        try:
            # Header with decorative elements
            self.printer.set(align='center', font='a', width=2, height=2)
            self.printer.text("=" * 32 + "\n")
            
            # Greeting
            self.printer.set(align='center', font='a', width=2, height=2)
            self.printer.text(f"{greeting}\n")
            
            # Subtitle
            self.printer.set(align='center', font='a', width=1, height=1)
            self.printer.text("KI-Tagesbrief\n")
            
            # Date (German format)
            from datetime import datetime
            now = datetime.now()
            german_months = {
                1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April', 5: 'Mai', 6: 'Juni',
                7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
            }
            german_days = {
                0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch', 3: 'Donnerstag', 
                4: 'Freitag', 5: 'Samstag', 6: 'Sonntag'
            }
            
            day_name = german_days[now.weekday()]
            month_name = german_months[now.month]
            date_str = f"{day_name}, {now.day}. {month_name} {now.year}"
            self.printer.text(f"{date_str}\n\n")
            
            # Separator
            self.printer.text("=" * 32 + "\n\n")
            
            # Main brief content
            self.printer.set(align='left', font='a', width=1, height=1)
            self.printer.text(f"{brief}\n\n")
            
            # Tasks section
            if tasks:
                self.printer.text("-" * 32 + "\n")
                self.printer.set(align='center', font='a', width=1, height=1)
                self.printer.text("✅ AUFGABEN\n\n")
                
                self.printer.set(align='left', font='a', width=1, height=1)
                for i, task in enumerate(tasks, 1):
                    # Tasks are now pre-processed strings, not TaskData objects
                    # No additional truncation needed here
                    task_title = str(task)
                    self.printer.text(f"□ {task_title}\n")
                
                self.printer.text("\n")
            
            # Shopping list section
            if shopping_list:
                self.printer.text("-" * 32 + "\n")
                self.printer.set(align='center', font='a', width=1, height=1)
                self.printer.text("🛒 EINKAUFSLISTE\n\n")
                
                self.printer.set(align='left', font='a', width=1, height=1)
                for i, item in enumerate(shopping_list, 1):
                    # Items are pre-processed strings, no additional truncation needed
                    item_title = str(item)
                    self.printer.text(f"□ {item_title}\n")
                
                self.printer.text("\n")
            
            # Footer
            self.printer.text("-" * 32 + "\n")
            self.printer.set(align='center', font='a', width=1, height=1)
            gen_time = datetime.now().strftime("%H:%M")
            self.printer.text(f"Erstellt um {gen_time}\n")
            
            # Final separator
            self.printer.text("=" * 32 + "\n")
            
            # Cut paper
            self.printer.cut()
            
            return True
            
        except ESCPOSError as e:
            print(f"❌ Printing error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected printing error: {e}")
            return False
    
    def print_receipt(self, store_name: str, items: List[dict], total: float):
        """Print a receipt using ESC/POS commands"""
        if not self.is_connected():
            print("❌ Printer not connected")
            return False
        
        try:
            # Header
            self.printer.set(align='center', font='a', width=2, height=2)
            self.printer.text(f"{store_name}\n")
            
            self.printer.set(align='center', font='a', width=1, height=1)
            self.printer.text("Thermal Receipt\n\n")
            
            # Timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.printer.text(f"{timestamp}\n")
            
            # Separator
            self.printer.text("-" * 32 + "\n\n")
            
            # Items
            self.printer.set(align='left', font='a', width=1, height=1)
            subtotal = 0
            
            for item in items:
                item_name = item['name'][:20] if len(item['name']) > 20 else item['name']
                item_total = item['price'] * item['qty']
                subtotal += item_total
                
                # Item line
                self.printer.text(f"{item_name} x{item['qty']}\n")
                
                # Price (right-aligned)
                price_str = f"${item_total:.2f}"
                self.printer.set(align='right')
                self.printer.text(f"{price_str}\n")
                self.printer.set(align='left')
            
            # Totals
            self.printer.text("\n" + "-" * 32 + "\n")
            
            # Subtotal
            self.printer.text("Subtotal:")
            self.printer.set(align='right')
            self.printer.text(f"${subtotal:.2f}\n")
            self.printer.set(align='left')
            
            # Total
            self.printer.set(font='a', width=2, height=2)
            self.printer.text("TOTAL:")
            self.printer.set(align='right')
            self.printer.text(f"${total:.2f}\n")
            self.printer.set(align='left')
            
            # Footer
            self.printer.set(font='a', width=1, height=1)
            self.printer.text("\n" + "=" * 32 + "\n")
            self.printer.set(align='center')
            self.printer.text("Thank you!\n")
            
            # Cut paper
            self.printer.cut()
            
            print("✅ Receipt printed successfully!")
            return True
            
        except ESCPOSError as e:
            print(f"❌ Printing error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected printing error: {e}")
            return False
    
    def test_print(self):
        """Print a test page"""
        if not self.is_connected():
            print("❌ Printer not connected")
            return False
        
        try:
            self.printer.set(align='center', font='a', width=2, height=2)
            self.printer.text("THERMAL PRINTER TEST\n\n")
            
            self.printer.set(align='center', font='a', width=1, height=1)
            self.printer.text("This is a test print\n")
            self.printer.text("to verify your printer\n")
            self.printer.text("is working correctly.\n\n")
            
            self.printer.text("=" * 32 + "\n")
            self.printer.text("Printer: OK\n")
            self.printer.text("Connection: OK\n")
            self.printer.text("ESC/POS: OK\n\n")
            
            self.printer.text("Ready for daily briefs!\n")
            
            self.printer.cut()
            
            print("✅ Test print completed!")
            return True
            
        except ESCPOSError as e:
            print(f"❌ Test print failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from printer"""
        if self.printer:
            try:
                self.printer.close()
                self.printer = None
                print("✅ Printer disconnected")
            except Exception as e:
                print(f"⚠️  Error disconnecting: {e}")

def create_default_configs():
    """Create example printer configurations"""
    configs = {
        'usb_example': PrinterConfig(
            connection_type='usb',
            device_id='USB001',
            vendor_id=0x0483,  # Example vendor ID
            product_id=0x5740, # Example product ID
            in_ep=0x81,        # Example endpoint
            out_ep=0x03
        ),
        'network_example': PrinterConfig(
            connection_type='network',
            device_id='192.168.1.100',
            host='192.168.1.100',
            port=9100
        ),
        'file_example': PrinterConfig(
            connection_type='file',
            device_id='outputs/escpos/test_print.txt'
        )
    }
    return configs

def main():
    """Test the thermal printer service"""
    print("🖨️  Thermal Printer Service Test")
    print("=" * 40)
    
    # Example: File-based printer (for testing without hardware)
    config = PrinterConfig(
        connection_type='file',
        device_id='outputs/escpos/test_print.txt'
    )
    
    # Create output directory
    os.makedirs('outputs/escpos', exist_ok=True)
    
    printer = ThermalPrinter(config)
    
    if printer.is_connected():
        print("✅ Printer connected successfully!")
        
        # Test print
        printer.test_print()
        
        # Test daily brief
        from .daily_brief import get_greeting
        test_greeting = get_greeting()
        test_brief = "Heute wird ein produktiver Tag. Das Wetter ist sonnig und du hast 3 wichtige E-Mails und 2 Termine."
        test_tasks = ["E-Mail beantworten", "Meeting vorbereiten", "Projekt planen"]
        
        printer.print_daily_brief(test_greeting, test_brief, test_tasks)
        
        printer.disconnect()
    else:
        print("❌ Could not connect to printer")

if __name__ == "__main__":
    main()
