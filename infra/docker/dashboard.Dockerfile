FROM node:20-alpine

WORKDIR /app/apps/dashboard

COPY apps/dashboard/package.json /app/apps/dashboard/package.json
COPY apps/dashboard/tsconfig.json /app/apps/dashboard/tsconfig.json
COPY apps/dashboard/next-env.d.ts /app/apps/dashboard/next-env.d.ts
RUN npm install

COPY apps/dashboard /app/apps/dashboard

CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3000"]
