@echo off
echo Starting Metabase for Climate Analytics...
echo.
echo Make sure Docker Desktop is running first!
echo.
pause

cd /d "c:\Users\kutlw\DE-AFRICA-CLIMATE-LAKE\metabase-setup"

echo Starting containers...
docker-compose up -d

echo.
echo Waiting for Metabase to initialize (60 seconds)...
timeout /t 60

echo.
echo Checking container status...
docker ps --filter "name=climate-metabase" --format "table {{.Names}}\t{{.Status}}"
docker ps --filter "name=climate-postgres" --format "table {{.Names}}\t{{.Status}}"

echo.
echo === METABASE SETUP COMPLETE ===
echo Access your Climate Dashboard at: http://localhost:3000
echo.
echo Next Steps:
echo 1. Open http://localhost:3000 in your browser
echo 2. Create admin account
echo 3. Add Athena database connection
echo 4. Create your first climate dashboard!
echo.
pause
