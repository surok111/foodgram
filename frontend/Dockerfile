# build env
FROM node:21.7.1-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --fetch-retries 5 --fetch-retry-mintimeout 20000 --fetch-retry-maxtimeout 120000
COPY . ./
RUN npm run build
CMD ["sh", "-c", "cp -r build result_build"]
