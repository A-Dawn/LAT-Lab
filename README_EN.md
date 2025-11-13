# LAT-Lab v1.0.1 - Modern Blog System

<div align="center">

**🌍 Languages / 语言选择**

[![简体中文](https://img.shields.io/badge/README-简体中文-blue.svg)](./README.md) [![English](https://img.shields.io/badge/README-English-red.svg)](./README_EN.md)

---

</div>

<div align="center">

![LAT-Lab Logo](https://img.shields.io/badge/LAT--Lab-v1.0.1-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red.svg)
![License](https://img.shields.io/badge/License-Hybrid-orange.svg)

**A modern personal blog system built with FastAPI + Vue.js**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Documentation](#-documentation) • [Contributing](#-contributing) • [License](#-license)

</div>

---

## 📖 Project Overview

LAT-Lab is a powerful, modern personal blog system with a frontend-backend separation design, providing complete content management, user systems, plugin extensions, and development tool support. The system is not only suitable for personal blog setup but also provides developers with powerful secondary development capabilities.

### 🏷️ Version Information
- **Current Version**: v1.0.1
- **Release Date**: 2025-08-15
- **Python**: 3.8+
- **Node.js**: 14+
- **Database**: SQLite/MySQL

For detailed changelog, please see [CHANGELOG_EN.md](./Docs/CHANGELOG_EN.md)

---

## 🚀 Features

### 📝 Content Management System
- **Article Editor**: Built-in Markdown editor with real-time preview
- **Content Status**: Draft, published, and private article management
- **Categories & Tags**: Flexible categorization and tagging system
- **Visibility Control**: Public, private, and password-protected articles
- **Article Statistics**: View count, likes, and comment statistics
- **Article Pinning**: Pin important articles to the top
- **RSS Feeds**: Automatic RSS/Atom feed generation

### 👥 User Management System
- **Multi-role Management**: Three-tier permissions for guests, users, and administrators
- **User Authentication**: JWT token authentication, secure and reliable
- **Email Verification**: User registration email verification mechanism
- **User Profiles**: Avatar, bio, and personalized settings
- **Security Enhancement**: Login rate limiting and password encryption storage

### 💬 Comment Interaction System
- **Multi-level Comments**: Supports unlimited level comment replies
- **Comment Management**: Administrators can review and delete comments
- **Real-time Updates**: New comments display in real-time
- **Anti-spam**: Built-in anti-spam comment mechanism

### 🔌 Plugin Extension System
- **Plugin Architecture**: Extensible plugin system
- **Plugin Marketplace**: Built-in plugin marketplace with one-click installation ([LAT-Lab-marketplace](https://github.com/A-Dawn/LAT-Lab-marketplace))
- **Custom Components**: Supports frontend custom widgets
- **Dynamic Loading**: Plugin hot-loading, no restart required
- **Configuration Management**: Independent plugin configuration system
- **Open Source Plugins**: Plugin ecosystem uses MIT license, fully open source

### 🛠️ Development Tool System
- **Visual Editing**: Real-time page editing and preview
- **Style Debugging**: CSS variable real-time adjustment tools
- **Text Editing**: Batch text content editing
- **Layout Tools**: Responsive layout visual adjustment
- **Code Export**: Modified content exported as code
- **Change History**: Complete modification history tracking
- **Multi-page Support**: Supports editing of 15 different page types

### 🔒 Security Protection System
- **Error Handling**: Global security error handling, prevents information leakage
- **Sensitive Information Filtering**: Automatically filters passwords, keys, and other sensitive information
- **Rate Limiting**: Multi-level rate limiting protection
- **Security Decorators**: Database, file, network operation security wrappers
- **Environment Adaptation**: Development/production environment security policy differentiation
- **Username Validation**: Complete username validation system, prevents malicious registration and system attacks
- **Security Error Framework**: Unified error handling standards, prevents sensitive information leakage
- **Connection Security**: Email system intelligent connection degradation, supports SSL/TLS automatic switching

---

## 🏗️ Architecture

### Backend Architecture
FastAPI-based backend using SQLAlchemy ORM, JWT authentication, and powerful security features.

### Frontend Architecture
Vue.js 3-based frontend with modern component architecture and responsive design.

### Database Model
Relational database design including users, articles, categories, tags, comments, and other core tables with complete data relationships.

---

## 🚀 Quick Start

### 🚀 One-Click Deployment (Recommended)

We provide rapid deployment scripts that automatically detect the environment and guide you through deployment:

#### Linux/macOS
```bash
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab
chmod +x deploy.sh
cp docker.env.example .env
# Update .env with your configuration values
./deploy.sh start
# Optional: follow with `./deploy.sh logs` to monitor startup
```

#### Windows PowerShell
```powershell
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab
Copy-Item docker.env.example .env
# For traditional installs copy env.traditional.example instead
notepad .env
.\deploy.ps1 start
# Optional: run `.\deploy.ps1 logs` to monitor startup
```

#### Deployment Script Features
- **Cross-platform Support**: Automatically detects operating system type and provides appropriate deployment solutions
- **Environment Checking**: Automatically checks Docker, memory, disk space, and other system requirements
- **Health Monitoring**: Real-time container status monitoring with automatic restart of failed services
- **Smart Deployment**: Supports start, stop, restart, status viewing, log viewing, and other operations
- **Error Handling**: Comprehensive error handling and retry mechanisms, improving deployment success rate

### 📚 Detailed Deployment Guides
- **Cross-platform Deployment**: [DEPLOYMENT_GUIDE_EN.md](./Docs/DEPLOYMENT_GUIDE_EN.md) - Complete deployment script usage guide
- **Docker Deployment**: [DOCKER_DEPLOYMENT.md](./Docs/DOCKER_DEPLOYMENT.md) - Docker containerized deployment details
- **Traditional Installation**: [TRADITIONAL_INSTALLATION.md](./Docs/TRADITIONAL_INSTALLATION.md) - Development environment installation guide

---

## 🏗️ Project Structure

```
LAT-Lab/
├── backend/                   # Backend service
│   ├── src/lat_lab/          # Application core code
│   ├── scripts/              # Management scripts
│   ├── data/                 # Data storage
│   ├── uploads/              # Uploaded files
│   ├── plugins/              # Installed plugins
│   └── plugin_examples/      # Example plugins
├── frontend/                 # Frontend application
│   ├── src/                  # Vue.js source code
│   ├── public/               # Static resources
│   └── package.json          # Dependency configuration
├── Docs/                     # Project documentation
├── docker-compose.yml        # Docker configuration
├── docker.env.example        # Docker deployment environment template
├── env.traditional.example   # Traditional deployment environment template
├── deploy.sh                 # Linux/macOS cross-platform deployment script
├── deploy.ps1                # Windows PowerShell cross-platform deployment script
└── README.md                 # Project description
```

---

## 📚 Documentation

### 📚 Complete Documentation Center
- **[Documentation Center](./Docs/README_EN.md)** - View all project documents and detailed guides

### Core Documentation
- 📖 **Project Overview**: The file you're currently reading
- 📝 **Changelog**: [CHANGELOG_EN.md](./Docs/CHANGELOG_EN.md) - Version update records
- 🔐 **Security Policy**: [SECURITY_EN.md](./Docs/SECURITY_EN.md) - Security reporting guide

### Deployment Guides
- 🚀 **Quick Deployment**: [DEPLOYMENT_GUIDE_EN.md](./Docs/DEPLOYMENT_GUIDE_EN.md) - Cross-platform deployment script usage guide
- 🐳 **Docker Deployment**: [DOCKER_DEPLOYMENT.md](./Docs/DOCKER_DEPLOYMENT.md) - Docker containerized deployment details

### Contribution Related
- 🤝 **Contribution Guide**: [CONTRIBUTORS_EN.md](./Docs/CONTRIBUTORS_EN.md) - How to participate in project contribution
- 📄 **Contributor Agreement**: [CONTRIBUTOR_LICENSE_AGREEMENT_EN.md](./Docs/CONTRIBUTOR_LICENSE_AGREEMENT_EN.md) - Contributor license agreement
- 🏆 **Security Contributors**: [SECURITY_CONTRIBUTORS_EN.md](./Docs/SECURITY_CONTRIBUTORS_EN.md) - Security researcher list

### License Related
- 📜 **License Mapping**: [LICENSE-MAPPING_EN.md](./Docs/LICENSE-MAPPING_EN.md) - Detailed license description
- 🔍 **Chinese Documentation**: Each document provides a corresponding Chinese version (filename ends with _EN)

---

## 🤝 Contributing

⚠️ **Important Reminder**: This project adopts a hybrid licensing strategy. Plugins and development tools use MIT license, while core code contributions require signing the [Contributor License Agreement](./Docs/CONTRIBUTOR_LICENSE_AGREEMENT_EN.md)

### Quick Participation Methods

#### 🆓 Contributions Not Requiring CLA
- 🐛 **Bug Reports** - Find and report issues
- 💡 **Feature Suggestions** - Propose new feature ideas
- 🔒 **Security Vulnerabilities** - Responsible disclosure (see [Security Policy](./Docs/SECURITY_EN.md))
- 💬 **Discussion Participation** - Exchange ideas in Issues and Discussions

#### 📝 Contributions Requiring CLA
- 🔧 **Code Submissions** - Feature development, bug fixes
- 📖 **Documentation Improvements** - Improve project documentation
- 🎨 **Interface Optimization** - UI/UX improvements

### Submission Process
1. Fork the project to your GitHub account
2. Create a feature branch `git checkout -b feature/awesome-feature`
3. Commit changes `git commit -m 'feat: add awesome-feature'`
4. Push the branch `git push origin feature/awesome-feature`
5. Create a Pull Request
6. Sign the CLA (if required)

For detailed contribution guidelines, please see [CONTRIBUTORS_EN.md](./Docs/CONTRIBUTORS_EN.md)

---

## 🛡️ Security Policy

We take LAT-Lab security very seriously and welcome security researchers to report vulnerabilities:

- 🔒 **Security Policy**: [SECURITY_EN.md](./Docs/SECURITY_EN.md) - Detailed security reporting guide
- 🏆 **Security Contributors**: [SECURITY_CONTRIBUTORS_EN.md](./Docs/SECURITY_CONTRIBUTORS_EN.md) - Security researcher list
- 📧 **Security Email**: security@luminarc.tech - Private security issue reporting
- ⚡ **Response Time**: Confirmation within 24 hours, actively cooperate in fixes

---

## 📞 Support & Feedback

### Getting Help
- 📖 **Documentation**: Check [Docs](./Docs/) directory for detailed information
- 🐛 **Issue Feedback**: [GitHub Issues](https://github.com/A-Dawn/LAT-Lab/issues)
- 💬 **Discussion**: [GitHub Discussions](https://github.com/A-Dawn/LAT-Lab/discussions)
- 📧 **Email Contact**: contact@luminarc.tech

### Frequently Asked Questions
For FAQ answers, please see [FAQ_EN.md](./Docs/FAQ_EN.md) or [Documentation Center](./Docs/README_EN.md)

---

## 📜 License

**This project adopts a hybrid licensing strategy with different components using different licenses.**

### 📋 License Distribution
- 🔒 **Core Business Code** (Proprietary License): Backend core, frontend core, configuration files
- 🆓 **Open Source Components** (MIT License): Plugin system, development tools, common components, deployment scripts

### 📋 Terms of Use
- ✅ **Personal Learning**: Allows forking for personal learning and research
- ✅ **Plugin Development**: Freely develop and distribute plugins based on the open source plugin system
- ✅ **Tool Usage**: Development tools can be freely used and modified
- ❌ **Core Commercial Use**: Core business code cannot be used for commercial purposes without authorization

For detailed license information, please see [LICENSE-MAPPING_EN.md](./Docs/LICENSE-MAPPING_EN.md)

### 📞 Commercial Licensing
For commercial use authorization of core code, please contact: `contact@luminarc.tech`

---

## 🙏 Acknowledgments

Thanks to the support of the following open source projects:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Vue.js](https://vuejs.org/) - Progressive JavaScript framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit
- [Element Plus](https://element-plus.org/) - Vue.js component library

Special thanks to all contributors and users for their support!

---

<div align="center">

**🌟 If this project helps you, please give it a Star ⭐**

Made with ❤️ by [Dawn_ARC](https://github.com/A-Dawn)

</div>