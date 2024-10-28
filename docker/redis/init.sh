#!/bin/bash
FUNCTIONS=$(cat /functions.json)

# Start Redis in the background
redis-server /usr/local/etc/redis/redis.conf --daemonize yes

# Wait for Redis to start
sleep 5

# Add default key-value pairs
# Initializing non-volatile keys
if [ "$(redis-cli EXISTS functions)" -eq 0 ]; then
  echo "Initializing Redis for the first time..."
  redis-cli SET functions "$FUNCTIONS" > /dev/null

  # Run your initialization logic here, like pre-loading data or configuration.
  # For example, you could load an RDB file or run Redis with a specific configuration.
else
  echo "Redis already initialized."
fi

redis-cli SET openai_api_key ${OPENAI_API_KEY} > /dev/null
redis-cli SET openai_base_url ${OPENAI_BASE_URL} > /dev/null
redis-cli SET openai_model ${OPENAI_MODEL} > /dev/null

redis-cli SET text2sql_api_key "${TEXT2SQL_API_KEY:-${OPENAI_API_KEY}}" > /dev/null
redis-cli SET text2sql_model "${TEXT2SQL_MODEL:-${OPENAI_MODEL}}" > /dev/null
redis-cli SET text2sql_base_url "${TEXT2SQL_BASE_URL:-${OPENAI_BASE_URL}}" > /dev/null

redis-cli SET max_temperature ${MAX_TEMPERATURE} > /dev/null
redis-cli SET temperature ${DEFAULT_TEMPERATURE} > /dev/null

redis-cli SET system_prompt ${SYSTEM_PROMPT} > /dev/null

# Stop Redis background process
redis-cli shutdown

# Start Redis in the foreground
redis-server /usr/local/etc/redis/redis.conf
