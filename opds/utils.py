import datetime
import json
import logging
import opds.filesystem as filesystem

__author__ = 'lei'


# #connect path
# 不是你这啥用处
def connect_path(base, name):
    if base is None or name is None:
        # print(base, name)
        return None
    # if name.startswith('/'):
    if len(name) == 0:
        return base
    if name[0] == '/':
        name = name[1:]

    if base[-1] == '/':
        return base + name
    else:
        return base + '/' + name


def getNow():
    return datetime.datetime.now().strftime("%Y-%m-%dT%I:%M:%SZ")


def getUpdateTime(name, default=None):
    if default is None:
        default = getNow()
    result = filesystem.bookdata.get(name, default)
    if type(result) is dict:
        result = result['last_modified']
    return result


def getFile(jjson, paths):
    '''
    get json object
    :param jjson:   json object
    :param paths:   json path
    :return:        json object
    '''
    try:
        if len(paths) == 1:
            if paths[0] == '':
                return jjson
            # elif jjson.has_key(paths[0]):
            elif paths[0] in jjson:

                return jjson[paths[0]]
            else:
                logging.warn('Jjson', json.dumps(jjson))
                logging.warn('No this Key:', paths[0])
                return None
        elif len(paths) > 1:
            return getFile(jjson[paths[0]], paths[1:])
    except AttributeError as e:
        logging.error(e)
        return None
