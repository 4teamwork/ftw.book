from ftw.book.browser.utils import filter_tree
from ftw.book.browser.utils import modify_tree


class BookTocTree(object):

    def __call__(self, tree):

        def filterer(item):
            return item.get('item').show_in_toc

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
