# 构建阶段
FROM node:16-alpine as build-stage
WORKDIR /app

# 接收构建参数
ARG VITE_API_BASE_URL=/api
ARG VITE_UPLOAD_URL=/uploads

# 设置构建环境变量
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_UPLOAD_URL=$VITE_UPLOAD_URL

COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 生产阶段
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"] 