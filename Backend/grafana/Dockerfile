FROM grafana/grafana:latest

# Override default admin password environment variable
ENV GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}

# Change default port to 3001
ENV GF_SERVER_HTTP_PORT 3000

# Copy the provisioning files
COPY Backend/grafana/provisioning /etc/grafana/provisioning

# Copy the dashboards directory
#COPY Backend/grafana/dashboards /var/lib/grafana/dashboards

# Make sure the provisioning files are readable by the grafana user
USER root
RUN chmod -R 777 /etc/grafana/provisioning

USER grafana
