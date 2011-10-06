def flaten_tree(item):
    """Accepts a navtree and returns a flat generator of every
    brain.
    """

    yield item.get('item')

    if item.get('children'):
        for subitem in item.get('children'):
            for brain in flaten_tree(subitem):
                yield brain
