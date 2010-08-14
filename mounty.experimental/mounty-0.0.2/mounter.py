#!/usr/bin/python

class Mounter(ProcessEvent):

    def __init__(self,config):

        if NOTIFY == 1:
            try:
                import pynotify
                pynotify.init("Mounty")
            except:
                log.error("Pynotify not installed")

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

    def mount_path(self,key,filename):
        if not os.path.exists(MOUNT_POINT+filename):i
            os.system("sudo -u #"+UID+" mkdir -p "+MOUNT_POINT+filename)
        if not os.path.exists(MOUNT_POINT+filename):
           os.system("sudo -u #"+UID+" mkdir -p "+MOUNT_POINT+filename)
        os.system(method+" -t "+mopts[key][0]+" -o "+mopts[key][1]+" "+UDEV_LOC+filename+" "+MOUNT_POINT+filename)
        log.info(method+" -t "+mopts[key][0]+" -o "+mopts[key][1]+" "+UDEV_LOC+filename+" "+MOUNT_POINT+filename)
        self.notify(filename+" mounted")
        self.mount_list[key]="1"

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

