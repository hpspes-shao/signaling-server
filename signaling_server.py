#!/usr/bin/env python3
import asyncio
import json
import os
import websockets

nodes = {}

async def handle_pipeline(websocket, path):
    peer_id = None
    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "REGISTER":
                peer_id = data.get("client_id")
                nodes[peer_id] = websocket
                print(f"[SYSTEM] Node registered successfully: {peer_id}")

            elif msg_type in ["OFFER", "ANSWER", "ICE_CANDIDATE", "INCOMING_CALL", "CALL_ACCEPTED", "CALL_DISCONNECTED"]:
                target = data.get("target_id")
                if target in nodes:
                    await nodes[target].send(json.dumps(data))
                else:
                    print(f"[WARNING] Target node '{target}' not online.")

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if peer_id in nodes:
            del nodes[peer_id]
            print(f"[SYSTEM] Node disconnected: {peer_id}")

async def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"[SERVER] Control Plane online on port {port}")
    async with websockets.serve(handle_pipeline, "0.0.0.0", port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
