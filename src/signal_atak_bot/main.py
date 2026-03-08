import asyncio
import logging

from .atak_sender import send_cot
from .config import Config
from .cot_formatter import format_cot_event
from .signal_client import SignalClient
from .signal_handler import parse_target_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def run(config: Config):
    client = SignalClient(
        tcp_host=config.signal_tcp_host,
        tcp_port=config.signal_tcp_port,
        http_url=config.signal_http_url,
        account=config.signal_account,
    )

    logger.info("Bot started, listening for messages on %s:%s", config.signal_tcp_host, config.signal_tcp_port)

    async for envelope in client.listen():
        data_message = envelope.get("dataMessage")
        if not data_message:
            continue

        text = data_message.get("message")
        if not text:
            continue

        source = envelope.get("source")
        group_info = data_message.get("groupInfo")
        logger.info("Message from %s: %s", source, text)

        try:
            report = parse_target_message(text)
        except ValueError:
            continue

        cot_xml = format_cot_event(report, config)
        send_cot(cot_xml, config.atak_host, config.atak_port, config.atak_use_multicast)

        reply = (
            f"Target sent to ATAK: {report.description} "
            f"at ({report.latitude}, {report.longitude})"
        )
        logger.info(reply)

        if group_info:
            await client.send_group_message(group_info["groupId"], reply)
        elif source:
            await client.send_message(source, reply)


def main():
    config = Config()
    asyncio.run(run(config))


if __name__ == "__main__":
    main()
