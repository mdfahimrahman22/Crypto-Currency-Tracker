#!/bin/sh
docker compose down --volumes
docker system prune -a -f
git pull
docker compose up -d --build
