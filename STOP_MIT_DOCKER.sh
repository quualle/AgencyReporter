#!/bin/bash

echo "Stoppe Agency Reporter..."
docker-compose -f docker-compose.simple.yml down
echo "✅ Agency Reporter wurde gestoppt"