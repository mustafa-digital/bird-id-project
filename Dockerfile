#---- STAGE 1: Build the backend ----#

FROM python:3.12-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Disable development dependencies
ENV UV_NO_DEV=1 \
UV_COMPILE_BYTECODE=1 \
UV_LINK_MODE=copy

# Set the working directory to /app
WORKDIR /app

# Copy root config files into working directory
COPY pyproject.toml uv.lock ./

# Sync the project to new environment using uv sync
RUN uv sync --frozen --no-dev --no-install-project

# Copy the backend project files into working directory
COPY ./backend ./backend

RUN uv sync --frozen --no-dev

# In production, this is where I would load the model weights from S3 bucket
# NEXT STEP: MODEL LOADING HERE

#--- STAGE 1 END ----#


#--- STAGE 2: Run the backend ----#
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /backend

COPY --from=builder /backend /backend

# Install FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
&& rm -rf /var/lib/apt/lists/* 

ENV PATH="/backend/.venv/bin:$PATH"

# Set environment variables, this is temporary and will be provided using secrets in production
ENV FFMPEG_PATH=/usr/bin/ffmpeg
ENV LOGGING_LEVEL=INFO
ENV CHROMA_DB_DIR=vector_store/chroma_db

# Make port 8000 available outside this container
EXPOSE 8000

# Set up and run as a non-root user for security
RUN useradd app
USER app

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

#--- STAGE 2 END ----#
