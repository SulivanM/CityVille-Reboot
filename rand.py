import hashlib
from ast import literal_eval

import users

# WARNING: this is not decoupled from users.py.  Requires users.init() to be called first.
# TODO: Special case 'holiday_tree_2010' not working


HARD_CODED_SECRET = 'YOUR_LIKE_AN_8'
secretHandshake = ''

def rand(userId, min, max):
    # TODO: move side effect changes to roll counter outta here...
    rollCounter = users.users[userId]['userInfo']['player']['rollCounter']
    rollCounter += 1
    s = HARD_CODED_SECRET + '::' + secretHandshake + "::" + userId + "::" + str(rollCounter)
    hash = hashlib.md5(s.encode('utf-8'))
    hexString = '0x' + hash.hexdigest()[:8]
    hexValue = literal_eval(hexString)        
    range = max - min + 1
    val = hexValue % range + min
    users.users[userId]['userInfo']['player']['rollCounter'] = rollCounter
    return val


def generateDoobers(userId,itemName):
    item = users.items[itemName]
    # print(item)
    return processRandomModifiers(userId, item,'')
        
def processRandomModifiers(userId, item, resource):
    dooberTypes = []
    dooberYields = []
    if 'coinYield' in item:
        dooberTypes.append('coin')
        dooberYields.append(item['coinYield'])
    if 'xpYield' in item:
        dooberTypes.append('xp')
        dooberYields.append(item['xpYield'])
    if 'goodsYield' in item:
        dooberTypes.append('goods')
        dooberYields.append(item['goodsYield'])
    
    # if 'randomModifierGroups' in item:
    #     xml = chooseRandomModifiersXML(item,,'default')
    
    return processRandomModifiersConfig(userId,item,dooberTypes,dooberYields)

def processRandomModifiersConfig(userId,item, dooberTypes, dooberModifiers):
    result = []
    secureRands = []
    if 'randomModifiers' not in item:
        return [result,secureRands]
    if type(item['randomModifiers']['modifier']) is list:
        modifiers = item['randomModifiers']['modifier']
    else:
        modifiers = [item['randomModifiers']['modifier']]
    for modifier in modifiers:
        secureRand = rand(userId,0,99)
        secureRands.append(secureRand)
        if modifier['@tableName'] == 'colltable': # No collectables for this item
            continue            
        if modifier['@tableName'] not in users.randomTables:
            print('Missing random table:',modifier['@tableName'])
            continue
        modifierTable = users.randomTables[modifier['@tableName']]
        itemType = modifierTable['@type']
        rolls = []
        if type(modifierTable['roll']) is list:
            rolls = modifierTable['roll']
        else:
            rolls.append(modifierTable['roll'])
        
        prevRollPercent = 0
        for roll in rolls:
            # print(roll)
            if '@percent' not in roll:
                continue
            rollPercent = float(roll['@percent']) + prevRollPercent
            prevRollPercent = rollPercent
            if secureRand < rollPercent:
                if type(roll[itemType]) is list:
                    items = roll[itemType]
                else:
                    items = [roll[itemType]]
                for item in items:
                    if itemType == 'collectable':
                        dooberType = 'collectable'
                        quantity = item['@name']
                    else:
                        dooberType = itemType
                        quantity = int(float(item['@amount']))
                    result.append([dooberType,quantity])
                break;
    return [result,secureRands]
            

def chooseRandomModifiersXML(item, randomModifiers, randomModifierName):
    randomModifier = randomModifiers[randomModifierName]
    runningTotalPercent = 0
    secureRand = rand(0,99)
    for modifier in randomModifier['modifiers']:
        rollPercent = float(modifier['@percent'])
        runningTotalPercent += rollPercent
        if secureRand < runningTotalPercent:
            selectedModifier = modifier['@name']
            break
    
        
        


    