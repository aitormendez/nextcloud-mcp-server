#!/bin/bash

case "$1" in
    "build")
        docker-compose build
        ;;
    "up")
        docker-compose up
        ;;
    "down")
        docker-compose down
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "bash")
        docker-compose exec mcp-server bash
        ;;
    *)
        echo "Usage: $0 {build|up|down|logs|bash}"
        exit 1
        ;;
esac