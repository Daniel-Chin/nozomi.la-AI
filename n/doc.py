from typing import List, Optional
import json

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

  def __init__(self, json_data: dict = None):
    self.response: Optional[str] = None
    self.tags: List[Tag] = []
    self.img_urls: List[str] = []
    self.local_filenames: List[str] = []
    if json_data is not None:
      self.parse(json_data)
  
  def getImgUrls(self):
    result = []
    for x in self.img_urls:
      if x.startswith('https://i.nozomi.la'):
        x = x.replace('i.nozomi.la', 'w.nozomi.la')
        parts = x.split('.')
        x = '.'.join(parts[:-1]) + '.webp'
      result.append(x)
    return result

  def parse(self, json_data: dict):
    with open('./logs/last.json', 'w') as f:
      json.dump(json_data, f, indent=2)
    for tag_type in ('general', 'character', 'artist'):
      for x in json_data.get(tag_type, []):
        self.tags.append(Tag(
          x['tag'], x['tagname_display'], x['tagtype'], 
        ))
    if not self.tags:
      raise DocNotSuitable('Doc not tagged.')
    for x in json_data['imageurls']:
      # if not x['is_video']: # cannot be video. 
        dataid = x['dataid']
        ext = x['type']
        if ext == 'jpg':
          ext = 'webp'
        self.img_urls.append(f'''https://{
          ext[0]
        }.nozomi.la/{
          dataid[-1]
        }/{
          dataid[-3:-1]
        }/{dataid}.{ext}''')
    if not self.img_urls:
      raise DocNotSuitable('Doc has no non-video materials.')
    self.id = str(json_data['postid'])
    self.img_type: str = json_data['type']
    self.width: int = json_data['width']
    self.height: int = json_data['height']
    self.date: str = json_data['date']
  
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
