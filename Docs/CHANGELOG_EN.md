# LAT-Lab Changelog

<div align="center">

**🌍 Languages / 语言选择**

[![简体中文](https://img.shields.io/badge/CHANGELOG-简体中文-blue.svg)](./CHANGELOG.md) [![English](https://img.shields.io/badge/CHANGELOG-English-red.svg)](./CHANGELOG_EN.md)

</div>

All notable changes to the LAT-Lab project will be documented in this file.

## [v1.0.1] - 2025-08-15

### 🔒 Major Security System Updates
- **Username Validation System**: New comprehensive username validation tool with 4 categories of prohibited usernames (administrative, system, technical, and inappropriate terms)
- **Security Error Handling Framework**: New security error handling system to prevent sensitive information leakage and provide unified error handling standards
- **Format Validation Enhancement**: Username length limits (3-32 characters), character type restrictions (alphanumeric and underscores), underscore rule checking
- **Security Protection**: Prevents malicious registration and system attacks, enhances overall system security

### 📧 Email System Optimization
- **Smart Connection Fallback**: Automatically adapts to different email service providers' connection methods, supports SSL/TLS auto-switching
- **Connection Failure Retry**: Automatically tries SSL as an alternative if standard connection fails
- **Email Type Smart Detection**: Optimizes connection parameters for different email providers like 163, Gmail, etc.
- **System Stability Improvement**: Increases email delivery success rate, supports more email service providers

### ⚙️ Configuration System Optimization
- **Docker Environment Adaptation**: Optimizes default configurations for containerized deployment, changes MySQL host default to "db"
- **Verification Email Resend Limits**: New rate limiting configuration for verification email resending to prevent email abuse
- **Email Configuration Environment Variables**: Email TLS/SSL configuration supports environment variables, improves configuration flexibility
- **BASE_URL Optimization**: Removes hardcoded port numbers, improves cross-environment compatibility

### 🐳 Docker Deployment System Major Upgrade
- **Complete Health Check System**: Database and backend service health monitoring, automatic restart of failed services
- **Resource Limits and Reservations**: Production-level resource configuration management, CPU and memory limit configuration
- **Comprehensive Environment Variable Support**: All key configurations support environment variables, improves deployment flexibility
- **Service Dependency Optimization**: Waits for database health before starting backend services
- **Cross-platform Deployment Scripts**: New Linux/macOS (deploy.sh) and Windows PowerShell (deploy.ps1) deployment scripts

### 🧪 Testing System Enhancement
- **Test Configuration Management**: New unified test environment configuration management file (test_config.py)
- **Environment Variable Support**: Fixes hardcoded API address issues in all test files
- **Configuration Validation**: Automatically validates test configuration effectiveness, supports different test environments
- **Flexible URL Building**: Dynamically builds test API addresses, improves test flexibility

### 🌐 Frontend Feature Updates
- **Login System Refactoring**: Supports both email and username login methods, optimizes login experience
- **Email Verification Status Handling**: Checks email verification status after login, provides clear status notifications
- **API Service Optimization**: Removes hardcoded addresses, simplifies response interceptors, supports guest mode
- **Theme System Enhancement**: Docker production environment theme support, development tools style loader integration
- **Error Handling Optimization**: More user-friendly error messages, removes complex redirect logic

### 📚 Documentation System Updates
- **Changelog Enhancement**: Bilingual version update records in Chinese and English, detailed version change descriptions
- **Deployment Guide Enhancement**: Cross-platform deployment script explanations, Docker environment configuration details
- **Environment Variable Configuration Templates**: Provides complete environment variable configuration examples
- **Troubleshooting Guide**: Common problem solutions and deployment recommendations

### 🔧 Development Tools Enhancement
- **Change Saving System**: Saves current page changes, supports multi-page data management
- **Server Synchronization**: Development tool configurations can be saved to server, supports team collaboration
- **Code Export Optimization**: Generates exportable code, supports CSS, JavaScript, and JSON formats

### 📊 Code Statistics
- **New Files**: 10 core files including security tools, deployment scripts, test configurations, etc.
- **Modified Files**: 13 main files covering backend, frontend, configuration, testing, and other modules
- **Code Lines**: Approximately 800 new lines, 300 modified lines, net increase of about 750 lines of code

---

## [v1.0.0] - 2025-08-14

### Initial Release
- 🚀 First public release of LAT-Lab
- 📝 Complete content management system
- 👥 User management system
- 💬 Comment interaction system
- 🔌 Plugin extension system
- 🛠️ Development tools system
- 🔒 Security protection system
- 📂 File management system
- 📊 Data statistics system 