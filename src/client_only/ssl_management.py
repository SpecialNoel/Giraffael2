# ssl_management.py

import ssl

def setup_ssl_context():
    context = ssl.create_default_context()
    # Disable hostname check (for self-signed certificates)
    context.check_hostname = False  
    # Accept self-signed certificates (use CERT_REQUIRED for CA validation)
    context.verify_mode = ssl.CERT_NONE 
    return context
