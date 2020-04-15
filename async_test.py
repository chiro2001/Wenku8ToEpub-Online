import asyncio
import random
import json


async def chapter(bid, vid, sem):
    async with sem:
        t = 1 + random.random()
        await asyncio.sleep(t)
        print('done', t)
        return ('%s %s' % (bid, vid)).encode()


async def volume(vid, chapters, sem_limit=10):
    sem = asyncio.Semaphore(sem_limit)
    chapter_data = [None for _ in range(len(chapters))]
    for i in range(len(chapters)):
        chapter_data[i] = chapter(chapters[i]['chapter_id'], vid, sem)
    res = await asyncio.wait(chapter_data)
    print(list(res[0])[0].result())
    return chapter_data


if __name__ == '__main__':
    test_js = '[{"volume_id":10728,"id":10728,"volume_name":"\u7b2c\u4e00\u5377","volume_order":10,"chapters":[{"chapter_id":104897,"chapter_name":"\u8f6c\u8f7d\u4fe1\u606f","chapter_order":1},{"chapter_id":104892,"chapter_name":"\u7b2c1\u8bdd \u4e24\u540dJK","chapter_order":10},{"chapter_id":104893,"chapter_name":"\u7b2c2\u8bdd \u5c31\u5bdd\u524d\u7684JK","chapter_order":20},{"chapter_id":104894,"chapter_name":"\u7b2c3\u8bdd \u5bb6\u52a1\u4e0eJK","chapter_order":30},{"chapter_id":104895,"chapter_name":"\u7b2c4\u8bdd \u8d2d\u7269\u4e0eJK","chapter_order":40},{"chapter_id":104896,"chapter_name":"\u7b2c5\u8bdd \u7535\u8111\u4e0eJK","chapter_order":50},{"chapter_id":104898,"chapter_name":"\u7b2c6\u8bdd \u610f\u5916\u4e0eJK","chapter_order":60},{"chapter_id":104899,"chapter_name":"\u7b2c7\u8bdd \u8840\u7f18\u4e0eJK","chapter_order":70},{"chapter_id":104900,"chapter_name":"\u7b2c8\u8bdd \u4f11\u606f\u65f6\u95f4\u4e0eJK","chapter_order":80},{"chapter_id":104901,"chapter_name":"\u7b2c9\u8bdd \u540d\u5b57\u4e0eJK","chapter_order":90},{"chapter_id":104902,"chapter_name":"\u7b2c10\u8bdd \u98df\u5802\u4e0e\u6211","chapter_order":100},{"chapter_id":104903,"chapter_name":"\u7b2c11\u8bdd \u517c\u804c\u4e0eJK","chapter_order":110},{"chapter_id":104904,"chapter_name":"\u7b2c12\u8bdd \u9752\u6885\u7af9\u9a6c\u4e0e\u6211","chapter_order":120},{"chapter_id":104905,"chapter_name":"\u7b2c13\u8bdd \u4f11\u606f\u65f6\u95f4\u4e0eJK\u2461","chapter_order":130},{"chapter_id":104906,"chapter_name":"\u7b2c14\u8bdd \u611f\u5192\u4e0eJK","chapter_order":140},{"chapter_id":104907,"chapter_name":"\u7b2c15\u8bdd \u88ad\u51fb\u4e0eJK","chapter_order":150},{"chapter_id":104908,"chapter_name":"\u7b2c16\u8bdd \u714e\u86cb\u4e0eJK","chapter_order":160},{"chapter_id":104909,"chapter_name":"\u540e\u8bb0","chapter_order":170},{"chapter_id":104910,"chapter_name":"\u63d2\u753b","chapter_order":180}]}]'
    test_data = json.loads(test_js)
    # volume_data = [None for _ in range(len(test_data))]
    # sem = None
    for i in range(len(test_data)):
        v = test_data[i]
        # volume_data[i] = volume(v['volume_id'], v['chapters'], sem)
        # asyncio.run(volume_data[i])
        asyncio.run(volume(v['volume_id'], v['chapters']))
