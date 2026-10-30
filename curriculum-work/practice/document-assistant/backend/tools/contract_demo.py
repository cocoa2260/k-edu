"""Explicit contract-only HTTP demo. No model, credentials or generation."""
from app.main import create_app


class ContractProvider:
    provider_name = "contract-demo"
    model_name = "no-model-executed"

    def generate(self, message: str) -> str:
        return "CONTRACT DEMO ONLY: " + message


def create_contract_app():
    return create_app(ContractProvider())

