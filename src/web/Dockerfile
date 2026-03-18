# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY src/web/package.json src/web/package-lock.json* ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy source
COPY src/web .

# Ensure the directory exists even when an empty public/ folder is not tracked by Git
RUN mkdir -p public

# Build Next.js
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install only production dependencies
COPY src/web/package.json src/web/package-lock.json* ./
RUN npm install --legacy-peer-deps --production

# Copy built app from builder
COPY --from=builder /app/.next /app/.next
COPY --from=builder /app/public /app/public

# Expose port
EXPOSE 3000

# Start app
CMD ["npm", "run", "start"]
