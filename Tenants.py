import json
from pathlib import Path

def load_tenants() -> list[dict[str, str]]:
    """
    Load and validate tenant objects from tenants.json located in the same directory as this script.
    
    @return: List of tenant dictionaries with normalized tenant_id (lowercase) and configuration
    @raises FileNotFoundError: If tenants.json cannot be found in the script directory
    """
    # Construct path to tenants.json relative to this script (not current working directory)
    config_path = Path(__file__).resolve().parent / "tenants.json"
    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"tenants.json not found at {config_path}")

    # Extract the tenants array from config, defaulting to empty list if missing
    tenants = config.get("tenants", [])
    
    # Build normalized tenant list: filter out any tenants without a tenant_id,
    # convert tenant_id to lowercase for case-insensitive matching in CLI args
    return [
        {
            "tenant_id": tenant.get("tenant_id", "").lower(),
            "business_unit_description": tenant.get("business_unit_description", ""),
            "tenant_name": tenant.get("tenant_name", ""),
        }
        for tenant in tenants
        if tenant.get("tenant_id")  # Only include tenants with a non-empty tenant_id
    ]