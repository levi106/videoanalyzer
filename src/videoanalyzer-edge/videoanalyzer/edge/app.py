import logging
import os
import signal

from .video_analyzer_edge_module import VideoAnalyzerEdgeModule


def main() -> None:
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=LOGLEVEL)
    module = VideoAnalyzerEdgeModule()

    def module_termination_handler_(signal, frame) -> None:
        module.terminate()

    signal.signal(signal.SIGTERM, module_termination_handler_)

    try:
        module.run()
    except Exception:
        raise
    finally:
        module.shutdown()


if __name__ == "__main__":
    main()
