import asyncio
import logging
import signal

from .video_analyzer_edge_module import VideoAnalyzerEdgeModule


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    module = VideoAnalyzerEdgeModule()

    def module_termination_handler_(signal, frame) -> None:
        module.terminate()

    signal.signal(signal.SIGTERM, module_termination_handler_)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(module.run())
    except Exception:
        raise
    finally:
        loop.run_until_complete(module.shutdown())
        loop.close()


if __name__ == "__main__":
    main()