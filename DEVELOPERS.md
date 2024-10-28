## Running Docker for ThanoSQL Chat App

### Prerequsites

First, make sure you have the Docker installed on your device. You can download and install it from [here](https://docs.docker.com/get-docker/).

### Get Started

1. Navigate to the `docker` directory in your forked repo

   ```sh
   cd docker
   ```

2. Copy the example `env` file

   ```sh
   cp .env.example .env.dev
   ```

3. Run docker

   ```sh
   docker compose -f dev.docker-compose.yml up --build
   ```
