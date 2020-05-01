# coding: UTF-8
import os, json, sys


def getTree(path):
    rs = {}
    for filename in os.listdir(path):

        print("filename :", filename)
        tmpname = os.path.join(path, filename)
        if os.path.isdir(tmpname):
            rs[filename] = getTree(tmpname)
        else:
            justname = filename[:filename.rfind('.'):]

            # if rs.has_key(justname):
            if justname in rs:
                rs[justname].append(filename)
            else:
                rs[justname] = [filename]
    return rs


def writeMetadata(rsjson):
    ff = open("metadata.json", mode='w')

    ff.write(json.dumps(rsjson, indent=4, encoding='gbk').encode('utf8'))
    ff.close()


def generateMetadataXml():
    rsjson = getTree('.')
    # if rsjson.has_key('generate'):
    if 'generate' in rsjson:
        rsjson.pop('generate')

    # if rsjson.has_key('metadata'):
    if 'metadata' in rsjson:
        rsjson.pop('metadata')

    writeMetadata(rsjson)


def getFile(jjson, paths):
    if len(paths) == 1:
        if paths[0] == '':
            return jjson
        # elif jjson.has_key(paths[0]):
        elif paths[0] in jjson:

            return jjson[paths[0]]
        else:
            print('Jjson', json.dumps(jjson))
            print('No this Key:', paths[0])
            return None
    elif len(paths) > 1:
        return getFile(jjson[paths[0]], paths[1:])


if __name__ == '__main__':
    generateMetadataXml()

    # rsjson=getTree(".")
    # print json.dumps(rsjson,encoding='gbk')
    # print getFile(rsjson, '/佛学'.split('/')[1:])

    pass
