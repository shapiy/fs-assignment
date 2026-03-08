import os
from dataclasses import dataclass, field


@dataclass
class Config:
    signal_tcp_host: str = field(
        default_factory=lambda: os.environ.get("SIGNAL_TCP_HOST", "localhost")
    )
    signal_tcp_port: int = field(
        default_factory=lambda: int(os.environ.get("SIGNAL_TCP_PORT", "7583"))
    )
    signal_http_url: str = field(
        default_factory=lambda: os.environ.get("SIGNAL_HTTP_URL", "http://localhost:8080")
    )
    signal_account: str = field(
        default_factory=lambda: os.environ.get("SIGNAL_ACCOUNT", "")
    )
    atak_host: str = field(
        default_factory=lambda: os.environ.get("ATAK_HOST", "239.2.3.1")
    )
    atak_port: int = field(
        default_factory=lambda: int(os.environ.get("ATAK_PORT", "6969"))
    )
    atak_use_multicast: bool = field(
        default_factory=lambda: os.environ.get("ATAK_USE_MULTICAST", "true").lower()
        == "true"
    )
    cot_stale_minutes: int = field(
        default_factory=lambda: int(os.environ.get("COT_STALE_MINUTES", "5"))
    )
    bot_callsign: str = field(
        default_factory=lambda: os.environ.get("BOT_CALLSIGN", "SIGBOT")
    )
