# S2G Backend - Charging Stations API

Backend API for managing electric vehicle charging stations, built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- User authentication with JWT tokens and Google OAuth
- CRUD operations for charging stations
- Scheduled status changes for stations
- Analytics endpoints for station data visualization
- Containerized with Docker and Docker Compose

## Requirements

- Docker and Docker Compose
- Python 3.9+ (for local development without Docker)

## Installation and Setup

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/jazrobot/s2g-backend.git
   cd s2g-backend
   ```

2. Create a `.env` file in the root directory (optional, you can also use the environment variables in docker-compose.yml):
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/s2g
   SECRET_KEY=your_secret_key_here
   BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/oauth/google/callback
   ```

3. Build and start the containers:
   ```bash
   docker-compose up -d --build
   ```

4. The API will be available at http://localhost:8000

### Local Development (Without Docker)

1. Clone the repository:
   ```bash
   git clone https://github.com/jazrobot/s2g-backend.git
   cd s2g-backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up a PostgreSQL database and update the DATABASE_URL in your environment variables

5. Run migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Sample Data

The application is initialized with sample data for charging stations. This data is automatically loaded when the application starts and includes:

- 10 charging stations across different locations
- Various capacity levels (from 50kW to 300kW)
- Different status values (active/inactive)

The sample data is defined in `app/core/init_data.py` and is used to populate the database on first run.

## Database Schema

The main entities in the database are:

- **Users**: Authentication and user management
- **Stations**: Charging station information including location, capacity, and status

## Environment Variables

| Variable | Description | Default |
|----------|-------------|--------|
| DATABASE_URL | PostgreSQL connection string | postgresql+asyncpg://postgres:postgres@db:5432/s2g |
| SECRET_KEY | Secret key for JWT token generation | your_secret_key_here |
| BACKEND_CORS_ORIGINS | List of allowed CORS origins | ["http://localhost:3000","http://localhost:8080"] |
| GOOGLE_CLIENT_ID | Google OAuth client ID | |
| GOOGLE_CLIENT_SECRET | Google OAuth client secret | |
| GOOGLE_REDIRECT_URI | Google OAuth redirect URI | http://localhost:8000/api/v1/oauth/google/callback |
