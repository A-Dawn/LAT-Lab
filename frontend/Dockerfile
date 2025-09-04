# 构建阶段
FROM node:18 as build-stage
WORKDIR /app

# 接收构建参数
ARG VITE_API_BASE_URL=/api
ARG VITE_UPLOAD_URL=/uploads
ARG VITE_ENABLE_DEV_TOOLS=false

# 设置构建环境变量
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_UPLOAD_URL=$VITE_UPLOAD_URL
ENV VITE_ENABLE_DEV_TOOLS=$VITE_ENABLE_DEV_TOOLS
ENV NODE_ENV=production

# 安装依赖
COPY package*.json ./
# 删除package-lock.json并使用npm install来避免Rollup原生模块问题
RUN rm -f package-lock.json && npm install && npm cache clean --force

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:stable-alpine as production-stage

# 安装必要的工具
RUN apk add --no-cache curl

# 复制构建产物
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# 创建健康检查文件
RUN echo "healthy" > /usr/share/nginx/html/health

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
