# NFL commerical quasher
# Turns down volume during a commercial (when logo is not shown in upper right corner)
# Fades volume up to full when logo reappears

from pyautogui import *
import pyautogui
# import keyboard
# import win32api, win32con
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

def commercialQuasher(networkNum):
	
	networkLogos =   ['nbc.png',     'cbs.png', 'fox.png',        'espn.png', 'nflnetwork.png', 'scoreboardonly.png']
	networkRegions = [(0,0,100,100), (0,0,0,0), (1674,54,145,48), (0,0,0,0),  (0,0,0,0),        (0,0,0,0)]

	networkLogo = networkLogos[networkNum]
	networkRegion = networkRegions[networkNum]

	print("You chose", networkLogos[networkNum])
	print("region = ", networkRegions[networkNum])

	onCommercial = False
	falseNegatives = 0
	loToHi = 3
	hiToLo = 10

	# region=networkRegion

	while 1:

		print(pyautogui.locateOnScreen(networkLogo, confidence=0.4))

		if (pyautogui.locateOnScreen(networkLogo, confidence=0.3) != None) and onCommercial:
			# the game MIGHT be on, not sure yet
			falseNegatives += 1

			if falseNegatives >= loToHi: # we know the game is actually back
				print("The game is back!")

				currentVol = volume.GetMasterVolumeLevel() # read current volume before for loop

				for i in range(volDecrease + 1):
					volume.SetMasterVolumeLevel(gameVolumeDb - (volDecrease - i), None) # fades game volume up, 1 dB per 0.1 s
					time.sleep(0.1)

				onCommercial = False # no longer on commercial
				falseNegatives = 0 # reset false positives
		
		elif (pyautogui.locateOnScreen(networkLogo, confidence=0.3) == None) and not onCommercial:

			# the game MIGHT be in commercial, we don't know yet
			falseNegatives += 1

			if falseNegatives >= hiToLo: # we know the game is actually in commercial
				print("The game is in commercial.")

				for i in range(volDecrease + 1):
						volume.SetMasterVolumeLevel((gameVolumeDb - i), None) # fades game volume down, 1 dB per 0.1 s
						time.sleep(0.1)

				onCommercial = True
				falseNegatives = 0 # reset false negatives

		else:
			falseNegatives = 0 # neither statement qualifies; game situation maintained

		# failsafe for loud volume
		currVolume = volume.GetMasterVolumeLevel()
		if currVolume >= maxVolume:
			volume.SetMasterVolumeLevel(gameVolumeDb - volDecrease, None)
			print("WARNING: Master volume too loud: ({} dB)! Terminating program...".format(currVolume))
			return

		time.sleep(0.25)

		# if keyboard.is_pressed('q') == True: # Press 'q' to quit
		# 	print("Til next time!")
		# 	break

commercialQuasher(2)


