# Railway.app Deployment Guide

## Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Create a new **private** repository named `billing-bot`
3. Don't initialize with README (we already have one)

## Step 2: Push Code to GitHub

Open your terminal in the `BillingAutomation` folder and run:

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add bot_zoho.py zoho_drive.py requirements.txt Dockerfile .dockerignore .gitignore README.md

# Commit
git commit -m "Initial commit - Zoho WorkDrive integrated bot"

# Add your GitHub repository as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/billing-bot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**IMPORTANT:** The `.env` file will NOT be pushed (it's in `.gitignore`). This is correct - you'll set environment variables in Railway instead.

## Step 3: Deploy to Railway

### A. Sign Up for Railway

1. Go to [Railway.app](https://railway.app/)
2. Click **"Start a New Project"**
3. Sign in with GitHub

### B. Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your `billing-bot` repository
4. Railway will auto-detect the Dockerfile and start deploying

### C. Set Environment Variables

1. In Railway dashboard, click on your service
2. Go to **"Variables"** tab
3. Click **"Add Variable"** and add each of these:

```
BOT_TOKEN=8370964383:AAGUh8O4PqyesqArTumv8toHRQj25egi2aI
SMTP_SERVER=smtp.zeptomail.com
SMTP_PORT=587
EMAIL_ADDRESS=billing@tsst.ai
EMAIL_PASSWORD=wSsVR61zr0T5Dal9nmH/c+hpzVVcDlnzHRt63lSpviP/HPqW88czwkbIBVKiGqJKQDVrRjoV8Op6yk0IgWYKith/ywwADCiF9mqRe1U4J3x17qnvhDzKVmVVlheAL4sKxAtvn2dpF8Ah+g==
SMTP_USERNAME=emailapikey
EXCLUDED_EMAIL=info@tsst.ai
ALLOWED_USERS=6967097635,1424297977,5269724650,905434593
ZOHO_CLIENT_ID=1000.4SYEBEAVK7CAXYJKJQPEHQRC9HAF9B
ZOHO_CLIENT_SECRET=be30b925915dc602f5ae7d174b0d81980b4a8bc1df
ZOHO_REFRESH_TOKEN=1000.01a6a9e0258ce70c064761c79ca26115.45550b58321c351a6ee38d25dc99b446
ZOHO_API_DOMAIN=https://www.zohoapis.com
ZOHO_INVOICE_FOLDER_ID=8rki82c5e27f62c3a4c2ea7486dffb42c8a35
ZOHO_ZELLE_FOLDER_ID=8rki86b4679facd0e497c8b1db27370f3780d
ZOHO_DEBTOR_FOLDER_ID=8rki879908b429f76407ea147f70486a5b2e6
ZOHO_SENT_FOLDER_ID=8rki8bbb277d4e2994d0e954cddca7e26459d
```

### D. Deploy!

1. Railway will automatically deploy after you set the variables
2. Watch the logs in Railway dashboard
3. You should see: `[BOT] BillingBot running with Zoho WorkDrive integration...`

## Step 4: Verify Deployment

1. Open Telegram
2. Send `/start` to your bot
3. Test with a carrier ID!

## Troubleshooting

### Bot not responding
- Check Railway logs for errors
- Verify all environment variables are set correctly
- Make sure bot token is correct

### "Rate limit" errors
- Wait 10-15 minutes for Zoho API rate limit to reset
- Reduce API calls if needed

### File not found errors
- Verify folder IDs are correct
- Check file naming format matches the pattern
- Ensure files are uploaded to the correct Zoho folders

## Monitoring

- **Railway Logs**: Click on your service → "Deployments" → Click latest deployment → View logs
- **Telegram**: Send `/start` to test bot responsiveness
- **Email**: Check if emails are being sent successfully

## Updating the Bot

To update after making code changes:

```bash
git add .
git commit -m "Description of changes"
git push
```

Railway will automatically redeploy!

## Cost

Railway free tier includes:
- 500 hours/month (enough for 24/7 operation)
- After that: ~$5/month

## Support

For issues, check:
1. Railway logs
2. Telegram bot responses
3. Zoho WorkDrive folder contents
