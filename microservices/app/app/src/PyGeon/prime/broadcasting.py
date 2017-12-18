# -*- coding: utf-8 -*-

import requests
import json
import sender

LEM_KEY = "EAACSTXh23oABAIyyasWMulQPbH9dO3TdKE6YZCqMYYHZC2991QaNnSgoFp1RjfRwbDT39LrSGMv78ULLsZCC8UAZADd8LyJMJ5ZCOl3jbPR9YroIXiP9l99xBupFqfF37jGlxZBl3Jnkij7Iiyj1uc85sIK68FpYcnGcGhXQpZBJgZDZD"

URL_BROADCAST_CREATE = "https://graph.facebook.com/v2.11/me/message_creatives?access_token=" + LEM_KEY
URL_BROADCAST_SEND = "https://graph.facebook.com/v2.11/me/broadcast_messages?access_token=" + LEM_KEY
URL_TARGET_LABEL_CREATE = "https://graph.facebook.com/v2.11/me/custom_labels?access_token=" + LEM_KEY
# Here the LabelID is also added to the middle of the string.
URL_TARGET_LABEL_ASSOC = "https://graph.facebook.com/v2.11/%s/label?access_token=" + LEM_KEY
URL_TARGET_LABEL_SEND = "https://graph.facebook.com/v2.11/me/broadcast_messages?access_token=" + LEM_KEY
URL_TARGET_LABEL_REMOVE_USER = "https://graph.facebook.com/v2.11/%s/label?access_token=" + \
    LEM_KEY  # Similarly the LabelID is also added here to send to
URL_TARGET_LABEL_RETREIVE = "https://graph.facebook.com/v2.11/%s/custom_labels?access_token=" + LEM_KEY
URL_TARGET_LABEL_KILL = "https://graph.facebook.com/v2.11/%s?access_token=" + LEM_KEY
URL_TARGET_GET_ALL_LABELS = "https://graph.facebook.com/v2.11/me/custom_labels?fields=name&access_token=" + LEM_KEY


def createBroadcast(mtype="template", title="Default Title", content="Default Content", image_url="Default Image URL", subtitle="Default Subtitle", url="https://facebook.com/", button_text="Default", payload="DEF::FAKE"):
    """
    Creates a Broadcast message that is stored natively on FB.
    A message ID is returned. This message ID is used to send the message.

    :param mtype = text or template
    :param title = a title string for template message
    :param content = content for a text message
    :param subtitle = a subtitle string for template message
    :param image_url = a image url string for template message
    :param url = a pointing url for template messages
    :param button_text = a list of buttons for template messages
    :param payload = a payload value to return on click for template messages

    msgID is returned.
    """
    tosend = {}
    if mtype == "text":
        tosend = sender.gen_text_message(text=content)
    elif mtype == "template":
        info = {
            'title': title,
            'image_url': image_url,
            'subtitle': subtitle,
            'url': url,
            'button_text': button_text,
            'payload': payload
        }
        print info
        tosend = sender.gen_cards(details=[info])

    req = requests.post(url=URL_BROADCAST_CREATE, headers={
                        "Content-Type": "application/json"}, data=json.dumps({'messages': [tosend]}))

    if req.status_code == 200:
        return req.json()[u'message_creative_id']
    else:
        print "LOG Server error, response status not 200\n", req.content
        return False


def sendNonTargetBroadcast(msgID=None):
    """
    Sends a non-targetted Broadcast message.
    Message ID is used to send the message.

    :param msgID = The ID of the created messsage.
    """
    if msgID:
        req = requests.post(url=URL_BROADCAST_SEND, headers={"Content-Type": "application/json"},
                            data=json.dumps({
                                "message_creative_id": msgID
                            }))
        if req.status_code == 200:
            return req.json()[u'broadcast_id']
            print "LOG Broadcast message sent successfully"
        else:
            print "LOG Server error, response status not 200\n", req.content
            return False
    else:
        print "LOG: No msgID received"
        return False


def createTargetBroadcastLabel(name=None):
    if name:
        req = requests.post(url=URL_TARGET_LABEL_CREATE, headers={"Content-Type": "application/json"},
                            data=json.dumps({
                                "name": name
                            }))
        if req.status_code == 200:
            return req.json()["id"]
        else:
            print "LOG Server error, response status not 200\n", req.content
            return False
    else:
        print "LOG: No name received"
        return False


def associateUserToLabel(lid=None, upsid=None):
    if upsid and lid:
        req = requests.post(url=URL_TARGET_LABEL_ASSOC % (lid), headers={"Content-Type": "application/json"},
                            data=json.dumps({
                                "user": upsid
                            }))
        if req.status_code == 200:
            return req.json()["success"]
        else:
            print "LOG Server error, response status not 200\n", req.content
            return False
    else:
        print "LOG: Label Name or Upsid not received"
        return False


def unssociateUserToLabel(lid=None, upsid=None):
    if upsid and lid:
        req = requests.delete(url=URL_TARGET_LABEL_REMOVE_USER % (lid), headers={"Content-Type": "application/json"},
                              data=json.dumps({
                                  "user": upsid
                              }))
        if req.status_code == 200:
            return req.json()["success"]
        else:
            print "LOG Server error, response status not 200\n", req.content
            return False
    else:
        print "LOG: Label Name or Upsid not received"
        return False


def sendTargetBroadcast(msgID=None, lid=None):
    if msgID and lid:
        req = requests.post(url=URL_BROADCAST_SEND, headers={"Content-Type": "application/json"},
                            data=json.dumps({
                                "message_creative_id": msgID,
                                "custom_label_id": lid
                            }))
        if req.status_code == 200:
            print "LOG Target broadcast message sent successfully"
            return req.json()[u'broadcast_id']
        else:
            print "LOG Server error, response status not 200\n", req.content
            return False
    else:
        print "LOG: msgID or lid not received"
        return False


def getLabelsOfUser(psid=None):
    if psid:
        req = requests.get(url=URL_TARGET_LABEL_RETREIVE % (psid))
        if req.status_code == 200:
            return req.json()[u'data']
        else:
            print "LOG Server error, response status not 200\n", req.content
            return False
    else:
        print "LOG: PSID not received"
        return False


def killLabel(lid):
    if lid:
        req = requests.delete(url=URL_TARGET_LABEL_KILL % (lid), headers={
                              "Content-Type": "application/json"}, data="")
        if req.status_code == 200:
            print "LOG The label was successfully murdered.\nHow can you live with yourself?"
            return req.json()[u'success']
        else:
            print "LOG Server error, response status not 200\n", req.content
            return False
    else:
        print "LOG: Label Name not received"
        return False


def getLabels():
    req = requests.get(url=URL_TARGET_GET_ALL_LABELS)
    if req.status_code == 200:
        return req.json()[u'data']
    else:
        print "LOG Server error, response status not 200\n", req.content
        return False
