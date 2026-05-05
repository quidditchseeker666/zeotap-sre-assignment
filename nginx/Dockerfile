FROM nginx:1.25-alpine

# Copy custom configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create log directory
RUN mkdir -p /var/log/nginx && \
    chown -R nginx:nginx /var/log/nginx

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/nginx-health || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]