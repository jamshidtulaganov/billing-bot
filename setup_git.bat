@echo off
echo ====================================
echo Git Repository Setup
echo ====================================
echo.

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Initializing git repository...
git init

echo.
echo Adding files to git...
git add bot_zoho.py zoho_drive.py requirements.txt Dockerfile .dockerignore .gitignore README.md DEPLOYMENT_GUIDE.md

echo.
echo Creating initial commit...
git commit -m "Initial commit - Zoho WorkDrive integrated bot"

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo Next steps:
echo 1. Create a private GitHub repository at https://github.com/new
echo 2. Copy the repository URL
echo 3. Run: git remote add origin YOUR_GITHUB_URL
echo 4. Run: git branch -M main
echo 5. Run: git push -u origin main
echo.
echo Then follow DEPLOYMENT_GUIDE.md to deploy to Railway!
echo.
pause
