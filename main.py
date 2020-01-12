import urllib.request
import json
from datetime import datetime

playerIDList = ['353431', '979205', '2702348', '3843035', '898689', '430222', '1114888']  # List of managers IDs  in mini league

# Check current game week
with urllib.request.urlopen("https://fantasy.premierleague.com/api/bootstrap-static/") as u:
    current = u.read()
    curr = json.loads(current)
    for elem in curr["events"]:
        if elem["is_current"]:
            currGW = elem['id']

with urllib.request.urlopen("https://fantasy.premierleague.com/api/bootstrap-static/") as u:
    ele = u.read()
    ele = json.loads(ele)['elements']

class Player:
    def __init__(self, name, team, playerid):
        self.name = name
        self.team = team
        self.playerid = playerid

    def description(self):
        return "{} | {} | {}".format(self.name, self.team, self.playerid)

    def picks(self):
        gws = []
        for i in range(1, currGW+1):
            gws.append(i)
        picks = []
        for i in gws:
            with urllib.request.urlopen("https://fantasy.premierleague.com/api/entry/{}/event/{}/picks/".format(self.playerid, i)) as u:
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
        for i in range(1,currGW + 1):
            GWfmtn = []
            GWcap=[]
            cost = a[i]["entry_history"]["event_transfers_cost"]
            if a[i]['active_chip'] == 'bboost':
                GWbboost = True
            else:
                GWbboost = False
            for j in range(0, 15):
                GWfmtn.append(a[i]['picks'][j]['element'])
                if a[i]['picks'][j]['multiplier'] == 2:
                    GWcap.append(a[i]['picks'][j]['element'])
                elif a[i]['picks'][j]['multiplier'] == 3:
                    GWcap.append(a[i]['picks'][j]['element'])
                    GWcap.append(a[i]['picks'][j]['element'])
            fmtn.append(GWfmtn)
            fmtn.append(GWcap)
            fmtn.append(GWbboost)
            fmtn.append(cost)
        return fmtn

def lookup_indvpts(gw,id):
    with urllib.request.urlopen("https://fantasy.premierleague.com/api/element-summary/{}/".format(id)) as u:
        indv = u.read()
        indv = json.loads(indv)
        idarr = []
        ptsarr = []
        for i in range(0, len(indv['history'])):
            if indv['history'][i]['round'] == gw:
                idarr.append(i)
        for j in idarr:
            ptsarr.append(indv['history'][j]['total_points'])
        pt = 0
        for k in ptsarr:
            pt = pt + k
    return pt

def lookup_pos(id):
    for i in ele:
        if i["id"] == id:
            pos = i['element_type']
    return pos

def classify_formation(GWfmtn):
    if GWfmtn[2]:
        starting = GWfmtn[0]
        sub = []
    else:
        starting = (GWfmtn[0])[0:11]
        sub = (GWfmtn[0])[11:15]
    cap = GWfmtn[1]
    cost = GWfmtn[3]
    for el in cap:
        starting.append(el)
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
    if len(cap) == 0:
        return [gk, df, mf, fw, sub, None, cost]
    else:
        return [gk, df, mf, fw, sub, cap[0], cost]

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
    if classified[5] is None:
        cappts = 0
    else:
        cappts = lookup_indvpts(gw, classified[5])
    defpts = sum(gkptslist) + sum(defptslist)
    midpts = sum(midptslist)
    fwpts = sum(fwptslist)
    subpts = sum(subptslist)
    cost = classified[6]
    return [defpts,midpts,fwpts,subpts,cappts,cost]

playerLib = []

# Instantiate managers
for el in playerIDList:
    with urllib.request.urlopen("https://fantasy.premierleague.com/api/entry/%s/" % el) as u:
        playerInfo = u.read()
        inf = json.loads(playerInfo)
        a = inf["player_first_name"] + " " + inf["player_last_name"]
        a = [a, inf["name"], inf["id"]]
        playerLib.append(a)
playerList = []  # list to store instances
for i in range (0, len(playerIDList)):
    playerList.append(Player(playerLib[i][0], playerLib[i][1], playerLib[i][2]))

# read old json
with open("data_file.json", "r") as read_file:
    old_data = json.load(read_file)

# Output necessary data and dump json
data = {}

# fast mode
for j in range(1, currGW):
    data[j] = old_data[str(j)]

nameDict = {}
for i in range(0,len(playerIDList)):
    nameDict.update({playerIDList[i]: playerList[i].description()})

for j in range(currGW - 1, currGW + 1):
    print("------------------------------------------------------------------------------------------------------------------------------------------\nGame Week " + str(j) + ":\n")
    gwpd = {}
    for i in playerList:
        print(i.description())
        output = (position_pts(j, (classify_formation(i.formation()[(j-1) * 4:(j * 4)]))))
        gwpoints = sum(output[0:3]) - output[5]
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

with open("data_file.json") as u:
    data = u.read()
    data = json.loads(data)

gameWeeks = []
for i in range (1,39):
    gameWeeks.append(str(i))
visual = []

def sum_up(indicator, name):
    playerTotalpts = [name]
    for j in playerIDList:
        totalpts = []
        for w in range(0, currGW):
            i = gameWeeks[w]
            totalpts.append(data[i][j][indicator])
        summation = sum(totalpts)
        playerTotalpts.append(summation)
    return playerTotalpts

title = ["Main Scores"]
for i in playerIDList:
    title.append(nameDict[i])
matr = [title, sum_up('game week points','Overall Points'),
        sum_up('points left on bench', 'Points left on bench'),
        sum_up('points by defense', 'Points scored by defense'),
        sum_up('points by midfield', 'Points scored by midfielders'),
        sum_up('points by forwards', "Points scored by forwards"),
        sum_up('points by captain', "Points scored by captain (x1)"),
        ]
for i in matr:
    visual.append(i)

mainvisual = []

for i in range(0,len(title)):
    lista = []
    for j in range (0,len(matr)):
        lista.append(visual[j][i])
    mainvisual.append(lista)

print(mainvisual)

monthHeader = ['Manager of the Month']
months = ['August', 'September', 'October', 'November', 'December', 'January', 'February', 'March', 'April', 'May']
monthLimit = [0, 4, 7, 10, 14, 20, 24, 28, 31, 35, 38]
for i in range(0, len(months)):
    if (currGW > monthLimit[i]) and (currGW <= monthLimit[i+1]):
        currMonth = months[i]
        monthIndex = i
        for j in range(0,i+1):
            monthHeader.append(months[j])

monthVisual = [monthHeader]

for i in playerIDList:
    monthPoints = [nameDict[i]]
    for j in range(0,monthIndex):
        weeksOfMonth = []
        for k in range(monthLimit[j], monthLimit[j+1]):
            weeksOfMonth.append(data[gameWeeks[k]][i]['game week points'])
            ptsOfMonth = sum(weeksOfMonth)
        monthPoints.append(ptsOfMonth)
    weeksOfMonth = []
    for l in range(monthLimit[monthIndex],currGW):
        weeksOfMonth.append(data[gameWeeks[l]][i]['game week points'])
        ptsOfMonth = sum(weeksOfMonth)
    monthPoints.append(ptsOfMonth)
    monthVisual.append(monthPoints)

print(monthVisual)

cum19Header = ['2019/20']
for i in range(1,currGW+1):
    cum19Header.append(str(i))
cum1920 = [cum19Header]

for i in playerIDList:
    cumPoints = [nameDict[i]]
    for j in range(0+1,currGW+1):
        cumCal = []
        for k in range (0,j):
            cumCal.append(data[gameWeeks[k]][i]['game week points'])
        cumWeek = sum(cumCal)
        cumPoints.append(cumWeek)
    cum1920.append(cumPoints)

print(cum1920)

with open("cum_file1819.json", "r", encoding="utf-8") as read_file:
    cum1819 = json.load(read_file)

with open("cum_file.json", "w") as write_file:
    json.dump([cum1920,cum1819], write_file)

rank1920 = cum1920[:]
rankDraft = []

for i in range(0, currGW+1):
    weekMat = []
    for j in range(1, 8):
        weekMat.append(rank1920[j][i])
    weekMat = sorted(weekMat,reverse=True)
    rankDraft.append(weekMat)

for i in range(1,8):
    for j in range(1, currGW+1):
        rank1920[i][j] = (rankDraft[j].index(rank1920[i][j])) + 1

print(rank1920)

with open("visual_file.json", "w") as write_file:
    json.dump([mainvisual,monthVisual], write_file)

with open("ranking_file1819.json", "r", encoding="utf-8") as read_file:
    rank1819 = json.load(read_file)

with open("ranking_file.json", "w") as write_file:
    json.dump([rank1920,rank1819], write_file)

indvHeader = [None,'GW points', 'Bench Points', 'Defense Points', 'Midfield Points', 'Forward Points', 'Captain Points']
indvInfo = ["game week points", "points left on bench", "points by defense", "points by midfield", "points by forwards", "points by captain"]
indvMatx = []
for i in playerIDList:
    playerMatx = []
    newHeader = indvHeader[:]
    newHeader[0] = nameDict[i]
    playerMatx.append(newHeader)
    for j in range(0,currGW):
        gw = gameWeeks[j]
        if int(gw) < 10:
            gwRow = ['GW0' + gw]
        else:
            gwRow = ['GW' + gw]
        for k in indvInfo:
            gwRow.append(data[gw][i][k])
        playerMatx.append(gwRow)
    indvMatx.append(playerMatx)
print(indvMatx)

with open("individuals_file.json", "w") as write_file:
    json.dump(indvMatx, write_file)

times = datetime.strftime(datetime.now(), "%d/%m/%y %H:%M UTC+8")
updateMsg = ["Last update: " + str(times) + " for GW" + str(currGW)]
print(updateMsg)
with open("update_time.json", "w") as write_file:
    json.dump([[updateMsg]], write_file)