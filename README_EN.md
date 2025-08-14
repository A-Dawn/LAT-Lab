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

LAT-Lab is a powerful, modern personal blog system with a front-end and back-end separation design, providing complete content management, user systems, plugin extensions, and development tool support. The system is not only suitable for personal blog setup but also provides developers with powerful secondary development capabilities.

### 🏷️ Version Information
- **Current Version**: v1.0.1
- **Release Date**: 2025-08-15
- **Python**: 3.8+
- **Node.js**: 14+
- **Database**: SQLite/MySQL

For detailed changelog, please see [CHANGELOG.md](./Docs/CHANGELOG_EN.md)

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
- **Multi-level Comments**: Support for unlimited nested comment replies
- **Comment Management**: Administrators can moderate and delete comments
- **Real-time Updates**: New comments display in real-time
- **Anti-spam**: Built-in anti-spam comment mechanism

### 🔌 Plugin Extension System
- **Plugin Architecture**: Extensible plugin system
- **Plugin Marketplace**: Built-in plugin marketplace with one-click installation ([LAT-Lab-marketplace](https://github.com/A-Dawn/LAT-Lab-marketplace))
- **Custom Components**: Support for front-end custom widgets
- **Dynamic Loading**: Plugin hot-loading without restart
- **Configuration Management**: Independent plugin configuration system
- **Open Source Plugins**: Plugin ecosystem uses MIT license, fully open source

### 🛠️ Development Tools System
- **Visual Editing**: Real-time page editing and preview
- **Style Debugging**: CSS variable real-time adjustment tools
- **Text Editing**: Batch text content editing
- **Layout Tools**: Responsive layout visual adjustment
- **Code Export**: Export modified content as code
- **Change History**: Complete modification history tracking
- **Multi-page Support**: Support for editing 15 different page types

### 🔒 Security Protection System
- **Error Handling**: Global secure error handling to prevent information leakage
- **Sensitive Information Filtering**: Automatic filtering of passwords, keys, and other sensitive information
- **Rate Limiting**: Multi-tier rate limiting protection
- **Security Decorators**: Secure wrappers for database, file, and network operations
- **Environment Adaptation**: Differentiated security strategies for development/production environments

---

## 🏗️ Architecture

### Backend Architecture
FastAPI-based backend with SQLAlchemy ORM, JWT authentication, and robust security features.

### Frontend Architecture
Vue.js 3-based frontend with modern component architecture and responsive design.

---

## ⚡ Quick Start

### Environment Requirements
Ensure your system meets the following requirements:
- Python 3.8 or higher
- Node.js 14 or higher
- MySQL 8.0+ (optional, SQLite used by default)
- Git (for cloning code)

### Method 1: Traditional Installation (Recommended for Development)

#### 1. Clone Project
```bash
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab
```

#### 2. Backend Configuration
```bash
# Enter backend directory
cd backend

# Copy and edit environment configuration
cp ../env.example .env
# Edit .env file, set necessary configuration items

# Create virtual environment and install dependencies
python scripts/setup_env.py

# Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Initialize database
mkdir -p data
python scripts/run_migrations.py run

# Create user (-a parameter for administrator) 
python scripts/create_user.py
# Start backend service
python -m src.lat_lab.main
```

#### 3. Frontend Configuration
```bash
# Open new terminal, enter frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### 4. Access System
- **Frontend Interface**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (development environment)
- **Admin Panel**: http://localhost:5173/admin

### Method 2: Docker Deployment (Recommended for Production)

#### 1. Prepare Configuration
```bash
# Clone project
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab

# Copy and edit environment configuration
cp env.example .env
# Modify database password and other configurations as needed
```

#### 2. Build and Start Services
```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# Initialize database (first deployment)
docker-compose exec backend python scripts/run_migrations.py run
docker-compose exec backend python -m src.lat_lab.init_examples
docker-compose exec backend python scripts/init_db.py
```

#### 3. Access System
- **Frontend Interface**: http://localhost (port 80)
- **Backend API**: http://localhost:45609
- **Admin Panel**: http://localhost/admin

### ⚠️ Production Deployment Notes

When deploying frontend code to production environment:

1. **Build for Production**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Configure File Location**:
   - Built files will be in `frontend/dist/` directory
   - You need to configure your web server (Nginx, Apache, etc.) to serve these static files
   - Point your domain/subdomain to the `dist` directory
   - Ensure API requests are properly proxied to your backend server

3. **Example Nginx Configuration**:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       # Serve frontend static files
       location / {
           root /path/to/LAT-Lab/frontend/dist;
           index index.html;
           try_files $uri $uri/ /index.html;
       }
       
       # Proxy API requests to backend
       location /api/ {
           proxy_pass http://your-backend-server:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

> **Important**: Never use `npm run dev` in production! Always use `npm run build` and serve the built files.

---

## 🏗️ Project Structure

```
LAT-Lab/
├── backend/                   # Backend service
│   ├── src/lat_lab/          # Application core code
│   ├── scripts/              # Management scripts
│   ├── data/                 # Data storage
│   ├── uploads/              # Upload files
│   ├── plugins/              # Installed plugins
│   └── plugin_examples/      # Example plugins
├── frontend/                 # Frontend application
│   ├── src/                  # Vue.js source code
│   ├── public/               # Static assets
│   └── package.json          # Dependency configuration
├── Docs/                     # Project documentation
├── docker-compose.yml        # Docker configuration
├── env.example               # Environment variable example
└── README.md                 # Project description
```

---

## 📚 Documentation

### Core Documentation
- 📖 **Project Overview**: The file you are reading
- 📝 **Changelog**: [CHANGELOG.md](./Docs/CHANGELOG_EN.md) - Version update records
- 🔐 **Security Policy**: [SECURITY.md](./Docs/SECURITY_EN.md) - Security reporting guidelines

### Contributing Related
- 🤝 **Contributing Guide**: [CONTRIBUTORS.md](./Docs/CONTRIBUTORS_EN.md) - How to participate in project contributions
- 📄 **Contributor Agreement**: [CONTRIBUTOR_LICENSE_AGREEMENT.md](./Docs/CONTRIBUTOR_LICENSE_AGREEMENT_EN.md) - Contributor license agreement
- 🏆 **Security Contributors**: [SECURITY_CONTRIBUTORS.md](./Docs/SECURITY_CONTRIBUTORS_EN.md) - Security researcher list

### License Related
- 📜 **License Mapping**: [LICENSE-MAPPING.md](./Docs/LICENSE-MAPPING_EN.md) - Detailed license description
- 🔍 **Chinese Documentation**: Each document provides a corresponding Chinese version (filename without _EN suffix)

---

## 🤝 Contributing

⚠️ **Important Notice**: This project uses a hybrid licensing strategy. Plugins and development tools use MIT license, core code contributions require signing the [Contributor License Agreement](./Docs/CONTRIBUTOR_LICENSE_AGREEMENT_EN.md)

### Quick Participation Methods

#### 🆓 Contributions Without CLA
- 🐛 **Bug Reports** - Discover and report issues
- 💡 **Feature Suggestions** - Propose new feature ideas
- 🔒 **Security Vulnerabilities** - Responsible disclosure (see [Security Policy](./Docs/SECURITY_EN.md))
- 💬 **Discussion Participation** - Exchange ideas in Issues and Discussions

#### 📝 Contributions Requiring CLA  
- 🔧 **Code Submissions** - Feature development, bug fixes
- 📖 **Documentation Improvements** - Improve project documentation
- 🎨 **Interface Optimization** - UI/UX improvements

### Submission Process
1. Fork the project to your GitHub account
2. Create feature branch `git checkout -b feature/awesome-feature`
3. Commit changes `git commit -m 'feat: add awesome-feature'`
4. Push branch `git push origin feature/awesome-feature`
5. Create Pull Request
6. Sign CLA (if required)

For detailed contribution guidelines, please see [CONTRIBUTORS.md](./Docs/CONTRIBUTORS_EN.md)

---

## 🛡️ Security Policy

We take LAT-Lab's security very seriously and welcome security researchers to report vulnerabilities:

- 🔒 **Security Policy**: [SECURITY.md](./Docs/SECURITY_EN.md) - Detailed security reporting guidelines
- 🏆 **Security Contributors**: [SECURITY_CONTRIBUTORS.md](./Docs/SECURITY_CONTRIBUTORS_EN.md) - Security researcher list
- 📧 **Security Email**: security@luminarc.tech - Private security issue reporting
- ⚡ **Response Time**: Confirmation within 24 hours, active cooperation in fixes

---

## 📞 Support & Feedback

### Getting Help
- 📖 **Documentation**: Check [Docs](./Docs/) directory for detailed information
- 🐛 **Issue Feedback**: [GitHub Issues](https://github.com/A-Dawn/LAT-Lab/issues)
- 💬 **Discussion**: [GitHub Discussions](https://github.com/A-Dawn/LAT-Lab/discussions)
- 📧 **Email Contact**: contact@luminarc.tech

### Frequently Asked Questions
- **Q: How to modify the default admin account?**  
  A: Running `python scripts/init_db.py` creates a default admin account (admin/admin123), it's recommended to immediately change the password in the admin panel.

- **Q: How to configure email service?**  
  A: Configure SMTP server information in the `.env` file, supports most email service providers.

- **Q: Can I customize themes?**  
  A: Yes, you can customize styles through the development tools system or directly modify frontend source code.

---

## 📜 License

**This project uses a hybrid licensing strategy with different licenses for different components.** 

### 📋 License Distribution
- 🔒 **Core Business Code** (Proprietary License): Backend core, frontend core, configuration files
- 🆓 **Open Source Components** (MIT License): Plugin system, development tools, common components, deployment scripts

### 📋 Usage Terms
- ✅ **Personal Learning**: Fork allowed for personal learning and research
- ✅ **Plugin Development**: Free to develop and distribute plugins based on the open source plugin system
- ✅ **Tool Usage**: Development tools can be freely used and modified
- ❌ **Core Commercial Use**: Core business code cannot be used commercially without authorization

For detailed license description, please see [LICENSE-MAPPING.md](./Docs/LICENSE-MAPPING_EN.md)

### 📞 Commercial Licensing
For commercial use authorization of core code, please contact: `contact@luminarc.tech`

---

## 🙏 Acknowledgments

Thanks to the following open source projects for their support:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python Web framework
- [Vue.js](https://vuejs.org/) - Progressive JavaScript framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit
- [Element Plus](https://element-plus.org/) - Vue.js component library

Special thanks to all contributors and users for their support!

---

<div align="center">

**🌟 If this project helps you, please give it a Star ⭐**

Made with ❤️ by [Dawn_ARC](https://github.com/A-Dawn)

</div> 