FROM node:20-bookworm-slim

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install --omit=dev

COPY cutout/ cutout/
COPY serving/ serving/

ENV NODE_ENV=production
ENV PORT=8000

EXPOSE 8000
CMD ["node", "serving/app.js"]
