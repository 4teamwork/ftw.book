from ftw.book.browser.utils import filter_tree
from ftw.book.browser.utils import modify_tree


class BookTocTree(object):

    def __call__(self, tree):

        def filterer(item):
            brain = item.get('item')
            if brain.portal_type in ('Book', 'Chapter'):
                return True

            elif not getattr(brain, 'showTitle', None):
                return False

            elif getattr(brain, 'hideFromTOC', None):
                return False

            else:
                return True

        tree = filter_tree(filterer, tree, copy=True)

        def toc_number_prefix_adder(node, parent):
            num = node.get('toc_number', None)

            if num is None:
                # We are on the root node, which is the book - it has
                # no table of content number.
                node['toc_number'] = ''
                num = ''

            else:
                num = '%s.' % num

            for i, child in enumerate(node.get('children', []), 1):
                child['toc_number'] = num + str(i)

        return modify_tree(toc_number_prefix_adder, tree)
