#!/usr/bin/python
import os 
import sys
import commands
import pprint
import atexit
from pyinotify import * 
import time
import signal

#UID - uid of the user to run certain commands when not root (default:1000)
#NOTIFY - to get libnotify desktop notifications (default:enabled)

class Mounty(object):
    def __int__(self):
       
        config={ 'NOTIFY':'1', \
         'LOG':'/var/log/mounty.log', \
         'MOUNT_POINT':'/media/', \
         'PID':'/var/run/mounty.pid', \
         'METHOD':'mount', \
         'UID':'1000', \
         'RELOAD':'1' \
         }
         CONFIG_FILE="/etc/mounty.tab"
         UDEV_LOC="/dev/disk/by-label/"
         mopts={}
         temp_str=""
         
         directory=UDEV_LOC
         mask=IN_CREATE|IN_DELETE
        
         if os.getuid() != 0:
             log.info("Running as non-root.....")

    def run(self):
        wm = WatchManager()
        wm.add_watch(directory,mask)
        self.m = Mounter(config)

        notifier=Notifier(wm,self,m,timeout=4)
        signal.signal(signal.SIGTERM,self.cleaner)
        signal.signal(signal.SIGUSR1,self.reload)
        signal.signal(signal.SIGUSR2,self.unmount)
        
        while True:
            time.sleep(6)
            handler()

    def handler(self):
        notifier.process_events()
        while notifier.check_events():  
            notifier.read_events()
            notifier.process_events()

    def cleaner(self,signum,frame):
        os.close(fd)

    def reload(self,signum,frame):
        m.reload()

    def unmount(self,signum,frame):
        m.unmount_removables()

    def parse(self):
    #{{{
        try:
            file=open(CONFIG_FILE,"r")
        except:
            temp_str+="Mounty tab missing"

        for line in file.readlines():
            if line.strip().startswith('#') or not line.strip('\n'):
                continue
            if line.strip().startswith('%'):
                t = line.strip().strip('%').split('=')
                config[str(t[0]).upper()] = str(t[1]).strip('\n')
                continue

            temp = line.split(' ')
            mopts[str(temp[0])] = []
            for j in temp[1:]:
                try:
                    mopts[str(temp[0])] += [str(j).strip('\n')]
                except:
                    temp_str += "Error in parsing "+str(j)
                    continue

        file.close()
    #}}}

os.system("echo -n "+str(os.getpid())+" >"+PID_FILE)
fd = os.open(LOG, os.O_WRONLY|os.O_CREAT)
os.dup2(fd,1)
os.dup2(fd,2)

if temp_str != "": 
    log.error(temp_str)
log.info(str(mopts))
log.info(str(config))



