# Inventory Agent

The Inventory Agent is a standalone FastAPI service for tracking miner devices.
It is containerized so contributors and operators can run the same runtime
locally, in Docker Compose, or later under an orchestrator such as Kubernetes.

## Local Python Run

```bash
cd braidpool
python -m venv .venv
. .venv/bin/activate
pip install -r inventory_agent/requirements.txt
uvicorn inventory_agent.main:app --host 0.0.0.0 --port 8000 --reload
```

On Windows PowerShell:

```powershell
cd braidpool
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r inventory_agent\requirements.txt
uvicorn inventory_agent.main:app --host 0.0.0.0 --port 8000 --reload
```

Open the API docs at `http://localhost:8000/docs`.

## Docker

```bash
docker build -f inventory_agent/Dockerfile -t braidpool/inventory-agent:local .
docker run --rm -p 8000:8000 braidpool/inventory-agent:local
```

Health check:

```bash
curl http://localhost:8000/health
```

## Docker Compose

```bash
docker compose up --build inventory-agent
```

The service listens on `http://localhost:8000` by default. Override the host
port with `INVENTORY_AGENT_PORT`:

```bash
INVENTORY_AGENT_PORT=8080 docker compose up --build inventory-agent
```

## Configuration

Environment variables:

- `INVENTORY_AGENT_SERVICE_NAME`: API service name. Defaults to
  `Inventory Agent`.
- `INVENTORY_AGENT_PORT`: host port used by Docker Compose. Defaults to `8000`.
- `INVENTORY_AGENT_SEED_EXAMPLES`: seed one ASIC miner and one CPU miner at
  startup. Defaults to `true`.

## API Shape

- `GET /health`: container and service health.
- `GET /miners`: list miners, optionally filtered with `miner_type=asic|cpu`
  and `status=online|warning|offline|unknown`.
- `POST /miners`: register an ASIC or CPU miner.
- `GET /miners/{miner_id}`: fetch a miner.
- `PATCH /miners/{miner_id}/status`: update miner status.
- `GET /miners/summary`: aggregate inventory counts by type and status.
