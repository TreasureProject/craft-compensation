import pandas as pd
import json
import datetime
from dateutil.parser import parse

CARDS = {
    73: "Diamond",
    68: "Common Bead",
    76: "Donkey",
    77: "Dragon Tail",
    48: "Beetle Wings",
    103: "Lumber",
    79: "Emerald",
    69: "Common Feather",
    151: "Silver Coin",
    92: "Gold Coin",
    162: "Unbreakable Pocketwatch",
    93: "Grain",
    72: "Cow",
    49: "Blue Rupee",
    71: "Common Relic",
    96: "Half Penny",
    115: "Pearl",
    117: "Quarter Penny",
    82: "Favor from the Gods",
    94: "Green Rupee",
    152: "Small Bird",
    133: "Red Rupee",
    116: "Pot of Gold",
    114: "Ox",
    91: "Framed Butterfly",
    75: "Divine Mask",
    100: "Jar of Fairies",
    164: "Witches Broom",
    141: "Score of Ivory",
}


ffile = "./affected_craftors.json"


with open(ffile) as f:
    raw_json = json.loads(f.read())


def format_as_json(x):
    date_string = x[2]
    date_parsed = parse(date_string)
    timestamp = date_parsed.timestamp()

    return {
        "address": x[0],
        "difficulty": x[1],
        "date": date_parsed,
        # "timestamp": timestamp,
        "tokenId": x[3][0],
        "num_broken": x[3][1],
    }


def countTokenIds(ddat):
    broken = {}

    for row in ddat.iterrows():
        tokenId = int(row[1]['tokenId'])
        tokenName = CARDS[tokenId]
        numToken = int(row[1]['num_broken'])

        if broken.get(tokenName):
            broken[tokenName] += numToken
        else:
            broken[tokenName] = numToken

    return broken


def countBrokenPerAddr(ddat):
    broken = {}

    for row in ddat.iterrows():

        addr = row[0]
        tokenId = int(row[1]['tokenId'])
        numToken = int(row[1]['num_broken'])

        if broken.get(addr):
            if broken[addr].get(tokenId):
                broken[addr][tokenId] += numToken
            else:
                broken[addr][tokenId] = numToken
        else:
            broken[addr] = {}
            broken[addr][tokenId] = numToken

    return broken


# startTime: May-07-2022 12:10:43 AM +UTC (block 11370606)
# endTime: May-16-2022 12:42:30 AM +UTC (block 12170718)
startTime = parse('May-07-2022 12:10:43 AM')
endTime = parse('May-16-2022 12:42:30 AM')

broken_items = [format_as_json(x) for x in raw_json]

ddat = pd.DataFrame(broken_items)
ddat = ddat.set_index("address")
compensate_addrs1 = ddat[(startTime < ddat['date']) & (ddat['date'] <= endTime)]


print("Total treasures broken")
print(countTokenIds(compensate_addrs1))


compensate_addrs2 = countBrokenPerAddr(compensate_addrs1)
print("Compensate addresses")
print(compensate_addrs2)


with open('compensate_addrs.json', 'w') as f:
    f.writelines(json.dumps(compensate_addrs2, indent=4))




