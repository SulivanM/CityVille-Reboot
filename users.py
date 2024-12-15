import json
import xmltodict
from pathlib import Path
import math
from datetime import datetime
from os import mkdir
import os

import rand

TEMP_ID_START = 63000
TEMP_ID_END = 63750

settings = {}
items = {}
users = {}
randomTables = {}

def timestamp():
    return int(datetime.now().timestamp())

def init():
    global settings, items, users, randomTables
    settings = initSettings()
    items = getItems(settings)
    randomTables = getRandomTables(settings)
    users = initUsers()


def getPopulation(userId):
    if userId not in users:
        return 0
    return users[userId]['userInfo']['world']['citySim']['population'] * 10

def getGold(userId):
    if userId not in users:
        return 0
    return users[userId]['userInfo']['player']['gold']


def initSettings():
    with open('public/game_data/gameSettings.xml') as f:
        xml_string = f.read()
    xml_dict = xmltodict.parse(xml_string)
    settings = xml_dict['settings']
    return settings

def initUsers():
    users = {}
    dir = Path('public/game_data/users')
    i = 0
    for subdir in dir.iterdir():
        id = subdir.stem
        filename = str(subdir) + '/user.json'
        with open(filename) as file:
            data = json.load(file)
        users[id] = data
        i += 1
    print('Users found:',i-1)
    return users

def recalcLevel(userId):
    player = users[userId]['userInfo']['player']
    xp = player['xp']
    player['level'] = getLevel(xp)
    player['energyMax'] = getEnergyMax(xp)

def save(userId):
    recalcLevel(userId)
    if not os.path.exists('users/' + userId):
        mkdir('users/' + userId)
    filename = 'users/' + userId + '/user.json'
    data = users[userId]
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


def getExpansions(userId):
    if userId not in users:
        return 0
    return users[userId]['userInfo']['player']['expansionsPurchased']

def remapIds(userId):
    worldObjects = users[userId]['userInfo']['world']['objects']
    result = []
    for obj in worldObjects:
        if 'id' not in obj:
            continue
        id = obj['id']
        if id >= TEMP_ID_START and id <= TEMP_ID_END:
            # assign permanent ids
            newId = users[userId]['idCounter']
            users[userId]['idCounter'] += 1
            # print(users[userId]['idCounter'])
            obj['id'] = newId
            result.append({'id': id, 'newId': newId })
    print('Assigned',len(result),'permanent IDs')
    return result
    
def createMapRect(expandType,pos):
    width = int(items[expandType]['@width'])
    height = int(items[expandType]['@height'])
    rect = { 'x': pos['x'], 'y': pos['y'], 'width': width, 'height': height}
    # print(rect)
    return rect

def expandCity(userId, data):
    print('Expanding Map')
    userInfo = users[userId]['userInfo']
    userInfo['player']['expansionsPurchased'] += 1
    # add rect to map rects
    userInfo['world']['mapRects'].append(createMapRect(data[0],data[1]))
    # remap ids first so that only wilderness gets done in next round
    remapIds(userId)
    # TODO: why bother?  just create a new world object, rather than edit these so much
    for item in data[2]:
        item['className'] = 'Wilderness'
        item['direction'] = item['dir']
        item['state'] = 'static'        
        item['position'] = { 'x': item['x'], 'y': item['y'], 'z': 0}
        del item['dir']
        del item['x']
        del item['y']
    userInfo['world']['objects'].extend(data[2])
    result = remapIds(userId)
    save(userId)
    return result

            
def renameCity(userId,newName):
    if userId not in users:
        return {}
    # TODO: i think the client does some sanitizing, we should probably do it again here
    # i.e. newName = newName.replace("'","").replace('"',"") -- Poor man's sanitizer.
    users[userId]['userInfo']['worldName'] = newName
    return { 'name': newName }
    
def getUser(userId):
    if userId == '-1':
        return users['samantha']    
    if userId not in users:
        print('User',userId,'not found. Creating new user.')
        data = users['newUser'].copy() # TODO: should be deep copy, not shallow copy !!!
        data['userInfo']['player']['uid'] = int(userId)
        users[userId] = data
        save(userId)
    else:
        if len(remapIds(userId)) > 0:
            save(userId)
    print('Got User',userId)
    return users[userId];
      
def updateWorld(id, message):
    print(id)
    print(message)
    save(id)
    
def updateOptions(id, options):
    print('Saving preferences for user',id)
    if id in users:
        # print(options)
        users[id]['userInfo']['player']['options'] = options[0]
        save(id)

def completedTutorial(userId):
    print('User',userId,'completed tutorial.')
    if userId in users:
        users[userId]['userInfo']['is_new'] = False
        save(userId)

def getIndexById(worldObjects, objectId):
    # TODO: use a faster lookup (dictionary)
    for i in range(len(worldObjects)):
        object = worldObjects[i]
        if 'id' in object and object['id'] == objectId:
            return i
    return -1

def getLevel(xp):
    levels = settings['levels']
    for level in levels['level']:
        if int(level['@requiredXP']) > xp:
            return int(level['@num'])
            return level['@num']
    return 1

def getEnergyMax(xp):
    levels = settings['levels']
    for level in levels['level']:
        if int(level['@requiredXP']) > xp:
            return int(level['@energyMax'])
    return 12
    

def getCost(itemId):
    print('TODO: Implement get cost')
    return 0


def giveRewards(userId, rewards, unknown):
    if userId not in users:
        return
    player = users[userId]['userInfo']['player']
    for item in rewards.keys():
        match item:
            case '@gold' | '@coins':
                player['gold'] += int(rewards[item])
            case '@cash':
                player['cash'] += int(rewards[item])
            case '@xp':
                player['xp'] += int(rewards[item])
            case '@energy':
                player['energy'] += int(rewards[item])
            case '@goods':
                player['commodities']['storage']['goods'] += int(rewards[item])
            case '@itemName' | '@item':                
                inventoryAdd(userId,rewards[item],1,True)
            case '@itemUnlock':
                player['seenFlags'][rewards[item]] = 1
            case '@grantHQ':
                if rewards[item] == "true":
                    franchises = getFranchisesByLocation(userId,'-1')
                    for franchise in franchises:
                        print(franchise)
                        franchiseType = franchiseGetHQType(franchise['name'])
                        franchiseGrantHQ(userId,franchiseType)
            case _:
                print(' UNKNOWN REWARD:',item,rewards[item])
    save(userId)

def collectDoobers(userId,itemName):
    doobers,secureRands = rand.generateDoobers(userId,itemName)
    player = users[userId]['userInfo']['player']
    for doober in doobers:
        match doober[0]:
            case 'food' | 'goods':
                player['commodities']['storage']['goods'] += doober[1]
            case 'coin':
                player['gold'] += doober[1]
            case 'xp':
                player['xp'] += doober[1]
            case 'energy':
                player['energy'] += doober[1]
            case 'collectable':
                collectionAdd(userId,doober[1])
            case _:
                print('UNKNOWN DOOBER:', doober)
    return secureRands

def recalcPop(worldObjects):
    print('Recalculating Population...')
    pop = 0
    for item in worldObjects:
        itemName = item['itemName']
        if 'populationYield' in items[itemName]:
            popYield = items[itemName]['populationYield']
            pop += 10 * int(popYield)
    print('Population:',pop)
    return pop

def recalcPopCap(worldObjects):
    print('Recalculating Population Limit...')
    popCap = int(settings['farming']['@initPopulationCap']) * 10
    for item in worldObjects:
        itemName = item['itemName']
        if 'populationCapYield' in items[itemName]:
            popCapYield = items[itemName]['populationCapYield']
            popCap += 10 * int(popCapYield)
    print('Population Limit:',popCap)
    return popCap
    
def handleVisits(userId,params):
    for i in range(len(params[0])):
        businessId = params[0][i]
        quantity = params[1][i]
        
        business = getObjectById(userId,businessId)
        if business != None:
            if 'visits' not in business:
                business['visits'] = quantity
            else:
                business['visits'] += quantity
            busData = items[business['itemName']]
            if 'commodityReq' in busData:
                if business['visits'] >= int(busData['commodityReq']):
                    business['state'] = 'closedHarvestable'
            save(userId)

def performAction(userId,params):
    if userId not in users:
        print('User not found')
        return
    action = params[0]
    resource = params[1]
    worldObjects = users[userId]['userInfo']['world']['objects']
    if action == 'place':
        print('Placing object')
        name = resource['itemName']
        item = items[name]
        if 'construction' in item:
            construction = item['construction']
            print(construction)
            site = createConstructionSite(resource['id'], construction, resource['direction'], name, resource['className'],resource['position'], resource['state'])
            worldObjects.append(site)
        else:
            worldObjects.append(resource)
        save(userId)            
        # return {'id': int(objectId)}
    elif action == 'build':
        objectId = resource['id']
        print('Building object')
        # print(resource)
        index = getIndexById(worldObjects,objectId)
        if index != -1 and 'builds' in worldObjects[index]:
            # print(worldObjects[index])
            currentBuild = worldObjects[index]['builds']
            currentBuild += 1
            currentStage = worldObjects[index]['stage']
            currentStage += 1
            worldObjects[index]['builds'] = currentBuild
            worldObjects[index]['finishedBuilds'] = currentBuild
            worldObjects[index]['stage'] = currentStage
            print('Current Stage:', currentStage)  
            save(userId)
        else:
            print('Could not find object',objectId)

    elif action == 'finish':
        objectId = resource['id']
        print('Finishing object')
        index = getIndexById(worldObjects,objectId)
        if index != -1:
            oldItem = worldObjects[index]            
            worldObjects[index] = {
                'itemName': oldItem['targetBuildingName'],
                'className': oldItem['targetBuildingClass'],
                'id': oldItem['id'],
                'position': oldItem['position'],
                'direction': oldItem['direction'],
                'state': oldItem['state']
            }
            if oldItem['state'] == 'planted':
                worldObjects[index]['plantTime'] = timestamp()
            
            users[userId]['userInfo']['world']['citySim']['population'] = recalcPop(worldObjects)//10
            users[userId]['userInfo']['world']['citySim']['populationCap'] = recalcPopCap(worldObjects)//10
            save(userId)
    elif action == 'move':
        print('Moving object')
        objectId = resource['id']
        index = getIndexById(worldObjects,objectId)
        if index != -1:
            print('New Position for Object',objectId,';',resource['position'])
            item = worldObjects[index] 
            item['position'] = resource['position']
            item['direction'] = resource['direction']
            save(userId)
    elif action == 'sell':
        print('Selling object')
        objectId = resource['id']
        index = getIndexById(worldObjects,objectId)
        if index != -1:
            del worldObjects[index]
            name = resource['itemName']
            sellAmount = math.ceil(getCost(name) * 0.05)
            users[userId]['userInfo']['player']['gold'] += sellAmount
            users[userId]['userInfo']['world']['citySim']['population'] = recalcPop(worldObjects)//10
            users[userId]['userInfo']['world']['citySim']['populationCap'] = recalcPopCap(worldObjects)//10
            save(userId)
        else:
            print('Object',objectId,'not found')
    elif action == 'clear':
        print('Clearing object')
        objectId = resource['id']
        index = getIndexById(worldObjects,objectId)
        if index != -1:
            itemName = worldObjects[index]['itemName']
            secureRands = collectDoobers(userId,itemName)
            del worldObjects[index]
            return { 'secureRands': secureRands }
    elif action == 'harvest':
        className = resource['className']
        coinYield = 0
        if className == 'Plot':
            contract = resource['contractName']
            print('Harvesting',contract)
            if contract in items:
                coinYield = items[contract]['coinYield']
        else:
            print('Harvesting',className)
            itemName = resource['itemName']
            if itemName in items and 'coinYield' in items[itemName]:
                coinYield = items[itemName]['coinYield']
        item = getObjectById(userId,resource['id'])
        if item != None:
            if item['className'] == 'Plot':
                item['state'] = 'plowed'
                print('Plowed')
            elif item['state'] == 'open':
                item['state'] = 'closed'
                item['visits'] = 0
            elif item['state'] == 'grown':
                item['state'] = 'planted'
                item['plantTime'] = timestamp() * 1000 # in milliseconds.
            secureRands = collectDoobers(userId,item['itemName'])
        else:
            secureRands = []
        save(userId)
        return { 'retCoinYield': coinYield , 'secureRands': secureRands }
    elif action == 'startContract':
        print('Starting Contract')
        replaceObjectById(userId,resource['id'],resource)
        save(userId)
    elif action == 'openBusiness':
        item = getObjectById(userId,resource['id'])
        if item != None:
            item['state'] = 'open'
            item['visits'] = 0
            itemData = items[item['itemName']]
            player = users[userId]['userInfo']['player']
            player['commodities']['storage']['goods'] -= int(itemData['commodityReq'])
            save(userId)
    else:
        print(action)
        print(resource)


    

def getItems(settings):
    dict = {}
    items  = settings['items']['item']
    for item in items:
        name = item['@name']
        dict[name] = item
    print('Items found:', len(items))
    return dict
    
def getRandomTables(settings):
    dict = {}
    randomTables = settings['randomModifierTables']['randomModifierTable']
    for table in randomTables:
        name = table['@name']
        dict[name] = table
    print('Random tables found:', len(randomTables))
    return dict

def createConstructionSite(id,construction,direction,targetName,targetClass,position,state):
    return {
        'position': position,
        'itemName': construction,
        'className': 'ConstructionSite',
        'id': id,
        'targetBuildingClass': targetClass,
        'targetBuildingName': targetName,
        'stage': 0,
        'finishedBuilds': 0,
        'builds': 0,
        'direction': direction,
        'state': state
    }

def getObjectById(userId, itemId):
    worldObjects = users[userId]['userInfo']['world']['objects']
    for obj in worldObjects:
        if 'id' in obj and obj['id'] == itemId:
            return obj
    return None
 
def replaceObjectById(userId, itemId, newItem):
    worldObjects = users[userId]['userInfo']['world']['objects']
    for i in range(len(worldObjects)):
        if worldObjects[i]['id'] == itemId:
            worldObjects[i] = newItem
            break

def getItemByName(name):
    if name in items:
        return items[name]
    return None

def getObjectsByName(userId,name):
    result = []
    if userId not in users:
        return result
    worldObjects = users[userId]['userInfo']['world']['objects']
    for obj in worldObjects:
        if obj['itemName'] == name:
            result.append(obj)
    return result

def getObjectsByClass(userId,className):
    result = []
    if userId not in users:
        return result
    worldObjects = users[userId]['userInfo']['world']['objects']
    for obj in worldObjects:
        if obj['className'] == className:
            result.append(obj)
    return result
    
def acquireLicense(userId,licenses):
    # code only seems to allow one license at a time
    player = users[userId]['userInfo']['player']
    player['licenses'][licenses[0]] = 1
    save(userId)
    return { 'itemName': licenses[0] }
    

def inventoryAdd(userId,itemName,quantity,isGift):
    # TODO: handle gift case
    # TODO: add max quantity checks
    inventory = users[userId]['userInfo']['player']['inventory']
    inventory['count'] += quantity
    if itemName in inventory['items']:
        inventory['items'][itemName] += quantity
    else:
        inventory['items'][itemName] = quantity
    save(userId)

def inventoryRemove(userId,itemName, quantity):
    inventory = users[userId]['userInfo']['player']['inventory']
    if quantity <= 0 or inventoryCount(userId,itemName) < quantity:
        return False
    inventory['count'] += quantity
    inventory['items'][itemName] -= quantity
    if inventory['items'][itemName] == 0:
        del inventory['items'][itemName]
    save(userId)

def inventoryCount(userId,itemName):
    inventory = users[userId]['userInfo']['player']['inventory']
    if itemName not in inventory['items']:
        return 0
    return inventory['items'][itemName]

def getCollectionByCollectableName(name):
    collections = settings['collections'][0]['collection']
    for collection in collections:
        collectionName = collection['@name']
        for collectable in collection['collectables']['collectable']:
            if collectable['@name'] == name:
                return collectionName
    return None

def collectionAdd(userId,itemName):
    if itemName not in items:
        print('Missing item:',itemName)
        return
    collection = getCollectionByCollectableName(itemName)
    if collection == None:
        print('Missing collection for',itemName)
        return
    collections = users[userId]['userInfo']['player']['collections']
    if collection not in collections:
        collections[collection] = {}
    if itemName in collections[collection]:
        collections[collection][itemName] += 1
    else:
        collections[collection][itemName] = 1
    save(userId)

def collectionRemove(userId,itemName):
    collection = getCollectionByCollectableName(itemName)
    collections = users[userId]['userInfo']['player']['collections']
    if collection in collections and itemName in collections[collection]:
        collections[collection][itemName] -= 1
        if collections[collection][itemName] <= 0:
            del collections[collection][itemName]
    save(userId)


def collectionTradeIn(userId,name):
    # remove one of each item in collection
    collections = users[userId]['userInfo']['player']['collections']
    if name not in collections:
        return False
    collectables = collections[name].copy()
    for collectable in collectables:
        collectionRemove(userId,collectable)
    completedCollections = users[userId]['userInfo']['player']['completedCollections']
    if name not in completedCollections:
        completedCollections[name] = 1
    else:
        completedCollections[name] += 1
    collectionGrantReward(userId,name)

def collectionGrantReward(userId,name):
    if userId not in users:
        return
    player = users[userId]['userInfo']['player']
    collections = settings['collections'][0]['collection']
    for collection in collections:
        if collection['@name'] == name:
            rewards = collection['tradeInReward']
            for reward in rewards:
                # print('Trade In Reward:',reward,rewards[reward])
                match reward:
                    case 'coin':
                        player['gold'] += int(rewards[reward]['@amount'])
                    case 'xp':
                        player['xp'] += int(rewards[reward]['@amount'])
                    case 'energy':
                        player['energy'] += int(rewards[reward]['@amount'])
                    case 'goods':
                        player['commodities']['storage']['goods'] += int(rewards[reward]['@amount'])
                    case 'item':           
                        inventoryAdd(userId,rewards[reward]['@name'],1,True)
                    case _:
                        print('UNKNOWN TRADE-IN REWARD',reward)
            break
    save(userId)

    
def getCollectableCount(userId,itemName):
    if userId not in users:
        return 0
    collection = getCollectionByCollectableName(itemName)
    collections = users[userId]['userInfo']['player']['collections']
    if collection in collections and itemName in collections[collection]:
        return collections[collection][itemName]
    return 0;

        
def getFranchisesByLocation(userId,neighborId):
    result = []
    franchises = users[userId]['franchises']
    for franchise in franchises:
        print(franchise)
        if neighborId in franchise['locations']:
            # result.append(franchise['locations'][neighborId])
            result.append(franchise)
    return result
    
def getFranchiseCountByLocation(userId,neighborId):
    return len(getFranchisesByLocation(userId,neighborId))

def getAllFranchises(userId):
    return users[userId]['franchises']
        
def getAllFranchiseAcceptedLocationsCount(userId):
    result = 0
    franchises = getAllFranchises(userId)
    for franchise in franchises:
        for location in franchise['locations']:
            if franchise['locations'][location]['time_last_operated'] > 0:
                result += 1
    return result


def franchiseGetHQType(franchiseType):
    item = items[franchiseType]
    if item != None:
        return item['headquarters']
    return None
    
def franchiseGrantHQ(userId,franchiseType):
    inventoryAdd(userId,franchiseType,1,True);
    pass

def createFranchise(userId,franchiseType,franchiseName):
    franchise = {
        'name': franchiseType,
        'franchise_name': franchiseName,
        'locations' : {},
        'time_last_collected': 0
    }
    users[userId]['franchises'].append(franchise)
        
def createFranchiseLocation(resourceId):
    now = timestamp()
    location = {
        'star_rating': 1,
        'commodity_left': 0,
        'commodity_max': 1,
        'customers_served': 0,
        'money_collected': 500,
        'obj_id': resourceId,
        'time_last_collected': now,
        'time_last_operated': now,
        'time_last_supplied': 0        
    }
    return location

def updateFranchiseName(userId,params):
    franchiseType = params[0]
    franchiseName = params[1]
    franchises = users[userId]['franchises']
    for franchise in franchises:
        if franchise['name'] == franchiseType:
            franchise['franchise_name'] = franchiseName
            save(userId)
            return
    createFranchise(userId,franchiseType,franchiseName)
    save(userId)
        
def replaceUserResource(userId,params):
    visitorId = params[0]
    resourceId = params[2]
    franchiseType = params[3]
    franchises = users[userId]['franchises']
    for franchise in franchises:
        if franchise['name'] == franchiseType:
            franchise['locations'][visitorId] = createFranchiseLocation(resourceId)
            break
    save(userId)