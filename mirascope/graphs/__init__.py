"""The `graphs` module for writing graphs in a declarative style.

This module provides graph interfacing for writing graphs as a collection of functions
that are marked as nodes. Simply calling the function for one node inside of another
node function indicates an edge.

The graph can run uncompiled, in which case it's simply a context management interface
that makes it easy to access / update a shared context across multiple functions.

Compiling the graph will construct the underlying graph represented by the implicit
edges defined in the code. The way a node function is executed inside of another node
function will determine the final node and edge structure of the graph.

For example, a node that calls another node and returns nothing will operate as it's own
node with an edge to the node it called. A node that calls another node and stores its
return value will split into two nodes, one for everything before the call, and one for
everything after.
"""

from .finite_state_machine import FiniteStateMachine, RunContext

__all__ = ["FiniteStateMachine", "RunContext"]
