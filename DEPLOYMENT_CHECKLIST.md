# Railway Deployment Checklist

## ✅ Pre-Deployment

- [x] Bot code ready (bot_zoho.py, zoho_drive.py)
- [x] Dockerfile created
- [x] requirements.txt updated
- [x] .gitignore created (protects .env)
- [x] .dockerignore created
- [x] README.md created

## 📋 Deployment Steps

### 1. GitHub Setup (5 minutes)

- [ ] Go to https://github.com/new
- [ ] Create repository name: `billing-bot`
- [ ] Make it **Private**
- [ ] Don't initialize with README
- [ ] Click "Create repository"

### 2. Push to GitHub (2 minutes)

```bash
# Option A: Use the setup script
setup_git.bat

# Then add your GitHub URL and push:
git remote add origin https://github.com/YOUR_USERNAME/billing-bot.git
git branch -M main
git push -u origin main
```

OR

```bash
# Option B: Manual setup
git init
git add bot_zoho.py zoho_drive.py requirements.txt Dockerfile .dockerignore .gitignore README.md
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_URL
git branch -M main
git push -u origin main
```

### 3. Railway Setup (5 minutes)

- [ ] Go to https://railway.app/
- [ ] Sign in with GitHub
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose `billing-bot` repository
- [ ] Wait for initial deployment

### 4. Configure Environment Variables (5 minutes)

- [ ] In Railway dashboard, click your service
- [ ] Go to "Variables" tab
- [ ] Add all variables from .env file:

**Required Variables:**
```
BOT_TOKEN
SMTP_SERVER
SMTP_PORT
EMAIL_ADDRESS
EMAIL_PASSWORD
SMTP_USERNAME
EXCLUDED_EMAIL
ALLOWED_USERS
ZOHO_CLIENT_ID
ZOHO_CLIENT_SECRET
ZOHO_REFRESH_TOKEN
ZOHO_API_DOMAIN
ZOHO_INVOICE_FOLDER_ID
ZOHO_ZELLE_FOLDER_ID
ZOHO_DEBTOR_FOLDER_ID
ZOHO_SENT_FOLDER_ID
```

- [ ] Click "Deploy" to restart with new variables

### 5. Verify Deployment (2 minutes)

- [ ] Check Railway logs: Look for "[BOT] BillingBot running..."
- [ ] Open Telegram
- [ ] Send `/start` to your bot
- [ ] Bot should respond with buttons
- [ ] Upload a test PDF to Zoho WorkDrive
- [ ] Test sending an email

## ✅ Post-Deployment

- [ ] Stop local bot (GUI → STOP BOT)
- [ ] Bot is now running 24/7 on Railway
- [ ] Team can use bot from anywhere
- [ ] Files are stored in Zoho WorkDrive
- [ ] Monitor Railway logs for any issues

## 📊 Monitoring

### Check Bot Health:
1. **Railway Dashboard** → Your service → "Logs"
2. **Telegram** → Send `/start` to test
3. **Zoho WorkDrive** → Check file movements

### If Something Goes Wrong:
1. Check Railway logs for errors
2. Verify environment variables
3. Test Zoho API rate limits (wait if hit)
4. Check Telegram bot token

## 🎉 Success Criteria

- [x] Bot responds to `/start` in Telegram
- [x] Bot finds PDFs in Zoho WorkDrive
- [x] Bot sends emails successfully
- [x] Bot moves files to Sent Files folder
- [x] Railway shows "Running" status
- [x] No errors in Railway logs

## 💰 Cost

**Railway Free Tier:**
- 500 execution hours/month
- Perfect for 24/7 bot
- After free tier: ~$5/month

## 🔄 Updating the Bot

When you make code changes:

```bash
git add .
git commit -m "Your change description"
git push
```

Railway auto-deploys on push! 🚀

## 📞 Need Help?

- Railway Docs: https://docs.railway.app/
- Telegram Bot API: https://core.telegram.org/bots/api
- Zoho WorkDrive API: https://www.zoho.com/workdrive/api/

---

**Estimated Total Time: 20 minutes**
