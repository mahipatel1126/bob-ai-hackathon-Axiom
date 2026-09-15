"""Chain Guard AI Backend Application Entrypoint.

Starts the REST API server, loads demo datasets, and handles incoming requests
from Person 3's frontend and Person 2's AI optimizer.
"""

import sys
import argparse
from pathlib import Path

# Ensure repository root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.backend import config
from src.backend.services import data_loader
from src.backend.api.server import run_server


def main() -> None:
    """Initialize backend services and launch API listener."""
    parser = argparse.ArgumentParser(description="Chain Guard AI Backend Server")
    parser.add_argument("--host", default=config.SERVER_HOST, help="Binding IP host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=config.SERVER_PORT, help="Server port (default: 8000)")
    args = parser.parse_args()

    print("================================================================")
    print("🛡️  Chain Guard AI — Supply Chain Disruption & Fleet Optimizer")
    print("================================================================")

    # Pre-flight data validation check
    shipments = data_loader.get_shipments()
    disruptions = data_loader.get_disruptions(active_only=True)
    print(f"📦 Preloaded {len(shipments)} shipments and {len(disruptions)} active disruptions.")

    # Start HTTP server
    run_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
