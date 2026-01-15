# Production stage - serve pre-built files
FROM nginx:alpine

# Copy pre-built assets directly
COPY assets /usr/share/nginx/html/assets
COPY index.html /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 8080 (Cloud Run requirement)
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
