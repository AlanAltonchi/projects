from cfg import NAME, TOKEN, CHAR_ID, WORLD_ID
import websocket
import json
import re
import os
try:
    import _thread as thread
except:
    import thread as thread
import time
ID = 3
msg = []
sentAttacks = []
myVillageID = 2486
tokenEmit = ""

''' 
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
TW2 Script
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
Latest Changes (Top-Down):
- Increased message received log to 8 and removed StableID from getResp().
- Automatically clear console every run (60s) and Automatically reconnect socket if disconnected.
- Updated getResp() to work with the new logging system (Increased performance by a lot!).
- Turned msg into a log that contains the 6 latest messages received from the socket.
- Added Automatic Resource Deposits.
- getResp() takes the current ID and makes a stable copy of it before looking for the response.
- * REMOVED: 'ID gets updated with the latest ID received from the stream.' Reason: Bugged getResp()
- If no attacks are being sent and we keep reading reports until Threshold is reached, we stop.
- Check all reports and send attacks to barbarians if there isn't already an attack on the way there.

Ideas (To-Do):
- Auto Build Queue

Current Features:
- Automatically take care of Resource Deposit
- Automatically raid barbarian villages from the latest reports.
'''

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Config =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
attackThreshold = 15
restartTimer = 2



# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Config [END] =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def clear():
    try:
        os.system('clear')
    except:
        clear_output()

def ping():
    while True:
        time.sleep(25)
        ws.send('2')
        
def sendMsg(m):
    global ID
    ID += 1
    tt = m
    tt = re.sub(r',"id":\d*',',"id":'+str(ID),tt)
    #print("\n\nSending: "+ tt)
    ws.send(tt)
        
def getResp():
    global ID
    global msg
    runs = 0
    while True:
        if runs > 30:
            return None
        for m in msg:
            if '"id":'+str(ID)+"," in m:
                return m.replace('42["msg",','')[:-1]
        runs += 1
        time.sleep(0.300)

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Auto Barbarian Raid =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def getOutgoing(v):
    sendMsg('42["msg",{"type":"Unit/getUnitScreenInfo","data":{"village_id":'+str(v)+'},"id":62,"headers":{"traveltimes":[["browser_send",1560294596237]]}}]')
    r = getResp()
    if r is None:
        return getOutgoing(v)
    y = json.loads(r)
    outgoing = y["data"]["outgoingArmies"]
    outlist = []
    for o in outgoing:
        if o["direction"] == "forward" and o["village"]["village_id"] not in outlist:
            outlist.append(o["village"]["village_id"])
    return outlist
        
def checkSingleReport(id_):
    sendMsg('42["msg",{"type":"Report/get","data":{"id":'+str(id_)+'},"id":38,"headers":{"traveltimes":[["browser_send",1560292401114]]}}]')
    r = getResp()
    if r is not None:
        print("\nChecking report...")
        return r
    else:
        print("\nTrying to check single report again...")
        return checkSingleReport(id_)

def sendAttack(rep):
    global sentAttacks
    attackerId = rep["attVillageId"]
    villageId = rep["defVillageId"]
    attUnits = rep["attUnits"]
    print("\nSending an attack to: " + str(villageId))
    sendMsg('42["msg",{"type":"Command/sendCustomArmy","data":{"start_village":'+str(attackerId)+',"target_village":'+str(villageId)+',"type":"attack","units":'+str(attUnits).replace("'",'"').replace('u"','"')+',"icon":0,"officers":{},"catapult_target":"headquarter"},"id":45,"headers":{"traveltimes":[["browser_send",1560292953441]]}}]')
    sentAttacks.append(villageId)
    
def checkReports():
    global sentAttacks
    sendMsg('42["msg",{"type":"Report/getListReverse","data":{"offset":0,"count":100,"query":"","types":["attack"],"filters":[]},"id":86,"headers":{"traveltimes":[["browser_send",1560296824048]]}}]')
    r = getResp()
    if r is not None:
        print("\nChecking all reports...")
        y = json.loads(r)
        reports = y["data"]["reports"]
        counter = 0
        for i in reports:
            rp = checkSingleReport(i["id"])
            if rp is None:
                print("Failed to get report")
            else:
                report = json.loads(rp)["data"]["ReportAttack"]
                sendMsg('42["msg",{"type":"Report/markSeen","data":{"ids":['+str(i["id"])+']},"id":33,"headers":{"traveltimes":[["browser_send",1560349653603]]}}]')
                if report["defCharacterId"] == 0:
                    if report["defVillageId"] not in sentAttacks and report["defVillageId"] not in getOutgoing(report["attVillageId"]):
                        sendAttack(report)
                        counter = 0
                    elif counter < attackThreshold:
                        counter +=1
                        print("\nAlready attacking " + str(report["defVillageId"]))
                    else:
                        print("\nReached threshold of: "+ str(attackThreshold) +"\nStopping the search for targets...")
                        break
        sentAttacks.clear()
        print("Checking all reports [COMPLETE]")
    else:
        print("\nTrying to check all reports again...")
        checkReports()
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Auto Barbarian Raid [END] =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Auto Resource Deposit =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def checkDeposit():
    sendMsg('42["msg",{"type":"ResourceDeposit/open","id":78,"headers":{"traveltimes":[["browser_send",1560299526301]]}}]')
    r = getResp()
    if r is not None:
        print("Checking Resource Deposit...")
        y = json.loads(r)
        try:
            if jobs := y["data"]["jobs"]:
                try:
                    if jobs[0]["time_completed"]:
                        if int(time.time()) >= jobs[0]["time_completed"]:
                            print("Collecting from Resource Deposit")
                            sendMsg('42["msg",{"type":"ResourceDeposit/collect","data":{"job_id":'+str(jobs[0]["id"])+',"village_id":'+str(myVillageID)+',"tokenEmit":"'+tokenEmit+'","userAgent":"browser"},"id":81,"headers":{"traveltimes":[["browser_send",1560299709896]]}}]')
                            if len(jobs) > 1:
                                sendMsg('42["msg",{"type":"ResourceDeposit/startJob","data":{"job_id":'+str(jobs[1]["id"])+'},"id":79,"headers":{"traveltimes":[["browser_send",1560299621373]]}}]')
                        else:
                            print("Resource Deposit not ready to collect yet.")
                except:
                    sendMsg('42["msg",{"type":"ResourceDeposit/startJob","data":{"job_id":'+str(jobs[0]["id"])+'},"id":79,"headers":{"traveltimes":[["browser_send",1560299621373]]}}]')
            print("Checking Resource Deposit [COMPLETE]")
        except:
            print("No jobs...")
    else:
        print("\nTrying to check resource deposit again...")
        checkDeposit()
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Auto Resource Deposit [END] =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Add all commands below (While loop) =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def initiate():
    ws.send('42["msg",{"type":"Authentication/login","data":{"name":"{0}","token":"{1}"},"id":1,"headers":{"traveltimes":[["browser_send",1560286567345]]}}]'.format(NAME,TOKEN))
    ws.send('42["msg",{"type":"System/identify","data":{"platform":"browser","device":"Mozilla/5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/74.0.3729.169%20Safari/537.36","api_version":"10.*.*"},"id":2,"headers":{"traveltimes":[["browser_send",1560286567540]]}}]')
    time.sleep(1)
    ws.send('42["msg",{"type":"Authentication/selectCharacter","data":{"id":{0},"world_id":"{1}"},"id":3,"headers":{"traveltimes":[["browser_send",1560289752002]]}}]'.format(CHAR_ID, WORLD_ID))
    thread.start_new_thread(ping, ())
    time.sleep(4)
    while True:
        checkDeposit()
        checkReports()

        print(f"Waiting {str(restartTimer*60)} seconds...")
        time.sleep(restartTimer*60)
        clear()
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Add all commands above (While loop) =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= 


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Socket Connection =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def on_message(ws, message):
    global msg
    global tokenEmit
    if "secret_token" in message:
        tokenEmit = message.split('secret_token":"')[1].split('"}}]')[0]
    if len(msg) >= 8:
        msg.pop()
    msg.insert(0,message)
    #o = re.findall(',"id":\d*,',msg)[0]
    #ID = int(re.search(r'\d+', o).group())
    # print("\n"+message)

def on_error(ws, error):
    print(error)

def on_close(ws,arg2,arg3):
    print("### connection closed ###")
    print("### restarting... ###")


def on_open(ws):
    def run(*args):
        initiate()
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://en.tribalwars2.com/socket.io/?platform=desktop&EIO=3&transport=websocket",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    while True:
        try:
            ws.run_forever()
        except:
            pass

