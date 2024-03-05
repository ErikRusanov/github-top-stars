# GitHub Top Stars

## Description

The **GitHub Top Stars** is a service designed to manage and monitor top repositories on GitHub. It utilizes
asynchronous tasks and integrates with the GitHub API to collect and update information about repositories, including
stars, forks, and other relevant data. The application is built with modular components, including a RepositoriesService
for handling repository data and a RepositoryActivityService for tracking repository activities over time.

## Requirements

- Docker
- Docker Compose

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/ErikRusanov/github-top-stars.git
cd github-top-stars
```

### 2. Configure Environment Variables

Create a .env file in the project root with the following content:

```ini
PSQL_URL = "postgresql://admin:1234@db:5432/default"
TOKEN = "token_from_github"
```

### 3. Build and Run with Docker Compose

```bash
docker-compose up -d --build
```

### 4. Access the Application

Once the containers are running, you can access your application at http://localhost:8000

### 5. Stop the Application

To stop the application and remove the containers, use:

```bash
docker-compose down
```