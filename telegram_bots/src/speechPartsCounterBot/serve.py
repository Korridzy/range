import falcon
from speechPartCounterBot import UpdatesReceiver

TELEBOT_WEBHOOK_KEY = 'bad_key'

try:
    from local_settings import *
except:
    pass

app = falcon.API()
app.add_route('/{}/'.format(TELEBOT_WEBHOOK_KEY), UpdatesReceiver())