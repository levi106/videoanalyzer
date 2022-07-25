import logging
import signal

from .video_analyzer_edge_module import VideoAnalyzerEdgeModule


def main() -> None:
    logging.basicConfig(level=logging.INFO)
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
