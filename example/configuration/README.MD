Full example of automatic monitoring from netbox changes to prometheus. Custom fields contain the email to notify on alert and a flag to monitor.

## Methodology:
  * Install plugin to netbox.
  * Create custom fields as desired (optional).
    * icmp  DCIM -> Device, Virtualization -> Virtual Machine, boolean default value false (don't monitor)
    * alert_notification_email  DCIM -> Device, Virtualization -> Virtual Machine, text default value desired normal email
  * Install prometheus, alertmanager, blackbox-exporter, other exporters as desired (snmp-exporter)
  * See examples for alert rules (endpoint down), prometheus and alertmanager configuration

## Use case
As you document a device (for example) in netbox, the object can be monitored automatically by setting appropriate (matching) flags. In my particular case, I use the icmp custom field as that trigger and in the prometheus config add &cf_icmp=true to the scraper. This narrows the scrape to just active devices with a primary ip and the flag set. Alert emails are sent to the default email address unless that field is changed within netbox.

## Optional simplified version
Alternatively, do not use the flag field and all devices/virtual machines will be monitored.
If you do not use email field, set the receiver of the alert to a specific email and remove that configuration.
