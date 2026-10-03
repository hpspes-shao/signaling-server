# Shao Call Sync v3 - Complete Cloud Architecture

Support for both **Incoming Calls** (Computer ringing & answering) and **Outgoing Calls** (Dialing from PC via `--dial <number>`) over WebSocket signaling (`wss://signaling-server-aqmh.onrender.com`).

## Usage

### 1. Receive Calls on PC
```bash
python desktop_operator.py --id pc_reception
```

### 2. Dial Out from PC through Gateway Phone
```bash
python desktop_operator.py --id pc_office --dial +255700000000
```
