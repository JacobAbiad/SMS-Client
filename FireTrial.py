from firebase import firebase
from flask import Flask, request
from twilio import twiml
from twilio.rest import TwilioRestClient
from time import localtime


now = localtime()
twilNum = '+12262419971'
app = Flask(__name__)
logged = False
admin = False

#firebase code
def getInfo(parent, index):
    return firebase.get(parent, index)

def getTime(parent, val, index):
    return firebase.get(parent, index, val)

def setNode(parent, name, val):
    firebase.put(parent, name, val)

def delete(parent, name):
    firebase.delete(parent, name)

def setEvent(title, startTime, endTime, description):
    firebase.put('events', title, {'startTime' : startTime, 'endTime' : endTime, 'description' : description})
############################################

#twilio code
@app.route('/', methods=["POST"])
def main():
    now = localtime()
    global logged
    #sending announcments
    number = request.form['From']
    number = phoneNumberParse(number, 0)
    messageBody = request.form["Body"]
    messageSplit = messageBody.split('*')
    if messageSplit[0].lower().strip() == '/text' and logged is True and admin is True:
        return announcements(number, messageSplit)
    elif messageSplit[0].lower().strip() == '/event' and logged is True and admin is True:
        return makeEvent(number, messageSplit)
    elif messageSplit[0].lower().strip() == '/current' and logged is True:
        return getCurrent()
    elif messageSplit[0].lower().strip() == '/help' and logged is True:
        return help(number)
    elif messageSplit[0].lower().strip() == '/hostlist' and logged is True:
        return hostList()
    elif messageSplit[0].lower().strip() == '/pm' and logged is True:
        return message(number, messageSplit)
    elif messageSplit[0].lower().strip() == '/login':
        return signIn(number, messageSplit)
    elif messageSplit[0].lower().strip() != '/login' and logged is False:
        resp = twiml.Response()
        resp.message('Please Log In First With /login * event name * your name')
        return str(resp)
    else:
        resp = twiml.Response()
        resp.message('Invalid Message Type, Type /help For Options')
        return str(resp)


def announcements(number, messageSplit):
    global now
    if number in getInfo('admins', None):
        for member in getInfo('members', None):
            sendMessage(member, twilNum, messageSplit[1])
        resp = twiml.Response()
        resp.message('Message Sent')
        setNode('announcements', messageSplit[1], '{}:{}:{}'.format(now.tm_hour, now.tm_min, now.tm_sec))
        return str(resp)
    else:
        resp = twiml.Response()
        resp.message('Cannot Message This Number')
        return str(resp)


def makeEvent(number, messageSplit):
    if number in getInfo('admins', None):
        if messageSplit[4] is not None:
            setEvent(messageSplit[1], messageSplit[2], messageSplit[3], messageSplit[4])
            resp = twiml.Response()
            resp.message('Event Set')
            return str(resp)
        else:
            resp = twiml.Response()
            resp.message('Invalid Message Type, Type /help For Options')
            return str(resp)
    else:
        resp = twiml.Response()
        resp.message('Permission Denied')
        return str(resp)


def getCurrent():
    global now
    currentEvents = ''
    for event in getInfo('events', None):
        eventDic = getInfo('events', event)
        startTime = eventDic['startTime'].split(':')
        endTime = eventDic['endTime'].split(':')
        if int(startTime[0]) < int(now.tm_hour) < int(endTime[0]):
            if currentEvents == '':
                currentEvents = str(event) + ': ' + eventDic['endTime']
            else:
                currentEvents = currentEvents + ', ' + str(event) + ': ' + eventDic['endTime']
        elif int(now.tm_hour) == int(startTime[0]) and int(now.tm_min) >= int(startTime[1]):
            if currentEvents == '':
                currentEvents = str(event) + ': ' + eventDic['endTime']
            else:
                currentEvents = currentEvents + ', ' + str(event) + ': ' + eventDic['endTime']
        elif int(now.tm_hour) == int(endTime[0]) and int(now.tm_min) <= int(endTime[1]):
            if currentEvents == '':
                currentEvents = str(event) + ': ' + eventDic['endTime']
            else:
                currentEvents = currentEvents + ', ' + str(event) + ': ' + eventDic['endTime']
    if currentEvents != '':
        resp = twiml.Response()
        resp.message(currentEvents)
        return str(resp)
    else:
        resp = twiml.Response()
        resp.message('No Events Planned')
        return str(resp)


def help(number):
    if number in getInfo('admins', None):
        resp = twiml.Response()
        resp.message('/text - sends an announcement to all event members\n'
                     '/event - sets an event, send /event * event name * starting time * ending time * description of event, with the asteriks format\n'
                     '/current - informs you of current events taking place and the end time\n'
                     '/hostList - gives you a list of hosts available at the event\n'
                     '/pm - direct messeges someone using their name, send /pm * name of person * messege')
        return str(resp)
    else:
        resp = twiml.Response()
        resp.message('/current - informs you of current events taking place and the end time\n'
                     '/hostList - gives you a list of hosts available at the event\n'
                     '/pm - directly message someone with /pm * name (found with /hostList), using the asteriks format shown')
        return str(resp)


def hostList():
    nameList = ''
    for name in getInfo('admins', None):
        nameList = nameList + getInfo('admins', None)[name] + '\n'
    resp = twiml.Response()
    resp.message(nameList)
    return str(resp)


def message(number, messageSplit):
    adminDict = getInfo('admins', None)
    memberDict = getInfo('members', None)
    if number in adminDict:
        for key, val in memberDict.iteritems():
            if val.lower().strip() == messageSplit[1].lower().strip():
                bodyText = adminDict[number].lower().strip() + ': ' + messageSplit[2].lower().strip()
                setNode('messages', key, {number: bodyText})
                sendMessage(key, twilNum, bodyText)
    else:
        for key, val in adminDict.iteritems():
            if val.lower().strip() == messageSplit[1].lower().strip():
                bodyText = memberDict[number].lower().strip() + ': ' + messageSplit[2].lower().strip()
                setNode('messages', key, {number : bodyText})
                sendMessage(key, twilNum, bodyText)
    resp = twiml.Response()
    resp.message('Message Sent')
    return str(resp)


def signIn(number, messageSplit):
    global eventName
    global firebase
    global logged
    global admin
    eventName = messageSplit[1].strip()
    firebase = firebase.FirebaseApplication(
        'https://fir-withpython-ec98a.firebaseio.com/{}/'.format(eventName), None)
    logged = True
    if getInfo('admins', number) is not None:
        admin = True
        resp = twiml.Response()
        resp.message('Signed In, Welcome Back Administrator!')
        return str(resp)
    else:
        setNode('members', number, messageSplit[2])
        resp = twiml.Response()
        resp.message('Signed In, Welcome Back!')
        return str(resp)


def sendMessage(to, from_, body):
    client = TwilioRestClient('ACeb797975cb0ac7c3680042a67753399b',
                              'cab43fc750fdc1309bebc5757407262c')
    client.messages.create(from_ = from_, to = to, body = body)


def phoneNumberParse(body, phoneIndex):
    phoneNumber = body[phoneIndex:].strip()
    if len(phoneNumber) == 11 and phoneNumber[0] == "1":
        phoneNumber = phoneNumber[1:]
    elif len(phoneNumber) == 12 and phoneNumber[0:2] == "+1":
        phoneNumber = phoneNumber[2:]
    elif len(phoneNumber) > 10 or len(phoneNumber) < 10:
        phoneNumber = None
    return phoneNumber
###########################################################################

if __name__ == "__main__":
    app.run(debug = True)
