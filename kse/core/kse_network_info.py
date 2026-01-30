"""
KSE Network Information
Utilities for detecting and displaying network information (public IP, hostname, etc.)
"""

import socket
import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


def get_public_ip() -> Optional[str]:
    """
    Detect the public IP address of the server.
    
    Uses multiple fallback services to ensure reliability.
    
    Returns:
        str: Public IP address, or None if detection fails
    """
    # List of public IP detection services (in order of preference)
    services = [
        'https://api.ipify.org',
        'https://icanhazip.com',
        'https://ifconfig.me/ip',
        'https://ident.me',
    ]
    
    for service in services:
        try:
            response = requests.get(service, timeout=3)
            if response.status_code == 200:
                ip = response.text.strip()
                logger.info(f"Public IP detected: {ip} (via {service})")
                return ip
        except Exception as e:
            logger.debug(f"Failed to get IP from {service}: {e}")
            continue
    
    logger.warning("Could not detect public IP address from any service")
    return None


def get_local_ip() -> Optional[str]:
    """
    Get the local/private IP address of the server.
    
    Returns:
        str: Local IP address, or None if detection fails
    """
    try:
        # Create a socket to determine local IP
        # This doesn't actually connect, just determines which interface would be used
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        logger.error(f"Failed to detect local IP: {e}")
        return None


def get_hostname() -> str:
    """
    Get the hostname of the server.
    
    Returns:
        str: Hostname
    """
    try:
        return socket.gethostname()
    except Exception as e:
        logger.error(f"Failed to get hostname: {e}")
        return "unknown"


def get_network_info() -> Dict[str, Optional[str]]:
    """
    Get comprehensive network information about the server.
    
    Returns:
        dict: Network information including public IP, local IP, and hostname
    """
    return {
        'public_ip': get_public_ip(),
        'local_ip': get_local_ip(),
        'hostname': get_hostname(),
    }


def format_server_info(host: str, port: int, network_info: Optional[Dict] = None) -> str:
    """
    Format server information for display.
    
    Args:
        host: Configured host (e.g., "127.0.0.1" or "0.0.0.0")
        port: Server port
        network_info: Optional network info dict from get_network_info()
    
    Returns:
        str: Formatted server information
    """
    if network_info is None:
        network_info = get_network_info()
    
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append("KSE Server Network Information")
    lines.append(f"{'='*60}")
    
    # Local access
    if host in ["127.0.0.1", "localhost"]:
        lines.append(f"Local Access:    http://localhost:{port}")
    else:
        local_ip = network_info.get('local_ip')
        if local_ip:
            lines.append(f"Local Network:   http://{local_ip}:{port}")
        lines.append(f"Listening on:    http://{host}:{port}")
    
    # Public access
    public_ip = network_info.get('public_ip')
    if public_ip:
        lines.append(f"Public Access:   http://{public_ip}:{port}")
        lines.append(f"  (Use this URL for remote clients)")
    else:
        lines.append("Public IP:       Could not detect")
    
    # Hostname
    hostname = network_info.get('hostname', 'unknown')
    lines.append(f"Hostname:        {hostname}")
    
    lines.append(f"{'='*60}\n")
    
    return "\n".join(lines)
