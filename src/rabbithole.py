#!/usr/bin/python2

import logging, subprocess
from multiprocessing import Pool
from genericore import Configurable
log = logging.getLogger('Rabbithole')

DEFAULT_CONFIG= {
    'repeat' : 30,
    'vhost' : '/', # TODO currently unsupported
    'cmds' : [
      'status',
      'list_vhosts',
      'list_users',
      'list_permissions',
      'list_queues',
      'list_exchanges',
      'list_bindings',
      'list_connections',
      'list_channels',
      'list_consumers' ]
}

def call_external(cmd):
    ''' calls the command for rabbitmq, use with caution!'''
    log.debug('calling ' + 'rabbitmqctl' + cmd)
    out = subprocess.Popen(
        ['rabbitmqctl',
          cmd],
        stdout=subprocess.PIPE).communicate()[0]
    return { 'cmd' : cmd ,'output' : out }

class Rabbithole(Configurable):
  mac_list = {}
  def __init__(self,MODULE_NAME='rabbithole',config=None):
    self.NAME = MODULE_NAME
    newconf = { MODULE_NAME : DEFAULT_CONFIG }
    Configurable.__init__(self,newconf)
    self.load_conf(config)

  def  getRepeat(self):
    ''' getter convenience function for long config path'''
    return self.config[self.NAME]['repeat']

  def parallel_call(self):
    cmds = self.config[self.NAME]['cmds']
    try:
      p = Pool(10)
      ret = p.map(call_external, cmds)
      
      p.terminate()
      return ret
    except Exception as e:
      log.warning("Something happened,falling back to original data: "+ str(e))
      return []

  def process_output(self,output):
    '''will pull the data together in one dictionary,
    TODO parse the output of every command differently'''
    ret = {}
    for i in output :
      ret[i['cmd']] = i['output']
    return ret

  def collect(self):
    output = self.parallel_call()
    log.debug(str(output))
    ret = self.process_output(output)
    return ret

  def print_output(self,data):
    for k,v in data.items():
      print str(k) + ' --> ' + str(v)
      print
  def populate_parser(self,parser):
    parser.add_argument('--repeat',type=int,dest='repeat',help='Seconds between Scans',metavar='SECS') #TODO add this to configuration

  def eval_parser(self,parsed):
    '''does not allow endless without delay'''
    self.repeat = parsed.repeat if parsed.repeat else self.getRepeat()

if __name__ == '__main__' :
  rab = Rabbithole()
  logging.basicConfig(level=logging.INFO)
  out = rab.collect()
  rab.print_output(out)
