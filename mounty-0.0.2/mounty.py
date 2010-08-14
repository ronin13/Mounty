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

config={'NOTIFY':'1','LOG':'/var/log/mounty.log','MOUNT_POINT':'/media/','PID':'/var/run/mounty.pid','METHOD':'mount','UID':'1000','RELOAD':'1'}

temp_str=""
mount_file="/etc/mounty.tab"
UDEV_LOC="/dev/disk/by-label/"
try:
    file=open(mount_file,"r")
except:
    temp_str+="Mounty tab missing"

mopts={}

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

MOUNT_POINT=config['MOUNT_POINT']
PID_FILE=config['PID']
LOG=config['LOG']
NOTIFY=int(config['NOTIFY'])
UID=int(config['UID'])
method=config['METHOD']
do_reload=config['RELOAD']

os.system("echo "+str(os.getpid())+" >"+PID_FILE)
fd = os.open(LOG, os.O_WRONLY|os.O_CREAT)
os.dup2(fd,1)
os.dup2(fd,2)

if temp_str != "": 
    log.error(temp_str)
log.info(str(mopts))
log.info(str(config))


if NOTIFY == 1:
    try:
        import pynotify
        pynotify.init("Mounty")
    except:
        log.info("Pynotify not installed")

def handler():
    notifier.process_events()
    while notifier.check_events():  
        notifier.read_events()
        notifier.process_events()



def cleaner(signum,frame):
    #signal.alarm(0)
    os.close(fd)

 

 
#{{{
class Mounter(ProcessEvent):
    def __init__(self):
        self.notify("Mounty started")
        self.mount_list={}
        if int(do_reload) == 1:
            self.reload()

    def unmount_removables(self):
        for key in mopts.keys():
            if self.mount_list.has_key(key) and self.mount_list[key] == "1":
                try:
                    os.system("umount "+MOUNT_POINT+key)
                except:
                    log.error("Error in unmounting(possibly busy)"+filename)
        self.notify("All removable drives unmounted")

   #{{{
    def mount_path(self,key,filename):
        if not os.path.exists(MOUNT_POINT+filename):
            os.system("sudo -u #"+UID+" mkdir -p "+MOUNT_POINT+filename)
        if not os.path.exists(MOUNT_POINT+filename):
           os.system("sudo -u #"+UID+" mkdir -p "+MOUNT_POINT+filename)
        os.system(method+" -t "+mopts[key][0]+" -o "+mopts[key][1]+" "+UDEV_LOC+filename+" "+MOUNT_POINT+filename)
        log.info(method+" -t "+mopts[key][0]+" -o "+mopts[key][1]+" "+UDEV_LOC+filename+" "+MOUNT_POINT+filename)
        self.notify(filename+" mounted")
        self.mount_list[key]="1"
    #}}}

    def reload(self):
        try:
            os.system("mount -a")
        except:
            log.error("Error in mounting fstab drives")

        list = self.get_mounted()
        for key in mopts.keys():
            if key not in list and os.path.exists(UDEV_LOC+key):
                filename=key
                self.mount_path(key,filename)
            if key in list:
                self.mount_list[key]="1"

    def get_mounted(self):
        status,output=\
        commands.getstatusoutput("mount -l | grep -Eo '\[.*\]$' | tr -d '[]'")
        mount_list=[]
        for str in output.split('\n'):
            mount_list.append(str)
        return mount_list

    def notify(self,message):
        if NOTIFY != 1:
            log.info("Notifications disabled")
            return

        if method == "mount":
            try:
                os.seteuid(UID) 
            except:
                log.error("Error in privilege setting")
        try:
            pynotify.Notification("Mounty",message).show()
        except:
            log.error("Error in notifying... ignore if everything is fine")

        if method == "mount":
            try:
                os.seteuid(0)
            except:
                log.error("Error in privilege setting")

    #{{{
    def process_IN_DELETE(self,event):
        filename=event.name
        self.notify(filename+" detached")
        self.mount_list[filename]="0"

    def process_IN_CREATE(self,event):
       filename = event.name

       status,output = commands.getstatusoutput('cat /proc/mounts | /bin/grep -i '+filename) 
       if status == 0:
           log.warning(filename+" already mounted")
           return
      
       key=filename #.lower()
       if mopts.has_key(key):
           self.mount_path(key,filename)
       else:
           os.system(method+" "+UDEV_LOC+filename+" "+MOUNT_POINT+filename)
           log.info(method+" "+UDEV_LOC+filename+" "+MOUNT_POINT+filename)
           self.notify(filename+" mounted")
           self.mount_list[filename]="1"

    #}}}

#}}}


if os.getuid() != 0:
    log.info("Running as non-root.....")
    #exit()

directory=UDEV_LOC
mask=IN_CREATE|IN_DELETE

wm = WatchManager()
wm.add_watch(directory,mask)
m = Mounter()


def reload(signum,frame):
    m.reload()

def unmount(signum,frame):
    m.unmount_removables()

notifier=Notifier(wm,m,timeout=4)
signal.signal(signal.SIGTERM,cleaner)
#signal.signal(signal.SIGALRM,handler)
signal.signal(signal.SIGUSR1,reload)
signal.signal(signal.SIGUSR2,unmount)
#signal.alarm(5)

while True:
    time.sleep(6)
    handler()



