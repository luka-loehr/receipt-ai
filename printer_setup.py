#!/usr/bin/env python3
"""
Printer Setup Utility

Lists connected USB devices and writes selected thermal printer configuration
to the .env file for centralized configuration.

Requires: pyusb (pip install pyusb)
"""

import os
from pathlib import Path


def list_usb_devices():
    try:
        import usb.core
        import usb.util
    except Exception as e:
        print("❌ pyusb not installed. Install with: pip install pyusb")
        return []

    devices = []
    for dev in usb.core.find(find_all=True):
        try:
            vendor_id = dev.idVendor
            product_id = dev.idProduct
            manufacturer = usb.util.get_string(dev, dev.iManufacturer) or "Unknown"
            product = usb.util.get_string(dev, dev.iProduct) or "Unknown"
            # Attempt to find endpoints
            in_ep = None
            out_ep = None
            for cfg in dev:
                for intf in cfg:
                    for ep in intf:
                        if ep.bEndpointAddress & 0x80:
                            in_ep = ep.bEndpointAddress
                        else:
                            out_ep = ep.bEndpointAddress
            devices.append({
                'vendor_id': vendor_id,
                'product_id': product_id,
                'manufacturer': manufacturer,
                'product': product,
                'in_ep': in_ep,
                'out_ep': out_ep,
            })
        except Exception:
            # Skip problematic devices
            continue
    return devices


def choose_device(devices):
    if not devices:
        print("No USB devices found.")
        return None
    print("\nConnected USB devices:")
    for idx, d in enumerate(devices, start=1):
        print(f"  {idx}: {d['manufacturer']} {d['product']} (vendor={hex(d['vendor_id'])}, product={hex(d['product_id'])})")
    choice = input("\nEnter the number of your thermal printer: ").strip()
    if not choice.isdigit():
        return None
    i = int(choice)
    if 1 <= i <= len(devices):
        return devices[i - 1]
    return None


def update_env(values):
    env_path = Path('.env')
    if not env_path.exists():
        # seed from example if available
        example = Path('env.example')
        if example.exists():
            env_path.write_text(example.read_text())
        else:
            env_path.write_text("")

    # read
    lines = env_path.read_text().splitlines()
    kv = {
        'THERMAL_PRINTER_TYPE': 'usb',
        'PRINTER_VENDOR_ID': str(values.get('vendor_id', '')),
        'PRINTER_PRODUCT_ID': str(values.get('product_id', '')),
        'PRINTER_IN_EP': str(values.get('in_ep', '')),
        'PRINTER_OUT_EP': str(values.get('out_ep', '')),
    }

    # update/replace
    def set_or_replace(lines, key, value):
        replaced = False
        for idx, line in enumerate(lines):
            if line.startswith(key + "="):
                lines[idx] = f"{key}={value}"
                replaced = True
                break
        if not replaced:
            lines.append(f"{key}={value}")
        return lines

    for k, v in kv.items():
        lines = set_or_replace(lines, k, v)

    env_path.write_text("\n".join(lines) + "\n")
    print("\n✅ Updated .env with USB thermal printer configuration")


def main():
    print("🖨️  Thermal Printer Setup")
    print("==========================\n")

    devices = list_usb_devices()
    device = choose_device(devices)
    if not device:
        print("❌ No device selected.")
        return

    print("\nSelected:")
    print(f"  {device['manufacturer']} {device['product']}")
    print(f"  Vendor: {hex(device['vendor_id'])}, Product: {hex(device['product_id'])}")
    print(f"  IN EP: {device['in_ep']}  OUT EP: {device['out_ep']}")

    update_env(device)

    print("\nDone. Your applications will read the configuration from .env.")


if __name__ == '__main__':
    main()


