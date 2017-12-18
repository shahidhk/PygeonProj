from firebase_admin.firestore import client
from firebase_admin import initialize_app, credentials
from google.cloud import datastore
from google.cloud.firestore_v1beta1 import GeoPoint
from google.cloud.exceptions import Conflict
from broadcasting import *
from data import labmap
import os
import json
import time
from data import sub_category_list, category_map
from datetime import datetime
# Dependencies : google-cloud google-cloud-firestore firebase_admin

# cd ..

# Only three Labels will exist now. (Not very scalable.)

from data import cities_list as cities_data


def init():
    try:
        try:
            cred = credentials.Certificate("prime/firestore_creds.json")
        except:
            cred = credentials.Certificate("firestore_creds.json")
        initialize_app(cred)
    except:
        print (os.getcwd())
        print (os.listdir('prime'))


def get_col(name):
    return cli.collection(name)


def get_docs_in_col(col):
    # Returns a generator
    return col.get()


def get_doc(name):
    return cli.document(name)

# d = list(col.get())[0]
# d.to_dict()


def add_collection(path='Event'):
    new_col = cli.collection(path)
    new_col.add(document_data={u"hello": u"world"}, document_id='000')


def add_record(col, id, rec, ovr):
    if ovr:
        col.document(id).set(rec)
    else:
        try:
            col.add(document_data=rec, document_id=id)
        except Conflict as f:
            if f.code == 409:
                raise Exception(
                    "Key '" + id + "'already exists\n===============")


def update_doc(col, key, field, val):
    city_ref = col.document(key)
    city_ref.update({field: val})


def create_all_sublists():
    col = get_col('Subscribers')
    for x in sub_category_list:
        # cat_col = cli.collection('Subscribers/' + x)
        col.add(document_data={u"hello": u"world"}, document_id=x)
        for event in sub_category_list[x]:
            print (event)
            event_col = cli.collection('Subscribers/' + x + '/' + event)
            event_col.add(
                document_data={u"hello": u"world"}, document_id='000')
            for city in cities_data:
                # city_col = cli.collection(
                #     'Subscribers/' + x + '/' + event + '/' + city[:4])
                #
                event_col.add(
                    document_data={u"list": []}, document_id=city)


def create_all_eventcolls():
    col = get_col('EventRoot')
    for x in sub_category_list:
        # cat_col = cli.collection('Subscribers/' + x)
        col.add(document_data={u"hello": u"world"}, document_id=x)
        for event in sub_category_list[x]:
            print (event)
            event_col = cli.collection('EventRoot/' + x + '/' + event)
            event_col.add(
                document_data={u"hello": u"world"}, document_id='000')
            for city in cities_data:
                event_col.add(
                    document_data={u"hello": "world"}, document_id=city)
                full_path = 'EventRoot/' + x + '/' + event + '/' + city + '/AllEvents'
                allevent_col = cli.collection(full_path)
                allevent_col.add(
                    document_data={u"hello": u"world"}, document_id='000')


CITY_COLLECTION = 'Cities'
ATTR_COLLECTION = 'Attractions'
SUBA_COLLECTION = 'SubAttractions'
try:
    cli = client()
except:
    init()
    cli = client()

# create_all_eventcolls()


def add_subscriber_combined(category, event, city, fbid):
    add_subscriber(category, event, city, fbid)
    print "ADDING USER"
    print fbid
    print category
    print labmap
    associateUserToLabel(lid=labmap[category], upsid=str(fbid))


def add_subscriber(category, event, city, fbid):
    # category = "Technology"
    # event = "Developer Meets"
    # city = "Chennai"
    # fbid = 18735873563765
    path = 'Subscribers/' + category + '/' + event + '/' + city
    doc = cli.document(path)
    sublist = doc.get().to_dict()['list']
    if fbid not in sublist:
        sublist.append(fbid)
        doc.update({'list': sublist})


def add_event(category, event, city, event_dict, id):
    # category = "Technology"
    # event = "Developer Meets"
    # city = "Chennai"
    # fbid = 18735873563765
    path = 'EventRoot/' + category + '/' + event + '/' + city + '/AllEvents'
    print(path)
    col = cli.collection(path)
    col.add(document_data=event_dict, document_id=id)


def query(category=None, event=None, city=None, epoch_end=None, dt_end=None):
    if not dt_end is None and epoch_end is None:
        epoch_end = (dt_end - datetime(1970, 1, 1, 0, 0)).total_seconds()
    if category is None and not event is None:
        if category in sub_category_list:
            category = sub_category_list[category][1]
        try:
            category = category_map[event]
        except KeyError:
            category = 'Developer Meets'

    # category = "Technology"
    # event = "Developer Meets"
    # city = "Bangalore"
    # fbid = 18735873563765

    epoch_start = time.time()
    col = cli.collection('EventRoot/' + category + '/' +
                         event + '/' + city + '/AllEvents')
    all_dicts = []
    for i in col.where('epoch', '<=', epoch_end).where('epoch', '>=', epoch_start).get():
        all_dicts.append(i.to_dict())
    return all_dicts
