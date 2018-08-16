import urllib.request
import json


playerIDList = [105045, 1164477, 92611, 1505241, 92236, 91449, 91225]  # List of managers IDs  in mini league

# Check current game week
with urllib.request.urlopen("https://fantasy.premierleague.com/drf/bootstrap-static") as u:
    current = u.read()
    curr = json.loads(current)
    currGW = curr["current-event"]

with urllib.request.urlopen("https://fantasy.premierleague.com/drf/elements/") as u:
    ele = u.read()
    ele = json.loads(ele)

class Player:
    def __init__(self, name, team, playerid):
        self.name = name
        self.team = team
        self.playerid = playerid

    def description(self):
        return "{} | {} | {}".format(self.name, self.team, self.playerid)

    def picks(self):
        gws = []
        for i in range (1, currGW+1):
            gws.append(i)
        picks = []
        for i in gws:
            with urllib.request.urlopen("https://fantasy.premierleague.com/drf/entry/{}/event/{}/picks".format(self.playerid, i)) as u:
                gwpicks = u.read()
                gwpicks = json.loads(gwpicks)
                picks.append(gwpicks)
        return dict(zip(gws, picks))

    def gwpoints(self):
        a = self.picks()
        gwpts = []
        for i in range(1, currGW + 1):
            gwpts.append(a[i]['entry_history']['points'])
        return gwpts

    def benchpoints(self):
        a = self.picks()
        benchpts = []
        for i in range(1, currGW + 1):
            benchpts.append(a[i]['entry_history']['points_on_bench'])
        return benchpts

    def formation(self):
        a = self.picks()
        fmtn = []
        GWfmtn = []
        GWcap=[]
        for i in range(1,currGW + 1):
            for j in range(0, 15):
                GWfmtn.append(a[i]['picks'][j]['element'])
                if a[i]['picks'][j]['multiplier'] == 2:
                    GWcap.append(a[i]['picks'][j]['element'])
            fmtn.append(GWfmtn)
            fmtn.append(GWcap)
        return fmtn

def lookup_indvpts(gw,id):
    with urllib.request.urlopen("https://fantasy.premierleague.com/drf/element-summary/{}".format(id)) as u:
        indv = u.read()
        indv = json.loads(indv)
        pt = indv['history'][gw-1]['total_points']
    return pt

def lookup_pos(id):
    for i in ele:
        if i["id"] == id:
            pos = i['element_type']
    return pos

def classify_formation(GWfmtn):
    starting = (GWfmtn[0])[0:11]
    sub = (GWfmtn[0])[11:15]
    cap = GWfmtn[1][0]
    starting.append(cap)
    gk = []; df = []; mf = []; fw = []
    for k in starting:
        if lookup_pos(k) == 1:
            gk.append(k)
        elif lookup_pos(k) == 2:
            df.append(k)
        elif lookup_pos(k) == 3:
            mf.append(k)
        elif lookup_pos(k) == 4:
            fw.append(k)
    return [gk, df, mf, fw, sub, cap]


def position_pts(gw, classified):
    gkptslist = []
    defptslist = []
    midptslist = []
    fwptslist = []
    subptslist = []
    for el in classified[0]:
        a = lookup_indvpts(gw,el)
        gkptslist.append(a)
    for el in classified[1]:
        a = lookup_indvpts(gw, el)
        defptslist.append(a)
    for el in classified[2]:
        a = lookup_indvpts(gw,el)
        midptslist.append(a)
    for el in classified[3]:
        a = lookup_indvpts(gw,el)
        fwptslist.append(a)
    for el in classified[4]:
        a = lookup_indvpts(gw,el)
        subptslist.append(a)
    cappts = lookup_indvpts(gw,classified[5])
    defpts = sum(gkptslist) + sum(defptslist)
    midpts = sum(midptslist)
    fwpts = sum(fwptslist)
    subpts = sum(subptslist)
    return [defpts,midpts,fwpts,subpts,cappts]

playerLib = []

# Instantiate managers
for el in playerIDList:
    with urllib.request.urlopen("https://fantasy.premierleague.com/drf/entry/%s" % el) as u:

        playerInfo = u.read()
        inf = json.loads(playerInfo)
        a = inf['entry']["player_first_name"] + " " + inf['entry']["player_last_name"]
        a = [a, inf['entry']["name"], inf['entry']["id"]]
        playerLib.append(a)
playerList = []  # list to store instances
for i in range (0, len(playerIDList)):
    playerList.append(Player(playerLib[i][0], playerLib[i][1], playerLib[i][2]))

# Output necessary data and dump json
data = {}
for j in range(1, currGW + 1):
    print("------------------------------------------------------------------------------------------------------------------------------------------\nGame Week " + str(j) + ":\n")
    gwpd = {}
    for i in playerList:
        print(i.description())
        output = (position_pts(j, (classify_formation(i.formation()))))
        gwpoints = sum(output[0:3])
        benchpoints = output[3]
        defpoints = output[0]
        midpoints = output[1]
        fwpoints = output[2]
        cappoints = output[4]
        gwd = {}
        gwd['game week points'] = gwpoints
        gwd['points left on bench'] = benchpoints
        gwd['points by defense'] = defpoints
        gwd['points by midfield'] = midpoints
        gwd['points by forwards'] = fwpoints
        gwd['points by captain'] = cappoints
        gwpd[i.playerid] = gwd
        print(" Game week points: {}\n "
              "Points left on bench: {}\n "
              "Points scored by defense: {}\n "
              "Points scored by midfielders: {}\n "
              "Points score by forwards: {}\n "
              "Points score by captain: {}\n"
              "---------------------------------------------------------------------".format(gwpoints, benchpoints, defpoints, midpoints, fwpoints, cappoints))
    data[j] = gwpd

with open("data_file.json", "w") as write_file:
    json.dump(data, write_file)
