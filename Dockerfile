FROM node:20-slim
WORKDIR /app
RUN npm install -g mongodb-mcp-server
EXPOSE 8081

# We leave the CMD empty or with defaults, 
# because docker-compose.yml will override these settings anyway.
ENTRYPOINT ["mongodb-mcp-server"]