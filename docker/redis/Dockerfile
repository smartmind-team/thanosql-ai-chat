FROM redis:7.4

RUN mkdir -p /usr/local/etc/redis

COPY ./redis.conf /usr/local/etc/redis/redis.conf
COPY ./functions.json /functions.json

# Copy the initialization script to the container
COPY ./init.sh /usr/local/bin/init.sh

# Make the script executable
RUN chmod +x /usr/local/bin/init.sh

# Run the initialization script when the container starts
CMD ["/usr/local/bin/init.sh"]
