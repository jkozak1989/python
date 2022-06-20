import json
from beem import Hive
from beem.blockchain import Blockchain
from beem.block import Block
from beem.account import Account
import requests
import pickle
import time

accName = ""
privateKey = ""
cardsByIds = pickle.load(open("cardsByIds.p", "rb"))
newRewardCards = [341, 347, 346, 332, 335, 350, 338, 344, 345, 333, 351, 348, 342, 336, 339]
lastCard = ""
boughtCards = {}

hive = Hive(keys=[privateKey])
blockchain = Blockchain()
account = Account(accName, blockchain_instance=hive)
num = blockchain.get_current_block_num()
counter = 1

def getCardPrices():
    result = requests.get("https://api2.splinterlands.com/market/for_sale_grouped")
    result = result.json()
    bids = requests.get("https://peakmonsters.com/api/bids/top")
    bids = bids.json()
    regularBids = {}
    goldBids = {}
    for bid in bids["bids"]:
        if bid["card_detail_id"] != None and bid["gold"] == False:
            regularBids[bid["card_detail_id"]] = bid["usd_price"]
        elif bid["card_detail_id"] != None and bid["gold"] == True:
            goldBids[bid["card_detail_id"]] = bid["usd_price"]
    regularDict = {}
    goldDict = {}
    for i in result:
        if i["gold"] == False:
            if regularBids[i["card_detail_id"]] < 0.75*i["low_price"]:
                regularDict[i["card_detail_id"]] = regularBids[i["card_detail_id"]]*1.3
            else:
                regularDict[i["card_detail_id"]] = i["low_price"]
        else:
            try:
                if goldBids[i["card_detail_id"]] < 0.75*i["low_price"]:
                    goldDict[i["card_detail_id"]] = goldBids[i["card_detail_id"]]*1.3
                else:
                    goldDict[i["card_detail_id"]] = i["low_price"]
            except:
                goldDict[i["card_detail_id"]] = i["low_price"]
    return regularDict, goldDict

def checkCardDetails(card, regularPrices, regularDiscount, goldPrices, goldDiscount):
    global newRewardCards
    global lastCard
    global boughtCards
    r = requests.get("https://api.splinterlands.io/cards/find?ids="+card['cards'][0])
    r = r.json()
    if r[0]['buy_price'] != None and int(r[0]["xp"]) == 1:
        if r[0]['gold'] == False:
            if float(r[0]['buy_price']) < regularDiscount*regularPrices[r[0]['card_detail_id']] and r[0]['edition'] == 7:
                if r[0]['market_id'] != lastCard:
                    buyCard(r[0]['market_id'], float(r[0]['buy_price']))
                    boughtCards[card['cards'][0]] = regularPrices[r[0]['card_detail_id']]
                    print(f"{cardsByIds[r[0]['card_detail_id']]} - {r[0]['buy_price']} - {r[0]['market_id']}")
                    lastCard = r[0]['market_id']
            elif float(r[0]['buy_price']) < regularDiscount*regularPrices[r[0]['card_detail_id']] and r[0]['card_detail_id'] in newRewardCards:
                if r[0]['market_id'] != lastCard:
                    buyCard(r[0]['market_id'], float(r[0]['buy_price']))
                    boughtCards[card['cards'][0]] = regularPrices[r[0]['card_detail_id']]
                    print(f"{cardsByIds[r[0]['card_detail_id']]} - {r[0]['buy_price']} - {r[0]['market_id']}")
                    lastCard = r[0]['market_id']
        """
        else:
            if float(r[0]['buy_price']) < goldDiscount*goldPrices[r[0]['card_detail_id']] and r[0]['edition'] == 7:
                buyCard(r[0]['market_id'])
                print(f"{cardsByIds[r[0]['card_detail_id']]} - {r[0]['buy_price']} - {r[0]['market_id']}")
            elif float(r[0]['buy_price']) < goldDiscount*goldPrices[r[0]['card_detail_id']] and r[0]['card_detail_id'] in newRewardCards:
                buyCard(r[0]['market_id'])
                print(f"{cardsByIds[r[0]['card_detail_id']]} - {r[0]['buy_price']} - {r[0]['market_id']}")
        """

def checkCardsForSale(block, regularPrices, goldPrices):
    for tr in block.json_transactions:
        if 'id' in tr['operations'][0]['value'].keys():
            if tr['operations'][0]['value']['id'] == 'sm_sell_cards':
                trJson = json.loads(tr['operations'][0]['value']['json'])
                if type(trJson) != dict:
                    for card in trJson:
                        if float(card['price']) > 0.03 and float(card['price']) < 16:
                            checkCardDetails(card, regularPrices, 0.9, goldPrices, 0.80)
                    #    elif float(card['price']) >= 16 and float(card['price']) < 80:
                    #        checkCardDetails(card, regularPrices, 0.85, goldPrices, 0.75)
                else:
                    if float(trJson['price']) > 0.03 and float(trJson['price']) < 16:
                        checkCardDetails(trJson, regularPrices, 0.9, goldPrices, 0.80)
                    #elif float(card['price']) >= 16 and float(card['price']) < 80:
                    #    checkCardDetails(card, regularPrices, 0.85, goldPrices, 0.75)

def buyCard(marketId, price):
    purchaseJson = {"items": [marketId],
                "price": price,
                "currency": "DEC",
                "market": "peakmonsters",
                "app": "peakmonsters"}
    hive.custom_json("sm_market_purchase", json_data=purchaseJson, required_auths=[accName])


def sellCard(cardId, price):
    saleJson = {"cards": [cardId], "currency": "USD", "price": price, "fee_pct": 500}
    hive.custom_json("sm_sell_cards", json_data=saleJson,
                         required_auths=[accName])

def followBlocks(regularPrices, goldPrices):
    global num
    try:
        block = Block(num)
        checkCardsForSale(block, regularPrices, goldPrices)
        num += 1
    except:
        try:
            num += 1
            block = Block(num)
            checkCardsForSale(block, regularPrices, goldPrices)
            num += 1
        except:
            num -= 3

def findCardsForSale(regularPrices, goldPrices):
    r = requests.get("https://api2.splinterlands.com/cards/collection/"+accName)
    r = r.json()
    for card in r['cards']:
        if card['market_listing_type'] == None:
            if card['gold'] == False:
                sellCard(card['uid'], boughtCards[card['uid']])
                print(f"{card['uid']}-{boughtCards[card['uid']]}")
            else:
                sellCard(card['uid'], boughtCards[card['uid']])

def main():
    global num
    global counter
    regularPrices, goldPrices = getCardPrices()

    while True:
        if counter % 100 == 0:
            findCardsForSale(regularPrices, goldPrices)
            time.sleep(2)
            try:
                regularPrices, goldPrices = getCardPrices()
            except:
                continue
            counter = 1
            num = blockchain.get_current_block_num()
        followBlocks(regularPrices, goldPrices)
        counter += 1


main()
