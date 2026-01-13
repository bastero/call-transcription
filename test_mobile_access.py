#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test mobile access connectivity."""

import socket
import subprocess
import sys


def get_local_ip():
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return None


def check_port_listening(port):
    """Check if a port is listening."""
    try:
        result = subprocess.run(
            ['lsof', '-i', ':{}'.format(port)],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


def check_firewall_status():
    """Check macOS firewall status."""
    try:
        result = subprocess.run(
            ['sudo', '/usr/libexec/ApplicationFirewall/socketfilterfw', '--getglobalstate'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except:
        return "Unable to check (requires sudo)"


def test_local_connection(port):
    """Test if we can connect to localhost."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False


def check_wifi_network():
    """Get current WiFi network."""
    try:
        result = subprocess.run(
            ['networksetup', '-getairportnetwork', 'en0'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except:
        return "Unable to detect"


def main():
    print("=" * 60)
    print("CallScribe Mobile Access Diagnostic")
    print("=" * 60)
    print()

    # Check local IP
    local_ip = get_local_ip()
    if local_ip:
        print(f"✓ Local IP Address: {local_ip}")
    else:
        print("✗ Could not detect local IP")
        return

    # Check WiFi network
    wifi = check_wifi_network()
    print(f"✓ WiFi Network: {wifi}")
    print()

    # Check common ports
    print("Checking ports:")
    for port in [3000, 5000, 8080]:
        listening = check_port_listening(port)
        can_connect = test_local_connection(port)

        status = "✓" if listening else "✗"
        print(f"{status} Port {port}: {'LISTENING' if listening else 'NOT LISTENING'}")

        if listening:
            local_status = "✓" if can_connect else "✗"
            print(f"  {local_status} Localhost connection: {'SUCCESS' if can_connect else 'FAILED'}")
    print()

    # Check firewall
    print("Firewall Status:")
    firewall = check_firewall_status()
    print(f"  {firewall}")
    print()

    # Provide recommendations
    print("=" * 60)
    print("Recommendations:")
    print("=" * 60)

    if not any(check_port_listening(p) for p in [3000, 5000, 8080]):
        print("⚠️  No server is running!")
        print("   Start the server first:")
        print("   python -m callscribe gui --port 3000")
        print()

    if "enabled" in firewall.lower():
        print("⚠️  Firewall is ENABLED - this may block mobile access")
        print("   Solution 1: Allow Python in firewall")
        print("     System Settings → Network → Firewall → Options")
        print("     Add Python to allowed apps")
        print()
        print("   Solution 2: Temporarily disable firewall (for testing)")
        print("     sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off")
        print("     [Test mobile access]")
        print("     sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on")
        print()

    # Mobile connection test
    print("Mobile Connection URLs:")
    for port in [3000, 5000, 8080]:
        if check_port_listening(port):
            print(f"  ✓ http://{local_ip}:{port}")
    print()

    print("To test from mobile:")
    print("  1. Ensure mobile is on same WiFi network")
    print(f"  2. Visit http://{local_ip}:3000 in mobile browser")
    print("  3. If timeout, check firewall settings above")
    print()


if __name__ == "__main__":
    main()
