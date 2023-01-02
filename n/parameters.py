from typing import Optional

DEBUG: bool = False
EXPERT: bool = True

EXPLORE_PROB: float = .03
ATTITUDE_TOWARDS_NOVEL_TAGS: float = 1.0
PORT: int = 2348
MAX_WORKERS: int = 32

START_BATCH: int = 2000
BATCH_SIZE: int = 256
JOB_POOL_SIZE: int = 16
JOB_POOL_THROTTLE: float = 3.0
VIEW_RATIO: float = .003
FILTER: Optional[str] = None

# START_BATCH: int = 0
# BATCH_SIZE: int = 64
# # BATCH_SIZE: int = 256
# JOB_POOL_SIZE: int = 6
# JOB_POOL_THROTTLE: float = 2.0
# VIEW_RATIO: float = .1
# FILTER: Optional[str] = '''
# '''.strip()

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
