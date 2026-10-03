#!/usr/bin/env python3
import asyncio
import json
import os
import websockets

active_desktops = {}
android_phone_socket = None

async def handle_routing_hub(websocket, path):
    global android_phone_socket
    peer_id = None
    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "REGISTER":
                role = data.get("role")
                peer_id = data.get("client_id")
                if role == "phone":
                    android_phone_socket = websocket
                    print(f"[SYSTEM] Gateway Phone Registered: {peer_id}")
                elif role == "desktop":
                    active_desktops[peer_id] = websocket
                    print(f"[SYSTEM] Desktop Operator Registered: {peer_id}")
            
            elif msg_type == "INCOMING_CALL":
                print(f"[RING] Call incoming from {data.get('number')}. Broadcasting to desktops...")
                for desktop_id, sock in list(active_desktops.items()):
                    try:
                        await sock.send(json.dumps(data))
                    except:
                        del active_desktops[desktop_id]

            elif msg_type == "OUTGOING_CALL":
                target_number = data.get("number")
                sender_id = data.get("sender_id")
                print(f"[DIAL] Outgoing call requested by {sender_id} to {target_number}. Forwarding to phone...")
                if android_phone_socket:
                    await android_phone_socket.send(json.dumps({
                        "type": "OUTGOING_CALL",
                        "number": target_number,
                        "sender_id": sender_id
                    }))
                else:
                    print("[WARNING] Gateway phone is not connected.")

            elif msg_type in ["OFFER", "ANSWER", "ICE_CANDIDATE"]:
                target = data.get("target_id")
                if target == "android_phone" and android_phone_socket:
                    await android_phone_socket.send(json.dumps(data))
                elif target in active_desktops:
                    await active_desktops[target].send(json.dumps(data))
                    
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if peer_id in active_desktops:
            del active_desktops[peer_id]
        elif websocket == android_phone_socket:
            android_phone_socket = None
            print("[SYSTEM] Gateway phone disconnected.")

async def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"[SERVER] Shao Call Sync Hub v3 online on port {port}...")
    async with websockets.serve(handle_routing_hub, "0.0.0.0", port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
