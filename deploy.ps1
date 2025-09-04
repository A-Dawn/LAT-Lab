# LAT-Lab 跨平台部署脚本 (Windows PowerShell)
# 支持 Docker 部署和传统安装部署
# 增强功能：
# - 容器健康检查
# - 服务可用性验证
# - 部署进度显示
# - 错误重试机制

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "help")]
    [string]$Command = "start",
    
    [Parameter()]
    [switch]$Force
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色定义
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$White = "White"
$Cyan = "Cyan"
$Gray = "Gray"
$Magenta = "Magenta"

# 日志函数
function Write-LogInfo {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-LogSuccess {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-LogWarning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-LogError {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

# 检查系统要求
function Test-Requirements {
    Write-LogInfo "Checking system requirements..."
    
    # 检查操作系统
    if ($env:OS -eq "Windows_NT") {
        Write-LogInfo "Detected Windows system"
    } else {
        Write-LogError "Unsupported operating system: $env:OS"
        exit 1
    }
    
    # 检查 Docker
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-LogSuccess "Docker is installed"
            Write-LogInfo "Docker version: $dockerVersion"
        } else {
            throw "Docker not installed"
        }
    } catch {
        Write-LogError "Docker not installed, please install Docker Desktop first"
        exit 1
    }
    
    # 检查 Docker Compose
    try {
        $composeVersion = docker-compose --version 2>$null
        if ($composeVersion) {
            Write-LogSuccess "Docker Compose is installed"
            Write-LogInfo "Docker Compose version: $composeVersion"
        } else {
            throw "Docker Compose not installed"
        }
    } catch {
        Write-LogError "Docker Compose not installed, please install Docker Compose first"
        exit 1
    }
    
    # 检查可用内存
    try {
        $memory = Get-CimInstance -ClassName Win32_ComputerSystem | Select-Object -ExpandProperty TotalPhysicalMemory
        $memoryGB = [math]::Round($memory / 1GB, 1)
        if ($memoryGB -lt 4) {
            Write-LogWarning "Available memory less than 4GB (current: ${memoryGB}GB), may affect performance"
        } else {
            Write-LogSuccess "Memory check passed (${memoryGB}GB)"
        }
    } catch {
        Write-LogWarning "Unable to check memory information"
    }
    
    # 检查磁盘空间
    try {
        $disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
        $freeSpaceGB = [math]::Round($disk.FreeSpace / 1GB, 1)
        if ($freeSpaceGB -lt 10) {
            Write-LogWarning "Available disk space less than 10GB (current: ${freeSpaceGB}GB)"
        } else {
            Write-LogSuccess "Disk space check passed (${freeSpaceGB}GB)"
        }
    } catch {
        Write-LogWarning "Unable to check disk space information"
    }
}

# 配置环境变量
function Setup-Environment {
    Write-LogInfo "Setting up environment variables..."
    
    if (-not (Test-Path ".env")) {
        if (Test-Path "env.example") {
            Write-LogInfo "Copying environment configuration template..."
            Copy-Item "env.example" ".env"
            Write-LogSuccess "Created .env file, please edit configuration"
        } else {
            Write-LogError "Environment configuration template file not found"
            exit 1
        }
    } else {
        Write-LogInfo ".env file already exists"
    }
    
    # 提示用户编辑配置
    Write-LogWarning "Please edit .env file with the following key configurations:"
    Write-Host "  - MYSQL_ROOT_PASSWORD: MySQL root password" -ForegroundColor $White
    Write-Host "  - MYSQL_USER: Database username" -ForegroundColor $White
    Write-Host "  - MYSQL_PASSWORD: Database password" -ForegroundColor $White
    Write-Host "  - SECRET_KEY: JWT secret key (minimum 32 characters)" -ForegroundColor $White
    Write-Host "  - BASE_URL: Website base URL" -ForegroundColor $White
    Write-Host "  - DEBUG: Debug mode (set to False for production)" -ForegroundColor $White
    Write-Host ""
    Read-Host "Press Enter after editing configuration"
}

# Docker 部署
function Test-ContainerHealth {
    param(
        [string]$containerName,
        [int]$maxRetries = 30,
        [int]$retryInterval = 5
    )
    
    $retryCount = 0
    $isHealthy = $false
    
    Write-Host "`nChecking health of container: $containerName" -ForegroundColor $Blue
    
    while ($retryCount -lt $maxRetries -and -not $isHealthy) {
        $containerInfo = docker inspect --format="{{.State.Health.Status}}" $containerName 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            if ($containerInfo -eq "healthy") {
                Write-Host "[$($retryCount + 1)/$maxRetries] $containerName is healthy" -ForegroundColor $Green
                $isHealthy = $true
                return $true
            } else {
                Write-Host "[$($retryCount + 1)/$maxRetries] $containerName status: $containerInfo" -ForegroundColor $Yellow
            }
        } else {
            Write-Host "[$($retryCount + 1)/$maxRetries] Waiting for $containerName to start..." -ForegroundColor $Yellow
        }
        
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Start-Sleep -Seconds $retryInterval
        }
    }
    
    if (-not $isHealthy) {
        Write-LogError "Container $containerName failed to become healthy after $maxRetries attempts"
        return $false
    }
}

function Test-ServiceAvailability {
    param(
        [string]$url,
        [int]$maxRetries = 10,
        [int]$retryInterval = 5
    )
    
    $retryCount = 0
    $isAvailable = $false
    
    Write-Host "`nTesting service availability: $url" -ForegroundColor $Blue
    
    while ($retryCount -lt $maxRetries -and -not $isAvailable) {
        try {
            $response = Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "[$($retryCount + 1)/$maxRetries] Service is available" -ForegroundColor $Green
                $isAvailable = $true
                return $true
            }
        } catch {
            Write-Host "[$($retryCount + 1)/$maxRetries] Waiting for service..." -ForegroundColor $Yellow
        }
        
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Start-Sleep -Seconds $retryInterval
        }
    }
    
    if (-not $isAvailable) {
        Write-LogError "Service at $url is not available after $maxRetries attempts"
        return $false
    }
}

function Show-ProgressBar {
    param(
        [string]$Activity,
        [string]$Status,
        [int]$PercentComplete,
        [int]$SecondsRemaining = 0
    )
    
    $progressParams = @{
        Activity = $Activity
        Status = $Status
        PercentComplete = $PercentComplete
    }
    
    if ($SecondsRemaining -gt 0) {
        $progressParams.SecondsRemaining = $SecondsRemaining
    }
    
    Write-Progress @progressParams
}

function Deploy-Docker {
    Write-LogInfo "Starting Docker deployment..."
    
    # 构建并启动服务
    Write-LogInfo "Building and starting Docker services..."
    
    # 显示构建进度
    $buildJob = Start-Job -ScriptBlock { 
        param($composeFile)
        docker-compose -f $composeFile up -d --build 
    } -ArgumentList (Resolve-Path "docker-compose.yml").Path
    
    # 显示构建进度
    $progress = 0
    $maxProgress = 100
    $progressStep = 5
    
    while ($buildJob.State -eq "Running") {
        $progress = [Math]::Min($progress + $progressStep, 90)  # 构建最多到90%
        Show-ProgressBar -Activity "Building Docker containers..." -Status "In progress" -PercentComplete $progress -SecondsRemaining 30
        Start-Sleep -Seconds 5
    }
    
    $buildResult = Receive-Job $buildJob -ErrorAction SilentlyContinue
    Remove-Job $buildJob -Force
    
    if ($LASTEXITCODE -ne 0) {
        Write-LogError "Failed to build and start Docker services"
        Write-Error $buildResult
        exit 1
    }
    
    # 检查服务状态
    Write-LogInfo "Checking service status..."
    docker-compose ps
    
    # 检查容器健康状态
    $containers = @("backend", "frontend", "mysql")
    $allHealthy = $true
    
    foreach ($container in $containers) {
        if (-not (Test-ContainerHealth -containerName $container)) {
            $allHealthy = $false
            break
        }
    }
    
    if (-not $allHealthy) {
        Write-LogError "Some containers failed health checks. Please check the logs and try again."
        exit 1
    }
    
    # 初始化数据库
    Write-LogInfo "Initializing database..."
    try {
        $migrationJob = docker-compose exec -T backend python scripts/run_migrations.py
        if ($LASTEXITCODE -ne 0) {
            throw "Database migration failed"
        }
        
        $initJob = docker-compose exec -T backend python scripts/init_db.py
        if ($LASTEXITCODE -ne 0) {
            throw "Database initialization failed"
        }
        
        # 验证服务可用性
        $services = @(
            @{Name = "Frontend"; Url = "http://localhost"},
            @{Name = "Backend API"; Url = "http://localhost:8000"},
            @{Name = "Admin Panel"; Url = "http://localhost/admin"}
        )
        
        foreach ($service in $services) {
            if (-not (Test-ServiceAvailability -url $service.Url)) {
                Write-LogWarning "$($service.Name) is not responding as expected, but deployment will continue"
            }
        }
        
        # 显示完成进度
        Show-ProgressBar -Activity "Deployment complete!" -Status "All services are up and running" -PercentComplete 100
        
        Write-LogSuccess "Docker deployment completed successfully!" -ForegroundColor $Green
        Write-Host "`n"
        Write-Host "  Access URLs:" -ForegroundColor $White
        Write-Host "  - Frontend:     http://localhost" -ForegroundColor $Cyan
        Write-Host "  - Backend API:  http://localhost:8000" -ForegroundColor $Cyan
        Write-Host "  - Admin Panel:  http://localhost/admin" -ForegroundColor $Cyan
        Write-Host "  - Default Admin: admin / admin123" -ForegroundColor $Cyan
        Write-Host "`n  To view logs, run: docker-compose logs -f" -ForegroundColor $Gray
        Write-Host "  To stop services: docker-compose down`n" -ForegroundColor $Gray
        
    } catch {
        Write-LogError "Deployment failed: $_"
        Write-LogInfo "Troubleshooting steps:"
        Write-LogInfo "1. Check container logs: docker-compose logs"
        Write-LogInfo "2. Check if all containers are running: docker-compose ps"
        Write-LogInfo "3. Try rebuilding the services: docker-compose up -d --build --force-recreate"
        exit 1
    }
}

# 传统安装部署
function Deploy-Traditional {
    Write-LogInfo "Starting traditional installation deployment..."
    
    # 检查 Python
    try {
        $pythonVersion = python --version 2>$null
        if (-not $pythonVersion) {
            $pythonVersion = python3 --version 2>$null
        }
        if ($pythonVersion) {
            Write-LogSuccess "Python installed: $pythonVersion"
        } else {
            throw "Python not installed"
        }
    } catch {
        Write-LogError "Python 3 not installed, please install Python 3.8+ first"
        exit 1
    }
    
    # 检查 Node.js
    try {
        $nodeVersion = node --version 2>$null
        if ($nodeVersion) {
            Write-LogSuccess "Node.js installed: $nodeVersion"
        } else {
            throw "Node.js not installed"
        }
    } catch {
        Write-LogError "Node.js not installed, please install Node.js 14+ first"
        exit 1
    }
    
    # 检查 MySQL
    try {
        $mysqlVersion = mysql --version 2>$null
        if ($mysqlVersion) {
            Write-LogSuccess "MySQL installed: $mysqlVersion"
        } else {
            throw "MySQL not installed"
        }
    } catch {
        Write-LogError "MySQL not installed, please install MySQL 8.0+ first"
        exit 1
    }
    
    Write-LogInfo "Installing backend dependencies..."
    Set-Location "backend"
    pip install -e .
    Set-Location ".."
    
    Write-LogInfo "Installing frontend dependencies..."
    Set-Location "frontend"
    npm install
    Set-Location ".."
    
    Write-LogInfo "Building frontend..."
    Set-Location "frontend"
    npm run build
    Set-Location ".."
    
    Write-LogSuccess "Traditional installation deployment completed!"
    Write-LogInfo "Please start services manually:"
    Write-LogInfo "  - Backend: cd backend && python -m src.lat_lab.main"
    Write-LogInfo "  - Frontend: Configure web server to point to frontend/dist directory"
}

# 停止服务
function Stop-Services {
    Write-LogInfo "Stopping services..."
    docker-compose down
    Write-LogSuccess "Services stopped"
}

# 重启服务
function Restart-Services {
    Write-LogInfo "Restarting services..."
    docker-compose restart
    Write-LogSuccess "Services restarted"
}

# 查看日志
function View-Logs {
    Write-LogInfo "Viewing service logs..."
    docker-compose logs -f
}

# 清理服务
function Clean-Services {
    Write-LogWarning "This will delete all containers and data, are you sure? (y/N)"
    $response = Read-Host
    if ($response -match "^[yY](es)?$") {
        Write-LogInfo "Cleaning services..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        Write-LogSuccess "Services cleaned"
    } else {
        Write-LogInfo "Clean operation cancelled"
    }
}

# 显示帮助信息
function Show-Help {
    Write-Host "LAT-Lab Cross-Platform Deployment Script" -ForegroundColor $White
    Write-Host ""
    Write-Host "Usage: .\deploy.ps1 [command]" -ForegroundColor $White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor $White
    Write-Host "  start           Start Docker deployment (recommended)" -ForegroundColor $White
    Write-Host "  traditional     Traditional installation deployment" -ForegroundColor $White
    Write-Host "  stop            Stop services" -ForegroundColor $White
    Write-Host "  restart         Restart services" -ForegroundColor $White
    Write-Host "  logs            View logs" -ForegroundColor $White
    Write-Host "  clean           Clean services (delete all data)" -ForegroundColor $White
    Write-Host "  help            Show this help information" -ForegroundColor $White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor $White
    Write-Host "  .\deploy.ps1 start        # Start Docker deployment" -ForegroundColor $White
    Write-Host "  .\deploy.ps1 traditional  # Traditional installation deployment" -ForegroundColor $White
    Write-Host "  .\deploy.ps1 stop         # Stop services" -ForegroundColor $White
}

# 主函数
function Main {
    switch ($Command.ToLower()) {
        "start" {
            Test-Requirements
            Setup-Environment
            Deploy-Docker
        }
        "traditional" {
            Test-Requirements
            Setup-Environment
            Deploy-Traditional
        }
        "stop" {
            Stop-Services
        }
        "restart" {
            Restart-Services
        }
        "logs" {
            View-Logs
        }
        "clean" {
            Clean-Services
        }
        "help" {
            Show-Help
        }
        default {
            Write-LogError "Unknown command: $Command"
            Show-Help
            exit 1
        }
    }
}

# 执行主函数
Main 