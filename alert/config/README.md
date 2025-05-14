# Email Configuration

This folder contains configuration files for the email alert service.

## email_config.json

This file stores the email credentials and settings for sending alert notifications.

Example configuration:
```json
{
  "from_email": "your.email@gmail.com",
  "from_password": "your-app-password",
  "to_email": "recipient@example.com"
}
```

### Important Notes:

1. For Gmail accounts, you need to use an "App Password" instead of your regular account password.
   - Go to your Google Account > Security > 2-Step Verification > App passwords
   - Generate a new app password for this application

2. Keep this file secure and don't commit it to version control
   - The file is mounted as a read-only volume in the alert service container
   - You may want to add it to your .gitignore file

3. Make sure to update the "to_email" address to the email where you want to receive alerts
