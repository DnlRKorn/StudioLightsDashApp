from dash import Dash, html, Input, Output, callback, State, ctx
import os.path
import asyncio
from dash import dcc
import dash_daq as daq
from pywizlight import wizlight, PilotBuilder, discovery
import csv
import os.path
import base64

app = Dash(__name__)

light_options = ["01-sr-group",
"02-sr-group",
"03-sl-group",
#"kipDesk",
"05-front-group",
"06-front-group",
"07-front-group",
"08-front-group",
"09-front-group",
"10-front-group",
"11-front-group",
"12-front-group",
"13-front-group",
"14-front-group",
"15-front-group",
"16-front-group"]

image_filename = 'Scenes_From_Dash/light_chart_small.jpg'
encoded_image = base64.b64encode(open(image_filename, 'rb').read()).decode('ascii')

app.layout = html.Div([
    html.Img(src='data:image/png;base64,{}'.format(encoded_image)),
#    html.Img(src='file:///C:/Users/dkorn_lenovo/Documents/JUPYTER/Scenes_From_Dash/light_chart.jpeg'),
    html.Br(),
    html.Button('Select All', id='select-all-btn', n_clicks=0),
    html.Button('Select None', id='select-none-btn', n_clicks=0),
    html.Button('Select Main Row', id='select-main-row-btn', n_clicks=0),
    html.Div([
        dcc.Checklist(id='checklist',options=light_options)]),
    html.Div(id='last-light-output'),
    html.Button('Lights On', id='lights-on-btn', n_clicks=0),
    html.Button('Lights Off', id='lights-off-btn', n_clicks=0),
    daq.ColorPicker(
        id='my-color-picker-1',
        label='Color Picker',
        value=dict(rgb=dict(r=255, g=0, b=0, a=0))
    ),
    html.P("Brightness"),
    dcc.Slider(0, 255,value=255, 
        id='my-slider'
    ),
    html.Div(id='color-picker-output-1'),
    html.Br(),
    html.P("Save Scene, please put in Name of Scene:"),
    dcc.Input(id="scene-save-input", type="text", placeholder="christening"),
    html.Button('Save Scene!', id='scene-save-btn', n_clicks=0),
    html.Div(id='save-scene-output'),
    html.P("Load Scene, please put in Name of Scene:"),
    dcc.Input(id="scene-load-input", type="text", placeholder="christening"),
    html.Button('Load Scene!', id='scene-load-btn', n_clicks=0),
    html.Div(id='load-scene-output'),
	    
])

async def saveLightScene(outf):
    print("We see this many bulbs",len(bulbNameToIP))
    with open(outf,'w',newline='') as csvfile:
        writer = csv.writer(csvfile)
        for bulb_name in sorted(list(bulbNameToIP),key=lambda k:int(k.split('-')[0])):
            bulb_ip = bulbNameToIP[bulb_name]
            light = wizlight(bulb_ip)
            state = await light.updateState()
            on = state.get_state()
            res = state.get_rgb()
            brightness = state.get_brightness()
            if(on==False): 
                writer.writerow([bulb_name,"OFF"])
            else:
                red, green, blue = res
                writer.writerow([bulb_name,red,green,blue,brightness])
                print(bulb_name, res)
    return [0]

async def loadLightScene(inf):
    with open(inf,newline='') as csvfile:
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

async def getLightString(bulb_name):
    bulb_ip = bulbNameToIP[bulb_name]
    light = wizlight(bulb_ip)
    state = await light.updateState()
    on = state.get_state()
    res = state.get_rgb()
    brightness = state.get_brightness()
    if(on==False): 
        return f"{bulb_name} is OFF"
    else:
        red, green, blue = res
        return f"{bulb_name} is red:{red} green:{green} blue: {blue} brightness: {brightness}"
        writer.writerow([bulb_name,red,green,blue,brightness])

@app.callback(
    Output('last-light-output', 'children'),
    Input("checklist", "value"),
)
def checkLight(lights):
    if(lights!=[]):
        light_name = lights[0]
        light_str = asyncio.run(getLightString(light_name))
        return light_str
    return ""


@app.callback(
    Output('load-scene-output', 'children'),
    [Input("scene-load-btn", "n_clicks")],
    [State("scene-load-input", "value")],
)
def load_scene_dash(n_clicks,scene_name):
    if(scene_name==None):
        outf="Scenes_From_Dash/default.csv"
    else:
        outf=f"Scenes_From_Dash/{scene_name}.csv"
    asyncio.run(loadLightScene(outf))
    return f"Scene saved to {outf}"

@app.callback(
    Output('save-scene-output', 'children'),
    [Input("scene-save-btn", "n_clicks")],
    [State("scene-save-input", "value")],
)
def save_scene_dash(n_clicks,scene_name):
    if(scene_name==None):
        outf="Scenes_From_Dash/default.csv"
    else:
        outf=f"Scenes_From_Dash/{scene_name}.csv"
    asyncio.run(saveLightScene(outf))
    return f"Scene saved to {outf}"

@app.callback(
    Output("checklist", "value"),
    [Input("select-all-btn", "n_clicks"),Input("select-none-btn", "n_clicks"),Input("select-main-row-btn","n_clicks")],
    [State("checklist", "options")],
)
def select_all(n_clicks1,n_click2,n_clicks3, options):
    all_or_none = []
    #print(options)
    #all_or_none = [option["value"] for option in options if True]
    prevent_inital_call=True
    if "select-all-btn" == ctx.triggered_id:
        all_or_none = options
    elif "select-main-row-btn" == ctx.triggered_id:
        all_or_none = ["7-front-group","8-front-group","9-front-group","10-front-group","11-front-group","12-front-group","13-front-group","14-front-group","15-front-group","16-front-group"]
#        print(options)
#        print(all_or_none)
    else:
        all_or_none = []
    return all_or_none

@app.callback(
    Output('color-picker-output-1', 'children'),
    [Input("lights-on-btn", "n_clicks"),Input("lights-off-btn", "n_clicks"),Input('my-color-picker-1', 'value'),Input("my-slider","value")],
    [State("checklist", "value")],
)
def update_output(on_btn_clicks,off_btn_clicks,color_value,brightness,bulb_names):
    if(bulb_names==None): bulb_names=[]
#    print("The options are",options)
    print(color_value)
    print(color_value['rgb'])
    r = color_value['rgb']['r']
    g = color_value['rgb']['g']
    b = color_value['rgb']['b']
    print(r)
    if "lights-off-btn" == ctx.triggered_id:
        x = asyncio.run(set_bulbs(bulb_names,ON=False))
        return f'THE LIGHTS ARE OFF!'
    else:
        x = asyncio.run(set_bulbs(bulb_names,red=r,green=g,blue=b,brightness=brightness))
        return f'The selected color is {color_value}. Brightness {brightness}.'


#https://stackoverflow.com/questions/57786520/how-to-run-dash-in-async-with-asyncio
#https://community.plotly.com/t/adding-a-select-all-button-to-a-multi-select-dropdown/8849/3






bulbNameToMac = {

    "01-sr-group":"a8bb50e0c944",
    "02-sr-group":"a8bb50e047c2",
    "03-sl-group":"444f8e9596c8",

#    "pianoLamp":"cc408512ae6e",
    
    "05-front-group":"444f8e95b5f0",
    "06-front-group":"444f8e9572c4",
    "07-front-group":"cc4085301c6c",
    "08-front-group":"444f8e95a018",
    "09-front-group":"cc408530170a",
    "10-front-group":"cc4085301616",
    "11-front-group":"cc408530119a",
    "12-front-group":"cc408547a2c6",
    "13-front-group":"cc408530116a",
    "14-front-group":"cc408547916c",
    "15-front-group":"cc408521ac7c",
    "16-front-group":"cc408547bac6",
}

bulbMacToName = {v: k for k, v in bulbNameToMac.items()}

bulbNameToIP = {
#    "front":"192.168.2.12"
}

async def bulbTest():
    seen_bulbs = set()
    bulbNameToIP = {}
    bulbs = await discovery.discover_lights(broadcast_space="192.168.12.255")
    for bulb in bulbs:
        #print(bulb.__dict__)
        bulb_mac = bulb.__dict__['mac']
        bulb_ip = bulb.__dict__['ip']
        if(bulb.__dict__['mac'] in bulbMacToName):
            bulb_name = bulbMacToName[bulb_mac]
            bulbNameToIP[bulb_name] = bulb_ip
            seen_bulbs.add(bulb_name)
        else: print(bulb_mac, "not assigned")
        
    unseen_bulbs = set(bulbNameToMac).difference(seen_bulbs)
    if(len(unseen_bulbs)>0):
         print("We didn't see the following bulbs",set(bulbNameToMac).difference(seen_bulbs))
         raise RuntimeError('We cannot find all the bulbs.')
    return bulbNameToIP
    
#bulbNameToIP = asyncio.run(bulbTest())
bulbNameToIP = {'03-sl-group': '192.168.12.100', '09-front-group': '192.168.12.248', '10-front-group': '192.168.12.209', '08-front-group': '192.168.12.115', '05-front-group': '192.168.12.160', '15-front-group': '192.168.12.237', '01-sr-group': '192.168.12.224', '02-sr-group': '192.168.12.130', '12-front-group': '192.168.12.211', '06-front-group': '192.168.12.133', '11-front-group': '192.168.12.247', '16-front-group': '192.168.12.186', '07-front-group': '192.168.12.139', '13-front-group': '192.168.12.199', '14-front-group': '192.168.12.187'}
print(sorted(list(bulbNameToIP.keys())))
print(bulbNameToIP)
#    await light.turn_off()
bulbObjDict = {}
for bulb_name in bulbNameToIP:
    bulbObjDict[bulb_name] = wizlight(bulbNameToIP[bulb_name])

async def turn_off_bulb(bulb_name):
    light = wizlight(bulbNameToIP[bulb_name])
    await light.turn_off()
    del light
    return [0]

async def set_bulb_to(bulb_name,pb_rgbw):
    light = wizlight(bulbNameToIP[bulb_name])
    await light.turn_on(pb_rgbw)
    del light
    return [0]

async def set_bulbs(bulb_names,red=0,green=0,blue=0,brightness=0,ON=True):
    bulbSet = set()
    async with asyncio.TaskGroup() as tg:
        for bulb_name in bulb_names:
            if(bulb_name not in bulbNameToIP):continue
            bulb = wizlight(bulbNameToIP[bulb_name])
            bulbSet.add(bulb)
            if(ON==False):
#                tg.create_task(turn_off_bulb(bulb_name))
#                tg.create_task(wizlight(bulbNameToIP[bulb_name]).turn_off())
                tg.create_task(bulb.turn_off())
            else:
#                red,green,blue,white,brightness = int(row[1]),int(row[2]),int(row[3]),int(row[4]),int(row[5])
                #tg.create_task(set_bulb_to(bulb_name,PilotBuilder(rgb=(red,green,blue),brightness=brightness)))
                pb = PilotBuilder(rgb=(red,green,blue),brightness=brightness)
#                tg.create_task(wizlight(bulbNameToIP[bulb_name]).turn_on(pb))
                tg.create_task(bulb.turn_on(pb))
    for bulb in bulbSet: del bulb
    return [0]

if __name__ == '__main__':
    app.run(debug=True)

