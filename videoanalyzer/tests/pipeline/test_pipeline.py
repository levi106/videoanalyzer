from unittest import mock

from videoanalyzer.pipeline.pipeline import Pipeline, State
from videoanalyzer.source._basesource import BaseSource
from videoanalyzer.sink._basesink import BaseSink
from videoanalyzer.processor._baseprocessor import BaseProcessor
from typing import Tuple, Dict, Any

def test_pipeline_create():
    source = BaseSource()
    sink = BaseSink()
    pipeline = Pipeline(source=('source', source), sinks=[('sink','source', sink)])
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
        ('sink1','source',sink1),
        ('sink2','source2',sink2)
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
        ('sink1','source',sink1),
        ('sink2','source',sink2)
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
        ('processor1','source',processor1),
        ('processor2','processor1',processor2)
    ]
    sink1 = BaseSink()
    sink2 = BaseSink()
    sinks = [
        ('sink1','processor1',sink1),
        ('sink2','processor2',sink2)
    ]
    pipeline = Pipeline(source=('source', source), processors=processors, sinks=sinks)
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

@mock.patch.object(BaseSource,'read')
@mock.patch.object(BaseSink,'write')
def test_pipeline_run_with_source_and_sink(sinkwrite_mock, sourceread_mock):
    source = BaseSource()
    sink = BaseSink()
    pipeline = Pipeline(source=('source', source), sinks=[('sink','source', sink)])

    def sinkwrite(*args, **kwargs):
        pipeline.stop()

    frame = b'\x00'
    props = {'prop1': 'value1'}
    def sourceread():
        return frame, props

    sinkwrite_mock.side_effect = sinkwrite
    sourceread_mock.side_effect = sourceread
    pipeline.start()
    sinkwrite_mock.assert_called_once_with(frame,props)
    sourceread_mock.assert_called_once()
    assert pipeline.state == State.Stopped