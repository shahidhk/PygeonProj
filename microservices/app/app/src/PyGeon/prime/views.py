import json
import requests
import random
import re
import time
from pprint import pprint
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import generic
from django.http.response import HttpResponse
from broadcasting import createBroadcast, sendTargetBroadcast
import os
import binascii
from sender import gen_text_message, gen_attachment
import sender
from pprint import pprint
from django.views.decorators.csrf import csrf_exempt
from data import template_list, sub_category_list, cities_list, labmap
from firebasic import add_subscriber_combined, query, add_event
from watson import watson_handler
import pandas as pd
import datetime
import datetime
from twit import Report
# Report = twit.Report
DEFAULT_URL = 'https://woocommerce.com/wp-content/themes/woo/images/wc-meetups/host-meetup.jpg'
# from user_form import temp_dict, User
# cd influx/pygeon/prime
PAGE_ACCESS_TOKEN = 'EAACSTXh23oABAGwu2YLuZBUC68XZAsmOOZAaCDp4kRinhZAxPkpZBuZARko78E8jFoABfjSV3BUpv2BPEGE5E0sXiKhxCAy7lehLQYbDfIICKQzVSoEONrKgAyprLvyQ9t4teqQ5JClZC3vWMzgRaTKL8F2UYOKE3siNaQ6W5xBsAZDZD'
city_wait_flag = {}


def init(fbid):
    """
        Called on clicking Get Started.
        Displays 4 messages and category List.
            Payload on selecting category : SEL1::CategoryTitle
    """
    messages = [
        "Hey. I'm PyGeon.",
        "I can keep you up to speed with events around you.",
        "If you're an event organiser, click here",
        "Would you like to Subscribe to events ? Choose a category :)"
    ]

    for i in messages:
        m = sender.gen_text_message(i)
        post_facebook_message(fbid, m)
    m = sender.gen_cards(template_list)
    post_facebook_message(fbid, m)


def sub_category(fbid, catname):
    """
        Called on clicking a category.
        Displays 3 sub categories in a button card.
            Payload on selecting sub category : SEL2::SubCategoryTitle
    """
    optlist = sub_category_list[catname]
    payloadlist = ["SEL2::" + i + "::" + catname for i in optlist]
    m = sender.gen_button_card(
        "What would you like to subscribe to ?", optlist, payloadlist)
    post_facebook_message(fbid, m)


def city_prompt(fbid, category, event):
    question = "Which cities would you like to subscribe these event for ?"
    q_add = "(Seperate multiple cities by commas.)"
    m = sender.gen_text_message(
        "You have chosen " + category + " : " + event + ".")
    post_facebook_message(fbid, m)
    m = sender.gen_text_message(question + "\n\n" + q_add)
    post_facebook_message(fbid, m)
    city_wait_flag[fbid] = {'status': True,
                            'category': category, 'event': event}


def city_prompt_temp(fbid, category, event):
    question = "Which cities would you like to subscribe these event for ?"
#    q_add = "(Seperate multiple cities by commas.)"
    optlist = ["Chennai", "Mumbai", "Bangalore"]
    payload = ["SEL3::" + i + "::" + category + "::" + event for i in optlist]
    m = sender.gen_button_card(question, optlist, payload)
    post_facebook_message(fbid, m)


def city_proc_temp(fbid, params):
    [city, cat, event] = params
    print params
    add_subscriber_combined(cat, event, city, fbid)
    epoch_end = time.time() + 30 * 24 * 60 * 60
    event_list = query(cat, event, city, epoch_end)
    if not event_list:
        m = sender.gen_text_message(
            "No" + event + " were found in " + c + "\n We shall keep you updated. :)")
        return
    m = sender.gen_text_message(event + " in " + city + ":")
    post_facebook_message(fbid, m)
    details_list = []
    for ev in event_list[:10]:
        details_dict = {}
        details_dict['title'] = ev['name']
        details_dict['image_url'] = DEFAULT_URL
        details_dict['subtitle'] = 'By : ' + ev['by'] + "\n On :" + ev['date']
        details_dict['url'] = ev['link']
        details_dict['button_text'] = "Open"
        details_dict['button_url'] = ev['link']
        details_list.append(details_dict)
        print(details_dict)
    m = sender.gen_link_cards(details_list)
    post_facebook_message(fbid, m)


def city_proc(fbid, message="Chennai, Mumbai and Bangalore"):
    cat = city_wait_flag[fbid]['category']
    event = city_wait_flag[fbid]['event']
    parts = re.split(r'(,|and)', message)
    if len(parts) == 1:
        cities = [parts[0]]
        cities = [i for i in cities if i in cities_list]
    elif len(parts) % 2 == 1:
        cities = parts[0::2]
        cities = [i.strip() for i in cities if i.strip() in cities_list]
    else:
        return
    print("Adding Cities ", cities)
    print(cat, event, fbid)
    str_fin = "You have subscribed to"
    for c in cities:
        add_subscriber_combined(cat, event, c, fbid)
        str_fin += "\n" + event + "in" + c
    m = sender.gen_text_message(str_fin)
    epoch_end = time.time() + 30 * 24 * 60 * 60
    for c in cities:
        event_list = query(cat, event, c, epoch_end)
        if not event_list:
            m = sender.gen_text_message(
                "No" + event + " were found in " + c + "\n We shall keep you updated. :)")
            continue
        m = sender.gen_text_message(event + " in " + c + ":")
        post_facebook_message(fbid, m)
        details_list = []
        for ev in event_list[:10]:
            details_dict = {}
            details_dict['title'] = ev['name']
            details_dict['image_url'] = DEFAULT_URL
            details_dict['subtitle'] = 'By : ' + \
                                       ev['by'] + "\n" + ev['description']
            details_dict['url'] = ev['link']
            details_dict['button_text'] = "Open"
            details_dict['button_url'] = ev['link']
            details_list.append(details_dict)
            print(details_dict)
        m = sender.gen_link_cards(details_list)
        post_facebook_message(fbid, m)
    del city_wait_flag[fbid]


# def form_start(fbid):
#     x = User(fbid)
#     x.start_form()
#     x.proc_form('text', data)


def payloadprocessor(name, fbid):
    """
         Processes payloads.
         Splits payloads at ::.
         pname = Payload tag
         add = Payload
    """
    if name == "GET_STARTED_PAYLOAD":
        init(fbid)
        return
    payload_params = name.split("::")
    pname = payload_params[0]
    params = payload_params[1:]
    # if pname == "FORM":
    #     x = temp_dict[fbid]
    #     x.proc_form('payload', params[0])
    print pname
    if pname == "SUB":
        print(params)
        pass
    elif pname == "SEL1":
        sub_category(fbid, params[0])
    elif pname == "SEL2":
        city_prompt_temp(fbid, params[1], params[0])
    elif pname == "SEL3":
        print "IN"
        city_proc_temp(fbid, params)


def whattodo(sender_id, data, mtype):
    global trap, tr_counter, questions, qanda, fl
    message = data
    if mtype == 'text':
        print('Received Message >>', message)
        message = gen_text_message(message)

    elif mtype == 'attachment':
        print('Received Message >>', message)
        message = gen_attachment(message)
    post_facebook_message(sender_id, message)


def post_facebook_message(fbid, message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": message})
    status = requests.post(post_message_url, headers={
        "Content-Type": "application/json"}, data=response_msg)

    print(status.json())


def df_check(fbid):
    return False


class BotView(generic.View):
    def get(self, request, *args, **kwargs):
        # return HttpResponse("Hello World!")
        if self.request.GET.get('hub.verify_token', '08081997') == '08081997':
            return HttpResponse(self.request.GET.get('hub.challenge', 'Default'))
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        print('\n\n-------------------------------------------------')
        pprint(incoming_message)
        for entry in incoming_message['entry']:
            for message in entry.get('messaging', []):
                print(message)
                if 'message' in message:
                    sender_id = message['sender']['id']
                    data = message['message']
                    print("Sender ID :", sender_id)
                    print(city_wait_flag)
                    if sender_id == u'254026515127873':
                        continue
                    if 'text' in data or 'attachments' in data:
                        if 'text' in data:
                            content = data['text']
                            mtype = 'text'
                        else:
                            content = data['attachments'][0]
                            mtype = 'attachments'
                    else:
                        continue

                    if mtype == 'text':
                        if city_wait_flag.get(sender_id, False):
                            city_proc(sender_id, content)
                        else:
                            message = watson_handler(content)
                            if not type(message) == type(dict()):
                                if message.startswith("Hello"):
                                    init(sender_id)
                                    return HttpResponse()
                            print message
                            print type(message)
                            if type(message) == type(u""):
                                message = sender.gen_text_message(message)
                                print "Sending :", message
                                post_facebook_message(sender_id, message)
                                print 'Message was sent'
                            else:
                                if "search_parameter" in message:
                                    date = message["date"]
                                    print(date)
                                    if len(date.strip()) == 0:
                                        # StartDate = "12/17/2018"
                                        # chalu_date = StartDate.split("/")
                                        # dt = datetime.datetime(
                                        #     chalu_date[-1], chalu_date[0], chalu_date[1])
                                        # epochs = (
                                        #     dt - datetime.datetime(1970, 1, 1, 0, 0)).total_seconds() + 30 * 24 * 60 * 60
                                        epoch = 1517298807
                                        # date = Date.today() + timedelta(days=30)
                                        # print(chalu_date)
                                    else:
                                        chalu_date = date.split("-")
                                        epoch = (datetime.datetime(
                                            int(chalu_date[0]), int(
                                                chalu_date[1]), int(chalu_date[2]), 0,
                                            0) - datetime.datetime(1970, 1, 1)).total_seconds()
                                    items = query(
                                        event=message["search_parameter"], city=message["location"], epoch_end=epoch)[:5]
                                    if len(items) == 0:
                                        m = sender.gen_text_message(
                                            "Sorry, we could not find any data for your query")
                                        post_facebook_message(sender_id, m)
                                    else:
                                        print items
                                        details_list = []
                                        for ev in items[:10]:
                                            details_dict = {}
                                            details_dict['title'] = ev['name']
                                            details_dict['image_url'] = DEFAULT_URL
                                            details_dict['subtitle'] = 'By : ' + \
                                                                       ev['by'] + "\n" + \
                                                ev['description']
                                            details_dict['url'] = ev['link']
                                            details_dict['button_text'] = "Open"
                                            details_dict['button_url'] = ev['link']
                                            details_list.append(details_dict)
                                            print(details_dict)
                                        m = sender.gen_link_cards(details_list)
                                        post_facebook_message(sender_id, m)

                                        """
                                        VISHAL BHAI IDHAR DEKH
                                        """
                                elif "hashtag" in message:
                                    hashtag = message["hashtag"]
                                    email = message["email"]
                                    #
                                    r = Report(email, hashtag)
                                    m = sender.gen_text_message(
                                        "Your request has been recorded, It might take a while to fullfill it based on the number of tweets")
                                    post_facebook_message(
                                        sender_id, m)
                                    # r.process(hashtag)

                    '''
                    # pprint(data)'''

                elif 'postback' in message:
                    pprint(message)
                    payloadprocessor(
                        message["postback"]["payload"], message["sender"]["id"])
        return HttpResponse()


class SheetsPingView(generic.View):
    def get(self, request, *args, **kwargs):
        # return HttpResponse("Hello World!")
        if self.request.GET.get('hub.verify_token', '08081997') == '08081997':
            return HttpResponse(self.request.GET.get('hub.challenge', 'Default'))
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        pprint(incoming_message)

        date = incoming_message[5]
        dt = pd.Timestamp(date).astimezone('Asia/Kolkata').to_pydatetime()
        datestring = str(dt.year) + '-' + str(dt.month) + '-' + str(dt.day)
        epochs = int(dt.strftime('%s'))

        details_dict = {}
        details_dict['title'] = incoming_message[1]
        details_dict['image_url'] = DEFAULT_URL
        details_dict['subtitle'] = 'By : ' + \
            incoming_message[-1] + "\n" + incoming_message[2]
        details_dict['url'] = incoming_message[4]
        details_dict['button_text'] = "Open"
        details_dict['button_url'] = incoming_message[4]

        event_dict = {
            'by': incoming_message[-1],
            'date': datestring,
            'description': incoming_message[2],
            'epoch': epochs,
            'link': details_dict['url'],
            'name': details_dict['title'],
        }
        add_event(category=incoming_message[3],
                  event=incoming_message[-2],
                  city=incoming_message[-3],
                  event_dict=event_dict,
                  id=binascii.hexlify(os.urandom(8))
                  )
        print "EVENT WAS ADDED"

        m = createBroadcast(mtype="template", title=details_dict['title'], image_url=DEFAULT_URL,
                            subtitle=details_dict["subtitle"], url=details_dict["url"], button_text="Interested")
        sendTargetBroadcast(msgID=m, lid=labmap[incoming_message[3]])

        # m = sender.gen_link_cards([details_dict])
        # post_facebook_message(1645332865512512, m)

        return HttpResponse()


""""
curl -X POST -H "Content-Type: application/json" -d '{
    "greeting": [
        {
            "locale": "de   fault",
            "text": "Up to Speed. At Lightning speed."
        }
    ],
    "get_started": {"payload": "GET_STARTED_PAYLOAD"}
}' "https://graph.facebook.com/v2.6/me/messenger_profile?access_token=EAACSTXh23oABAGwu2YLuZBUC68XZAsmOOZAaCDp4kRinhZAxPkpZBuZARko78E8jFoABfjSV3BUpv2BPEGE5E0sXiKhxCAy7lehLQYbDfIICKQzVSoEONrKgAyprLvyQ9t4teqQ5JClZC3vWMzgRaTKL8F2UYOKE3siNaQ6W5xBsAZDZD"
"""

# To Set GetStarted button"""
"""
    curl -X POST -H "Content-Type: application/json" -d '{
        "get_started": {"payload": "GET_STARTED_PAYLOAD"}
    }' "https://graph.facebook.com/v2.6/me/messenger_profile?access_token=EAACSTXh23oABAGwu2YLuZBUC68XZAsmOOZAaCDp4kRinhZAxPkpZBuZARko78E8jFoABfjSV3BUpv2BPEGE5E0sXiKhxCAy7lehLQYbDfIICKQzVSoEONrKgAyprLvyQ9t4teqQ5JClZC3vWMzgRaTKL8F2UYOKE3siNaQ6W5xBsAZDZD"
"""
