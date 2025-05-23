# Stage 1: Base build stage
FROM python:3.13-slim AS builder
ARG APP_DIR=dj_sd 
# Create the app directory
RUN mkdir /$APP_DIR
 
# Set the working directory
WORKDIR /$APP_DIR
 
# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
# Upgrade pip and install dependencies
RUN pip install --upgrade pip 
 
# Copy the requirements file first (better caching)
COPY ../requirements.txt /$APP_DIR/
 
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
 
# Stage 2: Production stage
FROM python:3.13-slim
ARG APP_DIR=dj_sd 
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USERNAME=sduser
ARG GROUPNAME=sduser

RUN groupadd --gid $GROUP_ID $GROUPNAME && \
    useradd -m -d /$APP_DIR -g $GROUP_ID -u $USER_ID $USERNAME
 
# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
 
# Set the working directory
WORKDIR /$APP_DIR
# Copy application code
# COPY --chown=$USERNAME:$USERNAME . .

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER $USERNAME
 
# Expose the application port
EXPOSE 8000
 
# Start the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "sd_proj.wsgi:application"]
