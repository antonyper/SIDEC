FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

FROM node:22-alpine AS builder
WORKDIR /app
# Next.js resuelve los rewrites de next.config.ts durante `next build` y los deja
# fijos en .next/routes-manifest.json: BACKEND_URL tiene que existir AQUÍ. Como
# variable de entorno del contenedor llega tarde y el proxy /api apunta a localhost.
ARG BACKEND_URL=http://backend:8000
ENV BACKEND_URL=$BACKEND_URL
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
# server.js escucha en HOSTNAME: sin fijarlo usa el hostname del contenedor/pod.
ENV HOSTNAME=0.0.0.0
ENV PORT=3000

COPY --from=builder --chown=node:node /app/public ./public
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static

USER node

EXPOSE 3000
CMD ["node", "server.js"]
