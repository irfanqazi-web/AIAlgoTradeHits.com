# Production stage - using pre-built assets
FROM nginx:alpine

# Copy built assets directly
COPY index.html /usr/share/nginx/html/
COPY vite.svg /usr/share/nginx/html/
COPY assets /usr/share/nginx/html/assets

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 8080 (Cloud Run requirement)
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
