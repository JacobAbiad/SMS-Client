from firebase import firebase
from flask import Flask, request
from twilio import twiml
from twilio.rest import TwilioRestClient
from time import localtime

twilNum = '+12262419971'
app = Flask(__name__)
eventName = 'MasseyHacks'
firebase = firebase.FirebaseApplication(
    'https://fir-withpython-ec98a.firebaseio.com/{}/'.format(eventName), None)

#firebase code
def getInfo(parent, index):
    return firebase.get(parent, index)

def getTime(parent, val, index):
    print firebase.get(parent, val)

def setParent(name):
    firebase.put(name, name, '')

def setChild(parent, name, val):
    firebase.put(parent, name, val)

def delete(parent, name):
    firebase.delete(parent, name)

def main():
    print firebase.__dict__
    print getInfo('admins', 5195646267)

if __name__ == '__main__':
    main()