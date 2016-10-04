#!/usr/bin/python
import simplejson as json
from decimal import *
import thread
import websocket

def on_message(ws, message):
    result = json.loads(message)
    transactions = 0
    print('\n')
    print('Time: ' + str(result['x']['time']))
    if 'inputs' in result['x']:
        totali = 0
        inids = []
        for sender in result['x']['inputs']:
            if 'prev_out' in sender:
                recipient = sender['prev_out']['addr']
                inids.append(recipient)
                transactions += 1
                value = Decimal(sender['prev_out']['value']) / Decimal(100000000.0)
                totali += value
                print('SEND:   ' + str(transactions)
                        + ' [' + str(sender['prev_out']['n'])
                        + '] ' + sender['prev_out']['addr']
                        + ' (-) ' + str(value))

    if 'out' in result['x']:
        totalo = 0
        change = 0
        oids = []
        for out in result['x']['out']:
            if 'addr' in out:
                recipient = out['addr']
                oids.append(recipient)
                transactions += 1
                value = Decimal(out['value']) / Decimal(100000000.0)
                totalo += value
                if recipient in inids:
                    change += value
                    print('  CHNG: ' + str(transactions)
                            + ' [' + str(out['n'])
                            + '] ' + out['addr']
                            + ' (+) ' + str(value))
                else:
                    print('* RECV: ' + str(transactions)
                            + ' [' + str(out['n'])
                            + '] ' + out['addr']
                            + ' (+) ' + str(value))

        print('Total in:  ' + str(totali) + '\nTotal out: ' + str(totalo-change))
        print('Change:    -' if change == 0 else 'Change:    ' + str(change))
        print('Fees:      -' if (totali-totalo) == 0 else 'Fees:      ' + str(totali-totalo))

def on_error(ws, error):
    print error

def on_close(ws):
    print "Connection closed"

def on_open(ws):
    def run(*args):
        ws.send('{"op":"unconfirmed_sub"}')

    thread.start_new_thread(run, ())

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://ws.blockchain.info/inv",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)

    ws.on_open = on_open

    ws.run_forever()