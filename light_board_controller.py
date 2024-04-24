from enum import Enum
import asyncio
from pywizlight import wizlight, PilotBuilder, discovery
from pywizlight.exceptions import WizLightConnectionError
import csv
import os.path

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# class syntax
class Scenes(Enum):
    SCENE_1 = 1
    SCENE_2 = 2
    SCENE_3 = 3
    SCENE_4 = 4
    SCENE_5 = 5
    SCENE_6 = 6
    SCENE_7 = 7
    SCENE_8 = 8

scene = Scenes.SCENE_1
print(scene)

button_to_scene = {
    0:"0",
    1:"1",
    2:"2",
    3:"3",
    4:"4",
    5:"5",
    6:"6",
    7:"7",
    16:"8",
    17:"9",
    18:"10",
    19:"11",
    20:"12",
    21:"13",
    22:"14"
}

bulbNameToIP = {'03-sl-group': '192.168.12.100', '09-front-group': '192.168.12.248', '10-front-group': '192.168.12.209', '08-front-group': '192.168.12.115', '05-front-group': '192.168.12.160', '15-front-group': '192.168.12.237', '01-sr-group': '192.168.12.224', '02-sr-group': '192.168.12.130', '12-front-group': '192.168.12.211', '06-front-group': '192.168.12.133', '11-front-group': '192.168.12.247', '16-front-group': '192.168.12.186', '07-front-group': '192.168.12.139', '13-front-group': '192.168.12.199', '14-front-group': '192.168.12.187'}

#This is purely for debugging.
#bulbNameToIP = {'03-sl-group': '192.168.12.245'}

async def loadLightState(scene):
    #Check if we don't have a file for this button.
    if(not os.path.isfile("Scenes_From_Dash/"+scene+".csv")):return [0]
    with open("Scenes_From_Dash/"+scene+".csv",newline='') as csvfile:
        reader = csv.reader(csvfile)
        async with asyncio.TaskGroup() as tg:
            for row in reader:
                bulb_name = row[0]
                if(row[1]=="OFF"):
                    tg.create_task(turn_off_bulb(bulb_name))
                else:
                    red,green,blue,brightness = int(row[1]),int(row[2]),int(row[3]),int(row[4])
                    tg.create_task(set_bulb_to(bulb_name,PilotBuilder(rgb=(red,green,blue),brightness=brightness)))
    return [0]


#asyncio.create_task(turn_off_bulb("front"))
async def turn_off_bulb(bulb_name):
    light = wizlight(bulbNameToIP[bulb_name])
#    try:
    await light.turn_off()
#    except pywizlight.exceptions.WizLightConnectionError:
#        print("Bu

async def set_bulb_to(bulb_name,pilotbuild):
    light = wizlight(bulbNameToIP[bulb_name])
    await light.turn_on(pilotbuild)
    #rgbw = PilotBuilder(rgbw=(0, 128, 255, 100))

async def changeScene(scene, bulbObjDict):
#    res = await loadLightState(scene)
    for finished in res:pass
    res = await loadLightState(scene,bulbObjDict)
    asyncio.sleep(0.2)
    return [0]
#res = await loadLightState(Scenes.SCENE_2)
#for finished in res:pass

async def loadLightState_OLD(scene):
    #Check if we don't have a file for this button.
    if(not os.path.isfile("Scenes_From_Dash/"+scene+".csv")):return [0]
    with open("Scenes_From_Dash/"+scene+".csv",newline='') as csvfile:
        reader = csv.reader(csvfile)
        async with asyncio.TaskGroup() as tg:
            for row in reader:
                bulb_name = row[0]
                if(row[1]=="OFF"):
                    tg.create_task(turn_off_bulb(bulb_name))
                else:
                    red,green,blue,brightness = int(row[1]),int(row[2]),int(row[3]),int(row[4])
                    tg.create_task(set_bulb_to(bulb_name,PilotBuilder(rgb=(red,green,blue),brightness=brightness)))
    return [0]


async def loadLightState(scene,bulbObjDict):
    #Check if we don't have a file for this button.
    #loop = asyncio.get_event_loop()
    if(not os.path.isfile("Scenes_From_Dash/"+scene+".csv")):return [0]
    with open("Scenes_From_Dash/"+scene+".csv",newline='') as csvfile:
        reader = csv.reader(csvfile)
        async with asyncio.TaskGroup() as tg:
            for row in reader:
                bulb_name = row[0]
                if(bulb_name not in bulbObjDict): continue
                if(row[1]=="OFF"):
                    tg.create_task(bulbObjDict[bulb_name].turn_off())
                else:
                    red,green,blue,brightness = int(row[1]),int(row[2]),int(row[3]),int(row[4])
                    pb = PilotBuilder(rgb=(red,green,blue),brightness=brightness)
                    tg.create_task(bulbObjDict[bulb_name].turn_on(pb))
    return [0]



#asyncio.create_task(turn_off_bulb("front"))
async def turn_off_bulb(bulb_name):
    if(bulb_name not in bulbNameToIP): return 
    light = wizlight(bulbNameToIP[bulb_name])
    await light.turn_off()

async def set_bulb_to(bulb_name,pilotbuild):
    if(bulb_name not in bulbNameToIP): return 
    light = wizlight(bulbNameToIP[bulb_name])
    await light.turn_on(pilotbuild)
    #rgbw = PilotBuilder(rgbw=(0, 128, 255, 100))

async def changeScene(scene,bulbObjDict):
    #try:
    #    res = yield from loadLightState(scene,timeout=0.3)
    #except asyncio.TimeoutError:
    #    res = yield from loadLightState(scene,timeout=1)
    res = await loadLightState(scene,bulbObjDict)
    for finished in res:pass
    return [0]
#res = await loadLightState(Scenes.SCENE_2)
#for finished in res:pass

async def checkAllTheLights(bulbObjDict):
    good_lights = {}
    for bulb_name in sorted(list(bulbObjDict.keys())):
        try:
            light = bulbObjDict[bulb_name]
            state = await light.updateState()
            brightness = state.get_brightness() + 1            
            good_lights[bulb_name] = light
        except WizLightConnectionError:
            print(f"{bulb_name} cannot connect")
            pass
    return good_lights
    
    
import rtmidi

midiin = rtmidi.RtMidiIn()

def print_message(midi):
    if midi.isNoteOn():
        print('ON: ', midi.getNoteNumber(), midi.getMidiNoteName(midi.getNoteNumber()), midi.getVelocity())
#    elif midi.isNoteOff():
#        print('OFF:', midi.getMidiNoteName(midi.getNoteNumber()))
    elif midi.isController():
        print('CONTROLLER', midi.getControllerNumber(), midi.getControllerValue())

async def main():
    bulbObjDict = {}
    for bulb_name in bulbNameToIP:
        bulbObjDict[bulb_name] = wizlight(bulbNameToIP[bulb_name])

    bulbObjDict = await checkAllTheLights(bulbObjDict)
    ports = range(midiin.getPortCount())
    print("PORTS",ports)
    if ports:
        for i in ports:
            print(midiin.getPortName(i))
        print("Opening port 0!") 
        midiin.openPort(0)
        while True:
            m = midiin.getMessage(250) # some timeout in ms
            if m:
                #print(m)
                if m.isNoteOn():
                    #print_message(m)
                    button_number = m.getNoteNumber()
                    #if(button_number==119):
                    #    print("Stopping light board")
                    #    break
                    if(button_number in button_to_scene):
                        print("Changing to scene", button_to_scene[button_number])
                        #loop = asyncio.get_event_loop()
                        finished = await changeScene(button_to_scene[button_number],bulbObjDict)
                        #finished = asyncio.run(changeScene(button_to_scene[button_number]))
                        #res = yield from asyncio.wait_for(changeScene(button_to_scene[button_number]), timeout=0.3)
    #                    finished =  asyncio.run()
                        for res in finished:
                            pass

asyncio.run(main())