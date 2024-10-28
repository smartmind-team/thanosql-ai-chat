# ThanoSQL Chat - Redis

This directory contains the Redis configuration and function definitions for ThanoSQL Chat's backend services.

## Overview

Redis is used as the primary database for storing chat-related data and function configurations. The setup includes predefined functions that enable AI chat capabilities within ThanoSQL Workspace.

## Function Configuration

### Setting up Functions

Functions are configured through the `functions.json` file in this directory. This file defines the available AI chat capabilities and their parameters.

Example structure of `functions.json`:

```json
[
  {
    "name": "function_name",
    "parameters": [
      {
        "name": "parameter_name",
        "type": "TEXT" // SQL parameter type
      }
    ],
    "return_type": "TEXT", // SQL return type
    "description": "Description of what the function does",
    "example_usage": "SELECT function_name(parameter) FROM table_name"
  }
]
```

> **Important Note**: Functions defined in `functions.json` must have corresponding SQL function implementations in your ThanoSQL Workspace for them to work. These implementations should follow the patterns shown in `functions.sql`.

### Updating Functions

When updating functions, you need to rebuild and restart the services as the functions are loaded during container initialization:

1. Modify the `functions.json` file with your desired changes
2. Stop and rebuild the services:
   ```bash
   docker compose down
   docker compose build
   docker compose up -d
   ```

## Environment Variables

The Redis service uses several environment variables that affect its behavior:

```
OPENAI_MODEL
OPENAI_API_KEY
OPENAI_BASE_URL
TEXT2SQL_MODEL
TEXT2SQL_API_KEY
TEXT2SQL_BASE_URL
MAX_TEMPERATURE
DEFAULT_TEMPERATURE
SYSTEM_PROMPT
```

Make sure these are properly set in your `.env` file.

## Database Management

### Resetting the Database

If you need to reset the Redis database to its initial state:

1. Stop the running containers:

   ```bash
   docker compose down
   ```

2. Remove the Redis dump file:

   ```bash
   rm ./redis/data/dump.rdb
   ```

3. Rebuild and restart the containers:
   ```bash
   docker compose build
   docker compose up -d
   ```

### Data Persistence

- Redis data is persisted in `./redis/data/dump.rdb`
- This directory is mounted as a volume in the Redis container
- Backup this file if you need to preserve the database state
