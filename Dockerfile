# Multi-stage Dockerfile: the build stage is kept separate from the runtime
# stage so the final image stays as small as possible.
# Multi-stage build reference: https://docs.docker.com/build/building/multi-stage/

# --- Stage 1: build / install dependencies ---
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
# Install production dependencies only, reproducibly.
RUN npm ci --omit=dev || npm install --omit=dev
COPY . .

# --- Stage 2: minimal runtime ---
FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
# Run as a non-root user (security-baseline good practice).
USER node
COPY --chown=node:node --from=build /app /app
EXPOSE 3000
CMD ["node", "src/server.js"]
