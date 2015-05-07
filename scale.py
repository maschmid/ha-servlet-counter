#!/usr/bin/env python

import sys
import getopt
import re
import subprocess
from time import sleep

error_pattern = re.compile(r'Undeployed .*ROOT.war.*')

def scalingScenario(replicationController, namespace, label):

    replicas = 3

    iteration = 0

    while True:
        # Lets keep the instances running for 5 minutes
        sleep(60 * 5)

        iteration += 1
        print ("Logs after iteration %d:" % iteration)

        errorSpotted = None

        for pod, logline in readlogs(namespace, label):
            print "%s\t%s" % (pod, logline)
            if error_pattern.search(logline) != None:
                errorSpotted = pod

        if errorSpotted is not None:
            print ("Spotted error pattern in the %s logs, ending test" % errorSpotted)
            return

        if replicas == 2:
            replicas = 3
        else:
            replicas = 2

        print ("Scaling %s to %d replicas for the next iteration" % (replicationController, replicas))
        scale(replicationController, namespace, replicas)

def scale(replicationController, namespace, replicas):
    cmd = "osc update rc %s -n %s --patch='{\"apiVersion\": \"v1beta3\", \"spec\": {\"replicas\":%d}}'" % (replicationController, namespace, replicas)
    output = subprocess.check_output(cmd, shell=True)
    if output.strip() != replicationController:
        sys.stderr.write("Error executing %s\n" % cmd)
        sys.stderr.write("Please check if the replication controller '%s' exists in namespace '%s'\n" % (replicationController, namespace))
        sys.exit(4)

def getpods(namespace, label):
    p = subprocess.Popen("osc get pods -n %s | cut -f1 -d' ' | grep %s" % (namespace, label), shell=True, stdout=subprocess.PIPE)
    for line in p.stdout:
        yield line.rstrip()

def getlog(namespace, pod):
    p = subprocess.Popen("osc log %s -n %s" % (pod, namespace), shell=True, stdout=subprocess.PIPE)
    for line in p.stdout:
        yield line.rstrip()

def readlogs(namespace, label):
    for pod in getpods(namespace, label):
        for logline in getlog(namespace, pod):
            yield (pod, logline)

def usage():
    print ("%s -r replicationController -n namespace -l label" % sys.argv[0])

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hr:n:l:", ["help", "replicationController=", "namespace=", "label="])
    except getopt.GetoptError as err:
        print (str(err))
        usage()
        sys.exit(2)

    replicationController = None
    namespace = None
    label = None

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-r", "--replicationController"):
            replicationController = a
        elif o in ("-n", "--namespace"):
            namespace = a
        elif o in ("-l", "--label"):
            label = a
        else:
            assert False, "unhandled option"

    if namespace is None or replicationController is None or label is None:
        usage()
        sys.exit(3)

    scalingScenario(replicationController, namespace, label)

if __name__ == "__main__":
    main()

