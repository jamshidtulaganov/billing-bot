# Billing Automation Bot

Telegram bot for automated billing email delivery with Zoho WorkDrive integration.

## Features

- 📧 Automated email sending with PDF attachments
- ☁️ Zoho WorkDrive cloud storage integration
- 🤖 Telegram bot interface
- 📊 Real-time progress tracking
- ✅ Email extraction from PDFs
- 📁 Automatic file organization

## Tech Stack

- Python 3.13
- aiogram (Telegram Bot Framework)
- Zoho WorkDrive API
- pdfplumber (PDF processing)
- SMTP (Email delivery)

## Deployment

### Railway.app

This bot is designed to run on Railway.app.

#### Prerequisites

1. Telegram Bot Token (from @BotFather)
2. Zoho WorkDrive API credentials
3. SMTP credentials (ZeptoMail)
4. Railway account

#### Environment Variables

Set these in Railway dashboard:

```
BOT_TOKEN=your_telegram_bot_token
SMTP_SERVER=smtp.zeptomail.com
SMTP_PORT=587
EMAIL_ADDRESS=billing@tsst.ai
EMAIL_PASSWORD=your_email_password
SMTP_USERNAME=emailapikey
EXCLUDED_EMAIL=info@tsst.ai
ALLOWED_USERS=comma,separated,user,ids
ZOHO_CLIENT_ID=your_zoho_client_id
ZOHO_CLIENT_SECRET=your_zoho_client_secret
ZOHO_REFRESH_TOKEN=your_zoho_refresh_token
ZOHO_API_DOMAIN=https://www.zohoapis.com
ZOHO_INVOICE_FOLDER_ID=your_invoice_folder_id
ZOHO_ZELLE_FOLDER_ID=your_zelle_folder_id
ZOHO_DEBTOR_FOLDER_ID=your_debtor_folder_id
ZOHO_SENT_FOLDER_ID=your_sent_folder_id
```

#### Deploy Steps

1. Push code to GitHub
2. Connect GitHub to Railway
3. Set environment variables
4. Deploy!

## Usage

1. Start the bot: `/start`
2. Select document type (Invoice/Zelle/Debtor)
3. Send carrier IDs (space-separated)
4. Bot processes and sends emails automatically

## File Structure

```
BillingAutomation/
├── bot_zoho.py          # Main bot application
├── zoho_drive.py        # Zoho WorkDrive API wrapper
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── .dockerignore       # Docker ignore patterns
└── README.md           # This file
```

## License

Proprietary - TSS Technology LLC
