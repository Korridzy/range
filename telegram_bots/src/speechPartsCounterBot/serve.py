import falcon
from speechPartCounterBot import UpdatesReceiver


app = falcon.API()
app.add_route('/caesaimairooP2na/', UpdatesReceiver())