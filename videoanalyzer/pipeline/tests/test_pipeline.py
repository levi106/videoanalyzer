import pytest

from ..pipeline import Pipeline
from ...source._basesource import BaseSource
from ...sink._basesink import BaseSink
from ...processor._baseprocessor import BaseProcessor

class TestSource(BaseSource):
    pass

class TestSink(BaseSink):
    pass

class TestProcessor(BaseProcessor):
    pass

def test_pipeline_create():
    source = TestSource()
    sink = TestSink()
    pipeline = Pipeline(source=('source', source), sinks=[('sink','source', sink)])
    root = pipeline._tree
    assert len(root) == 1
    assert root.name == 'source'
    child = next(iter(root))
    assert len(child) == 0
    assert child.name == 'sink'

def test_pipeline_create_with_isolated_sink():
    source = TestSource()
    sink1 = TestSink()
    sink2 = TestSink()
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
    source = TestSource()
    sink1 = TestSink()
    sink2 = TestSink()
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
    source = TestSource()
    processor1 = TestProcessor()
    processor2 = TestProcessor()
    processors = [
        ('processor1','source',processor1),
        ('processor2','processor1',processor2)
    ]
    sink1 = TestSink()
    sink2 = TestSink()
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