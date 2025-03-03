# Copyright © 2021 by Shun Huang. All rights reserved.
# Licensed under MIT License.
# See LICENSE in the project root for license information.

"""AVL Tree."""

from dataclasses import dataclass
from typing import Any, Optional

from trees import tree_exceptions

from trees.binary_trees import binary_tree


@dataclass
class AVLNode(binary_tree.Node):
    """AVL Tree node definition."""

    left: Optional["AVLNode"] = None
    right: Optional["AVLNode"] = None
    parent: Optional["AVLNode"] = None
    height: int = 0


class AVLTree(binary_tree.BinaryTree):
    """AVL Tree.

    Attributes
    ----------
    root: `Optional[AVLNode]`
        The root node of the binary search tree.
    empty: `bool`
        `True` if the tree is empty; `False` otherwise.

    Methods
    -------
    search(key: `Any`)
        Look for a node based on the given key.
    insert(key: `Any`, data: `Any`)
        Insert a (key, data) pair into a binary tree.
    delete(key: `Any`)
        Delete a node based on the given key from the binary tree.
    get_leftmost(node: `AVLNode`)
        Return the node whose key is the smallest from the given subtree.
    get_rightmost(node: `AVLNode`)
        Return the node whose key is the biggest from the given subtree.
    get_successor(node: `AVLNode`)
        Return the successor node in the in-order order.
    get_predecessor(node: `AVLNode`)
        Return the predecessor node in the in-order order.
    get_height(node: `Optional[AVLNode]`)
        Return the height of the given node.

    Examples
    --------
    >>> from trees.binary_trees import avl_tree
    >>> tree = avl_tree.AVLTree()
    >>> tree.insert(key=23, data="23")
    >>> tree.insert(key=4, data="4")
    >>> tree.insert(key=30, data="30")
    >>> tree.insert(key=11, data="11")
    >>> tree.insert(key=7, data="7")
    >>> tree.insert(key=34, data="34")
    >>> tree.insert(key=20, data="20")
    >>> tree.insert(key=24, data="24")
    >>> tree.insert(key=22, data="22")
    >>> tree.insert(key=15, data="15")
    >>> tree.insert(key=1, data="1")
    >>> tree.get_leftmost().key
    1
    >>> tree.get_leftmost().data
    '1'
    >>> tree.get_rightmost().key
    34
    >>> tree.get_rightmost().data
    "34"
    >>> tree.get_height(tree.root)
    4
    >>> tree.search(24).data
    `24`
    >>> tree.delete(15)
    """

    def __init__(self):
        binary_tree.BinaryTree.__init__(self)

    # Override
    def search(self, key: Any) -> AVLNode:
        """Look for an AVL node by a given key.

        See Also
        --------
        :py:meth:`trees.binary_trees.binary_tree.BinaryTree.search`.
        """
        current = self.root

        while current:
            if key < current.key:
                current = current.left
            elif key > current.key:
                current = current.right
            else:  # Key found
                return current  # type: ignore
        raise tree_exceptions.KeyNotFoundError(key=key)

    # Override
    def insert(self, key: Any, data: Any):
        """Insert a (key, data) pair into the AVL tree.

        See Also
        --------
        :py:meth:`trees.binary_trees.binary_tree.BinaryTree.insert`.
        """
        new_node = AVLNode(key=key, data=data)
        parent: Optional[AVLNode] = None
        current: Optional[AVLNode] = self.root
        while current:
            parent = current
            if new_node.key < current.key:
                current = current.left
            elif new_node.key > current.key:
                current = current.right
            else:
                raise tree_exceptions.DuplicateKeyError(key=new_node.key)
        new_node.parent = parent
        # If the tree is empty, set the new node to be the root.
        if parent is None:
            self.root = new_node
        else:
            if new_node.key < parent.key:
                parent.left = new_node
            else:
                parent.right = new_node

            # After the insertion, fix the broken AVL-tree-property.
            # If the parent has two children after inserting the new node,
            # it means the parent had one child before the insertion.
            # In this case, neither AVL-tree property breaks nor
            # heights update requires.
            if not (parent.left and parent.right):
                self._insert_fixup(new_node)

    # Override
    def delete(self, key: Any):
        """Delete the node by the given key.

        See Also
        --------
        :py:meth:`trees.binary_trees.binary_tree.BinaryTree.delete`.
        """
        deleting_node = self.search(key=key)
        if self.root and deleting_node:

            # Case: no child
            if (deleting_node.left is None) and (deleting_node.right is None):
                self._delete_no_child(deleting_node=deleting_node)
            # Case: Two children
            elif deleting_node.left and deleting_node.right:
                replacing_node = self.get_leftmost(node=deleting_node.right)
                # Replace the deleting node with the replacing node,
                # but keep the replacing node in place.
                deleting_node.key = replacing_node.key
                deleting_node.data = replacing_node.data
                if replacing_node.right:  # The replacing node cannot have left child.
                    self._delete_one_child(deleting_node=replacing_node)
                else:
                    self._delete_no_child(deleting_node=replacing_node)
            # Case: one child
            else:
                self._delete_one_child(deleting_node=deleting_node)

    # Override
    def get_leftmost(self, node: AVLNode) -> AVLNode:
        """Return the leftmost node from a given subtree.

        See Also
        --------
        :py:meth:`trees.binary_trees.binary_tree.BinaryTree.get_leftmost`.
        """
        current_node = node
        while current_node.left:
            current_node = current_node.left
        return current_node

    # Override
    def get_rightmost(self, node: AVLNode) -> AVLNode:
        """Return the rightmost node from a given subtree.

        See Also
        --------
        :py:meth:`trees.binary_trees.binary_tree.BinaryTree.get_rightmost`.
        """
        current_node = node
        if current_node:
            while current_node.right:
                current_node = current_node.right
        return current_node

    # Override
    def get_successor(self, node: AVLNode) -> Optional[AVLNode]:
        """Return the successor node in the in-order order.

        See Also
        --------
        :py:meth:`trees.binary_trees.binary_tree.BinaryTree.get_successor`.
        """
        if node.right:
            return self.get_leftmost(node=node.right)
        parent = node.parent
        while parent and node == parent.right:
            node = parent
            parent = parent.parent
        return parent

    # Override
    def get_predecessor(self, node: AVLNode) -> Optional[AVLNode]:
        """Return the predecessor node in the in-order order.

        See Also
        --------
        :py:meth:`trees.binary_trees.binary_tree.BinaryTree.get_predecessor`.
        """
        if node.left:
            return self.get_rightmost(node=node.left)
        parent = node.parent
        while parent and node == parent.left:
            node = parent
            parent = parent.parent
        return parent

    # Override
    def get_height(self, node: Optional[AVLNode]) -> int:
        """Return the height of the given node.

        See Also
        --------
        :py:meth:`trees.binary_trees.binary_tree.BinaryTree.get_height`.
        """
        if node:
            return node.height
        # None has height -1
        return -1

    def _get_balance_factor(self, node: Optional[AVLNode]):
        if node:
            return self.get_height(node.left) - self.get_height(node.right)
        # Empty node's height is -1
        return -1

    def _left_rotate(self, node_x: AVLNode):
        node_y = node_x.right  # Set node y
        if node_y:
            # Turn node y's subtree into node x's subtree
            node_x.right = node_y.left
            if node_y.left:
                node_y.left.parent = node_x
            node_y.parent = node_x.parent

            # If node's parent is a Leaf, node y becomes the new root.
            if node_x.parent is None:
                self.root = node_y
            # Otherwise, update node x's parent.
            elif node_x == node_x.parent.left:
                node_x.parent.left = node_y
            else:
                node_x.parent.right = node_y

            node_y.left = node_x
            node_x.parent = node_y

            node_x.height = 1 + max(
                self.get_height(node_x.left), self.get_height(node_x.right)
            )
            node_y.height = 1 + max(
                self.get_height(node_y.left), self.get_height(node_y.right)
            )

    def _right_rotate(self, node_x: AVLNode):
        node_y = node_x.left  # Set node y
        if node_y:
            # Turn node y's subtree into node x's subtree
            node_x.left = node_y.right
            if node_y.right:
                node_y.right.parent = node_x
            node_y.parent = node_x.parent

            # If node's parent is a Leaf, node y becomes the new root.
            if node_x.parent is None:
                self.root = node_y
            # Otherwise, update node x's parent.
            elif node_x == node_x.parent.right:
                node_x.parent.right = node_y
            else:
                node_x.parent.left = node_y

            node_y.right = node_x
            node_x.parent = node_y

            node_x.height = 1 + max(
                self.get_height(node_x.left), self.get_height(node_x.right)
            )
            node_y.height = 1 + max(
                self.get_height(node_y.left), self.get_height(node_y.right)
            )

    def _insert_fixup(self, new_node: AVLNode) -> None:
        parent = new_node.parent

        while parent:
            parent.height = 1 + max(
                self.get_height(parent.left), self.get_height(parent.right)
            )

            grandparent = parent.parent
            # grandparent is unbalanced
            if grandparent:
                if self._get_balance_factor(grandparent) > 1:
                    # Case Left-Left
                    if self._get_balance_factor(parent) >= 0:
                        self._right_rotate(grandparent)
                    # Case Left-Right
                    elif self._get_balance_factor(parent) < 0:
                        self._left_rotate(parent)
                        self._right_rotate(grandparent)
                    # Since the fixup does not affect the ancestor of the unbalanced
                    # node, exit the loop to complete the fixup process.
                    break
                elif self._get_balance_factor(grandparent) < -1:
                    # Case Right-Right
                    if self._get_balance_factor(parent) <= 0:
                        self._left_rotate(grandparent)
                    # Case Right-Left
                    elif self._get_balance_factor(parent) > 0:
                        self._right_rotate(parent)
                        self._left_rotate(grandparent)
                    # Since the fixup does not affect the ancestor of the unbalanced
                    # node, exit the loop to complete the fixup process.
                    break
            parent = parent.parent

    def _delete_no_child(self, deleting_node: AVLNode) -> None:
        parent = deleting_node.parent
        self._transplant(deleting_node=deleting_node, replacing_node=None)
        if parent:
            self._delete_fixup(fixing_node=parent)

    def _delete_one_child(self, deleting_node: AVLNode) -> None:
        parent = deleting_node.parent
        replacing_node = (
            deleting_node.right if deleting_node.right else deleting_node.left
        )
        self._transplant(deleting_node=deleting_node, replacing_node=replacing_node)
        if parent:
            self._delete_fixup(fixing_node=parent)

    def _transplant(
        self, deleting_node: AVLNode, replacing_node: Optional[AVLNode]
    ) -> None:
        if deleting_node.parent is None:
            self.root = replacing_node
        elif deleting_node == deleting_node.parent.left:
            deleting_node.parent.left = replacing_node
        else:
            deleting_node.parent.right = replacing_node

        if replacing_node:
            replacing_node.parent = deleting_node.parent

    def _delete_fixup(self, fixing_node: AVLNode) -> None:
        while fixing_node:
            fixing_node.height = 1 + max(
                self.get_height(fixing_node.left), self.get_height(fixing_node.right)
            )

            if self._get_balance_factor(fixing_node) > 1:
                # Case Left-Left
                if self._get_balance_factor(fixing_node.left) >= 0:
                    self._right_rotate(fixing_node)
                # Case Left-Right
                elif self._get_balance_factor(fixing_node.left) < 0:
                    # The fixing node's left child cannot be empty
                    self._left_rotate(fixing_node.left)  # type: ignore
                    self._right_rotate(fixing_node)

            elif self._get_balance_factor(fixing_node) < -1:
                # Case Right-Right
                if self._get_balance_factor(fixing_node.right) <= 0:
                    self._left_rotate(fixing_node)
                # Case Right-Left
                elif self._get_balance_factor(fixing_node.right) > 0:
                    # The fixing node's right child cannot be empty
                    self._right_rotate(fixing_node.right)  # type: ignore
                    self._left_rotate(fixing_node)

            fixing_node = fixing_node.parent  # type: ignore
