import pytest

from ..pipeline import Pipeline
from ...source._basesource import BaseSource
from ...sink._basesink import BaseSink

class TestSource(BaseSource):
    pass

class TestSink(BaseSink):
    pass

def test_pipeline_create():
    source = TestSource()
    sink = TestSink()
    pipeline = Pipeline(source=('source', source), sinks={'sink': ('source', sink)})
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
    sinks = {
        'sink1': ('source',sink1),
        'sink2': ('source2',sink2)
    }
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
    sinks = {
        'sink1': ('source',sink1),
        'sink2': ('source',sink2)
    }
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
