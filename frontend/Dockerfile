# frontend/Dockerfile
# Stage 1: build
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: serve (lightweight)
FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html
# Copy a custom nginx.conf to add headers, security
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN adduser --disabled-password --gecos '' appuser
USER appuser
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
