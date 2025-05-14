import json
import os
import smtplib, ssl
import time
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from nats.aio.client import Client as NATS
import asyncio

def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)

def send_email(config, subject, message_content):
    sender_email = config['from_email']
    receiver_email = config['to_email']
    password = config['from_password']

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    print(f"Sending email with subject: {subject}")
    print(f"Sender: {sender_email}")
    print(f"Receiver: {receiver_email}")

    # Create the plain-text and HTML version of your message
    text = message_content
    
    html = f"""\
    <html>
    <body style="font-family: Arial, sans-serif; background: #f4f4f9; color: #333; padding: 40px;">
        <p style="font-size: 18px; line-height: 1.6; max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        {message_content}
        </p>
    </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
    print("Email sent successfully")

async def email_service(config):
    # Connect to NATS
    nats_url = os.environ.get('NATS_URL', 'nats://nats:4222')
    print(f"Connecting to NATS at {nats_url}")
    
    nc = NATS()
    await nc.connect(nats_url)
    
    # Subscribe to the emails channel
    async def message_handler(msg):
        subject = msg.subject
        data = msg.data.decode()
        print(f"Received a message on '{subject}': {data}")
        
        try:
            # Parse the message data
            email_data = json.loads(data)
            subject = email_data.get('subject', 'Alert Notification')
            message = email_data.get('message', 'No message content provided')
            
            # Send the email
            send_email(config, subject, message)
            
        except Exception as e:
            print(f"Error processing message: {e}")
    
    # Subscribe to the emails channel
    await nc.subscribe("emails", cb=message_handler)
    print("Subscribed to 'emails' channel")
    
    # Keep the service running
    while True:
        await asyncio.sleep(1)
        
async def main():
    config_path = os.environ.get('CONFIG_PATH', './config/email_config.json')
    config = load_config(config_path)
    await email_service(config)

if __name__ == "__main__":
    asyncio.run(main())
