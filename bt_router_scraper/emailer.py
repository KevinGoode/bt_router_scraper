# Import smtplib for the actual sending function
import smtplib
import json
# Import the email modules we'll need
from email.mime.text import MIMEText


class ConnectionAlerts:
    def __init__(self, config, previous, present):
        self.previous = previous
        self.present = present
        self.address = config.alerts_username
        self.alerts_conf = config.alerts_conf
        self.sender = smtplib.SMTP(config.alerts_smtp_address, config.alerts_smtp_port)
        self.sender.ehlo() 
        self.sender.starttls() #Puts connection to SMTP server in TLS mode
        self.sender.ehlo()
        self.sender.login(config.alerts_username, config.alerts_password)
    
    def __del__(self):
        self.sender.quit()

    def _get_trigggers_and_recipients(self):
        json_file = open(self.alerts_conf)
        json_data = json_file.read()
        data = json.loads(json_data)
        json_file.close()
        return data['triggers'], data['alerts']
            
    def send_all_alerts(self):
        triggers, recipients = self._get_trigggers_and_recipients()
        new_connections = self._get_all_new_connections()    
        lost_connections = self._get_all_lost_connections()
        self._alert_all_new_connections(triggers, recipients, new_connections)
        self._alert_all_lost_connections(triggers, recipients, lost_connections)

    def _get_all_new_connections(self):
        new_connections = []
        for new in self.present:
            if new not in self.previous:
                new_connections.append(new)
        return new_connections

    def _get_all_lost_connections(self):
        old_connections = []
        for old in self.previous:
            if old not in self.present:
                old_connections.append(old)
        return old_connections

    def _alert_all_new_connections(self, triggers, recipients, connections):
        for connection in connections:
            for trigger in triggers:
                if trigger['id'] == connection["id"]:
                    self._send_new_connection_email(trigger["name"],recipients)

    def _alert_all_lost_connections(self, triggers, recipients, connections):
        for connection in connections:
            for trigger in triggers:
                if trigger['id'] == connection["id"]:
                    self._send_lost_connection_email(trigger["name"],recipients)

    def _send_new_connection_email(self, name, recipients):
        msg = MIMEText(name + " has just connected to BTRouter.")
        msg['Subject'] = name + " has just connected to BTRouter."
        msg['From'] = self.address
        for recipient in recipients:
            msg['To'] = recipient
            self.sender.sendmail(self.address, [recipient], msg.as_string())
 
    def _send_lost_connection_email(self, name, recipients):
        msg = MIMEText(name + " has just disconnected from BTRouter.")
        msg['Subject'] = name + " has just disconnected from BTRouter."
        msg['From'] = self.address
        for recipient in recipients:
            msg['To'] = recipient
            self.sender.sendmail(self.address, [recipient], msg.as_string())

