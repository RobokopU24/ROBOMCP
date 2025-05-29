#FROM python:3.11-slim
# leverage the renci python base image
FROM ghcr.io/translatorsri/renci-python-image:3.12.4

WORKDIR /app
COPY . /app

# Install uv
RUN pip install uv

# Copy requirements and install
#COPY requirements.txt .
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip install -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
#COPY robokop_mcp_server.py .
#COPY robokop_mcp_client.py .
#COPY robokop_mcp_client_with_remote_server.py .

# Expose server port
EXPOSE 8050

# Using the uv virtual environment
CMD ["python", "robokop_mcp_client.py", "--provider", "openai"]