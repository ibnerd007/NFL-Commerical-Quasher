# NFL commerical quasher
# Turns down volume during a commercial (when logo is not shown in upper right corner)
# Fades volume up to full when logo reappearsq

from pyautogui import *
import pyautogui
import keyboard
import win32api, win32con
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math

# Get default audio device using PyCAW
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# get current volume
gameVolumeDb = volume.GetMasterVolumeLevel()
# change volume by decibel amount
# volume.SetMasterVolumeLevel(currentVolumeDb - 6.0, None)

maxVolume = -6.6 #dB, volume cannot rise above this level
volDecrease = 20 # dB, level commerical volume is lowered

# define regions for screens and different logos
nbcRegion = (1435,200,100,60)

def commercialQuasher(networkNum):
	
	networkLogos = ['nbc.png','cbs.png','fox.png','espn.png','nflnetwork.png','scoreboardonly.png']
	networkRegions = [(1435,200,100,60),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0)]

	networkLogo = networkLogos[networkNum]
	networkRegion = networkRegions[networkNum]

	print("You chose", networkLogos[networkNum])

	onCommercial = False
	falsePositives = 0
	falseNegatives = 0

	while 1:
		if (pyautogui.locateOnScreen(networkLogo, region=networkRegion, confidence = 0.2) != None) & onCommercial:
			# the game MIGHT be on, not sure yet
			falsePositives += 1

			if falsePositives >= 3: # we know the game is actually back
				print("The game is back!")

				currentVol = volume.GetMasterVolumeLevel() # read current volume before for loop

				for i in range(volDecrease + 1):
					volume.SetMasterVolumeLevel(gameVolumeDb - (volDecrease - i), None) # fades game volume up, 1 dB per 0.1 s
					time.sleep(0.1)

				onCommercial = False # no longer on commercial
				falsePositives = 0 # reset false positives

			time.sleep(0.25)
			
		elif (pyautogui.locateOnScreen(networkLogo, region=networkRegion, confidence = 0.2) == None) & (onCommercial == 0):
			# the game MIGHT be in commercial, we don't know yet
			falseNegatives += 1

			if falseNegatives >= 3: # we know the game is actually in commercial
				print("The game is in commercial.")

				for i in range(volDecrease + 1):
						volume.SetMasterVolumeLevel((gameVolumeDb - i), None) # fades game volume down, 1 dB per 0.1 s
						time.sleep(0.1)

				onCommercial = True
				falseNegatives = 0 # reset false negatives

			time.sleep(0.25)

		else:
			falseNegatives = 0
			falsePositives = 0 # neither statement qualifies; game situation maintained
			time.sleep(0.25)

		# failsafe for loud volume
		if volume.GetMasterVolumeLevel() >= maxVolume:
			volume.SetMasterVolumeLevel(gameVolumeDb - volDecrease, None)
			print("WARNING: Master volume too loud! Terminating program...")
			return

		if keyboard.is_pressed('q') == True: # Press 'q' to quit
			print("Til next time!")
			return	

commercialQuasher(0)


