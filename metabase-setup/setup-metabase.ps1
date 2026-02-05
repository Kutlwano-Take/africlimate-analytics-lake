# Setup Metabase for Climate Analytics Dashboard
Write-Host "Setting up Metabase for Climate Analytics..."

# Check if Docker is installed
try {
    docker --version
    Write-Host "Docker found, proceeding with setup..."
} catch {
    Write-Host "Docker not found. Please install Docker Desktop first."
    Write-Host "Download from: https://www.docker.com/products/docker-desktop"
    exit 1
}

# Navigate to metabase directory
Set-Location "c:\Users\kutlw\DE-AFRICA-CLIMATE-LAKE\metabase-setup"

# Start Metabase and PostgreSQL
Write-Host "Starting Metabase containers..."
docker-compose up -d

# Wait for containers to start
Write-Host "Waiting for Metabase to initialize (60 seconds)..."
Start-Sleep -Seconds 60

# Check if containers are running
$metabaseStatus = docker ps --filter "name=climate-metabase" --format "table {{.Names}}\t{{.Status}}"
$postgresStatus = docker ps --filter "name=climate-postgres" --format "table {{.Names}}\t{{.Status}}"

Write-Host "Container Status:"
Write-Host $metabaseStatus
Write-Host $postgresStatus

Write-Host ""
Write-Host "=== METABASE SETUP COMPLETE ==="
Write-Host "Access your Climate Dashboard at: http://localhost:3000"
Write-Host ""
Write-Host "Next Steps:"
Write-Host "1. Open http://localhost:3000 in your browser"
Write-Host "2. Create admin account"
Write-Host "3. Add Athena database connection"
Write-Host "4. I'll help you create your first climate dashboard!"
