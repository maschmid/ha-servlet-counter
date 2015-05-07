#!/usr/bin/env python

from threading import Thread, Lock
import cookielib, urllib2
import subprocess
import sys
from time import sleep
import datetime

consoleLock = Lock()

url = "http://hsc.cloudapps.example.com/Counter"

def log(msg):
    consoleLock.acquire()
    print ("%s\t%s" % (datetime.datetime.utcnow().isoformat(), msg))
    consoleLock.release()

def client_thread(i):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    count = 0

    while True:
        try:
            r = opener.open(url, timeout=10)

            output = r.read().strip()

            messageId, newCount = output.split(" ", 1)
            if count + 1 != int(newCount):
                log("Thread %d Unexpected count, expected %d, was %s" % (i, (count + 1), newCount))

            count = int(newCount)
        except Exception, e:
            log("Thread %d connection error: %s" % (i, e))

        sleep(1)

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print "Usage: %s <url>" % sys.argv[0]
        sys.exit(2)

    url = sys.argv[1]

    for i in range(8):
        thread = Thread(target = client_thread, args = (i, ))
        thread.daemon = True
        thread.start()

    while True:
        # just wait for a kill
        sleep(1)

