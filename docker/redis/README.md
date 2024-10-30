# ThanoSQL AI Chat - Redis

This directory contains the Redis configuration and function definitions for ThanoSQL AI Chat's backend services.

## Overview

Redis is used as the primary database for storing chat-related data and function configurations. The setup includes predefined functions that enable AI chat capabilities within ThanoSQL Workspace.

## Model Related Variables

The Redis service uses several environment variables that affect its behavior:

| Variable              | Description                             | Required |
| --------------------- | --------------------------------------- | -------- |
| `OPENAI_MODEL`        | The OpenAI model to use (e.g., gpt-4)   | Yes      |
| `OPENAI_API_KEY`      | Your OpenAI API key                     | Yes      |
| `OPENAI_BASE_URL`     | Custom API endpoint (if using a proxy)  | No       |
| `TEXT2SQL_MODEL`      | Model for SQL generation                | Yes      |
| `TEXT2SQL_API_KEY`    | API key for SQL generation service      | Yes      |
| `TEXT2SQL_BASE_URL`   | Base URL for SQL generation service     | No       |
| `MAX_TEMPERATURE`     | Maximum temperature for model responses | No       |
| `DEFAULT_TEMPERATURE` | Default temperature for model responses | No       |
| `SYSTEM_PROMPT`       | System prompt for chat initialization   | No       |

Make sure these are properly set in your `.env` file.

## Function Configuration

The `functions.json` file is crucial for LLM to utilize user-defined functions effectively. It serves as a bridge between natural language processing and database operations.

### Setting up Functions

Functions are configured through the `functions.json` file in this directory. This file defines the available AI chat capabilities and their parameters.

#### Function Definition Structure

Each function in `functions.json` should follow this structure:

```json
{
  "name": "function_name",
  "parameters": [
    {
      "name": "parameter_name",
      "type": "TEXT", // SQL parameter type
      "description": "Description of the parameter",
      "required": true // Whether the parameter is mandatory
    }
  ],
  "return_type": "TEXT", // SQL return type
  "description": "Description of what the function does",
  "example_usage": "SELECT function_name(parameter) FROM table_name"
}
```

#### Example Implementation

Here's an example of implementing a speech-to-text function:

```sql
-- Speech to text
CREATE or REPLACE FUNCTION stt(file_path TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN thanosql.predict(
        task := 'automatic-speech-recognition',
        engine := 'thanosql',
        input := file_path,
        model := 'smartmind/whisper-large'
    );
END;
$$ LANGUAGE plpgsql;
```

Corresponding `functions.json` entry:

```json
{
  "name": "stt",
  "parameters": [
    {
      "name": "file_path",
      "type": "TEXT",
      "description": "Path to the audio file for transcription",
      "required": true
    }
  ],
  "return_type": "TEXT",
  "description": "Converts speech audio to text using Whisper model",
  "example_usage": "SELECT stt('/path/to/audio.wav')"
}
```

### Updating Functions

When making changes to functions, follow these steps to ensure proper implementation:

1. Update your SQL function in ThanoSQL Workspace
2. Modify the corresponding entry in `functions.json`
3. Rebuild and restart the services:

```bash
docker compose down
docker compose build
docker compose up -d
```

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
