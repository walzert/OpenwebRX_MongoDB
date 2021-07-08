import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time
import json 
#import pprint
import maidenhead as mh
import datetime
import call_to_dxcc
import sys, getopt
import time
import pymongo
from math import sin, cos, sqrt, atan2, radians     
import urllib.parse

import sys
sys.path.append('/data')
import gc
gc.enable

import configparser
config = configparser.ConfigParser()
config.sections()
config.read('data.ini')
config.read('/data/data.ini')

import band_slots 
band_time = band_slots.band_time
#print(band_time)


import pymongo
import urllib.parse
username = urllib.parse.quote_plus('username')
password = urllib.parse.quote_plus('password')
uri = 'mongodb://'+username+':'+password  +config['mongoDB']['uri']
myclient = pymongo.MongoClient(uri)

mydb = myclient[str(config['mongoDB']['connections_db'])]
mycol = mydb[str(config['mongoDB']['openwebrx__col'])]

mycol_summary = mydb[str(config['mongoDB']['openwebrx__col_summary'])]
mycol_sideband = mydb[str(config['mongoDB']['openwebrx__col_sideband'])]

aprs = False
server = ''
#f = ''
band_reporter = 'None'
last_planned_band = 'None'
R = 6373.0
lat_home = 0 
lon_home = 0 
kw_distance = 0
kw_distance_mean = 0
kw_counter = 0
minuteFormat = "%M"
timeFormat = "%H:%M:%S"
band_callsign  = []
aprs_callsign  = []
sideband_callsign  = []
sideband_callsign_list  = []
aprs_print = False
#band_time = None
import logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)



def band_timer(x):
    current_band = ''
    for band in band_time:
    #print((int(band_time[a]["start"]) > x) and (x < int(band_time[a]["start"])))
        #print(band)
        #print(band_time[band][0])
        #print(band_time[band][1])
        if ((x <= int(band_time[band][0]["end"]) and x >= int(band_time[band][0]["start"])) or (x >= int(band_time[band][1]["start"]) and x <= int(band_time[band][1]["end"]))) :
            current_band = band
            #print(band)
            #print("True")
    return str(current_band)

def on_message(ws, message):
    if  'CLIENT DE SERVER server=openwebrx version=' in message:
        logger.log(logging.INFO, ("Start message"))
        print("Start message")
        print('--------')
    elif '"type": "receiver_details",' in message:
        global lat_home
        global lon_home
        logger.log(logging.INFO, ("Receiver details"))
        print("Receiver details")
        json_data = json.loads(message)
        #print(json_data)  #print(lat_home)  #print(lon_home) #print(json_data["value"])  #print(json_data["value"]["locator"])
        data_locator_maidenhead = json_data["value"]["locator"]
        #print(data_locator)
        data_locator_maidenhead_gps = mh.to_location(data_locator_maidenhead,center=True)
        #print(data_locator_maidenhead) #print(data_locator_maidenhead[0]) #print(data_locator_maidenhead[1]) #print(lon + "  " + lat)
        lat_home = radians(data_locator_maidenhead_gps[0])
        lon_home = radians(data_locator_maidenhead_gps[1])
        #print(lat_home)
        #print(lon_home)
        print('--------')
        
    elif '"type": "config", ' in message:
        logger.log(logging.INFO, ("Config details"))
        print("Config details")
        #print(message)
        print('--------')
    else:
        #print(message)
        #print('--------')
        json_data = json.loads(message)
        #print(len(json_data['value']))
        #print(json_data)
        #print(len(json_data['value']) > 1)
        if len(json_data['value']) > 1:
            print("Old " + str(len(json_data['value'])) )
            print('--------')
        else:
            lat = 0
            lon = 0
            #print(message)
            data_ = json_data['value'][0]
            data_callsign = data_['callsign']
            data_location = data_['location']
            data_mode = data_['mode']
            data_band = data_['band']
            data_lastseen = data_['lastseen']
            #print(data_band)
            global band_reporter
            global kw_distance
            global kw_distance_mean
            global kw_counter
            global band_time
            global band_callsign
            global aprs_callsign
            global sideband_callsign
            global sideband_callsign_list
            global mycol
            global mycol_sideband
            #global f
            #print(data_band)
            unix_ts= int(str(data_lastseen)[:10])
            timestamp = datetime.datetime.fromtimestamp(float(unix_ts))
            timestampTime = timestamp.strftime(timeFormat)
            #print(timestampTime)
            minuteTime = int(timestamp.strftime(minuteFormat))
            
            now = datetime.datetime.now()

            current_time = now.strftime("%M")
            #print("\n ----------Time --------- ")
            #print(str(minuteTime))
            #print(str(current_time))
            #print(band_timer(int(current_time)))
            planned_band = str(band_timer(int(current_time)))
            #print(planned_band)
            #print(str(current_time))
            #print("\n ----------Time  end --------- ")
            #print(band_time)  #print(minuteTime)
            #if data_band != '2m':
            #    current_band =  band_time[data_band]
                #print("Band: " +str(data_band) + " Time: " +str(minuteTime) + "  " + str(current_band[0]["start"]) + " " + str(current_band[0]["end"]) + " " + str(current_band[1]["start"]) + " " + str(current_band[1]["end"]) )
                #print (str(minuteTime) + " " + str(current_band[0]["end"]) + "  " +  str(current_band[0]["start"] )+  " " +  str(current_band[1]["end"]) + "  " +  str(current_band][1]["start"]) )
            
            #print((minuteTime < band_time[band][0]["end"] and minuteTime >= band_time[band][0]["start"]) or (minuteTime < band_time[band][1]["end"] and minuteTime >= band_time[band][1]["start"]))
            #rint("------------------- ")
            #print(data_band)
            #print(planned_band)
            #print(band_reporter)
            #print(data_band != "2m")
            #print(band_reporter !=   planned_band)
            #print( band_reporter != data_band)
            #print("------------------- ")
            #if ( (data_band != "2m" and band_reporter != data_band )  or band_reporter !=   planned_band  ) : # or bandchangeband_reporter != band_timercurrent_time()

            if (   band_reporter !=   planned_band  ) : # data_band != "2m" and  
                # or bandchangeband_reporter != band_timercurrent_time()
                logger.log(logging.INFO, ("Band " + str(band_reporter)))
                print("\n--------------- Band "+ band_reporter + " -------------")
                #print("Last Band: " +  band_reporter)
                #mean_counter = int(kw_distance_mean) // int(kw_counter)
                print("Max distance: " + str(int(kw_distance)))
                print("Summed up distance: " + str(int(kw_distance_mean)))
                print("Unique signals/stations:" +str(int(kw_counter)))
                if(kw_counter<0):
                    mean_value = int(int(kw_distance_mean)/int(kw_counter))
                else: 
                    mean_value = 0
                print(band_callsign)
                if aprs:
                    print("Aprs:")
                    print(aprs_callsign)
                print("Other Bands:")
                print(sideband_callsign_list)
                print("--------------------------------------\n")
                band_slot_time = timestampTime[:-3]
                    #datetimeObj = datetime.strptime(timestampTime, '%H::%M::%S')
                    #print(datetimeObj)
                    #print(band_slot_time)
                band_slot_time_split= band_slot_time.split(":")
                if int(band_slot_time_split[1]) < 30 :
                    band_slot = str(band_slot_time_split[0])+"00_"+ band_reporter
                else:
                    band_slot = str(band_slot_time_split[0])+"30_"+ band_reporter
                data = {   "band_slot" :band_slot , "band" : band_reporter , "max_distance": int(kw_distance), "summed_distance" :int(kw_distance_mean) , "number" : int(kw_counter) , "mean_value" : mean_value  }
                summary = mycol_summary.insert_one(data)
                band_reporter = planned_band
                last_planned_band
                kw_distance = 0
                kw_distance_mean = 0
                kw_counter = 0
                band_callsign.clear()
                sideband_callsign.clear()
                sideband_callsign_list.clear()
                aprs_callsign.clear()
            
            #print(data_callsign) #print(data_location) #print(data_mode) #print(data_band) #print(json_data['value'][0]['location']['type']) #print(data_callsign + "\t" + data_band + "\t" + data_mode)
            if data_location['type'] == 'latlon':
                lat = data_location['lat']
                lon = data_location['lon']
                data_locator_maidenhead = mh.to_maiden(lat, lon)
                if aprs:
                    if data_callsign not in aprs_callsign:
                        aprs_callsign.append(data_callsign)
                        print("(A) " +str(timestampTime) + " \t" + str(data_callsign) + "   \t" + str(data_band) + "\t" + str(data_mode) + "\t" + str(data_locator_maidenhead) + "\t"+ str(lat)[:6] + "\t" + str(lon)[:6]  )
                    


            if data_location['type'] == 'locator':
                data_locator_maidenhead = data_location['locator']
                data_locator_maidenhead_gps = mh.to_location(data_locator_maidenhead,center=True)
                lat = data_locator_maidenhead_gps[0]
                lon = data_locator_maidenhead_gps[1]

            lat_qrx = radians(lat)
            lon_qrx = radians(lon)

            dlon = lon_qrx - lon_home
            dlat = lat_qrx - lat_home
            a = sin(dlat / 2)**2 + cos(lat_home) * cos(lat_qrx) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            distance = R * c
            #if data_band != "2m" and distance > kw_distance :
                

            country = call_to_dxcc.data_for_call(data_callsign)
            #print(country)
            if data_band != '2m' and  data_band  ==  planned_band :
                if distance > kw_distance:
                    kw_distance = distance
                if data_callsign not in band_callsign:
                    band_callsign.append(data_callsign)
                    kw_distance_mean += distance
                    kw_counter = kw_counter +1
                    #print(timestampTime)
                    #datetimeObj = datetime.strptime(timestampTime, '%H:%M:%S')
                    #print(band_callsign)   #print(str(kw_distance_mean))   #print(str(kw_counter))
                    #connectionstring = "(✓) " +str(timestampTime) + " \t" +data_callsign + "\t" + str(country[1]) +  "\t"+ data_band + "\t" + data_mode + "\t" + data_locator_maidenhead + "\t"+ str(lat) + "\t" + str(lon) + "\t" + str(int(distance))+ " km"  
                    #print(connectionstring)
                    #print(datetimeObj)
                    band_slot_time = timestampTime[:-3]
                    #datetimeObj = datetime.strptime(timestampTime, '%H::%M::%S')
                    #print(datetimeObj)
                    #print(band_slot_time)
                    band_slot_time_split= band_slot_time.split(":")
                    #print(band_slot_time_split)
                    #print(band_slot_time_split[0])
                    #print(band_slot_time_split[1])
                    #print( str(timestamp))
                    #print(band_slot_time_split[0])
                    #test =(int(band_slot_time_split[1])<30)
                    #print(test)
                    if int(band_slot_time_split[1]) < 30 :
                        band_slot = str(band_slot_time_split[0])+"00"+ data_band
                    else:
                        band_slot = str(band_slot_time_split[0])+"30"+ data_band
                    #print(band_slot)
                    #print(str(timestampTime[:-3])+"_"+ data_band)
                    data = {  "time": timestamp,  "band_slot" :band_slot , "call"  :	data_callsign , "continent"	:country[1], "band" : data_band , "mode" :	data_mode, "maidenhead"	 : data_locator_maidenhead ,"lat" :	lat, "lon" :	lon , "distance(km)" :	int(distance) }
                    x = mycol.insert_one(data)
                    #print(x)
                    #f.write(connectionstring)
                    #f.write("\n")
                    #print("(✓) " +str(timestampTime) + " \t" +data_callsign + "\t" + str(country[1]) +  "\t"+ data_band + "\t" + data_mode + "\t" + data_locator_maidenhead + "\t"+ str(lat) + "\t" + str(lon) + "\t" + str(int(distance))+ " km \n")
            else:
                if data_mode != "APRS":
                    #print("-----------------------------") 
                    #print("Zusätzlicher Empfang auf  Band: " + data_band )
                    if data_callsign not in sideband_callsign:
                        sb_call = [data_callsign,data_band]
                        sideband_callsign.append(data_callsign)
                        sideband_callsign_list.append(sb_call)
                        #print(str(timestampTime))
                        #print(timestampTime)
                        side_band_output = ("( ) " +str(timestampTime) + " \t" +data_callsign + "\t" + str(country[1]) +  "\t"+ data_band + "\t" + data_mode + "\t" + data_locator_maidenhead + "\t"+ str(lat) + "\t" + str(lon) + "\t" + str(int(distance))+ " km"  )
                        data = {"time": timestamp, "call"  :	data_callsign , "continent"	:country[1], "band" : data_band , "mode" :	data_mode, "maidenhead"	 : data_locator_maidenhead ,"lat" :	lat, "lon" :	lon , "distance(km)" :	int(distance) }
                        x = mycol_sideband.insert_one(data)
                        #print(x)
                        print(side_band_output)
                        #f.write(side_band_output)
                        #f.write("\n")
                        #print("( ) " +str(timestampTime) + " \t" +data_callsign + "\t" + str(country[1]) +  "\t"+ data_band + "\t" + data_mode + "\t" + data_locator_maidenhead + "\t"+ str(lat) + "\t" + str(lon) + "\t" + str(int(distance))+ " km"  )

                        #sideband_callsign.append(data_callsign)
                    #print("-----------------------------") 
            #print(sideband_callsign)
            #else:
            #    print("APRS: ")

def on_error(ws, error):
    print("### Error ###")
def on_close(ws):
    print("### closed ###")

def on_open(ws):
    ws.send('SERVER DE CLIENT client=map.js type=map')
    #startmessage = ws.recv()
    #print(startmessage)
    #    time.sleep(1)
        #ws.close()
    #    print("thread terminating...")
    #thread.start_new_thread(run, ())

#def bandByTime(time):
     #minuteTime <= current_band[0]["end"] or minuteTime >= current_band[0]["start"]) or (minuteTime <= current_band[1]["end"] or minuteTime >= current_band[1]["start"])





def main(argv):
    global aprs
    global server
    global lat_home
    global lon_home
    global band_reporter
    global mycol
    global mycol_sideband
    #mydb = myclient["connections"]
    #mycol = mydb['openwebrx']
    #mycol_summary = mydb['openwebrx']
    #mycol_sideband = mydb['openwebrx_sideband']
    #global f
    #try:
    #    opts, args = getopt.getopt(argv,"hs:a",["--server=","--aprs"])
    #except getopt.GetoptError:
    #    print ('test.py --server [--aprs",]')
    #    sys.exit(2)
    #for opt, arg in opts:
    #    if opt == '-h':
    #        print ('test.py -i <inputfile> -o <outputfile>')
    #        sys.exit(2)
    #    elif opt in ("-s", "--server"):
    #        server = arg
    #    elif opt in ("-a", "--aprs"):
    #        aprs = True
    #with open('band_timer.json') as json_file:
        #band_time = json.loads(json_file)
        #print(json_file)
        #print(band_time)
        #band_time = data
    #test = json.dumps(band_time)
    #print(test)
    websocket.enableTrace(False)
    server = config['openwebrx']['url']
    ws = websocket.WebSocketApp("ws://"+server+"/ws/",
                              on_open = on_open,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)

    #mycol = 'openwebrx'
    #mycol_sideband = 'openwebrx_sideband'
    #mycol = mydb["connections"]
    starttime = datetime.datetime.now()
    current_time = starttime.strftime("%M")
    current_date=  starttime.strftime("%Y-%m-%d")
    #mycol = mydb[current_date]
    #sideband_date= current_date +"_sb"
    #mycol_sideband = mydb[sideband_date]

    #filestring= str(starttime) + ".txt"
    #f = open(filestring, "a")
    startband = str(band_timer(int(current_time)))
    band_reporter = startband
    ws.run_forever()

if __name__ == "__main__":
    main(sys.argv[1:])
