FROM node:20-alpine AS base
RUN corepack enable && pnpm add -g pnpm

FROM base AS deps
WORKDIR /app
COPY package.json pnpm-workspace.yaml ./
COPY packages/shared/package.json ./packages/shared/
COPY apps/web/package.json ./apps/web/
RUN pnpm install --frozen-lockfile || pnpm install

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm install
RUN pnpm --filter @liveproof/shared build 2>/dev/null || true
RUN pnpm --filter web build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/apps/web/.next/standalone ./
COPY --from=builder /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder /app/apps/web/public ./apps/web/public 2>/dev/null || true
ENV NEXT_PUBLIC_API_URL=http://api:8000
ENV HOSTNAME=0.0.0.0
EXPOSE 3000
# Next standalone: server.js is at root of standalone output
CMD ["node", "server.js"]
