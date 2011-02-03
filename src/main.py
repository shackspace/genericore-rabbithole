#!/usr/bin/env python2
import json,time
from rabbithole import Rabbithole
import logging
import genericore as gen
MODULE_NAME='rabbithole'

log = logging.getLogger(MODULE_NAME)
PROTO_VERSION = 1
DESCRIPTION = 'Periodically sends Status informations of Rabbitmq'


# set up instances of needed modules
conf = gen.Configurator(PROTO_VERSION,DESCRIPTION)  
amqp = gen.auto_amqp(MODULE_NAME)   
s = Rabbithole(MODULE_NAME)       # the magic mail parsing class

conf.configure([amqp,s]) #set up parser and eval parsed stuff

# start network connections
amqp.create_connection()

log.info('Starting up infinite loop')
print ' Sending Messages in Intervals. To exit press CTRL+C'
try:
  while True:
    log.info("Collecting from Database")
    ret = s.collect()
    data = { 'type' : 'backbone', 'subtype' : 0, 'data' : ret}
    log.debug("writing data to queue : %s" % data)
    amqp.publish(json.dumps(data))
    log.info('Sleeping for %d Seconds' % s.getRepeat())
    time.sleep(s.getRepeat())
except Exception as e:
  print "something happened :( " + str(e)
