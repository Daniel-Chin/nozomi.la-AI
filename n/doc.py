from typing import List, Optional

from tag import Tag

class DocNotSuitable(Exception): pass

class Doc:
  __slots__ = [
    'id', 'tags', 'img_urls', 'img_type',
    'width', 'height', 
    'date', 
    'response', 
    'local_filenames',
  ]

  def __init__(self, json: dict = None):
    self.response: Optional[str] = None
    self.tags: List[Tag] = []
    self.img_urls: List[str] = []
    self.local_filenames: List[str] = []
    if json is not None:
      self.parse(json)

  def parse(self, json: dict):
    for tag_type in ('general', 'character', 'artist'):
      for x in json.get(tag_type, []):
        self.tags.append(Tag(
          x['tag'], x['tagname_display'], x['tagtype'], 
        ))
    if not self.tags:
      raise DocNotSuitable('Doc not tagged.')
    for x in json['imageurls']:
      if not x['is_video']: # cannot be video. 
        dataid = x['dataid']
        ext = x['type']
        self.img_urls.append(f'''https://w.nozomi.la/{
          dataid[-1]
        }/{
          dataid[-3:-1]
        }/{dataid}.webp''')
    if not self.img_urls:
      raise DocNotSuitable('Doc has no non-video materials.')
    self.id = str(json['postid'])
    self.img_type: str = json['type']
    self.width: int = json['width']
    self.height: int = json['height']
    self.date: str = json['date']
  
  def getArtists(self):
    return [x.display for x in self.tags if x.type == 'artist']

  def __repr__(self):
    return f"<doc {self.id} {self.response} {'saved' if self.local_filenames else ''}>"
  
  def __hash__(self) -> int:
    return hash(self.id)
  
  def __eq__(self, __o: object) -> bool:
    if isinstance(__o, __class__):
      return self.id == __o.id
    return False
