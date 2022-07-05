from videoanalyzer.pipeline._treebuilder import TreeBuilder

def test_tree_builder_add_in_order():
    builder = TreeBuilder('root', 'root')
    builder.append('child1', 'root', 'child1')
    builder.append('child2', 'child1', 'child2')
    root = builder.root
    assert root.name == 'root'
    assert len(root) == 1
    child = next(iter(root))
    assert child.name == 'child1'
    assert len(child) == 1
    child = next(iter(child))
    assert child.name == 'child2'
    assert len(child) == 0
    assert len(builder._tmp_nodes) == 0

def test_tree_builder_add_in_reverse_order():
    builder = TreeBuilder('root', 'root')
    builder.append('child2', 'child1', 'child2')
    builder.append('child1', 'root', 'child1')
    root = builder.root
    assert root.name == 'root'
    assert len(root) == 1
    child = next(iter(root))
    assert child.name == 'child1'
    assert len(child) == 1
    child = next(iter(child))
    assert child.name == 'child2'
    assert len(child) == 0
    assert len(builder._tmp_nodes) == 0

def test_tree_builder_has_branch():
    builder = TreeBuilder('root', 'root')
    builder.append('child2', 'child1', 'child2')
    builder.append('child1', 'root', 'child1')
    builder.append('child3', 'child1', 'child3')
    builder.append('child4', 'child2', 'child4')
    root = builder.root
    assert root.name == 'root'
    assert len(root) == 1
    child = next(iter(root))
    assert child.name == 'child1'
    assert len(child) == 2
    it = iter(child)
    child = next(it)
    assert child.name == 'child2'
    assert len(child) == 1
    child = next(iter(child))
    assert child.name == 'child4'
    assert len(child) == 0
    child = next(it)
    assert child.name == 'child3'
    assert len(child) == 0
    assert len(builder._tmp_nodes) == 0