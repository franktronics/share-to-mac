"""
Utility helpers for discovering the machine's local IP address
and computing a human-readable network info string.
"""

import socket


def get_local_ip() -> str:
    """
    Returns the machine's LAN IP address by opening a dummy UDP connection.
    Falls back to 127.0.0.1 if no network is available.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Does not actually send data; just retrieves the outbound interface IP.
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
