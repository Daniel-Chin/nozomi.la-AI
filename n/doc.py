from collections import namedtuple

Tag = namedtuple('Tag', ['name', 'display', 'type'])

class DocNotSuitable(Exception): pass

class Doc:
  __slots__ = [
    'id', 'tags', 'img_urls', 'img_type',
    'width', 'height', 
    'date', 
    'response', 
    'local_filenames',
  ]

  def __init__(self, json = None):
    self.response = None
    self.tags = []
    self.img_urls = []
    self.local_filenames = []
    if json is not None:
      self.parse(json)

  def parse(self, json):
    # Must have >=1 tags. Must not have video. 
    for tag_type in ('general', 'character', 'artist'):
      for i in json.get(tag_type, []):
        self.tags.append(Tag(i['tag'], i['tagname_display'], i['tagtype']))
    if not self.tags:
      raise DocNotSuitable
    for i in json['imageurls']:
      if not i['is_video']:
        self.img_urls.append('https:' + i['imageurl'])
    if not self.img_urls:
      raise DocNotSuitable
    self.id = str(json['postid'])
    self.img_type = json['type']
    self.width = json['width']
    self.height = json['height']
    self.date = json['date']
  
  def getArtists(self):
    return [x.display for x in self.tags if x.type == 'artist']

  def __str__(self):
    return f"<doc {self.id} {self.response} {'saved' if self.local_filenames else ''}>"
