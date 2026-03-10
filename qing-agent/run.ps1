# 求职 Agent 启动脚本
# 版本：v1.3.0

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   求职 Agent API v1.3.0" -ForegroundColor Green
Write-Host "   启动检查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 .env 文件
if (Test-Path ".env") {
    Write-Host "[OK] .env 配置文件存在" -ForegroundColor Green
} else {
    Write-Host "[ERROR] .env 文件不存在！" -ForegroundColor Red
    Write-Host "请复制 .env.example 并配置" -ForegroundColor Yellow
    exit 1
}

# 检查关键依赖
Write-Host ""
Write-Host "检查依赖..." -ForegroundColor Cyan

$modules = @("fastapi", "uvicorn", "pydantic", "jwt", "cryptography")
$allInstalled = $true

foreach ($module in $modules) {
    try {
        Import-Module $module -ErrorAction Stop
        Write-Host "  [OK] $module" -ForegroundColor Green
    } catch {
        Write-Host "  [MISSING] $module" -ForegroundColor Red
        $allInstalled = $false
    }
}

if (-not $allInstalled) {
    Write-Host ""
    Write-Host "请运行：pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# 显示配置信息
Write-Host ""
Write-Host "配置信息:" -ForegroundColor Cyan
$envContent = Get-Content ".env"
$apiHost = ($envContent | Where-Object { $_ -like "API_HOST=*" }) -replace "API_HOST="
$apiPort = ($envContent | Where-Object { $_ -like "API_PORT=*" }) -replace "API_PORT="
$auth0Domain = ($envContent | Where-Object { $_ -like "AUTH0_DOMAIN=*" }) -replace "AUTH0_DOMAIN="
$jwtEnabled = ($envContent | Where-Object { $_ -like "JWT_ENABLED=*" }) -replace "JWT_ENABLED="

Write-Host "  API 地址：http://$apiHost:$apiPort" -ForegroundColor White
Write-Host "  Auth0: $auth0Domain" -ForegroundColor White
Write-Host "  JWT 认证：$jwtEnabled" -ForegroundColor White

# 启动服务
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   启动服务..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 使用 uvicorn 启动
uvicorn main:app --host $apiHost --port $apiPort --reload
