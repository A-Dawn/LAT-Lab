# LAT-Lab Frequently Asked Questions (FAQ)

This document collects common questions and answers during the use of the LAT-Lab project.

---

## 🚀 Deployment Related

### Q: How to modify the default administrator account?
**A**: Running `python scripts/init_db.py` will create a default administrator account (admin/admin123). It's recommended to change the password immediately in the admin panel.

### Q: How to configure email service?
**A**: Configure SMTP server information in the `.env` file, supporting most email service providers. For detailed configuration, please refer to [Email Configuration Guide](./MAIL_CONFIG_EN.md).

### Q: What to do when ports are occupied during Docker deployment?
**A**: You can resolve this in the following ways:
1. Modify port mappings in `docker-compose.yml`
2. Use `netstat -tulpn | grep :port_number` to view occupying processes
3. Use `sudo kill -9 <PID>` to kill occupying processes

### Q: What should be paid attention to in production environment deployment?
**A**: When deploying to production environment:
1. Never use `npm run dev`, must use `npm run build`
2. Configure HTTPS certificates
3. Set strong passwords and secure SECRET_KEY
4. Configure firewall and access control
5. Regular data backup

---

## 🔧 Feature Usage

### Q: Can themes be customized?
**A**: You can customize styles through the development tool system, or directly modify the frontend source code. For detailed instructions, please refer to [Theme Customization Guide](./THEME_CUSTOMIZATION_EN.md).

### Q: How to add new plugins?
**A**: For plugin development, please refer to [Plugin Development Guide](./PLUGIN_DEVELOPMENT_EN.md), or download ready-made plugins from the [Plugin Marketplace](https://github.com/A-Dawn/LAT-Lab-marketplace).

### Q: Which databases are supported?
**A**: SQLite is supported by default, MySQL 8.0+ is recommended for production environments. For database configuration, please refer to [Database Configuration Guide](./DATABASE_CONFIG_EN.md).

### Q: How to backup and restore data?
**A**: Data backup methods:
1. **Database backup**: `docker-compose exec db mysqldump -u root -p lat_lab_db > backup.sql`
2. **File backup**: `tar -czf uploads_backup.tar.gz uploads/`
3. **Complete backup**: Use `./deploy.sh backup` command

---

## 🐛 Troubleshooting

### Q: What to do when service startup fails?
**A**: Troubleshoot according to the following steps:
1. Check logs: `./deploy.sh logs` or `docker-compose logs`
2. Check environment configuration: Confirm `.env` file configuration is correct
3. Check port occupancy: Confirm required ports are not occupied
4. Check resources: Confirm sufficient memory and disk space

### Q: Frontend page displays abnormally?
**A**: Possible causes and solutions:
1. **API connection failure**: Check if backend service is running normally
2. **Static resource loading failure**: Check if frontend build is correct
3. **Browser compatibility**: Recommend using modern browsers

### Q: Email sending fails?
**A**: Email sending problem troubleshooting:
1. Check if SMTP configuration is correct
2. Confirm if email service provider supports SMTP
3. Check network connection and firewall settings
4. View email service logs

---

## 🔒 Security Related

### Q: How to improve system security?
**A**: Security recommendations:
1. Regularly update passwords and SECRET_KEY
2. Enable HTTPS
3. Configure firewall rules
4. Regular data backup
5. Monitor system logs
6. Update dependencies promptly

### Q: What to do when security vulnerabilities are found?
**A**: Please report security vulnerabilities through the following ways:
1. Send email to security@luminarc.tech
2. Create private Issue on GitHub
3. Describe vulnerability situation and reproduction steps in detail

---

## 📱 Mobile Support

### Q: Does it support mobile access?
**A**: Yes, LAT-Lab adopts responsive design and supports various mobile devices. It's recommended to use modern browsers on mobile devices for the best experience.

### Q: Are mobile features complete?
**A**: Mobile supports all core features, including:
- Article browsing and search
- User login and registration
- Comment publishing and replies
- Admin panel operations

---

## 🔌 Plugin Development

### Q: How to develop custom plugins?
**A**: Plugin development process:
1. Refer to [Plugin Development Guide](./PLUGIN_DEVELOPMENT_EN.md)
2. Use plugin template to create project
3. Implement plugin functionality
4. Test and debug
5. Package and publish

### Q: What skills are needed for plugin development?
**A**: Plugin development requires:
- Basic Python programming knowledge
- Understanding of FastAPI framework
- Familiarity with HTML/CSS/JavaScript
- Understanding of Vue.js component development

---

## 📊 Performance Optimization

### Q: How to improve system performance?
**A**: Performance optimization suggestions:
1. Use CDN to accelerate static resources
2. Configure database indexes
3. Enable caching mechanisms
4. Optimize images and media files
5. Use load balancing

### Q: Does it support high concurrency access?
**A**: LAT-Lab adopts asynchronous architecture and supports high concurrency access. It's recommended to use in production environment:
- Multi-instance deployment
- Load balancing
- Database read-write separation
- Caching strategies

---

## 🌐 Internationalization

### Q: Does it support multiple languages?
**A**: Currently supports Chinese and English, more language support is under development. For adding new languages, please refer to [Internationalization Guide](./I18N_GUIDE_EN.md).

### Q: How to switch languages?
**A**: Language switching methods:
1. Select language in user settings
2. Specify language through URL parameters
3. Automatically select based on browser language

---

## 📞 Getting Help

If this document doesn't solve your problem, you can get help through the following ways:

1. **View Documentation**: [Documentation Center](./README_EN.md)
2. **Search Issues**: Search in [GitHub Issues](https://github.com/A-Dawn/LAT-Lab/issues)
3. **Create Issue**: Create new Issue describing the problem
4. **Participate in Discussion**: Exchange ideas in [GitHub Discussions](https://github.com/A-Dawn/LAT-Lab/discussions)
5. **Email Contact**: contact@luminarc.tech

---

<div align="center">

**🌟 If this FAQ helps you, please give the project a Star ⭐**

Made with ❤️ by [Dawn_ARC](https://github.com/A-Dawn)

</div> 