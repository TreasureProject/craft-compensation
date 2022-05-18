from datetime import datetime
import json
import requests

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

def post_bridgeworld_query(query):
  response = requests.post("https://api.thegraph.com/subgraphs/name/treasureproject/bridgeworld", json={ "query": query })
  response_json = response.json()
  return response_json["data"] if "data" in response_json else {}

def get_affected_craftors():
  data = {}
  reporting_data = {}
  # startTime: May-07-2022 12:10:43 AM +UTC (block 11370606)
  # endTime: May-16-2022 12:42:30 AM +UTC (block 12170718)
  start_time = 1651882243 + 171000 # 47.5hrs
  end_time = 1652661750 + 171000 # 47.5hrs
  last_timestamp = str(start_time * 1000)
  end_timestamp = str(end_time * 1000)
  while True:
    print("Fetching crafts after %s" % last_timestamp)
    response = post_bridgeworld_query("""
      {
        crafts(
          first: 1000,
          where: {
            endTimestamp_gt: %s
            endTimestamp_lte: %s
          }
          orderBy: endTimestamp
          orderDirection: asc
        ) {
          endTimestamp
          difficulty
          user {
            id
          }
          outcome {
            broken {
              quantity
              token {
                tokenId
                name
              }
            }
          }
        }
      }
    """ % (last_timestamp, end_timestamp))

    # If no crafts are in response, we've paginated too far
    if not "crafts" in response or len(response["crafts"]) == 0:
      break
    
    for craft in response["crafts"]:
      # Only log crafts that had a broken
      if craft["outcome"] != None and len(craft["outcome"]["broken"]) > 0:
        user_id = craft["user"]["id"]

        # Add user to data dict
        if user_id not in data:
          data[user_id] = {}

        # Iterate over all their broken tokens
        for broken in craft["outcome"]["broken"]:
          token_id = int(broken["token"]["tokenId"])
          token_name = CARDS[token_id]
          quantity = int(broken["quantity"])

          # Add token to data dict
          if token_id not in data[user_id]:
            data[user_id][token_id] = 0
          if token_name not in reporting_data:
            reporting_data[token_name] = 0

          # Increment break count
          data[user_id][token_id] += quantity
          reporting_data[token_name] += quantity
    last_timestamp = response["crafts"][-1]["endTimestamp"]
  return data, reporting_data

data, reporting_data = get_affected_craftors()
with open("compensate_addrs.json", "wt") as out:
  out.write(json.dumps(data, indent=4, sort_keys=True))
with open("total_breaks.json", "wt") as out:
  out.write(json.dumps(reporting_data, indent=4, sort_keys=True))
