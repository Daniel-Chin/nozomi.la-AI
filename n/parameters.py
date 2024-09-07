from typing import Optional
from math import ceil

DEBUG: bool = False
EXPERT: bool = True

IMG_DOWNLOAD_IN_BROWSER = True

EXPLORE_PROB: float = .05
ATTITUDE_TOWARDS_NOVEL_TAGS: float = 1.0
PORT: int = 2348
MAX_WORKERS: int = 32

# START_BATCH: int = 0
START_BATCH: int = 300
# START_BATCH: int = 2000
# JOB_POOL_SIZE: int = 6
JOB_POOL_SIZE: int = 8
JOB_POOL_THROTTLE: float = 2.0
VIEW_RATIO: float = .007
BATCH_SIZE: int = ceil(6 / VIEW_RATIO / 64) * 64
FILTER: Optional[str] = None

# START_BATCH: int = 0
# # BATCH_SIZE: int = 64
# # BATCH_SIZE: int = 256
# JOB_POOL_SIZE: int = 8
# JOB_POOL_THROTTLE: float = 2.0
# VIEW_RATIO: float = .01
# BATCH_SIZE: int = ceil(6 / VIEW_RATIO / 64) * 64
# FILTER: Optional[str] = '''
# '''.strip()
# '''
# '''
# assert FILTER is not None and FILTER != ''

# Below are default values. 
# DEBUG: bool = False
# EXPERT: bool = False
# START_BATCH: int = 2000

# EXPLORE_PROB: float = .05
# BATCH_SIZE: int = 64
# VIEW_RATIO: float = .01
# ATTITUDE_TOWARDS_NOVEL_TAGS: float = 1.0

# JOB_POOL_SIZE: int = 4
# JOB_POOL_THROTTLE: float = 1.0
# PORT: int = 2348

# FILTER: Optional[str] = None

assert VIEW_RATIO * BATCH_SIZE > 1
