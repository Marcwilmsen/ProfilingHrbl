import numpy as np
import logging
import os.path


logger = logging.getLogger('py_gad')


def save_file(path, object):
    try:
        os.makedirs("./herbGA_cache")
    except FileExistsError:
        pass
    np.save(path, object)
    if file_exists(path):
        logging.debug("Temporary file created")


def load_file(path):
    logger.debug("Temporary file loaded")
    return np.load(path + ".npy")


def load_dictionary(path):
    logger.debug("Temporary file loaded")
    return np.load(path + ".npy", allow_pickle=True)


def delete_file(path):
    try:
        os.remove("./" + path + ".npy")
    except OSError as e:
        logger.error("Failed with:", e.strerror)

    if not file_exists(path):
        logger.debug("Temp.-file successfully deleted")


def file_exists(path):
    return os.path.isfile(path + ".npy")