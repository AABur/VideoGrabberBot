#!/bin/bash

# VideoGrabberBot Deployment Script
# Usage: ./deploy.sh [dev|prod] [build|start|stop|restart|logs|status]

set -e

ENVIRONMENT=${1:-dev}
ACTION=${2:-start}

case $ENVIRONMENT in
    dev|development)
        COMPOSE_FILE="docker-compose.dev.yml"
        CONTAINER_NAME="videograbber-bot"
        ;;
    prod|production)
        COMPOSE_FILE="docker-compose.prod.yml"
        CONTAINER_NAME="videograbber-bot-prod"
        ;;
    *)
        echo "Usage: $0 [dev|prod] [build|start|stop|restart|logs|status]"
        echo "Environment must be 'dev' or 'prod'"
        exit 1
        ;;
esac

echo "VideoGrabberBot Deployment - Environment: $ENVIRONMENT, Action: $ACTION"

case $ACTION in
    build)
        echo "Building Docker image..."
        docker compose -f $COMPOSE_FILE build --no-cache
        ;;
    start)
        echo "Starting services..."
        if [ ! -f .env ]; then
            echo "Warning: .env file not found. Please create one from .env.example"
            exit 1
        fi
        docker compose -f $COMPOSE_FILE up -d
        echo "Services started successfully!"
        ;;
    stop)
        echo "Stopping services..."
        docker compose -f $COMPOSE_FILE down
        echo "Services stopped successfully!"
        ;;
    restart)
        echo "Restarting services..."
        docker compose -f $COMPOSE_FILE down
        docker compose -f $COMPOSE_FILE up -d
        echo "Services restarted successfully!"
        ;;
    logs)
        echo "Showing logs for $CONTAINER_NAME..."
        docker compose -f $COMPOSE_FILE logs -f $CONTAINER_NAME
        ;;
    status)
        echo "Checking service status..."
        docker compose -f $COMPOSE_FILE ps
        ;;
    *)
        echo "Usage: $0 [dev|prod] [build|start|stop|restart|logs|status]"
        echo "Actions:"
        echo "  build   - Build Docker image"
        echo "  start   - Start services"
        echo "  stop    - Stop services"
        echo "  restart - Restart services"
        echo "  logs    - Show logs"
        echo "  status  - Show service status"
        exit 1
        ;;
esac