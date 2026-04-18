from enum import Enum
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

from inventory_agent.settings import settings


class MinerType(str, Enum):
    ASIC = "asic"
    CPU = "cpu"


class MinerStatus(str, Enum):
    ONLINE = "online"
    WARNING = "warning"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class MinerCreate(BaseModel):
    name: str = Field(..., min_length=1, examples=["Antminer S19"])
    miner_type: MinerType
    status: MinerStatus = MinerStatus.UNKNOWN
    manufacturer: Optional[str] = Field(default=None, examples=["Bitmain"])
    miner_model: Optional[str] = Field(default=None, examples=["S19"])
    location: Optional[str] = Field(default=None, examples=["Rack A, Unit 3"])
    ip_address: Optional[str] = Field(default=None, examples=["192.168.1.42"])
    hash_rate_ths: Optional[float] = Field(default=None, ge=0)
    hash_rate_hs: Optional[float] = Field(default=None, ge=0)
    temperature_c: Optional[float] = None
    power_watts: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = None


class Miner(MinerCreate):
    id: str


class MinerStatusUpdate(BaseModel):
    status: MinerStatus


class InventorySummary(BaseModel):
    total: int
    asic: int
    cpu: int
    online: int
    warning: int
    offline: int
    unknown: int


def build_app() -> FastAPI:
    app = FastAPI(
        title=settings.service_name,
        version="0.1.0",
        description="Standalone inventory service for ASIC and CPU miners.",
    )
    inventory: dict[str, Miner] = {}

    if settings.seed_examples:
        for miner in _example_miners():
            inventory[miner.id] = miner

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.service_name}

    @app.get("/miners", response_model=list[Miner], tags=["miners"])
    def list_miners(
        miner_type: Optional[MinerType] = Query(default=None),
        miner_status: Optional[MinerStatus] = Query(default=None, alias="status"),
    ) -> list[Miner]:
        miners = list(inventory.values())
        if miner_type is not None:
            miners = [miner for miner in miners if miner.miner_type == miner_type]
        if miner_status is not None:
            miners = [miner for miner in miners if miner.status == miner_status]
        return miners

    @app.post(
        "/miners",
        response_model=Miner,
        status_code=status.HTTP_201_CREATED,
        tags=["miners"],
    )
    def create_miner(payload: MinerCreate) -> Miner:
        miner = Miner(id=f"miner-{uuid4().hex[:12]}", **payload.model_dump())
        inventory[miner.id] = miner
        return miner

    @app.get("/miners/summary", response_model=InventorySummary, tags=["miners"])
    def summarize_inventory() -> InventorySummary:
        miners = list(inventory.values())
        return InventorySummary(
            total=len(miners),
            asic=sum(1 for miner in miners if miner.miner_type == MinerType.ASIC),
            cpu=sum(1 for miner in miners if miner.miner_type == MinerType.CPU),
            online=sum(1 for miner in miners if miner.status == MinerStatus.ONLINE),
            warning=sum(1 for miner in miners if miner.status == MinerStatus.WARNING),
            offline=sum(1 for miner in miners if miner.status == MinerStatus.OFFLINE),
            unknown=sum(1 for miner in miners if miner.status == MinerStatus.UNKNOWN),
        )

    @app.get("/miners/{miner_id}", response_model=Miner, tags=["miners"])
    def get_miner(miner_id: str) -> Miner:
        try:
            return inventory[miner_id]
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="miner not found") from exc

    @app.patch("/miners/{miner_id}/status", response_model=Miner, tags=["miners"])
    def update_miner_status(miner_id: str, payload: MinerStatusUpdate) -> Miner:
        miner = get_miner(miner_id)
        updated = miner.model_copy(update={"status": payload.status})
        inventory[miner_id] = updated
        return updated

    return app


def _example_miners() -> list[Miner]:
    return [
        Miner(
            id="miner-asic-001",
            name="Antminer S19",
            miner_type=MinerType.ASIC,
            status=MinerStatus.ONLINE,
            manufacturer="Bitmain",
            miner_model="S19",
            location="Rack A, Unit 3",
            ip_address="192.168.10.21",
            hash_rate_ths=95.2,
            temperature_c=65,
            power_watts=3250,
        ),
        Miner(
            id="miner-cpu-001",
            name="CPUnet worker",
            miner_type=MinerType.CPU,
            status=MinerStatus.ONLINE,
            manufacturer="Generic",
            miner_model="x86_64",
            location="dev workstation",
            hash_rate_hs=3_300_000,
            power_watts=125,
        ),
    ]


app = build_app()
