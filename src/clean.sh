#!/bin/sh
sudo docker stop src_web_1 src_db_1
sudo docker rm src_web_1 src_db_1
sudo docker volume rm src_postgres_value
sudo docker rmi src_web postgres:13.0-alpine
sudo docker system prune