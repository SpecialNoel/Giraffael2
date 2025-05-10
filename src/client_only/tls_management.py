# tls_management.py

import ssl

def setup_tls_context():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT) # TLS
    # Disable hostname check (for self-signed certificates)
    context.check_hostname = False  
    # Accept self-signed certificates (use CERT_REQUIRED for CA validation)
    context.verify_mode = ssl.CERT_NONE 
    return context
