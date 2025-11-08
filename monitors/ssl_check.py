# -*- coding: utf-8 -*-
"""
Monitors the SSL certificate validity for a list of domains, sending alerts
for certificates that are expiring soon, already expired, or invalid.
"""

import ssl
import socket
from datetime import datetime, timezone
import logging
from typing import List, Dict, Any

# Assuming this module is run in an environment where utils can be imported
from utils.google_chat import send_alert

# Set up a logger for this module
log = logging.getLogger(__name__)

def _get_issuer_cn(issuer_tuple: tuple) -> str:
    """Extracts the Common Name (CN) from a certificate issuer tuple."""
    try:
        for rdn in issuer_tuple:
            for key, value in rdn:
                if key == 'commonName':
                    return value
    except (TypeError, ValueError):
        pass
    return "Unknown Issuer"


def check_ssl_certs(domains: List[str], alert_days: Dict[str, int]) -> List[Dict[str, Any]]:
    """
    Connects to a list of domains, checks their SSL certificates, sends
    alerts for issues, and returns a detailed status for each.

    Args:
        domains (List[str]): A list of domain names to check.
        alert_days (Dict[str, int]): A dictionary with integer values for
                                     'critical' and 'warning' day thresholds.

    Returns:
        A list of dictionaries, one for each domain, containing its status.
    """
    results = []
    context = ssl.create_default_context()
    
    # Get thresholds from config, with sensible defaults
    critical_threshold = alert_days.get('critical', 7)
    warning_threshold = alert_days.get('warning', 30)

    for domain in domains:
        status_report = {
            'domain': domain,
            'status': 'error',
            'days_until_expiry': -1,
            'expiry_date': 'N/A',
            'issuer': 'N/A'
        }
        try:
            log.info(f"Checking SSL for domain: {domain}")
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    expiry_date_str = cert['notAfter']
                    expiry_date = datetime.strptime(expiry_date_str, '%b %d %H:%M:%S %Y %Z').replace(tzinfo=timezone.utc)
                    days_left = (expiry_date - datetime.now(timezone.utc)).days

                    status_report['expiry_date'] = expiry_date.isoformat()
                    status_report['days_until_expiry'] = days_left
                    status_report['issuer'] = _get_issuer_cn(cert.get('issuer', ''))

                    if days_left < 0:
                        status_report['status'] = 'critical'
                        send_alert(
                            message=f"The SSL certificate for {domain} EXPIRED {-days_left} days ago!",
                            severity="critical",
                            title="SSL Certificate EXPIRED",
                            details="This site is now showing a security warning to all visitors. Immediate action required."
                        )
                    elif days_left < critical_threshold:
                        status_report['status'] = 'critical'
                        send_alert(
                            message=f"The SSL certificate for {domain} expires in just {days_left} days.",
                            severity="critical",
                            title="CRITICAL: SSL Certificate Expiring Soon",
                            details="Action needed: Renew certificate immediately or the site will show a security warning."
                        )
                    elif days_left < warning_threshold:
                        status_report['status'] = 'warning'
                        send_alert(
                            message=f"The SSL certificate for {domain} expires in {days_left} days.",
                            severity="warning",
                            title="SSL Certificate Renewal Due",
                            details="Schedule renewal in the next 2 weeks to avoid a last-minute rush."
                        )
                    else:
                        status_report['status'] = 'valid'
                        log.info(f"SSL for {domain} is valid for {days_left} days.")

        except (socket.gaierror, socket.timeout, ConnectionRefusedError) as e:
            log.warning(f"Could not reach {domain} to check SSL: {e}")
            status_report['status'] = 'error'
            send_alert(
                message=f"Could not connect to {domain} on port 443 to check its SSL certificate.",
                severity="warning",
                title=f"Cannot Check SSL for {domain}",
                details="This may indicate the site or service is down. Please verify."
            )
        except ssl.SSLCertVerificationError as e:
            log.error(f"Invalid SSL certificate for {domain}: {e}")
            status_report['status'] = 'critical'
            send_alert(
                message=f"The SSL certificate on {domain} is invalid (e.g., hostname mismatch).",
                severity="critical",
                title=f"Invalid SSL Certificate on {domain}",
                details="Visitors will see a security error. This needs to be fixed immediately."
            )
        except Exception as e:
            log.error(f"An unexpected error occurred while checking SSL for {domain}: {e}")
            status_report['status'] = 'error'
            send_alert(
                message=f"An unexpected error occurred while checking SSL for {domain}.",
                severity="critical",
                title="SSL Check Failed Unexpectedly",
                details=f"Error details: {str(e)}"
            )
        
        results.append(status_report)
        
    return results

if __name__ == '__main__':
    # This block allows for direct testing of the module.
    import json

    print("--- Running SSL Certificate Check Module ---")
    
    test_domains = [
        "google.com",
        "expired.badssl.com",
        "wrong.host.badssl.com",
        "this-domain-definitely-does-not-exist-123.com"
    ]
    
    # In a real test, this would come from a loaded config file.
    mock_alert_days = {
        'critical': 7,
        'warning': 30
    }
    
    print(f"Checking domains: {test_domains}\n")
    
    results = check_ssl_certs(test_domains, alert_days=mock_alert_days)
    
    print("\n--- Check Complete ---")
    print("Final data structure returned by the function:")
    print(json.dumps(results, indent=4))
    print("----------------------\n")
    print("Please check your Google Chat room for any alerts that were triggered.")