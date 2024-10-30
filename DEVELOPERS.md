# Developing ThanoSQL AI Chat

This guide will help you set up and contribute to the ThanoSQL AI Chat development environment. The project uses Docker for containerization and provides a comprehensive development environment for working with ThanoSQL's AI chat capabilities.

## Getting Started

### Prerequsites

First, make sure you have Docker installed on your device. You can download and install it from [here](https://docs.docker.com/get-docker/).

## Local Development

1. Navigate to the `docker` directory in your cloned repo

   ```sh
   cd docker
   ```

2. Copy the example `env` file

   ```sh
   cp .env.example .env.dev
   ```

3. Configure environment variables

   Make sure to set Secrets:

   - ThanoSQL Workspace Engine URL
   - API Token, etc

4. Run Docker

   ```sh
   docker compose -f dev.docker-compose.yml --env-file .env.dev up --build
   ```
