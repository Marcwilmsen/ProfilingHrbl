# Build the React application
FROM node:20 AS build
WORKDIR /app
COPY Frontend/dashboard/package.json Frontend/dashboard/package-lock.json ./
RUN npm install
COPY Frontend/dashboard/ ./
RUN npm run build

# Serve the React application using Nginxxx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY Frontend/dashboard/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 2223
CMD ["nginx", "-g", "daemon off;"]
###