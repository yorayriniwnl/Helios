# Optimized multi-stage Dockerfile for Helios Next.js frontend
# Builder stage: install deps and build the app
FROM node:18-slim AS builder

WORKDIR /app

# Copy package manifests first to leverage Docker cache
COPY package*.json ./

# Install full deps for build
RUN npm ci --legacy-peer-deps

# Copy source and build (NEXT_PUBLIC_* env injected at build time)
COPY . .
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://backend:8000}
RUN npm run build


# Runtime stage: keep image small by installing only production deps
FROM node:18-slim AS runner

WORKDIR /app
ENV NODE_ENV=production

# Copy package manifests and install only production deps
COPY package*.json ./
RUN npm ci --omit=dev --no-audit --no-fund

# Copy built output from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./next.config.js

# Expose the standard Next.js port
EXPOSE 3000

# Start production server
CMD ["npm", "run", "start"]
