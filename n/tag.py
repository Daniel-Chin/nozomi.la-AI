from typing import Dict

from shared import *

class Tag:
  __slots__ = [
    'name', 'display', 'type', 
  ]

  def __init__(self, name, display, _type):
    self.name: str = name
    self.display: str = display
    self.type: str = _type
  
  def __repr__(self):
    return f"<tag {self.type} {self.name}>"

class TagInfo:
  __slots__ = [
    'tag', 'responses', 
  ]

  def __init__(self, tag):
    self.tag: Tag = tag
    self.responses: Dict[str, int] = {}
  
  def sum(self):
    return sum([self.responses.get(x, 0) for x in ALL_RESPONSES])

  def __repr__(self):
    return f'<tagInfo {self.tag} {self.responses}>'
