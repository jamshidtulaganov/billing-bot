@echo off
echo ====================================
echo Push to GitHub
echo ====================================
echo.
echo You need a GitHub Personal Access Token.
echo.
echo Get one here: https://github.com/settings/tokens
echo 1. Click "Generate new token (classic)"
echo 2. Name: BillingBot
echo 3. Check: repo (all sub-options)
echo 4. Generate and copy the token
echo.
set /p TOKEN="Paste your GitHub token here: "
echo.
echo Setting remote URL with token...
git remote set-url origin https://%TOKEN%@github.com/jamshidtulaganov/billing-bot.git
echo.
echo Pushing to GitHub...
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo ====================================
    echo SUCCESS! Code pushed to GitHub!
    echo ====================================
    echo.
    echo Next: Deploy to Railway.app
    echo 1. Go to https://railway.app/
    echo 2. Sign in with GitHub
    echo 3. New Project - Deploy from GitHub repo
    echo 4. Choose: jamshidtulaganov/billing-bot
    echo 5. Add environment variables from .env
    echo.
) else (
    echo ====================================
    echo ERROR: Failed to push
    echo ====================================
    echo Please check your token and try again.
)
pause
