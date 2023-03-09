Full example of automatic monitoring from netbox changes to prometheus. Custom fields contain the email to notify on alert and a flag to monitor.

Methodology:
  * Install plugin to netbox.
  * Create custom fields as desired.
    ** icmp  DCIM -> Device, Virtualization -> Virtual Machine, boolean default value false (don't monitor)
    ** alert_notification_email  DCIM -> Device, Virtualization -> Virtual Machine, text default value desired normal email
  * Install prometheus, alertmanager, blackbox-exporter, other exporters as desired (snmp-exporter)
  * See examples for alert rules (endpoint down), prometheus and alertmanager configuration
