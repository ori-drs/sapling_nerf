import os
import re

from linuxpy.video.device import Device

AUTO_ACTIVATE = 1 # Check for econ cameras
AUTO_DEACTIVATE = 3

if __name__ == '__main__':

    list_dev = os.listdir("/dev")

    print("VIDEO DEVICES AVALAIBLE:")

    for device in list_dev:
        if re.match("video.*", device):
            print(device)
    
    dev_id = int(input("Select video device id: "))

    cam = Device.from_id(dev_id)
    cam.open()
    print("CAMERA INFO: {}".format(cam.info.card))

    if cam.controls.auto_exposure.value == AUTO_ACTIVATE:
        print("CURRENTLY AUTO EXPOSURE ACTIVATED")
    elif cam.controls.auto_exposure.value == AUTO_DEACTIVATE:
        print("CURRENTLY AUTO EXPOSURE DEACTIVATED")

    # cam.controls.auto_exposure
    
    print("Activate auto exposure?: ")
    print("0. No")
    print("1. Yes (or configure if it is currently activated)")
    auto = int(input("Choose option: "))

    if auto == 1: 
        cam.controls.auto_exposure.value = AUTO_ACTIVATE
        print("AUTO EXPOSURE ACTIVATED")
        print("EXPOSURE TIME: min = {}, max = {}, default = {}".format(cam.controls.exposure_time_absolute.minimum, cam.controls.exposure_time_absolute.maximum, cam.controls.exposure_time_absolute.default))
        print("CURRENT EXPOSURE TIME: {}".format(cam.controls.exposure_time_absolute.value))
        exposure = int(input("Choose exposure time: "))
        cam.controls.exposure_time_absolute.value = exposure
        print("NEW EXPOSURE TIME: {}".format(cam.controls.exposure_time_absolute.value))
    else:
        cam.controls.auto_exposure.value = AUTO_DEACTIVATE
        print("AUTO EXPOSURE DEACTIVATED")
   
