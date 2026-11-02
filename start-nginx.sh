#!/bin/sh
# Generate nginx config from template with correct PORT
PORT=${PORT:-80}
export PORT
envsubst '${PORT}' < /etc/nginx/nginx-single.conf.template > /etc/nginx/conf.d/default.conf
exec nginx -g "daemon off;"
