import logging
import time
from videoanalyzer.source import CameraSource
from videoanalyzer.sink import MetadataLogger
from videoanalyzer.processor import HttpExtension
from videoanalyzer.pipeline import Pipeline
from typing import cast
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor
)

def main():
    logging.basicConfig(level=logging.INFO)
    trace.set_tracer_provider(TracerProvider())
    provider: TracerProvider = cast(TracerProvider, trace.get_tracer_provider())
    # provider.add_span_processor(
    #     SimpleSpanProcessor(ConsoleSpanExporter())
    # )

    url = 'http://localhost:8000/analyze'
    source = ('camera', CameraSource(0))
    processors = [
        ('http', 'camera', HttpExtension(url=url, max_samples_per_sec=2))
    ]
    sinks = [
        ('logger', 'http', MetadataLogger())
    ]
    pipeline = Pipeline(source=source, processors=processors, sinks=sinks)
    pipeline.start()
    time.sleep(5)
    pipeline.stop()

if __name__ == "__main__":
    main()