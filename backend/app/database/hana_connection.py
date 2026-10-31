import os
from pathlib import Path

from dotenv import load_dotenv
from hdbcli import dbapi


# Locate the .env file in the main FORESIGHTX project folder
PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


def get_hana_connection():
    """Create and return a SAP HANA database connection."""

    host = os.getenv("HANA_HOST")
    port = int(os.getenv("HANA_PORT", "443"))
    user = os.getenv("HANA_USER")
    password = os.getenv("HANA_PASSWORD")

    if not all([host, user, password]):
        raise ValueError(
            "SAP HANA configuration is incomplete. "
            "Check the project root .env file."
        )

    return dbapi.connect(
        address=host,
        port=port,
        user=user,
        password=password,
        encrypt=True,
        sslCryptoProvider="mscrypto",
    )