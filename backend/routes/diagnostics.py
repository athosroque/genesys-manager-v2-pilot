import asyncio
import re
from fastapi import APIRouter, Depends, Path, HTTPException
from typing import Dict, Any

from auth import get_token, h
from auth_local import get_current_user
from config import BASE_URL
import httpx

router = APIRouter()

UUID_REGEX = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

MAX_RETRIES = 5
DEFAULT_RETRY_SECONDS = 2.0
HTTP_TIMEOUT = 30.0

def _retry_after_seconds(resp: httpx.Response) -> float:
    header = resp.headers.get("Retry-After")
    if header:
        try:
            return max(float(header), 0.5)
        except ValueError:
            pass
    try:
        message = resp.json().get("message", "")
        match = re.search(r"\[(\d+(?:\.\d+)?)\]", message)
        if match:
            return max(float(match.group(1)), 0.5)
    except Exception:
        pass
    return DEFAULT_RETRY_SECONDS


async def genesys_request(
    method: str,
    path: str,
    *,
    json_data: dict | None = None,
    params: dict | None = None,
) -> Any:
    token = await get_token()
    headers = h(token)

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        for attempt in range(MAX_RETRIES + 1):
            resp = await client.request(
                method, f"{BASE_URL}{path}", json=json_data, params=params, headers=headers
            )
            if resp.status_code != 429 or attempt == MAX_RETRIES:
                break
            await asyncio.sleep(_retry_after_seconds(resp))

    if resp.status_code == 404:
        return None
    if resp.status_code >= 400:
        raise HTTPException(resp.status_code, f"Genesys API Error: {resp.text[:300]}")
    return resp.json() if resp.text else {}


@router.get("/{conversation_id}")
async def get_diagnostic_data(
    conversation_id: str = Path(..., description="UUID Genesys da conversa"),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Busca os detalhes de analytics e do call state de uma conversa no Genesys Cloud
    para alimentar o Dashboard de Diagnóstico.
    """
    uid = conversation_id.strip("{}")
    if not UUID_REGEX.match(uid):
        raise HTTPException(422, "conversation_id deve ser um UUID válido.")

    # Disparar chamadas em paralelo para /analytics/conversations/{id}/details 
    # e para /conversations/{id}
    details_task = genesys_request("GET", f"/analytics/conversations/{uid}/details")
    calls_task = genesys_request("GET", f"/conversations/{uid}")

    results = await asyncio.gather(details_task, calls_task, return_exceptions=True)
    
    details_data = results[0]
    calls_data = results[1]

    if isinstance(details_data, Exception):
        raise HTTPException(500, f"Erro buscando details: {str(details_data)}")
    if isinstance(calls_data, Exception):
        raise HTTPException(500, f"Erro buscando calls: {str(calls_data)}")

    if not details_data:
        raise HTTPException(404, "Conversa não encontrada nos registros de analytics.")

    return {
        "details": details_data,
        "calls": calls_data or {}
    }
