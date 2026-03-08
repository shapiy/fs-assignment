# Signal-ATAK Bot

A Python bot that bridges Signal messenger and ATAK (Android Team Awareness Kit). Send a geolocation message via Signal, and it appears as a map marker in ATAK.

## How It Works

```
Signal Message → signal-cli → Bot → CoT XML → UDP → ATAK
```

1. User sends a message to the bot via Signal: `48.567123 39.87897 tank`
2. The bot receives it from signal-cli's JSON-RPC interface
3. Parses coordinates and target description
4. Converts to [Cursor on Target (CoT)](https://www.mitre.org/sites/default/files/pdf/09_4937.pdf) XML
5. Sends CoT via UDP (unicast or multicast) to ATAK
6. Marker appears on the ATAK map

## Message Format

```
<latitude> <longitude> <description>
```

Examples:
```
48.567123 39.87897 tank
-33.8688 151.2093 vehicle convoy
50.4501 30.5234 infantry patrol
```

### Recognized Target Types

The first word of the description maps to a MIL-STD-2525 CoT type code:

| Keyword | CoT Type | Description |
|---|---|---|
| tank | a-h-G-U-C-A | Hostile armor |
| infantry | a-h-G-U-C-I | Hostile infantry |
| vehicle | a-h-G-U-C-V | Hostile vehicle |
| artillery | a-h-G-U-C-F | Hostile artillery |
| apc | a-h-G-U-C-A-W | Hostile APC |
| helicopter | a-h-A-C-H | Hostile helicopter |
| drone | a-h-A-C-F-q | Hostile drone/UAV |
| ship | a-h-S | Hostile ship |
| sniper | a-h-G-U-C-I-s | Hostile sniper |
| sam | a-h-G-U-C-D-A | Hostile SAM |
| *(other)* | a-h-G | Generic hostile |

## Setup

### Prerequisites

- [uv](https://docs.astral.sh/uv/) for Python dependency management
- [signal-cli](https://github.com/AsamK/signal-cli) (`brew install signal-cli` on macOS)
- A Signal account (phone number)
- ATAK/iTAK/WinTAK on the same network

### 1. Clone and install

```bash
git clone <repo-url> && cd signal-atak-bot
uv sync
```

### 2. Link signal-cli to your Signal account

```bash
signal-cli link -n signal-atak-bot
```

This prints a `sgnl://` URI. On your phone, open Signal > Settings > Linked Devices > Link New Device and scan the QR code (or paste the URI).

Once you see `Associated with: +<your-number>`, the link is complete.

### 3. Start signal-cli daemon

```bash
signal-cli -a <your-number> daemon --tcp localhost:7583 --http localhost:8080 --no-receive-stdout
```

### 4. Start the bot

```bash
SIGNAL_ACCOUNT=<your-number> uv run signal-atak-bot
```

### 5. Configure ATAK

In ATAK, ensure you're listening for CoT on the same network:
- Settings > Network Preferences > Network Connections
- Add a UDP input on port `6969` (or your configured port)
- If using multicast, join group `239.2.3.1`

## Testing

### Unit tests

```bash
uv run pytest -v
```

### Standalone CoT test (no Signal needed)

Terminal 1 -- mock ATAK receiver:
```bash
uv run python scripts/listen_cot.py
```

Terminal 2 -- send test marker:
```bash
uv run python scripts/send_test_cot.py 48.567123 39.87897 tank
```

You should see the CoT XML printed in Terminal 1.

### Test with real ATAK

```bash
uv run python scripts/send_test_cot.py 48.567123 39.87897 tank --host <ATAK_IP> --unicast
```

A hostile armor marker should appear on the ATAK map.

## Architecture

```
src/signal_atak_bot/
├── main.py              # Entry point, async event loop
├── signal_client.py     # JSON-RPC client for signal-cli (TCP + HTTP)
├── signal_handler.py    # Parses geolocation messages
├── cot_formatter.py     # Builds CoT XML from TargetReport
├── atak_sender.py       # Sends CoT XML over UDP
├── models.py            # TargetReport dataclass
└── config.py            # Settings from environment variables
```

## CoT Protocol

Cursor on Target (CoT) is an XML-based protocol used by ATAK and other tactical systems. Each event contains:

- **event**: Root element with `type` (target classification), `uid`, timestamps
- **point**: Latitude, longitude, altitude (HAE), circular/linear error
- **detail**: Additional metadata -- callsign, remarks, etc.

The bot sets `how="h-g-i-g-o"` (human-generated, derived from observation) and uses `ce/le="9999999"` (unknown precision).
