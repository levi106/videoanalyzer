from typing import cast
from unittest import mock

import pytest

from videoanalyzer.pipeline.pipeline import Pipeline, State
from videoanalyzer.processor._baseprocessor import BaseProcessor
from videoanalyzer.sink._basesink import BaseSink
from videoanalyzer.source._basesource import BaseSource
from videoanalyzer.source.rtspsource import RtspSource


class TestSource1(BaseSource):
    def __init__(self, name):
        self.name = name


class TestSink1(BaseSink):
    def __init__(self, name):
        self.name = name


class TestSink2(BaseSink):
    def __init__(self, name):
        self.name = name


class TestProcessor1(BaseProcessor):
    def __init__(self, name):
        self.name = name


class TestProcessor2(BaseProcessor):
    def __init__(self, name):
        self.name = name


def test_pipeline_create():
    source = BaseSource()
    sink = BaseSink()
    pipeline = Pipeline(source=('source', source),
                        sinks=[('sink', 'source', sink)])
    root = pipeline._tree
    assert len(root) == 1
    assert root.name == 'source'
    child = next(iter(root))
    assert len(child) == 0
    assert child.name == 'sink'


def test_pipeline_create_with_isolated_sink():
    source = BaseSource()
    sink1 = BaseSink()
    sink2 = BaseSink()
    sinks = [
        ('sink1', 'source', sink1),
        ('sink2', 'source2', sink2)
    ]
    pipeline = Pipeline(source=('source', source), sinks=sinks)
    root = pipeline._tree
    assert len(root) == 1
    assert root.name == 'source'
    child = next(iter(root))
    assert len(child) == 0
    assert child.name == 'sink1'
    assert len(pipeline._sinks) == 2


def test_pipeline_create_with_multiple_sink():
    source = BaseSource()
    sink1 = BaseSink()
    sink2 = BaseSink()
    sinks = [
        ('sink1', 'source', sink1),
        ('sink2', 'source', sink2)
    ]
    pipeline = Pipeline(source=('source', source), sinks=sinks)
    root = pipeline._tree
    assert len(root) == 2
    assert root.name == 'source'
    it = iter(root)
    child = next(it)
    assert len(child) == 0
    assert child.name == 'sink1'
    child = next(it)
    assert len(child) == 0
    assert child.name == 'sink2'


def test_pipeline_create_with_multiple_pipeline_and_sink():
    source = BaseSource()
    processor1 = BaseProcessor()
    processor2 = BaseProcessor()
    processors = [
        ('processor1', 'source', processor1),
        ('processor2', 'processor1', processor2)
    ]
    sink1 = BaseSink()
    sink2 = BaseSink()
    sinks = [
        ('sink1', 'processor1', sink1),
        ('sink2', 'processor2', sink2)
    ]
    pipeline = Pipeline(source=('source', source),
                        processors=processors, sinks=sinks)
    root = pipeline._tree
    assert len(root) == 1
    assert root.name == 'source'
    it = iter(root)
    child = next(it)
    assert len(child) == 2
    assert child.name == 'processor1'
    it = iter(child)
    child = next(it)
    assert len(child) == 1
    assert child.name == 'processor2'
    child = next(iter(child))
    assert len(child) == 0
    assert child.name == 'sink2'
    child = next(it)
    assert len(child) == 0
    assert child.name == 'sink1'


@mock.patch.object(BaseSource, 'read')
@mock.patch.object(BaseSink, 'write')
def test_pipeline_run_with_source_and_sink(sinkwrite_mock, sourceread_mock):
    source = BaseSource()
    sink = BaseSink()
    pipeline = Pipeline(source=('source', source),
                        sinks=[('sink', 'source', sink)])

    def sinkwrite(*args, **kwargs):
        pipeline.stop()

    frame = b'\x00'
    props = {'prop1': 'value1'}

    def sourceread():
        return frame, props

    sinkwrite_mock.side_effect = sinkwrite
    sourceread_mock.side_effect = sourceread
    pipeline.start()
    sinkwrite_mock.assert_called_once_with(frame, props)
    sourceread_mock.assert_called_once()
    assert pipeline.state == State.Stopped


def test_pipeline_create_from_json():
    jsonData = """
{
    "name": "TestPipeline1",
    "@apiVersion": "1.0",
    "properties": {
        "source": {
            "@type": "videoanalyzer.source._basesource.BaseSource",
            "name": "source"
        },
        "processors": [
            {
                "@type": "videoanalyzer.processor._baseprocessor.BaseProcessor",
                "name": "processor",
                "input": {
                    "nodeName": "source"
                }
            }
        ],
        "sinks": [
            {
                "@type": "videoanalyzer.sink._basesink.BaseSink",
                "name": "sink",
                "input": {
                    "nodeName": "processor"
                }
            }
        ]
    }
}
"""
    pipeline = Pipeline.create_from_json(jsonData)

    root = pipeline._tree
    assert root.name == 'source'
    assert type(root.data) is BaseSource
    assert len(root) == 1
    it = iter(root)
    child = next(it)
    assert child.name == 'processor'
    assert type(child.data) is BaseProcessor
    assert len(child) == 1
    it = iter(child)
    child = next(it)
    assert child.name == 'sink'
    assert type(child.data) is BaseSink
    assert len(child) == 0


def test_pipeline_create_from_json_with_param():
    jsonData = """
{
    "name": "TestPipeline1",
    "@apiVersion": "1.0",
    "properties": {
        "source": {
            "@type": "videoanalyzer.source.RtspSource",
            "name": "source",
            "parameters": {
                "url": "http://localhost"
            }
        },
        "processors": [
            {
                "@type": "videoanalyzer.processor._baseprocessor.BaseProcessor",
                "name": "processor",
                "input": {
                    "nodeName": "source"
                }
            }
        ],
        "sinks": [
            {
                "@type": "videoanalyzer.sink._basesink.BaseSink",
                "name": "sink",
                "input": {
                    "nodeName": "processor"
                }
            }
        ]
    }
}
"""
    pipeline = Pipeline.create_from_json(jsonData)

    root = pipeline._tree
    assert root.name == 'source'
    assert type(root.data) is RtspSource
    assert len(root) == 1
    it = iter(root)
    child = next(it)
    assert child.name == 'processor'
    assert type(child.data) is BaseProcessor
    assert len(child) == 1
    it = iter(child)
    child = next(it)
    assert child.name == 'sink'
    assert type(child.data) is BaseSink
    assert len(child) == 0


def test_pipeline_create_from_json_raise_exception_if_json_has_invalid_api_version():
    jsonData = """
{
    "name": "TestPipeline1",
    "@apiVersion": "0.0",
    "properties": {
        "source": {
            "@type": "videoanalyzer.source._basesource.BaseSource",
            "name": "source"
        },
        "sinks": [
            {
                "@type": "videoanalyzer.sink._basesink.BaseSink",
                "name": "sink",
                "input": {
                    "nodeName": "source"
                }
            }
        ]
    }
}
"""
    with pytest.raises(Exception) as e:
        _ = Pipeline.create_from_json(jsonData)
    assert str(e.value) == 'Invalid API version 0.0'


def test_pipeline_create_from_json_raise_exception_if_name_does_not_exist():
    jsonData = """
{
    "@apiVersion": "1.0",
    "properties": {
        "source": {
            "@type": "videoanalyzer.source._basesource.BaseSource",
            "name": "source"
        },
        "sinks": [
            {
                "@type": "videoanalyzer.sink._basesink.BaseSink",
                "name": "sink",
                "input": {
                    "nodeName": "source"
                }
            }
        ]
    }
}
"""
    with pytest.raises(KeyError) as e:
        _ = Pipeline.create_from_json(jsonData)
    assert str(e.value) == "'name'"


def test_pipeline_get_test_processor1():
    source = BaseSource()
    processor1_1 = TestProcessor1('processor1_1')
    processor1_2 = TestProcessor1('processor1_2')
    processor2_1 = TestProcessor2('processor2_1')
    processors = [
        ('processor1_1', 'source', processor1_1),
        ('processor1_2', 'source', processor1_2),
        ('processor2_1', 'source', processor2_1)
    ]
    sink1_1 = TestSink1('sink1_1')
    sink1_2 = TestSink1('sink1_2')
    sink2_1 = TestSink2('sink2_1')
    sinks = [
        ('sink1_1', 'processor1_1', sink1_1),
        ('sink1_2', 'processor1_2', sink1_2),
        ('sink2_1', 'processor2_1', sink2_1)
    ]
    pipeline = Pipeline(source=('source', source), processors=processors, sinks=sinks)
    result = pipeline.get_processor(TestProcessor1)
    assert len(result) == 2
    assert cast(TestProcessor1, result[0]).name == 'processor1_1'
    assert cast(TestProcessor1, result[1]).name == 'processor1_2'


def test_pipeline_get_test_sink1():
    source = BaseSource()
    processor1_1 = TestProcessor1('processor1_1')
    processor1_2 = TestProcessor1('processor1_2')
    processor2_1 = TestProcessor2('processor2_1')
    processors = [
        ('processor1_1', 'source', processor1_1),
        ('processor1_2', 'source', processor1_2),
        ('processor2_1', 'source', processor2_1)
    ]
    sink1_1 = TestSink1('sink1_1')
    sink1_2 = TestSink1('sink1_2')
    sink2_1 = TestSink2('sink2_1')
    sinks = [
        ('sink1_1', 'processor1_1', sink1_1),
        ('sink1_2', 'processor1_2', sink1_2),
        ('sink2_1', 'processor2_1', sink2_1)
    ]
    pipeline = Pipeline(source=('source', source), processors=processors, sinks=sinks)
    result = pipeline.get_sink(TestSink1)
    assert len(result) == 2
    assert cast(TestSink1, result[0]).name == 'sink1_1'
    assert cast(TestSink1, result[1]).name == 'sink1_2'


def test_pipeline_get_test_source1():
    source = TestSource1('source_1')
    processor1_1 = TestProcessor1('processor1_1')
    processor1_2 = TestProcessor1('processor1_2')
    processor2_1 = TestProcessor2('processor2_1')
    processors = [
        ('processor1_1', 'source', processor1_1),
        ('processor1_2', 'source', processor1_2),
        ('processor2_1', 'source', processor2_1)
    ]
    sink1_1 = TestSink1('sink1_1')
    sink1_2 = TestSink1('sink1_2')
    sink2_1 = TestSink2('sink2_1')
    sinks = [
        ('sink1_1', 'processor1_1', sink1_1),
        ('sink1_2', 'processor1_2', sink1_2),
        ('sink2_1', 'processor2_1', sink2_1)
    ]
    pipeline = Pipeline(source=('source', source), processors=processors, sinks=sinks)
    result = pipeline.get_source()
    assert cast(TestSource1, result).name == 'source_1'
