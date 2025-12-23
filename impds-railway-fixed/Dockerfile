FROM node:18-alpine

# Install Python and create virtual environment
RUN apk add --no-cache python3 py3-pip && \
    python3 -m venv /app/venv

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install --production

# Copy requirements and install in virtual environment
COPY requirements.txt .
RUN source /app/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set Python path to virtual environment
ENV PATH="/app/venv/bin:$PATH"
ENV PYTHON_PATH="/app/venv/bin/python3"

EXPOSE 3000

CMD ["node", "server.js"]
