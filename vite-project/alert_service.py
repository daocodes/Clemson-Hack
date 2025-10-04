import csv


# get registees tuple from csv (email, epsg:3257 tuple)
# run through registees and make request to server is_dangerous to see if their coordinates are a hit
# use SMTP handler to send email to them if they happen to be
# functions for removing and adding users to CSV

# csv handler functions (register, remove)
# poll call function (run through and check)
# check function (handle calling server)
# email send function using STMP handler


def register_user(csv_file, email, x, y):
    """Add a user to the CSV with their coordinates."""
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([email, x, y])


def remove_user(csv_file, email):
    """Remove a user from the CSV by email."""
    rows = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        rows = [row for row in reader if row[0] != email]
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def get_registrants(csv_file):
    """Get all registrants from CSV as list of (email, (x, y)) tuples."""
    registrants = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            email = row[0]
            coords = (float(row[1]), float(row[2]))
            registrants.append((email, coords))
    return registrants


# Check Function
def check_coordinates(server_url, x, y):
    """Check if coordinates are dangerous by calling server."""
    response = requests.get(f"{server_url}/is_dangerous", params={'x': x, 'y': y})
    return response.json().get('dangerous', False)


# Email Send Function
def send_danger_alert(notifier, email, x, y):
    """Send danger alert email to user."""
    subject = "⚠️ Danger Alert for Your Location"
    body = f"""
    Warning: Your registered location ({x}, {y}) is currently in a danger zone.
    Please take appropriate precautions.
    """
    notifier.send(email, subject, body)


# Poll Function
def poll_and_notify(csv_file, server_url, smtp_notifier):
    """Run through all registrants and notify if in danger zone."""
    registrants = get_registrants(csv_file)
    
    for email, (x, y) in registrants:
        if check_coordinates(server_url, x, y):
            print(f"Danger detected for {email} at ({x}, {y})")
            send_danger_alert(smtp_notifier, email, x, y)
        else:
            print(f"{email} is safe")




import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class SMTPNotifier:
    def __init__(self, server, port, username, password):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
    
    def send(self, to, subject, body, html=False):
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to if isinstance(to, str) else ', '.join(to)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html' if html else 'plain'))
        
        with smtplib.SMTP(self.server, self.port) as s:
            s.starttls()
            s.login(self.username, self.password)
            s.send_message(msg)


