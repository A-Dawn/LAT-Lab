# LAT-Lab v1.0.0 - Modern Blog System

<div align="center">

**🌍 Languages / 语言选择**

[![简体中文](https://img.shields.io/badge/README-简体中文-blue.svg)](./README.md) [![English](https://img.shields.io/badge/README-English-red.svg)](./README_EN.md)

---

</div>

<div align="center">

![LAT-Lab Logo](https://img.shields.io/badge/LAT--Lab-v1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red.svg)
![License](https://img.shields.io/badge/License-Hybrid-orange.svg)

**A modern personal blog system built with FastAPI + Vue.js**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Dev Tools](#-dev-tools) • [Deployment](#-deployment) • [Contributing](#-contributing) • [Security](#️-security) • [API Docs](#-api-docs)

</div>

---

## 📖 Project Overview

LAT-Lab is a powerful, modern personal blog system with a front-end and back-end separation design, providing complete content management, user systems, plugin extensions, and development tool support. The system is not only suitable for personal blog setup but also provides developers with powerful secondary development capabilities.

### 🏷️ Version Information
- **Current Version**: v1.0.0
- **Release Date**: 2025-08-14
- **Python**: 3.8+
- **Node.js**: 14+
- **Database**: SQLite/MySQL

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

### 🛠️ Development Tools System (v1.0.0 New)
- **Visual Editing**: Real-time page editing and preview
- **Style Debugging**: CSS variable real-time adjustment tools
- **Text Editing**: Batch text content editing
- **Layout Tools**: Responsive layout visual adjustment
- **Code Export**: Export modified content as code
- **Change History**: Complete modification history tracking
- **Multi-page Support**: Support for editing 15 different page types

### 🔒 Security Protection System (v1.0.0 Enhanced)
- **Error Handling**: Global secure error handling to prevent information leakage
- **Sensitive Information Filtering**: Automatic filtering of passwords, keys, and other sensitive information
- **Rate Limiting**: Multi-tier rate limiting protection
- **Security Decorators**: Secure wrappers for database, file, and network operations
- **Environment Adaptation**: Differentiated security strategies for development/production environments

### 📂 File Management System
- **Multi-file Upload**: Support for batch file uploads
- **Image Processing**: Automatic image compression and format conversion
- **File Classification**: Automatic categorized storage by type
- **Security Validation**: File type and size restrictions

### 📊 Data Statistics System
- **Access Statistics**: Article view count statistics
- **User Behavior**: User activity analysis
- **Content Analysis**: Article publishing trends
- **System Monitoring**: System operation status monitoring

---

## 🏗️ Architecture

### Backend Architecture
```
FastAPI (Web Framework)
├── SQLAlchemy (ORM)
├── Alembic (Database Migration)
├── Pydantic (Data Validation)
├── JWT (Authentication)
├── Passlib (Password Encryption)
├── Python-multipart (File Handling)
└── Uvicorn (ASGI Server)
```

### Frontend Architecture
```
Vue.js 3 (Frontend Framework)
├── Vue Router (Route Management)
├── Vuex (State Management)
├── Composition API (Composition API)
├── Axios (HTTP Client)
├── Marked (Markdown Rendering)
├── Highlight.js (Code Highlighting)
└── DOMPurify (XSS Protection)
```

### Database Model
```
Database Design
├── users (User Table)
├── articles (Article Table)
├── categories (Category Table)
├── tags (Tag Table)
├── comments (Comment Table)
├── plugins (Plugin Table)
├── system_configs (System Configuration Table)
└── article_tags (Article-Tag Association Table)
```

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
docker-compose exec backend python scripts/copy_config.py
docker-compose exec backend python scripts/run_migrations.py run
docker-compose exec backend python -m src.lat_lab.init_examples
docker-compose exec backend python scripts/init_db.py
```

> ⚠️ **Important Notes**：
> - MySQL 8.0 configuration uses `mysql_native_password` authentication plugin for compatibility
> - The order of initialization commands is important, please execute strictly in the above order
> - If you encounter bcrypt warning messages, you can safely ignore them, just make sure you see the "Admin user created successfully" message

#### 3. Access System
- **Frontend Interface**: http://localhost (port 80)
- **Backend API**: http://localhost:45609
- **Admin Panel**: http://localhost/admin

---

## 🛠️ Dev Tools

LAT-Lab v1.0.0 introduces a powerful frontend development tool system that allows you to perform visual development and debugging directly in the browser.

### 🎨 Development Tool Features

#### 1. Page Selector
- Support for real-time editing of 15 different page types
- iframe embedded preview, truly simulating user access
- Cross-domain message communication for instant synchronization

#### 2. Style Editor
- Real-time CSS variable adjustment
- Integrated color picker
- Numeric slider controls
- Change preview and one-click undo

#### 3. Text Editor
- Batch editing of page text content
- Precise element positioning and highlighting
- Multi-language content support
- Real-time preview of modifications

#### 4. Layout Editor
- Visual adjustment of element dimensions
- Intuitive editing of position properties
- Responsive layout support
- Grid/Flexbox layout tools

#### 5. Code Exporter
- CSS variable modification export
- Vue component template generation
- Automatic configuration file generation
- Complete project file export

#### 6. Change History
- Detailed operation timeline
- Before and after comparison display
- One-click rollback to any historical point
- Batch operation undo support

### 🔧 Using Development Tools

#### Enable Development Tools
Development tools are only available in development environment, ensure you start the frontend service with `npm run dev`.

#### Access Development Tools
1. Log in as administrator
2. Enter admin panel (`/admin`)
3. Find "Development Tools" option in the left menu
4. Start your visual editing journey!

#### Workflow
```
Select Page → Real-time Edit → Preview Effects → Export Code → Apply to Project
```

---

## 🔧 Configuration

### Environment Variables Configuration

#### Basic Configuration
```env
# Application Configuration
DEBUG=False                    # Set to False for production
HOST=0.0.0.0
PORT=8000

# Security Configuration
SECRET_KEY=your_secret_key_here  # Please change to random key

# Database Configuration
DB_TYPE=sqlite                 # sqlite or mysql
MYSQL_USER=lat_lab_user
MYSQL_PASSWORD=your_db_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=lat_lab_db
```

#### Email Service Configuration
```env
# Email Settings (for user registration verification)
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
MAIL_FROM=your-email@example.com
MAIL_TLS=True
MAIL_SSL=False
```

#### Rate Limiting Configuration
```env
# Rate Limiting (prevent malicious requests)
RATE_LIMIT_ENABLED=True
RATE_LIMIT_LOGIN_REQUESTS=20      # Login max 20 times per minute
RATE_LIMIT_API_REQUESTS=200       # API max 200 times per minute
RATE_LIMIT_UPLOAD_REQUESTS=20     # Upload max 20 times per minute
RATE_LIMIT_PLUGIN_REQUESTS=100    # Plugin execution max 100 times per minute
```

#### Plugin Marketplace Configuration
```env
# Plugin Marketplace Data Source
PLUGIN_MARKETPLACE_SOURCE=local        # local or git
PLUGIN_MARKETPLACE_GIT_REPO=           # Git repository URL
PLUGIN_MARKETPLACE_GIT_BRANCH=main     # Git branch
PLUGIN_MARKETPLACE_GIT_TOKEN=          # Git access token
```

### Database Configuration

#### SQLite (Default)
No additional configuration required, the system will automatically create database files in the `backend/data/` directory.

#### MySQL
1. Create database and user:
```sql
CREATE DATABASE lat_lab_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'lat_lab_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON lat_lab_db.* TO 'lat_lab_user'@'localhost';
FLUSH PRIVILEGES;
```

2. Update database configuration in `.env` file

### Plugin Configuration

#### Plugin Directory Structure
```
backend/
├── plugins/                   # Installed plugins
├── plugin_examples/           # Example plugins
└── data/
    └── marketplace_config.json  # Plugin marketplace configuration
```

#### Creating Custom Plugins
Refer to example plugins in the `backend/plugin_examples/` directory to create your custom plugins.

## 🏗️ Project Structure

```
LAT-Lab/
├── backend/                   # Backend service
│   ├── src/
│   │   └── lat_lab/
│   │       ├── api/           # API interfaces
│   │       ├── core/          # Core configuration
│   │       ├── crud/          # Database operations
│   │       ├── models/        # Data models
│   │       ├── schemas/       # Data schemas
│   │       ├── services/      # Service layer
│   │       ├── utils/         # Utility functions
│   │       └── main.py        # Application entry
│   ├── scripts/               # Management scripts
│   ├── data/                  # Data storage
│   ├── uploads/               # Upload files
│   ├── plugins/               # Installed plugins
│   ├── plugin_examples/       # Example plugins
│   └── pyproject.toml         # Project configuration
├── frontend/                  # Frontend application
│   ├── src/
│   │   ├── components/        # Vue components
│   │   │   └── dev-tools/     # Development tool components
│   │   ├── views/             # Page views
│   │   │   └── admin/         # Admin panel
│   │   ├── store/             # Vuex state management
│   │   ├── services/          # API services
│   │   ├── router/            # Route configuration
│   │   └── App.vue            # Root component
│   ├── public/                # Static assets
│   └── package.json           # Dependency configuration
├── docs/                      # Documentation
├── docker-compose.yml         # Docker configuration
├── env.example                # Environment variable example
└── README.md                  # Project description
```

---

## 🔐 Security Best Practices

### Production Environment Security Configuration

#### 1. Environment Variable Security
```env
# Must modify configuration items
SECRET_KEY=YOUR_RANDOM_SECRET_KEY_HERE
MYSQL_PASSWORD=YOUR_STRONG_DB_PASSWORD
DEBUG=False

# Email security configuration
MAIL_PASSWORD=YOUR_EMAIL_APP_PASSWORD
```

#### 2. Database Security
- Use strong passwords
- Regular data backup
- Limit database access permissions
- Enable SSL connections

#### 3. File Upload Security
- Limit file types and sizes
- Scan uploaded files
- Isolate storage of uploaded files

#### 4. Network Security
- Use HTTPS
- Configure firewall
- Enable rate limiting
- Regular dependency updates

### Security Features

#### 1. Error Handling
The system implements global secure error handling to ensure no sensitive internal error information is leaked to users.

#### 2. Sensitive Information Filtering
Automatically filters and hides the following types of sensitive information:
- Passwords (password, pwd, passwd)
- Keys (secret, token, key, api_key)
- Authentication information (access_token, refresh_token)

#### 3. Rate Limiting
Multi-tier rate limiting protection:
- Login attempt limiting
- API request frequency limiting
- File upload limiting
- Plugin execution limiting

---

## 🚀 Deployment Guide

### Production Environment Deployment (Docker)

#### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Deploy Application
```bash
# Clone project
git clone https://github.com/A-Dawn/LAT-Lab.git
cd LAT-Lab

# Configure environment variables
cp env.example .env
nano .env  # Edit configuration

# Build and start
docker-compose up -d

# Initialize database (first deployment)
docker-compose exec backend python scripts/copy_config.py
docker-compose exec backend python scripts/run_migrations.py run
docker-compose exec backend python -m src.lat_lab.init_examples
docker-compose exec backend python scripts/init_db.py
```

> ⚠️ **Important Notes**：
> - MySQL 8.0 configuration uses `mysql_native_password` authentication plugin for compatibility
> - The order of initialization commands is important, please execute strictly in the above order
> - If you encounter bcrypt warning messages, you can safely ignore them, just make sure you see the "Admin user created successfully" message

#### 3. Reverse Proxy Configuration (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend static files
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:45609;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # File upload
    location /uploads/ {
        proxy_pass http://localhost:45609;
        proxy_set_header Host $host;
        client_max_body_size 100M;
    }
}
```

### Performance Optimization

#### 1. Database Optimization
- Create appropriate indexes
- Regular analysis and query optimization
- Configure database connection pool

#### 2. Caching Strategy
- Redis cache hot data
- Static file CDN acceleration
- Browser cache configuration

#### 3. Monitoring and Logging
- Set up system monitoring
- Configure log rotation
- Performance metrics tracking

---

## 🧪 Development Guide

### Development Environment Setup

#### 1. Code Style
Backend uses Black + isort + mypy for code formatting and type checking:
```bash
# Install development dependencies
pip install -e ".[dev]"

# Code formatting
black src/
isort src/

# Type checking
mypy src/
```

#### 2. Testing
```bash
# Run tests
pytest

# Test coverage
pytest --cov=src
```

### Plugin Development

#### 1. Plugin Structure
```python
# plugin_info.json
{
    "id": "my_plugin",
    "name": "My Plugin",
    "version": "1.0.0",
    "description": "Plugin description",
    "author": "Author",
    "main": "main.py"
}

# main.py
def init_plugin():
    """Plugin initialization"""
    pass

def get_widget():
    """Get frontend component"""
    return {
        "name": "MyWidget",
        "component": "widget.vue"
    }
```

#### 2. Plugin API
Plugins can use the following APIs:
- Database operations
- User authentication
- File operations
- Email sending
- Cache operations

### Frontend Development

#### 1. Component Development
```vue
<template>
  <div class="my-component">
    <!-- Component content -->
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
// Component logic
</script>

<style scoped>
/* Component styles */
</style>
```

#### 2. State Management
Use Vuex to manage application state:
```javascript
// store/modules/myModule.js
const state = {
  // State definition
}

const mutations = {
  // Synchronous modifications
}

const actions = {
  // Asynchronous operations
}

const getters = {
  // Computed properties
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
```

---

## 🤝 Contributing

### Participation in Contribution

⚠️ **Important Notice**: This project uses a hybrid licensing strategy. Plugins and development tools use MIT license, core code contributions require signing the [Contributor License Agreement](./CONTRIBUTOR_LICENSE_AGREEMENT_EN.md)

We welcome the following forms of contribution:

#### 🆓 Contributions Without CLA
- 🐛 **Bug Reports** - Discover and report issues
- 💡 **Feature Suggestions** - Propose new feature ideas
- 🔒 **Security Vulnerabilities** - Responsible disclosure (see [Security Policy](./SECURITY.md))
- 💬 **Discussion Participation** - Exchange ideas in Issues and Discussions

#### 📝 Contributions Requiring CLA  
- 🔧 **Code Submissions** - Feature development, bug fixes
- 📖 **Documentation Improvements** - Improve project documentation
- 🎨 **Interface Optimization** - UI/UX improvements

> 💡 **Why CLA?** Due to the proprietary license, we need to clarify code copyright ownership to ensure the project's legal compliance.

### Submission Standards

#### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type Categories
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation updates
- `style`: Code formatting adjustments
- `refactor`: Code refactoring
- `test`: Test related
- `chore`: Other modifications

#### Example
```
feat(auth): add email verification feature

- Implement email verification token generation
- Add verification email sending
- Improve user registration process

Closes #123
```

### Development Process

#### 🔧 Code Contribution Process
1. **Read CLA** - Review [Contributor License Agreement](./CONTRIBUTOR_LICENSE_AGREEMENT_EN.md)
2. **Fork Project** to your GitHub account  
3. **Create Branch** `git checkout -b feature/awesome-feature`
4. **Develop Feature** - Follow code standards for development
5. **Commit Changes** `git commit -m 'feat: add awesome-feature'`
6. **Push Branch** `git push origin feature/awesome-feature`
7. **Create Pull Request** 
8. **Sign CLA** - Confirm agreement to CLA terms in PR
9. **Code Review** - Wait for maintainer review
10. **Merge Code** - Merge after review approval

#### 🐛 Bug Report Process  
1. **Search Existing Issues** - Avoid duplicate reports
2. **Create New Issue** - Use bug report template
3. **Provide Details** - Reproduction steps, environment information, etc.
4. **Follow Up** - Assist in verifying fix results

> 📋 **CLA Signing**: Small code contributions (<50 lines) can be confirmed by commenting in PR, large contributions need to send email, see license agreement for details.

---

## 🛡️ Security Policy

We take LAT-Lab's security very seriously and welcome security researchers to report vulnerabilities:

- 🔒 **Security Policy**: [SECURITY.md](./SECURITY.md) - Detailed security reporting guidelines
- 🏆 **Security Contributors**: [SECURITY_CONTRIBUTORS.md](./SECURITY_CONTRIBUTORS.md) - Security researcher list
- 📧 **Security Email**: security@luminarc.tech - Private security issue reporting
- ⚡ **Response Time**: Confirmation within 24 hours, active cooperation in fixes

We commit to not taking legal action against good-faith security research and will permanently acknowledge security contributors in our list.

---

## 📞 Support & Feedback

### Getting Help

- 📖 **Documentation**: View detailed documentation for more information
- 🐛 **Issue Feedback**: [GitHub Issues](https://github.com/A-Dawn/LAT-Lab/issues)
- 💬 **Discussion**: [GitHub Discussions](https://github.com/A-Dawn/LAT-Lab/discussions)
- 📧 **Email Contact**: contact@luminarc.tech

### Frequently Asked Questions

#### Q: How to modify the default admin account?
A: Running `python scripts/init_db.py` creates a default admin account (admin/admin123), it's recommended to immediately change the password in the admin panel.

#### Q: How to configure email service?
A: Configure SMTP server information in the `.env` file, supports most email service providers.

#### Q: Can I customize themes?
A: Yes, you can customize styles through the development tools system or directly modify frontend source code.

#### Q: How to backup data?
A: Regularly backup the `backend/data/` directory and database files, or use database export commands.

#### Q: Does it support multiple languages?
A: The current version mainly supports Chinese, multi-language support is planned for future versions.

---

## 📜 License

**This project uses a hybrid licensing strategy with different licenses for different components.** See [LICENSE-MAPPING.md](./LICENSE-MAPPING.md) for detailed mapping.

### 📋 License Distribution

#### 🔒 **Core Business Code** (Proprietary License)
- **Backend Core**: User authentication, article management, database models, etc.
- **Frontend Core**: Admin dashboard, editors, user interfaces, etc.
- **Configuration Files**: Core configuration and routing system

#### 🆓 **Open Source Components** (MIT License)
- **Plugin System**: Complete plugin architecture and examples ([LAT-Lab-marketplace](https://github.com/A-Dawn/LAT-Lab-marketplace))
- **Development Tools**: Visual editors, style debugging tools, etc.
- **Common Components**: Theme switcher, toast notifications, utility functions, etc.
- **Deployment Scripts**: Docker configs, installation scripts, environment setup, etc.

### 📋 Usage Terms
- ✅ **Personal Learning**: Fork allowed for personal learning and research
- ✅ **Plugin Development**: Free to develop and distribute plugins based on the open source plugin system
- ✅ **Tool Usage**: Development tools can be freely used and modified
- ✅ **Bug Reports**: Welcome to report issues and suggestions  
- ✅ **Security Research**: Support responsible security vulnerability disclosure
- ❌ **Core Commercial Use**: Core business code cannot be used commercially without authorization
- ❌ **Core Distribution**: Cannot redistribute core business code or create complete derivative products

### 🤝 Contribution Methods

#### 🔓 **Open Source Component Contributions** (Recommended)
- **Plugin Development**: Contribute plugins directly to [LAT-Lab-marketplace](https://github.com/A-Dawn/LAT-Lab-marketplace)
- **Tool Improvements**: Submit improvements to development tools and common components
- **Documentation**: Help improve documentation for open source components

#### 🔒 **Core Code Contributions**
- Requires signing the [Contributor License Agreement](./CONTRIBUTOR_LICENSE_AGREEMENT_EN.md)
- For bug fixes and improvements to core functionality

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