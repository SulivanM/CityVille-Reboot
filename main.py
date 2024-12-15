from flask import Flask, render_template, send_from_directory, request, send_file, Response
from pyamf import remoting
from datetime import datetime
import pyamf
import json
import os
import users
import quests

users.init()
quests.init()

app = Flask(__name__, static_folder='public/static', template_folder='public')

writeStats = True

def timestamp():
    return datetime.now().timestamp()

@app.route('/game_data/<filename>')
def serve_game_data(filename):
    game_data_folder = os.path.join(app.root_path, 'public', 'game_data')
    return send_from_directory(game_data_folder, filename)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/record_stats.php', methods=['POST'])
@app.route('/127.0.0.1record_stats.php', methods=['POST'])
def stats():
    print('Stats Received')
    if writeStats:
        with open('stats.txt', 'a') as file:
            json.dump(request.get_json(), file, indent=4)
    return ''

@app.route('/error.php', methods=['POST'])
@app.route('/127.0.0.1error.php', methods=['POST'])
def post_error():
    print('Error Received')
    if writeStats:
        with open('error.txt', 'a') as file:
            json.dump(request.get_json(), file, indent=4)
    return ''

@app.route('/flashservices/gateway.php', methods=['POST'])
def post_gateway():
    resp_msg = remoting.decode(request.data)        
    responses = []
    id = resp_msg.bodies[0][1].body[0]['zyUid']
    
    for reqq in resp_msg.bodies[0][1].body[1]:        
        print(reqq)
        if reqq.functionName == 'UserService.initUser':
            responses.append(userResponse())
        elif reqq.functionName == 'UserService.initNeighbors':
            responses.append(neighborResponse())
        elif reqq.functionName == 'UserService.getZEventCount':
            responses.append(zCount())
        elif reqq.functionName == 'QuestService.requestManualQuest':
            responses.append(questResponse(reqq.params))
        elif reqq.functionName == 'UserService.pingFeedQuests':
            quests.handleQuestProgress(id, ['pingFeedQuests'])
            responses.append(feedQuests(id))
        elif reqq.functionName == 'UserService.setCityName':
            responses.append(setCityNameResponse(id, reqq.params[1]))
        elif reqq.functionName == 'UserService.checkForNewNeighbors':
            responses.append(dummy_response())                
        elif reqq.functionName == 'UserService.updateTopFriends':
            responses.append(dummy_response())            
        elif reqq.functionName == 'UserService.seenQuest':
            quests.handleQuestProgress(id, reqq.params)
            responses.append(dummy_response())
        elif reqq.functionName == 'WorldService.performAction':
            data = users.performAction(id, reqq.params)
            print(data)
            quests.handleQuestProgress(id, reqq.params)
            responses.append(performAction(data))
        elif reqq.functionName == 'WorldService.loadWorld':
            responses.append(visit(id, reqq.params))
        elif reqq.functionName == 'UserService.onValidCityName':
            quests.handleQuestProgress(id, ['onValidCityName'])
            responses.append(dummy_response())
        elif reqq.functionName == 'UserService.popNews':
            quests.handleQuestProgress(id, reqq.params)
            responses.append(dummy_response())
        elif reqq.functionName == 'UserService.saveOptions':
            users.updateOptions(id, reqq.params)
            responses.append(dummy_response())
        elif reqq.functionName == 'UserService.completeTutorial':
            users.completedTutorial(id)
            responses.append(dummy_response())
        elif reqq.functionName == 'VisitorService.initialVisit':
            quests.handleQuestProgress(id, reqq.params)
            responses.append(initialVisit(id))
        elif reqq.functionName == 'VisitorService.help':
            quests.handleQuestProgress(id, reqq.params)
            responses.append(dummy_response())
        elif reqq.functionName == 'TrainService.completeWelcomeTrainOrder':
            quests.handleQuestProgress(id, ['welcomeTrain', reqq.params])
            responses.append(dummy_response())            
        elif reqq.functionName == 'TrainService.placeInitialOrder':
            quests.handleQuestProgress(id, ['placeInitialOrder', reqq.params])
            responses.append(dummy_response())
        elif reqq.functionName == 'UserService.purchaseQuestProgress':
            quests.purchaseQuestProgress(id, reqq.params)
            responses.append(dummy_response())
        elif reqq.functionName == 'FarmService.expandCity':
            data = users.expandCity(id, reqq.params)
            responses.append(wrap(data))
        elif reqq.functionName == 'UserService.processVisitsBatch':
            users.handleVisits(id, reqq.params)
            responses.append(dummy_response())
        elif reqq.functionName == 'UserService.acquireLicense':
            data = users.acquireLicense(id, reqq.params)
            responses.append(wrap(data))
        elif reqq.functionName == 'FranchiseService.onSupply':
            quests.handleQuestProgress(id, ['onSupply', reqq.params])
            responses.append(dummy_response())
        elif reqq.functionName == 'FranchiseService.updateFranchiseName':
            users.updateFranchiseName(id, reqq.params)
            responses.append(dummy_response())
        elif reqq.functionName == 'UserService.onReplaceUserResource':
            users.replaceUserResource(id, reqq.params)
            responses.append(dummy_response())
        else:
            print(reqq)
            responses.append(dummy_response())
        
    emsg = {
        "serverTime": timestamp(),
        "errorType": 0,
        "data": responses
    }

    req = remoting.Response(emsg)
    ev = remoting.Envelope(pyamf.AMF0)
    ev[resp_msg.bodies[0][0]] = req
    ret_body = remoting.encode(ev, strict=True, logger=True).getvalue()
    return Response(ret_body, mimetype='application/x-amf')

@app.route('/<path:path>')
def send_sol_assets_alternate(path):
    return send_file(path)

def dummy_response():
    dummy_response = {"errorType": 0, "userId": 333, "metadata": {"newPVE": 0}, "data": [], "serverTime": timestamp()}
    return dummy_response

def wrap(data, meta = {}):
    user_response = {"errorType": 0, "userId": 333, "metadata": meta, "data": data, "serverTime": timestamp()}
    return user_response

def zCount():
    msg = { "count": 0 } 
    meta = {}
    user_response = {"errorType": 0, "userId": 333, "metadata": meta, "data": msg, "serverTime": timestamp()}
    return user_response

def initialVisit(id):
    msg = { "energyLeft": 4 } 
    meta = {}
    user_response = {"errorType": 0, "userId": 333, "metadata": meta, "data": msg, "serverTime": timestamp()}
    return user_response

def userResponse():
    user = initUser()
    meta = {}
    user_response = {"errorType": 0, "userId": 333, "metadata": meta, "data": user, "serverTime": timestamp()}
    return user_response

def questResponse(quest):
    print('Quest Started:', quest[0])
    quest = { "questStarted": 1 } 
    meta = {}
    user_response = {"errorType": 0, "userId": 333, "metadata": meta, "data": quest, "serverTime": timestamp()}
    return user_response
    
def setCityNameResponse(userId, newName):
    data = users.renameCity(userId, newName) 
    meta = {}
    user_response = {"errorType": 0, "userId": 333, "metadata": meta, "data": data, "serverTime": timestamp()}
    return user_response    

def visit(id, params):
    userId = params[0]
    data = users.getUser(userId)['userInfo']
    data['franchises'] = [] 
    meta = {}
    user_response = {"errorType": 0, "userId": 333, "metadata": meta, "data": data, "serverTime": timestamp()}
    return user_response    

def feedQuests(id):
    quest = { } 
    meta = quests.getQuests(id)
    user_response = {"errorType": 0, "userId": 333, "metadata": meta, "data": quest, "serverTime": timestamp()}
    return user_response

first = True
def neighborResponse():
    global first
    meta = {}
    neighbors = { "neighbors": [ { "uid": -1, "fake": 1}, { "uid": 3}, {"uid": 4}, {"uid": 5}, {"uid": 6} ] }
    response = {"errorType": 0, "userId": 333, "metadata": meta, "data": neighbors, "serverTime": timestamp()}
    if not first:
        return {}
    first = False
    return response

def performAction(data):
    meta = {}        
    response = {"errorType": 0, "userId": 333, "metadata": meta, "data": data, "serverTime": timestamp()}
    return response

def initUser():
    global first
    first = True
    user = users.getUser('333')
    return user

if __name__ == '__main__':
    app.run(debug=True, port=5000)