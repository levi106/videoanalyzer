import logging
import time
from typing import cast

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor
)

from videoanalyzer.pipeline import Pipeline
from videoanalyzer.sink import LocalVideoSink
from videoanalyzer.sink import MetadataLogger
from videoanalyzer.source import CameraSource


def main():
    trace.set_tracer_provider(TracerProvider())
    provider: TracerProvider = cast(
        TracerProvider, trace.get_tracer_provider())
#    provider.add_span_processor(
#        SimpleSpanProcessor(ConsoleSpanExporter())
#    )
    logging.basicConfig(level=logging.DEBUG)

    source = ('camera', CameraSource(0))
    sinks = [
        ('file', 'camera', LocalVideoSink(output_dir="/tmp/")),
        ('meta', 'camera', MetadataLogger())
    ]
    pipeline = Pipeline(source=source, sinks=sinks)
    pipeline.start()
    time.sleep(5)
    pipeline.stop()


if __name__ == "__main__":
    main()
