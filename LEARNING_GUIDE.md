# Docker Learning Guide

This project is already implemented, so your goal is not to memorize the files. Your goal is to learn how the pieces relate, then make small controlled changes and verify what happens.

Use this guide like a lab notebook. Before each command, predict what you expect. After each command, write down what surprised you.

## Mental Model

The app has three running services:

- `frontend`: React app built into static files and served by Nginx.
- `backend`: FastAPI app that exposes `/todos`.
- `postgres`: PostgreSQL database that stores todos.

The important Docker idea:

- Containers talk to each other by Compose service name, such as `postgres` or `backend`.
- Your browser is not inside the Docker network. It talks through published host ports like `localhost:3000` and `localhost:8000`.

That difference explains many real Docker bugs.

## Lesson 1: Read The Compose File

Open `docker-compose.yml`.

Answer these before running anything:

1. Which services are defined?
2. Which ports are exposed to your laptop?
3. Which service has persistent data?
4. Which service waits for another service to become healthy?
5. What is the database hostname from the backend container's point of view?

Then run:

```bash
docker compose config
```

Look for the final resolved values after `.env` interpolation. This command is safer than guessing because it shows what Compose will actually use.

## Lesson 2: Build And Start The Stack

Run:

```bash
docker compose up --build
```

In another terminal, inspect the running services:

```bash
docker compose ps
```

Expected result:

- `postgres` should become healthy.
- `backend` should start after Postgres is healthy.
- `frontend` should serve on `localhost:3000`.

Visit:

- `http://localhost:8000/health`
- `http://localhost:8000/docs`
- `http://localhost:3000`

Checkpoint question:

Why does the backend publish `8000:8000`, but still uses `postgres:5432` internally instead of `localhost:5432`?

## Lesson 3: Debug The Frontend API URL

Open `frontend/src/App.jsx` and find `API_URL`.

Now open `docker-compose.yml` and find the frontend environment:

```yaml
VITE_API_URL: http://backend:8000
```

Prediction:

Will your browser be able to call `http://backend:8000/todos`?

Hint: `backend` is a Docker DNS name. Your browser runs on your laptop, not inside the Compose network.

If the UI fails to load todos, fix the frontend environment to:

```yaml
VITE_API_URL: http://localhost:8000
```

Then rebuild the frontend:

```bash
docker compose up --build frontend
```

Important detail:

Vite bakes `VITE_*` variables into the built JavaScript at build time. Changing the variable usually means rebuilding the frontend image.

## Lesson 4: Follow A Request Through The Stack

Create a todo from the frontend.

Then watch backend logs:

```bash
docker compose logs -f backend
```

Then inspect the database directly:

```bash
docker compose exec postgres psql -U postgres -d todos_db
```

Inside `psql`, run:

```sql
select id, title, completed, created_at from todos;
```

Exit with:

```sql
\q
```

Checkpoint:

Trace the request path in your own words:

browser -> published port -> backend container -> Docker network -> postgres container -> named volume

## Lesson 5: Prove Persistence

First stop containers without deleting volumes:

```bash
docker compose down
docker compose up
```

Your todos should still exist.

Now stop containers and delete volumes:

```bash
docker compose down -v
docker compose up
```

Your todos should be gone.

Checkpoint:

What did `postgres_data:/var/lib/postgresql/data` preserve?

## Lesson 6: Understand Images Vs Containers

List containers:

```bash
docker compose ps
```

List images:

```bash
docker images
```

Then change a backend log message in `backend/app.py`.

Because `./backend:/app` is bind-mounted, restart only the backend:

```bash
docker compose restart backend
```

Checkpoint:

Why did this change not require rebuilding the backend image?

Now change `backend/requirements.txt`.

Checkpoint:

Why does this change require:

```bash
docker compose up --build backend
```

## Lesson 7: Read The Backend Dockerfile

Open `backend/Dockerfile`.

Questions:

1. What base image does it use?
2. Why does it copy `requirements.txt` before copying the rest of the app?
3. What command starts the app?
4. What endpoint does the Docker health check call?

Experiment:

Temporarily change the health endpoint path in the Dockerfile to a bad path, rebuild, and inspect:

```bash
docker compose up --build backend
docker compose ps
```

Then change it back.

## Lesson 8: Read The Frontend Dockerfile

Open `frontend/Dockerfile`.

This is a multi-stage build:

- Stage 1 uses Node to install dependencies and build static files.
- Stage 2 uses Nginx to serve those static files.

Questions:

1. Why is Node not needed in the final runtime image?
2. Where are the built files copied?
3. Why does Nginx listen on port `3000` here?

Checkpoint:

Explain the difference between `npm run dev` and this production-style Nginx container.

## Lesson 9: Make One Small Feature Yourself

Add a priority field to todos.

Do this in small steps:

1. Add `priority` to `backend/models.py`.
2. Add it to `TodoCreate`, `TodoUpdate`, and `TodoResponse` in `backend/schemas.py`.
3. Update `backend/app.py` so created todos save priority.
4. Add a priority input or select in `frontend/src/App.jsx`.
5. Rebuild and test.

After changing the database model, use:

```bash
docker compose down -v
docker compose up --build
```

This deletes the old database volume so SQLAlchemy can create the updated table from scratch. Later, you can learn Alembic migrations so schema changes do not require deleting data.

## Lesson 10: Clean Up Production Gaps

Once you understand the basics, improve the project:

1. Fix the frontend API URL if needed.
2. Add a backend health check to `docker-compose.yml`, not only the Dockerfile.
3. Replace `allow_origins=["*"]` with `http://localhost:3000`.
4. Remove the old root `app.py` and root `Dockerfile` if they are no longer part of the lesson.
5. Add Alembic migrations.

## Suggested Learning Rhythm

Do one lesson per session. Docker is easier when each idea has a concrete symptom:

- Ports answer "how do I reach it from my laptop?"
- Networks answer "how do containers reach each other?"
- Volumes answer "what survives container deletion?"
- Images answer "what filesystem template creates containers?"
- Bind mounts answer "how does local code appear inside a container?"
- Health checks answer "is the process ready, not just started?"

