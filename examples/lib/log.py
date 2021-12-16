""" Initialize log files """
import os
import logging

_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
_LOG_FILE_PATH = os.path.join(_ROOT_PATH, '../logs')
_LOG_BACKUP_PATH = os.path.join(_LOG_FILE_PATH, 'prev')

def setup(filename, debug):
    """ Create handlers to log into a file and to console output"""
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s (%(name)s)', datefmt='%H:%M:%S')
    #logfile = os.path.join(_LOG_FILE_PATH, filename)
    #if os.path.isfile(logfile):
    #    old_path = os.path.join(_LOG_BACKUP_PATH, filename)
    #    os.rename(logfile, old_path)

    #handler = logging.FileHandler(logfile)
    #handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s (%(name)s)',
    #                                       datefmt='%H:%M:%S'))
    #logging.getLogger('').addHandler(handler)
