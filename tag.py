from ai import RES_FINE, RES_NEGATIVE, RES_SAVE, RES_WOW

class TagInfo:
  __slots__ = [
    'name', 'display', 'type', 
    'n_responses', 
  ]

  def __init__(self):
    self.n_responses = {
      RES_FINE: 0,
      RES_NEGATIVE: 0, 
      RES_SAVE: 0,
      RES_WOW: 0,
    }
  
  def parseTag(self, tag):
    self.name = tag.name
    self.display = tag.display
    self.type = tag.type
