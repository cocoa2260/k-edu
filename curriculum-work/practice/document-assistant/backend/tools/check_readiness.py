"""Read-only local Ollama readiness check; never requests generation/downloads."""
import importlib.metadata
import json
import os

import httpx


def main():
    result = {
        "scope": "local_ollama_inventory_only_no_generation",
        "base_url": "http://localhost:11434",
        "ollama_model_configured": bool(os.getenv("OLLAMA_MODEL", "").strip()),
        "openai_key_configured": bool(os.getenv("OPENAI_API_KEY", "").strip()),
        "openai_api_called": False,
        "generation_executed": False,
        "model_download_attempted": False,
    }
    try:
        response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        response.raise_for_status()
        body = response.json()
        if not isinstance(body.get("models"), list):
            raise ValueError("Unexpected model list")
        result.update(service_status="reachable", listed_model_count=len(body["models"]))
    except httpx.ConnectError:
        result["service_status"] = "connection_failed"
    except httpx.TimeoutException:
        result["service_status"] = "timeout"
    except httpx.HTTPStatusError as exc:
        result.update(service_status="http_error", http_status=exc.response.status_code)
    except (ValueError, AttributeError, httpx.RequestError):
        result["service_status"] = "unverified_response_or_transport"
    result["gate"] = "G_MODEL_PENDING"
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
