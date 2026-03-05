# Use a slim Node.js image to keep it lightweight
FROM node:20-slim

# Set the working directory
WORKDIR /app

# Install the MCP server globally inside the container
RUN npm install -g mongodb-mcp-server

# Expose the port the server will run on
EXPOSE 8081

# Command to run the server
# Note: We use 0.0.0.0 accessible from outside the container
ENTRYPOINT ["mongodb-mcp-server"]
CMD [ \
    "--transport", "http", \
    "--httpHost", "0.0.0.0", \
    "--httpPort", "8081", \
    "--connectionString", "mongodb://admin:password123@host.docker.internal:27017/", \
    "--loggers", "stderr" \
]