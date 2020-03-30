from ..exception import CTERAException
from ..common import Object


class DirectoryTree:

    def __init__(self, tree):
        self.root = self._decorate(tree)

    def _decorate(self, root):
        root._parent = None  # pylint: disable=protected-access
        nodes = [root]
        while nodes:
            node = nodes.pop(0)
            if self._has_children(node):
                for child_node in node.children:
                    child_node._parent = node  # pylint: disable=protected-access
                    nodes.append(child_node)
        return root

    def include_folder(self, path):
        self._configure_selection(path, True, True)

    def include_file(self, path):
        self._configure_selection(path, False, True)

    def exclude_folder(self, path):
        self._configure_selection(path, True, False)

    def exclude_file(self, path):
        self._configure_selection(path, False, False)

    def _configure_selection(self, path, is_dir, include):
        self._check_root_dir(path)
        node, parts = self._lookup(path)
        if not parts:
            if is_dir and not DirectoryTree._is_dir(node):
                raise CTERAException('Expected to find a directory but found file', None, path=path)
            if DirectoryTree._is_dir(node) and not is_dir:
                raise CTERAException('Expected to find a file but found a directory', None, path=path)
            node.isIncluded = include
            node.children = None
        else:
            self._populate_selection(node, parts, is_dir, include)

    def remove_selection(self, path):
        self._check_root_dir(path)
        node, parts = self._lookup(path)
        if not parts:
            if node._parent is not None:  # pylint: disable=protected-access
                self._remove_child(node._parent, node.name)  # pylint: disable=protected-access
            else:
                node.isIncluded = False
                node.children = None
        else:
            raise CTERAException('Could not find directory path', None, path=path)

    def select_all(self):
        self.root.isIncluded = True
        self.root.children = None

    def unselect_all(self):
        self.root.isIncluded = False
        self.root.children = None

    def _check_root_dir(self, path):
        parts = path.split('/')
        if self.root.name != parts[0]:
            raise CTERAException('Invalid root directory', None, input=parts[0], should_start_with=self.root.name)

    def _lookup(self, path):
        parts = path.split('/')[1:]
        node = self.root
        while parts:
            if self._has_children(node):
                child_name = parts.pop(0)
                child_node = self._get_child(node, child_name)
                if child_node is None:
                    parts.insert(0, child_name)
                    break
                node = child_node
            else:
                break
        return (node, parts)

    @staticmethod
    def _is_dir(node):
        return getattr(node, '_classname', 'DirEntry') == 'DirEntry'

    # pylint: disable=R0201
    def _has_children(self, node):
        return node.children is not None

    def _get_child(self, node, child_name):
        if self._has_children(node):
            for i in range(0, len(node.children)):
                if node.children[i].name == child_name:
                    return node.children[i]
        return None

    # pylint: disable=R0201
    def _add_child(self, parent, node):
        node._parent = parent  # pylint: disable=protected-access
        if parent.children is None:
            parent.children = []
        parent.children.append(node)

    def _remove_child(self, parent, child_name):
        child = None
        if self._has_children(parent):
            for i in range(0, len(parent.children)):
                if parent.children[i].name == child_name:
                    child = parent.children.pop(i)
                    if not parent.children:
                        parent.children = None
                    break
        return child

    def _populate_selection(self, parent, parts, is_dir, include):
        descendant_name = parts.pop()
        descendant = self._get_dir_entry(descendant_name, include) if is_dir else self._get_file_entry(descendant_name, include)
        for part in parts:
            child_node = self._get_dir_entry(part, parent.isIncluded)
            self._add_child(parent, child_node)
            parent = child_node
        self._add_child(parent, descendant)

    def _get_file_entry(self, name, include):
        return self._get_entry(False, name, include)

    def _get_dir_entry(self, name, include):
        return self._get_entry(True, name, include)

    def _get_entry(self, is_dir, name, include):
        param = Object()
        param.displayName = None
        param.name = name
        param.isIncluded = include
        if is_dir:
            param._classname = 'DirEntry'  # pylint: disable=protected-access
            param.children = None
        else:
            param._classname = 'FileEntry'  # pylint: disable=protected-access
        return param
