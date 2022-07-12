import time
from videoanalyzer.source import CameraSource
from videoanalyzer.sink import LocalVideoSink
from videoanalyzer.pipeline import Pipeline
from typing import cast
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor
)


def main():
    trace.set_tracer_provider(TracerProvider())
    provider: TracerProvider = cast(
        TracerProvider, trace.get_tracer_provider())
    provider.add_span_processor(
        SimpleSpanProcessor(ConsoleSpanExporter())
    )

    source = ('camera', CameraSource(0))
    sinks = [
        ('file', 'camera', LocalVideoSink(output_dir="/tmp/"))
    ]
    pipeline = Pipeline(source=source, sinks=sinks)
    pipeline.start()
    time.sleep(5)
    pipeline.stop()


if __name__ == "__main__":
    main()
