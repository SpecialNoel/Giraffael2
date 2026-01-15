# get_self_ip.py

import socket

def get_local_ip():
    s = None
    try:
        # Create a temporary socket to connect to a known external address
        # Google's DNS server 8.8.8.8 is used as a reliable destination.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip_address = s.getsockname()[0]
        return ip_address
    except socket.error:
        # Fallback approach
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            return ip_address
        except socket.error:
            return '127.0.0.1' # Default to loopback if all else fails
    finally:
        if s:
            s.close()
