import asyncio
import json

import websockets

WS_URL = "ws://localhost:8000/ws/projects/3"


async def main():
    print(f"Connecting to {WS_URL}...\n")

    async with websockets.connect(WS_URL) as websocket:
        print("Connected. Waiting for events...\n")

        while True:
            message = await websocket.recv()

            payload = json.loads(message)

            print("=" * 60)
            print(json.dumps(payload, indent=2))
            print("=" * 60)
            print()


if __name__ == "__main__":
    asyncio.run(main())
