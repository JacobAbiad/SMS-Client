from flask import Flask, request
from twilio import twiml
from twilio.rest import TwilioRestClient

app = Flask(__name__)

try:
    global harDatabase
    database = open("harassmentDatabase.txt", "r")
    harDatabase = database.readlines()
    database.close()
except FileNotFoundError:
    harDatabase = [""]

try:
    global textOnce
    data = open("textOnce.txt", "r")
    tOnce = data.readlines()
    data.close()
except FileNotFoundError:
    tOnce = [""]

data = open("reviewing.txt", "r")
reviewing = data.readline()
if reviewing=="True":
    reviewingBool=True
else:
    reviewingBool=False
data.close()

data = open("admins.txt","r")
adminList = data.readlines()
data.close()

def send_message(to, from_, body):
    client = TwilioRestClient('ACeb797975cb0ac7c3680042a67753399b', 'cab43fc750fdc1309bebc5757407262c')

    client.messages.create(from_=from_, to=to, body=body)

def send_media(to, from_, body, media_url):
    client = TwilioRestClient('ACeb797975cb0ac7c3680042a67753399b', 'cab43fc750fdc1309bebc5757407262c')

    client.messages.create(from_=from_, to=to, body=body, media_url=media_url)
    
def make_call(to, from_):
    # Get these credentials from http://twilio.com/user/account
    client = TwilioRestClient('ACeb797975cb0ac7c3680042a67753399b', 'cab43fc750fdc1309bebc5757407262c')

    # Make the call
    call = client.calls.create(to=to,  # Any phone number
                               from_=from_, # Must be a valid Twilio number
                               url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient")
def messageR(number, body):
    global harDatabase
    global reportCount
    global tOnce
    global adminList
    global reviewingBool
    if "report" in body.lower():
        if reportCount==0:
            phoneIndex = body.find("/")+1
            if phoneIndex==-1:
                return "Hey there, please try again. It appears as if your entry is invalid."
            else:
                phoneNumber = phoneNumberParse(body, phoneIndex)
                if phoneNumber==None:
                    return "Hey there, please try again. Please do not put any characters in the message after you enter the phone number."
                tOnce.append(phoneNumberParse(str(number),0))
                tOnce=list(set(tOnce))
                data = open("textOnce.txt", "w")
                data.write("\n".join(tOnce))
                data.close()
                print(tOnce)
                try:
                    global review
                    d = open("underRev.txt", "r")
                    review = d.readLines()
                    d.close()
                except:
                    review=[]
                review.append(phoneNumberParse(str(number), 0)+" "+phoneNumber)#review element follows phone numer that called, then phone number being targeted
                d = open("underRev.txt", "w")
                d.write("\n".join(review))
                d.close()
                return "Are you sure you want to continue? If so, please provide photographic proof and the phone number to a reference who will verify your claim in the format ref//### Input exit// if you wish to cancel."
    if reportCount==1:
        print("Triggered!")
        if "exit" in body.lower():
            for item in tOnce:
                if len(item)>10:
                    index = tOnce.index(item)
                    item = item[:10]
                    if index<len(tOnce):
                        tOnce = tOnce[:index]+[item]+tOnce[index+1:]
                    else:
                        tOnce = tOnce[:index]+[item]
            tOnce=list(set(tOnce))
            tOnce.remove(phoneNumberParse(str(number),0))
            data = open("textOnce.txt","w")
            data.write("\n".join(tOnce))
            data.close()
            return "Thank you. Your request has been terminated."
        elif "ref" in body.lower():
            phoneIndex = body.find("/")+1
            if phoneIndex==-1:
                return "Hey there, please try again. It appears as if your entry is invalid."
            else:
                pNumber = phoneNumberParse(body, phoneIndex)
                if pNumber==None:
                    return "Hey there, please try again. Please do not put any characters in the message after you enter the phone number."
                else:
                    tOnce=list(set(tOnce))
                    tOnce.remove(phoneNumberParse(str(number),0))
                    data = open("textOnce.txt","w")
                    data.write("\n".join(tOnce))
                    data.close() #get the # out of the text once

                    
                    try:
                        global adminReview
                        d = open("adminReview.txt", "r")
                        adminReview = d.readlines()
                        d.close()
                    except FileNotFoundError:
                        global adminReview
                        adminReview=[]
                        print("adminReview fail")

                    try:
                        global review
                        data = open("underRev.txt", "r")
                        review = data.readlines()
                        data.close()
                    except FileNotFoundError:
                        global review
                        review=[]
                        print("reviewFail")
                        
                    for index in range(len(review)):
                        if phoneNumberParse(str(number),0) in review[index]:
                            if media!=None:
                                adminReview.append(review[index]+" "+pNumber+" none "+media)#claimant, claimedNumber, reference number, reference response, media links
                            else:
                                adminReview.append(review[index]+" "+pNumber+" none")
                            review = review[:index] + review[index+1:]
                            print(adminReview)

                    data = open("underRev.txt", "w")
                    data.write("\n".join(review))
                    data.close()
                    
                    data = open("adminReview.txt","w")
                    data.write("\n".join(adminReview))
                    print(adminReview)
                    data.close()
                    
                    send_message(pNumber, "+13133273325", "Hey there, you have been asked by %s to verify that they have been harassed by %s. Please respond in the form verify/yes or verify/no to indicate whether or not this is factual."%(adminReview[-1].split(" ")[0], adminReview[-1].split(" ")[1]))
                    
                    return "Your request has been processed. Thank you."
                    #add code here to text the reference and verify

                    
        else:
            return "Invalid. Enter exit/ to leave the current convo."
    if "verify" in body.lower():
        respIndex = body.find("/")+1
        if respIndex == -1:
            return "Hey there, please try again. It appears as if your entry is invalid."
        else:
            originNumber = phoneNumberParse(str(number),0)
            editLine=[]
            try:
                global adminReview
                data = open("adminReview.txt","r")
                adminReview = data.readlines()
                data.close()
            except:
                adminReview = []
            while True:
                try:
                    adminReview.remove("\n")
                except:
                   break
            print(adminReview)
            for index in range(len(adminReview)):
                print(adminReview[index].split(" ")[2], originNumber)
                if adminReview[index].split(" ")[2]==originNumber:
                    editLine = adminReview[index].split(" ")
                    saveIndex = index
                    print("Yes this happened!")
            if editLine==[]:
                return "Hmmmm. Seems like you weren't asked to verify a claim. Sorry about that!"
            if "yes" in body.lower():
                editLine[3]="yes"
            elif "no" in body.lower():
                editLine[3]="no"
            else:
                return "Please try again. Your response was invalid."
            if saveIndex-1 != len(adminReview):
                adminReview = adminReview[:index] + [" ".join(editLine)] + adminReview[index+1:]
            else:
                adminReview = adminReview[:index] + [" ".join(editLine)]
            data = open("adminReview.txt","w")
            data.write("\n".join(adminReview))
            data.close()
            return "Thank you. Your response has been recorded."
            
    if "check" in body.lower():
        phoneIndex = body.find("/")+1
        if phoneIndex==-1:
            return "Hey there, please try again. It appears as if your entry is invalid"
        else:
            phoneNumber = phoneNumberParse(body, phoneIndex)
            print(phoneNumber)
            if phoneNumber==None:
                return "Hey there,please try again. Please do not put any characters in the message after you enter the phone number."
            
            if phoneNumber in harDatabase:
                return "Red alert! This number is in our harassment database."
            else:
                print(harDatabase)
                return "All clear! This number is not in our harassment database."
    if "escape" in body.lower():
        make_call(number, "+13133273325")
        return "A call is incoming"
    if "admin" in body.lower() and "password" in body.lower() or reviewingBool and phoneNumberParse(str(number),0) in adminList:#least secure password ever lol
        data = open("adminReview.txt","r")
        adminReview = data.readlines()
        data.close()
        adminList.append(phoneNumberParse(str(number),0))
        adminList = list(set(adminList))
        data = open("admins.txt","w")
        data.write("\n".join(adminReview))
        data.close()
        print(reviewingBool)
        if reviewingBool==False:
            reviewingBool=True
            data = open("reviewing.txt","w")
            data.write("True")
            data.close()
            print("got here 2!")

            if len(adminReview)==0:
                data = open("reviewing.txt","w")
                data.write("False")
                data.close()
                return "Thank you! All done!"
            print(adminReview)
        
            if len(adminReview[0].split(" "))==4:
                response = adminReview[0].split(" ")
                while response[-2]=="\n":
                    response = response[:len(response)-3]
                send_message(phoneNumberParse(str(number),0), "+13133273325", "Number being reported: %s, Reference: %s, Reference response: %s"%(adminReview[0].split(" ")[1], adminReview[0].split(" ")[2], response))
                return "Please respond with yes or no for this entry"
            elif len(adminReview[0].split(" "))==5:
                mediaLink = adminReview[0].split(" ")[-1]
                while mediaLink[-2]=="\n":
                    mediaLink = mediaLink[:len(mediaLink)-3]
                send_media(phoneNumberParse(str(number),0), "+13133273325", "Number being reported: %s, Reference: %s, Reference response: %s"%(adminReview[0].split(" ")[1], adminReview[0].split(" ")[2], adminReview[0].split(" ")[3]), mediaLink)
                return "Please respond with yes or no for this entry" 
        elif "yes" in body.lower():
            phoneNumberAffected = adminReview[0].split(" ")[1]
            data = open("harassmentDatabase.txt", "r")
            existingDatabase = data.readlines()
            data.close()

            data = open("harassmentDatabase.txt","w")
            existingDatabase.append(" "+phoneNumberAffected)
            data.write("\n".join(existingDatabase))
            data.close()

            adminReview = adminReview[1:]
            data = open("adminReview.txt", "w")
            data.write("\n".join(adminReview))
            data.close()
            
            if len(adminReview)==0:
                data = open("reviewing.txt","w")
                data.write("False")
                data.close()
                return "Thank you! All done!"
        
            if len(adminReview[0].split(" "))==4:
                response = adminReview[0].split(" ")
                while response[-2]=="\n":
                    response = response[:len(response)-3]
                send_message(phoneNumberParse(str(number),0), "+13133273325", "Number being reported: %s, Reference: %s, Reference response: %s"%(adminReview[0].split(" ")[1], adminReview[0].split(" ")[2], response))
                return "Please respond with yes or no for this entry"
            elif len(adminReview[0].split(" "))==5:
                mediaLink = adminReview[0].split(" ")[-1]
                while mediaLink[-2]=="\n":
                    mediaLink = mediaLink[:len(mediaLink)-3]
                send_media(phoneNumberParse(str(number),0), "+13133273325", "Number being reported: %s, Reference: %s, Reference response: %s"%(adminReview[1], adminReview[2], adminReview[3]), mediaLink)
                return "Please respond with yes or no for this entry" 
            

        elif "no" in body.lower():
            adminReview = adminReview[1:]
            data = open("adminReview.txt", "w")
            data.write("\n".join(adminReview))
            data.close()
            if len(adminReview)==0:
                data = open("reviewing.txt","w")
                data.write("False")
                data.close()
                return "Thank you! All done!"
        
            if len(adminReview[0].split())==4:
                send_message(phoneNumberParse(str(number),0), "+13133273325", "Number being reported: %s, Reference: %s, Reference response: %s"%(adminReview[1], adminReview[2], adminReview[3]))
                return "Please respond with yes or no for this entry"
            elif len(adminReview[1].split())==5:
                send_media(phoneNumberParse(str(number),0), "+13133273325", "Number being reported: %s, Reference: %s, Reference response: %s"%(adminReview[1], adminReview[2], adminReview[3]), adminReview[4])
                return "Please respond with yes or no for this entry" 
        else:
            print("yes")
            return "Please enter a valid response"
        
    
    else:
        return "Hey there, please try again. It appears as if your entry is invalid."


                
def phoneNumberParse(body, phoneIndex):
    phoneNumber = body[phoneIndex:].strip()
    if len(phoneNumber)==11 and phoneNumber[0]=="1":
        phoneNumber=phoneNumber[1:]
    elif len(phoneNumber)==12 and phoneNumber[0:2]=="+1":
        phoneNumber=phoneNumber[2:]
    elif len(phoneNumber)>10 or len(phoneNumber)<10:
        phoneNumber=None
    return phoneNumber





                
@app.route('/', methods=["POST"])
def sms():
    global reportCount
    global media
    client = TwilioRestClient('ACeb797975cb0ac7c3680042a67753399b', 'cab43fc750fdc1309bebc5757407262c')
    message = client.messages.get(request.form["MessageSid"])
    number = request.form['From'] # phone # from
    message_body = request.form["Body"]
    
    if request.form["NumMedia"] == "1":#can expand
        media = request.form["MediaUrl0"]
    else:
        media=None
        print(request.form["NumMedia"])
    print(media)

    
    

    if phoneNumberParse(str(number),0) in tOnce or phoneNumberParse(str(number),0)+"\n" in tOnce or "\n"+phoneNumberParse(str(number),0) in tOnce:
        reportCount=1
        print(phoneNumberParse(str(number),0))
        print(tOnce)
    else:
        reportCount=0

    resp = twiml.Response()
    resp.message(messageR(number, message_body))
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
