#!/bin/bash

# LAT-Lab 跨平台部署脚本 (Linux/macOS)
# 支持 Docker 部署和传统安装部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查系统要求
check_requirements() {
    log_info "检查系统要求..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "检测到 Linux 系统"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "检测到 macOS 系统"
    else
        log_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
    
    # 检查 Docker
    if command -v docker &> /dev/null; then
        log_success "Docker 已安装"
        DOCKER_VERSION=$(docker --version)
        log_info "Docker 版本: $DOCKER_VERSION"
    else
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    # 检查 Docker Compose
    if command -v docker-compose &> /dev/null; then
        log_success "Docker Compose 已安装"
        COMPOSE_VERSION=$(docker-compose --version)
        log_info "Docker Compose 版本: $COMPOSE_VERSION"
    else
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    # 检查可用内存
    if command -v free &> /dev/null; then
        MEMORY_KB=$(free | awk '/^Mem:/{print $2}')
        MEMORY_GB=$((MEMORY_KB / 1024 / 1024))
        if [ $MEMORY_GB -lt 4 ]; then
            log_warning "可用内存不足 4GB (当前: ${MEMORY_GB}GB)，可能影响性能"
        else
            log_success "内存检查通过 (${MEMORY_GB}GB)"
        fi
    fi
    
    # 检查磁盘空间
    DISK_SPACE=$(df . | awk 'NR==2 {print $4}')
    DISK_SPACE_GB=$((DISK_SPACE / 1024 / 1024))
    if [ $DISK_SPACE_GB -lt 10 ]; then
        log_warning "可用磁盘空间不足 10GB (当前: ${DISK_SPACE_GB}GB)"
    else
        log_success "磁盘空间检查通过 (${DISK_SPACE_GB}GB)"
    fi
}

# 配置环境变量
setup_environment() {
    log_info "配置环境变量..."
    
    if [ ! -f .env ]; then
        if [ -f docker.env.example ]; then
            log_info "复制 Docker 环境配置模板..."
            cp docker.env.example .env
            log_success "已创建 .env 文件，请编辑配置"
        else
            log_error "未找到环境配置模板文件"
            exit 1
        fi
    else
        log_info ".env 文件已存在"
    fi
    
    # 提示用户编辑配置
    log_warning "请编辑 .env 文件，设置以下关键配置："
    echo "  - MYSQL_ROOT_PASSWORD: MySQL root 密码"
    echo "  - MYSQL_USER: 数据库用户名"
    echo "  - MYSQL_PASSWORD: 数据库密码"
    echo "  - SECRET_KEY: JWT 密钥 (至少32字符)"
    echo "  - BASE_URL: 网站基础URL"
    echo "  - DEBUG: 调试模式 (生产环境设为False)"
    echo ""
    read -p "编辑完成后按 Enter 继续..."
}

# Docker 部署
deploy_docker() {
    log_info "开始 Docker 部署..."
    
    # 构建并启动服务
    log_info "构建并启动 Docker 服务..."
    docker-compose up -d --build
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    log_info "检查服务状态..."
    docker-compose ps
    
    # 初始化数据库
    log_info "初始化数据库..."
    docker-compose exec -T backend python scripts/run_migrations.py
    docker-compose exec -T backend python scripts/init_db.py
    
    log_success "Docker 部署完成！"
    log_info "访问地址："
    log_info "  - 前端界面: http://localhost"
    log_info "  - 后端API: http://localhost:8000"
    log_info "  - 管理后台: http://localhost/admin"
    log_info "  - 默认管理员: admin / admin123"
}

# 传统安装部署
deploy_traditional() {
    log_info "开始传统安装部署..."
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装，请先安装 Python 3.8+"
        exit 1
    fi
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装，请先安装 Node.js 14+"
        exit 1
    fi
    
    # 检查 MySQL
    if ! command -v mysql &> /dev/null; then
        log_error "MySQL 未安装，请先安装 MySQL 8.0+"
        exit 1
    fi
    
    log_info "安装后端依赖..."
    cd backend
    pip install -e .
    cd ..
    
    log_info "安装前端依赖..."
    cd frontend
    npm install
    cd ..
    
    log_info "构建前端..."
    cd frontend
    npm run build
    cd ..
    
    log_success "传统安装部署完成！"
    log_info "请手动启动服务："
    log_info "  - 后端: cd backend && python -m src.lat_lab.main"
    log_info "  - 前端: 配置 Web 服务器指向 frontend/dist 目录"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose down
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    docker-compose restart
    log_success "服务已重启"
}

# 查看日志
view_logs() {
    log_info "查看服务日志..."
    docker-compose logs -f
}

# 清理服务
clean_services() {
    log_warning "这将删除所有容器和数据，确定继续吗？(y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "清理服务..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        log_success "服务已清理"
    else
        log_info "取消清理操作"
    fi
}

# 显示帮助信息
show_help() {
    echo "LAT-Lab 跨平台部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start          启动 Docker 部署 (推荐)"
    echo "  traditional    传统安装部署"
    echo "  stop           停止服务"
    echo "  restart        重启服务"
    echo "  logs           查看日志"
    echo "  clean          清理服务 (删除所有数据)"
    echo "  help           显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start        # 启动 Docker 部署"
    echo "  $0 traditional  # 传统安装部署"
    echo "  $0 stop         # 停止服务"
}

# 主函数
main() {
    case "${1:-start}" in
        "start")
            check_requirements
            setup_environment
            deploy_docker
            ;;
        "traditional")
            check_requirements
            setup_environment
            deploy_traditional
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "logs")
            view_logs
            ;;
        "clean")
            clean_services
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 