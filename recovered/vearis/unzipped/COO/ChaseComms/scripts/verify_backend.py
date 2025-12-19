#!/usr/bin/env python3

import asyncio
import websockets
import aiohttp
import json
import time
import sys
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

console = Console()

# Configuration
BASE_URL = "http://localhost:3001"
WS_URL = "ws://localhost:3001"
TIMEOUT = 5  # seconds

async def test_http_endpoint(session, endpoint, method="GET", data=None):
    try:
        start_time = time.time()
        if method == "GET":
            async with session.get(f"{BASE_URL}{endpoint}") as response:
                elapsed = (time.time() - start_time) * 1000
                return {
                    "status": response.status,
                    "latency": elapsed,
                    "ok": response.status == 200
                }
        elif method == "POST":
            async with session.post(f"{BASE_URL}{endpoint}", json=data) as response:
                elapsed = (time.time() - start_time) * 1000
                return {
                    "status": response.status,
                    "latency": elapsed,
                    "ok": response.status == 200
                }
    except Exception as e:
        return {
            "status": 0,
            "latency": 0,
            "ok": False,
            "error": str(e)
        }

async def test_websocket_endpoint(endpoint):
    try:
        start_time = time.time()
        async with websockets.connect(f"{WS_URL}{endpoint}") as websocket:
            await websocket.ping()
            await websocket.recv()
            elapsed = (time.time() - start_time) * 1000
            return {
                "status": "Connected",
                "latency": elapsed,
                "ok": True
            }
    except Exception as e:
        return {
            "status": "Failed",
            "latency": 0,
            "ok": False,
            "error": str(e)
        }

async def main():
    console.print("\n[bold green]NOVA COMMS Backend Verification[/bold green]")
    console.print("=====================================\n")

    # Required endpoints to test
    http_endpoints = {
        "Health Check": "/health",
        "Metrics": "/metrics",
        "Nova Field Status": "/nova-field/status",
        "Tasks List": "/tasks",
        "Messages": "/messages",
        "Model Status": "/model/status"
    }

    websocket_endpoints = {
        "Nova Field Updates": "/ws/nova-field",
        "Chat": "/ws/chat",
        "Metrics Stream": "/ws/metrics"
    }

    results_table = Table(title="Endpoint Verification Results")
    results_table.add_column("Endpoint", style="cyan")
    results_table.add_column("Type", style="magenta")
    results_table.add_column("Status", style="green")
    results_table.add_column("Latency (ms)", style="yellow")
    results_table.add_column("Requirements Met", style="blue")

    with Progress() as progress:
        task = progress.add_task("[cyan]Testing endpoints...", total=len(http_endpoints) + len(websocket_endpoints))

        async with aiohttp.ClientSession() as session:
            # Test HTTP endpoints
            for name, endpoint in http_endpoints.items():
                result = await test_http_endpoint(session, endpoint)
                status = "✅" if result["ok"] else "❌"
                latency = f"{result['latency']:.2f}" if result["ok"] else "N/A"
                requirements_met = "Yes" if result["ok"] and result["latency"] < 100 else "No"
                
                results_table.add_row(
                    name,
                    "HTTP",
                    status,
                    latency,
                    requirements_met
                )
                progress.advance(task)

            # Test WebSocket endpoints
            for name, endpoint in websocket_endpoints.items():
                result = await test_websocket_endpoint(endpoint)
                status = "✅" if result["ok"] else "❌"
                latency = f"{result['latency']:.2f}" if result["ok"] else "N/A"
                requirements_met = "Yes" if result["ok"] and result["latency"] < 50 else "No"
                
                results_table.add_row(
                    name,
                    "WebSocket",
                    status,
                    latency,
                    requirements_met
                )
                progress.advance(task)

    console.print("\n")
    console.print(results_table)
    console.print("\n")

    # Summary
    total_endpoints = len(http_endpoints) + len(websocket_endpoints)
    passed_endpoints = sum(1 for row in results_table.rows if row[2] == "✅")
    performance_met = sum(1 for row in results_table.rows if row[4] == "Yes")

    console.print("[bold]Summary:[/bold]")
    console.print(f"Total Endpoints: {total_endpoints}")
    console.print(f"Passed: {passed_endpoints}")
    console.print(f"Performance Requirements Met: {performance_met}")

    # Requirements check
    requirements_met = passed_endpoints == total_endpoints and performance_met == total_endpoints
    if requirements_met:
        console.print("\n[bold green]✅ All requirements met![/bold green]")
    else:
        console.print("\n[bold red]❌ Some requirements not met![/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
