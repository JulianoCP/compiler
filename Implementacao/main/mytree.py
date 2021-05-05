from anytree import Node, RenderTree, AsciiStyle, PreOrderIter
from anytree.exporter import DotExporter
from anytree import NodeMixin, RenderTree

node_sequence = 0

class MyNode(NodeMixin):

  def __init__(self, name, parent=None, id=None, type=None, label=None, children=None):
    super(MyNode, self).__init__()
    global node_sequence

    if (id):
      self.id = id
    else:
      self.id = str(node_sequence) + ': ' + str(name)
        
    self.label = name
    self.name = name
    node_sequence = node_sequence + 1
    self.type = type
    self.parent = parent
    if children:
      self.children = children

  def clearChildren():
    self.children = None
    return
  def nodenamefunc(node):
    return '%s' % (node.name)

  def nodeattrfunc(node):
    return '%s' % (node.name)

  def edgeattrfunc(node, child):
    return ''

  def edgetypefunc(node, child):
    return '--'
