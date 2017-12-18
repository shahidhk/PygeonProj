import json
from broadcasting import getLabels, createTargetBroadcastLabel
MAILBOX_KEY = 'Bearer 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'

sub_category_list = {
    'Technology': ['Hackathons', 'Developer Meets', 'TechFests'],
    'Photography': ['Contests', 'Meetups', 'Walks'],
    'Entertainment': ['Shows', 'Concerts', 'Movies']
}

TECH_LABEL_ID = ""
PHOTO_LABEL_ID = ""
ENT_LABEL_ID = ""

# PRESETS:
# This is to preset the Label ID's. This must be run when the server is being initialized.

for i in getLabels():
    if i['name'] == 'TECH':
        TECH_LABEL_ID = i['id']
    elif i['name'] == 'PHOTO':
        PHOTO_LABEL_ID = i['id']
    elif i['name'] == 'ENT':
        ENT_LABEL_ID = i['id']

if not(TECH_LABEL_ID):
    TECH_LABEL_ID = createTargetBroadcastLabel("TECH")
if not(PHOTO_LABEL_ID):
    PHOTO_LABEL_ID = createTargetBroadcastLabel("PHOTO")
if not(ENT_LABEL_ID):
    ENT_LABEL_ID = createTargetBroadcastLabel("ENT")

# END PRESETS

labmap = {
    "Technology": TECH_LABEL_ID,
    "Photography": PHOTO_LABEL_ID,
    "Entertainment": ENT_LABEL_ID
}

template_list = [
    {
        'title': 'Technology',
        'image_url': 'https://www.gsa.gov/cdnstatic/getMediaDatamediaId168142.jpg',
        'subtitle': '',
        'url': 'www.wikipedia.org',
        'button_text': '',
        'payload': 'SEL1::Technology'
    },
    {
        'title': 'Photography',
        'image_url': 'http://www.seamedu.com/wp-content/uploads/photography.jpg',
        'subtitle': '',
        'url': 'www.wikipedia.org',
        'button_text': '',
        'payload': 'SEL1::Photography'
    },
    {
        'title': 'Entertainment',
        'image_url': 'http://dakotadunescasino.com/wp-content/uploads/2016/04/ddc_23.jpg',
        'subtitle': '',
        'url': 'www.wikipedia.org',
        'button_text': '',
        'payload': 'SEL1::Entertainment'
    }
]

for x in range(len(template_list)):
    title = template_list[x]['title']
    template_list[x]['subtitle'] = sub_category_list[title][0] + ', ' + \
        sub_category_list[title][1] + ' and ' + sub_category_list[title][2]
    template_list[x]['button_text'] = title + ' events  '

try:
    cities_list = json.loads(open('prime/cities.json').read()).keys()
except:
    cities_list = json.loads(open('cities.json').read()).keys()

category_map = dict()
for i in sub_category_list:
    for x in sub_category_list[i]:
        category_map[x] = i
