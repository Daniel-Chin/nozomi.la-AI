from ai import ALL_RESPONSES

class TagInfo:
  __slots__ = [
    'name', 'display', 'type', 
    'n_responses', 
  ]

  def __init__(self):
    self.n_responses = {}
    for response in ALL_RESPONSES:
      self.n_responses[response] = 0
  
  def parseTag(self, tag):
    self.name = tag.name
    self.display = tag.display
    self.type = tag.type
  
  def __str__(self):
    return f"<tag {self.name} {self.type} {self.n_responses}>"
  
  def sum(self):
    return sum([self.n_responses.get(x, 0) for x in ALL_RESPONSES])
