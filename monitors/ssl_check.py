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

from utils.google_chat import send_alert
from utils.state_manager import is_service_down, mark_service_down, mark_service_up

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

def check_ssl_certs(monitor_config: Dict[str, Any], integrations_config: Dict[str, Any], state: Dict[str, Any], send_alerts: bool = True) -> List[Dict[str, Any]]:
    """
    Connects to a list of domains, checks their SSL certificates, sends
    alerts for issues, and returns a detailed status for each.
    """
    options = monitor_config.get('options', {})
    domains = options.get('domains', [])
    alert_days = options.get('alert_days', {})
    alert_on_recovery = monitor_config.get('alert_on_recovery', True)
    
    nginx_proxy_manager_url = integrations_config.get('nginx_proxy_manager_url')
    nginx_button = [{"text": "Manage Certificates", "url": nginx_proxy_manager_url}] if nginx_proxy_manager_url else []

    results = []
    context = ssl.create_default_context()
    
    critical_threshold = alert_days.get('critical', 7)
    warning_threshold = alert_days.get('warning', 30)

    for domain in domains:
        domain_down = False
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
                        domain_down = True
                        if send_alerts:
                            details = (
                                f"<b>What's happening:</b> The website security lock (SSL certificate) for <b>{domain}</b> has expired.\n"
                                f"<b>Impact:</b> Visitors will see a large, scary security warning and may be blocked from using the site. This damages trust.\n\n"
                                "<b>What to do:</b> Please contact the technical team at tech@pinoyseoul.com and report that the 'SSL certificate for {domain} has expired'."
                            )
                            send_alert(f"Website Security EXPIRED for {domain}", severity="critical", title="URGENT: Website Security Expired", details=details, extra_buttons=nginx_button)
                    
                    elif days_left < critical_threshold:
                        status_report['status'] = 'critical'
                        domain_down = True
                        if send_alerts:
                            details = (
                                f"<b>What's happening:</b> The website security lock for <b>{domain}</b> will expire in only {days_left} days.\n"
                                f"<b>Impact:</b> If this is not fixed, the site will soon show a security warning to all visitors.\n\n"
                                "<b>What to do:</b> Please contact the technical team at tech@pinoyseoul.com and ask them to 'renew the SSL certificate for {domain}'."
                            )
                            send_alert(f"Website Security for {domain} expires in {days_left} days", severity="critical", title=f"URGENT: Renew Website Security", details=details, extra_buttons=nginx_button)

                    elif days_left < warning_threshold:
                        status_report['status'] = 'warning'
                        if send_alerts:
                            details = (
                                f"<b>What's happening:</b> This is a routine notice that the website security lock for <b>{domain}</b> is due for renewal in {days_left} days.\n"
                                f"<b>Impact:</b> There is no impact to users right now.\n\n"
                                "<b>What to do:</b> No action is needed from you. The technical team has been notified and will renew it before it expires."
                            )
                            send_alert(f"Website security for {domain} needs renewal soon", severity="warning", title=f"Heads-Up: Security Renewal", details=details, extra_buttons=nginx_button)
                    
                    else:
                        status_report['status'] = 'valid'
                        log.info(f"SSL for {domain} is valid for {days_left} days.")
                        if is_service_down(domain, state):
                            if send_alerts and alert_on_recovery:
                                details = f"<b>What happened:</b> The security or connectivity issue affecting <b>{domain}</b> has been resolved. The site is now secure and accessible."
                                send_alert(f"The issue with {domain} is resolved", severity="info", title=f"ALL CLEAR: {domain} Restored", details=details)
                            mark_service_up(domain, state)

        except (socket.gaierror, socket.timeout, ConnectionRefusedError) as e:
            log.warning(f"Could not reach {domain} to check SSL: {e}")
            status_report['status'] = 'error'
            domain_down = True
            if send_alerts:
                details = (
                    f"<b>What's happening:</b> The monitor can't connect to the server at <b>{domain}</b>. This usually means the website or service is offline.\n"
                    f"<b>Impact:</b> The service at this domain is unavailable.\n\n"
                    "<b>What to do:</b> Please contact the technical team at tech@pinoyseoul.com and report that the service at '{domain}' is unreachable."
                )
                send_alert(f"Cannot connect to the server for {domain}", severity="warning", title=f"Service Unreachable: {domain}", details=details)

        except ssl.SSLCertVerificationError as e:
            log.error(f"Invalid SSL certificate for {domain}: {e}")
            status_report['status'] = 'critical'
            domain_down = True
            if send_alerts:
                details = (
                    f"<b>What's happening:</b> The website security lock for <b>{domain}</b> is broken or misconfigured.\n"
                    f"<b>Impact:</b> Visitors will see a security error and may be blocked from the site.\n\n"
                    "<b>What to do:</b> Please contact the technical team at tech@pinoyseoul.com and report an 'Invalid SSL Certificate on {domain}'."
                )
                send_alert(f"The security certificate for {domain} is invalid", severity="critical", title=f"CRITICAL: Invalid Website Security", details=details, extra_buttons=nginx_button)
        
        except Exception as e:
            log.error(f"An unexpected error occurred while checking SSL for {domain}: {e}")
            status_report['status'] = 'error'
            domain_down = True
        
        if domain_down:
            mark_service_down(domain, state)

        results.append(status_report)
        
    return results