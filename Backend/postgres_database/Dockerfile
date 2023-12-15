# Use the official PostgreSQL image as a parent image
FROM postgres:latest

# Optionally, add initialization scripts
#COPY ./init.sql /docker-entrypoint-initdb.d/

# The default port 5432 is used within the container
EXPOSE 5433

# Set the default command for the container to run  postgres.
CMD ["postgres", "-p", "5433"]
