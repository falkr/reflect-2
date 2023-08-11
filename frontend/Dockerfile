FROM node:18-alpine

WORKDIR /app
COPY . .
RUN npm install
RUN npm run build

CMD ["node", "build"]
# CMD ["npm", "run", "dev", "--" , "--host", "3000"]
# CMD ["npm", "run", "dev", "--", "--host"]

EXPOSE 3000
