#!/usr/bin/python
import os 
import sys
import commands
import pprint
import atexit
from pyinotify import * 

#UID - uid of the user to run certain commands when not root (default:1000)
#NOTIFY - to get libnotify desktop notifications (default:enabled)

config={'NOTIFY':'1','LOG':'/tmp/mounty.log','MOUNT_POINT':'/media/','PID':'/tmp/mounty.pid','METHOD':'mount','UID':'1000'}

temp_str=""
mount_file="/etc/mounty.tab"
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
    mopts[str(temp[0]).lower()] = []
    for j in temp[1:]:
        try:
            mopts[str(temp[0]).lower()] += [str(j).strip('\n')]
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

os.dup2(os.open(LOG, os.O_WRONLY|os.O_CREAT),1)
os.dup2(os.open(LOG, os.O_WRONLY|os.O_CREAT),2)

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
   
class Mounter(ProcessEvent):
    def __init__(self):
        self.notify("Mounty started")
        pass

    def notify(self,message):
        if NOTIFY != 1:
            log.info("Notifications disabled")
            return

        try:
            if method == "mount":
                try:
                    os.seteuid(UID) 
                except:
                    log.error("Error in privilege setting")
            pynotify.Notification("Mounty",message).show()
            if method == "mount":
                try:
                    os.seteuid(0)
                except:
                    log.error("Error in privilege setting")
        except:
            log.error("Error in notification")

    def process_IN_DELETE(self,event):
        filename=event.name
        self.notify(filename+" detached")

    def process_IN_CREATE(self,event):
       filename = event.name

       status,output = commands.getstatusoutput('cat /proc/mounts | /bin/grep -i '+filename) 
       if status == 0:
           log.warning(filename+" already mounted")
           return

       # It is better if mount points have been created before itself
       if not os.path.exists(MOUNT_POINT+filename):
           os.system("sudo -u #"+UID+" mkdir -p "+MOUNT_POINT+filename)
           log.info("sudo -u #"+UID+" mkdir -p "+MOUNT_POINT+filename)
      
       key=filename.lower()
       if mopts.has_key(key):
           os.system(method+" -t "+mopts[key][0]+" -o "+mopts[key][1]+" /dev/disk/by-label/"+filename+" "+MOUNT_POINT+filename)
           log.info(method+" -t "+mopts[key][0]+" -o "+mopts[key][1]+" /dev/disk/by-label/"+filename+" "+MOUNT_POINT+filename)
       else:
           os.system(method+" /dev/disk/by-label/"+filename+" "+MOUNT_POINT+filename)
           log.info(method+" /dev/disk/by-label/"+filename+" "+MOUNT_POINT+filename)
       self.notify(filename+" mounted")
   

def cleanup():
    os.close(LOG)

if os.getuid() != 0:
    log.info("Running as non-root.....")
    #exit()

wm = WatchManager()
notifier = Notifier(wm,Mounter())
directory="/dev/disk/by-label/"
mask=IN_CREATE|IN_DELETE
wm.add_watch(directory,mask)
atexit.register(cleanup)
notifier.loop(daemonize=True, pid_file=PID_FILE, force_kill=True,stdout=LOG+".d",stderr=LOG+".d")

