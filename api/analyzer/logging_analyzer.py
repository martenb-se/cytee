import os
import logging
import sys

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
LOGGER_STDOUT = os.environ.get('LOGGER_STDOUT', '0').upper()

logging.basicConfig(
    level=LOGLEVEL,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s %(levelname)-8s %(message)s')

if LOGGER_STDOUT == "1":
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
