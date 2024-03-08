# GitHub Top Stars

## Description

The **GitHub Top Stars** is a service designed to manage and monitor top repositories on GitHub. It utilizes
asynchronous tasks and integrates with the GitHub API to collect and update information about repositories, including
stars, forks, and other relevant data. The application is built with modular components, including a RepositoriesService
for handling repository data and a RepositoryActivityService for tracking repository activities over time.

## Requirements

- Docker
- Docker Compose
- Yandex Cloud CLI

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/ErikRusanov/github-top-stars.git
cd github-top-stars
```

### 2. Configure Environment Variables

Create a `.env` file in the project root. Example content:

```ini
PSQL_URL = "postgresql://admin:1234@db:5432/default"
TOKEN = "token_from_github"
YCF_URL = "https://functions.yandexcloud.net/your-id"
```

You need to specify only one variable from `TOKEN` and `YCF_URL`. The last one has higher priority.

### 3. Build and Run with Docker Compose

#### 3.1. Run application locally without YCF

```bash
docker-compose up -d --build
```

This command will build and run application and postgresql database locally. It is recommended to specify a `TOKEN`
here.

#### 3.2. Run application with YCF

If you are only running the application in docker, you need to connect the remote database by specifying the
correct `PSQL_URL` and you also need to configure the Yandex Cloud function with a trigger.

1. [Install and initialize Yandex Cloud CLI](https://cloud.yandex.ru/ru/docs/cli/quickstart)
2. Create serverless function:
   ```bash
   yc serverless function create myfunction    
   ```
3. Copy the `http_invoke_url` of the created function and pass it into `.env` file. Then run the application:
   ```bash
   docker-compose up -d --build
   ```

4. Copy the `id` and upload the code:
   ```bash
   yc serverless function version create \
   --runtime 'python311' \
   --execution-timeout '120s' \
   --entrypoint 'main.handler' \
   --source-path './ycf.zip' \
   --environment 'PSQL_URL=postgresql://admin:1234@db:5432/default,TOKEN=token_from_github' --function-id '<myfunction-id>'
   ```

   If you need to specify extra flags, read more
   about [creating function versions](https://cloud.yandex.ru/ru/docs/cli/cli-ref/managed-services/serverless/function/version/create).
5. Allow unauthenticated invoke (optionally):
   ```bash
   yc serverless function allow-unauthenticated-invoke '<myfunction-id>'
   ```

6. Create cron trigger to parse data automatically:
   ```bash
   yc serverless trigger create timer mytrigger \
   --cron-expression '* * ? * * *' \
   --invoke-function-id '<myfunction-id>'
   ```

7. Add service account into function and trigger

_**Important:** the method that creates tables in the database is called only inside the application, so you first need
to run it and then configure Yandex Cloud._

### 4. Access the Application

Once the containers are running, you can access your application at http://localhost:8000

### 5. Stop the Application

To stop the application and remove the containers, use:

```bash
docker-compose down
```

To pause or delete YC function and trigger using CLI, read more
in [documentation](https://cloud.yandex.ru/ru/docs/cli/cli-ref/managed-services/serverless/)