import os
import logging
import sys

logging.basicConfig(
    level=os.environ.get('LOGLEVEL', 'WARNING').upper(),
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s %(levelname)-8s %(message)s')
