def filter_tree(function, root, copy=True):
    """Filters a navtree using `function(item)` where item is the navtree
    item - use `item.get('item')` for accessing the brain. If `function`
    returns `True`, the item is kept.

    The argument `root` is the root item of the navtree.
    Creates a deepcopy of the tree by default when `copy=True` (default).
    """

    item = copy and dict(root.items()) or root

    if not function(item):
        return None

    new_children = []
    for child in item.get('children'):
        child = filter_tree(function, child, copy=copy)
        if child:
            new_children.append(child)
    item['children'] = new_children

    return item


def modify_tree(function, root, parent=None):
    """Runs `function(node, parent)` for every node in a tree recursively,
    the function may modify the node.
    """

    function(root, parent)

    for node in root.get('children', []):
        modify_tree(function, node, parent=root)

    return root
