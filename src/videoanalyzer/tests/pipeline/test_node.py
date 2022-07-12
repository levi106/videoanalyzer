from videoanalyzer.pipeline._node import Node

def test_node_create_valid_tree():
    root = Node("root", 0, [])
    child1_1 = Node("child1_1", 1, [])
    child1_2 = Node("child1_2", 2, [])
    child2_1 = Node("child2_1", 3, [])
    root.add_child(child1_1)
    root.add_child(child1_2)
    child1_1.add_child(child2_1)
    assert len(root) == 2
    assert root.name == "root"
    assert root.data == 0
    iterator1 = iter(root)
    child1 = next(iterator1)
    assert len(child1) == 1
    assert child1.name == "child1_1"
    assert child1.data == 1
    iterator2 = iter(child1)
    child2 = next(iterator2)
    assert len(child2) == 0
    assert child2.name == "child2_1"
    assert child2.data == 3
    child1 = next(iterator1)
    assert len(child1) == 0
    assert child1.name == "child1_2"
    assert child1.data == 2

def test_node_find_name():
    root = Node("root", 0, [])
    child1_1 = Node("child1_1", 1, [])
    child1_2 = Node("child1_2", 2, [])
    child2_1 = Node("child2_1", 3, [])
    root.add_child(child1_1)
    root.add_child(child1_2)
    child1_1.add_child(child2_1)
    assert root.find_node("root") == root
    assert root.find_node("child1_1") == child1_1
    assert root.find_node("child1_2") == child1_2
    assert root.find_node("child2_1") == child2_1
    assert root.find_node("child2_2") == None
    