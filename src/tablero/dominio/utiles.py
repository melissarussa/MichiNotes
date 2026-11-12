import uuid
from datetime import datetime, timezone


def ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


def nuevo_id() -> str:
    return str(uuid.uuid4())
