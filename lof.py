import time
import requests
import re
import pytz
import json
import os
import configparser
from datetime import datetime


class LOF:
    def __init__(self):
        self.cp = configparser.ConfigParser()
        self.cp.read("config.cfg", encoding="utf8")
        if "LOF" and "content" not in list(self.cp.sections()):
            raise Exception("Please create config.cfg first")
        self.content = self.cp._sections['content']
        self.LOFList = json.loads(self.cp.get('LOF','LOFList'))
        self.LOFList.sort()
        self.disLimit = self.cp.getfloat('LOF', 'disLimit')
        self.preLimit = self.cp.getfloat('LOF', 'preLimit')
        if self.disLimit < 0.: self.disLimit = 0.
        if self.preLimit > 0.: self.preLimit = 0.
        self.apiKey = self.cp.get('LOF', 'apiKey')

        self.session = requests.Session()
        header = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",}
        self.session.headers.update(header)
        self.urlBase = "https://www.jisilu.cn/data/lof/detail/"
        self.urlLOF = "https://www.jisilu.cn/data/lof/stock_lof_list/?___jsl=LST___t="
    
    def nextTime(self):
        now = time.localtime()

        year, mon, day, hour, minu = now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min
        if now.tm_hour >= 15:
            # Next day
            hour, minu = 9, 30
            if now.tm_mon == 12 and now.tm_mday == 31:
                year, mon, day = year + 1, 1, 1
            else:
                if now.tm_mday == 31 or now.tm_mday == 30 and now.tm_mon in [4, 6, 9, 11] or now.tm_mon == 2 and now.tm_mday >= 28:
                    mon, day = now.tm_mon + 1, 1
                else:
                    day += 1
        else:
            # Today
            if now.tm_hour < 9:
                hour, minu = 9, 30
            else:
                if now.tm_min < 30:
                    minu = 30
                else:
                    hour, minu = hour + 1, 0
        
        return time.mktime(time.strptime(" ".join(map(str, [year, mon, day, hour, minu])), "%Y %m %d %H %M"))

    def getInfo(self):
        r = self.session.get(self.urlLOF + str(int(time.time())*1000))
        if r.status_code == 200:
            return r.text
        else:
            return
    
    def save(self, t, text):
        t = time.localtime(t)
        
        d = "-".join(map(str, [t.tm_year, t.tm_mon]))
        f = "-".join(map(str, [t.tm_mday, t.tm_hour, t.tm_min]))
        if not os.path.exists(d):
            os.mkdir(d)

        with open(os.path.join(d, f), "w") as outFile:
            outFile.write(text)

    def message(self, key, title, body):
        msg_url = "https://sc.ftqq.com/{}.send?text={}&desp={}".format(key, title, body)
        requests.get(msg_url)

    def main(self):
        while True:
            nt = self.nextTime()
            print("Next time: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(nt)))
            time.sleep(nt - time.time())

            text = self.getInfo()
            if text:
                self.save(nt, text)


if __name__ == "__main__":
    lof = LOF()
    lof.main()
