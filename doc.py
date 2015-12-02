"""
MOESI cache coherence protocol implementation in DistAlgo
based on the online implementation - https://github.com/samuelbritt/CS6290-prj3
To implement the protocol in DistAlgo, I am using directory-based protocol logic.
Note: The basic structural view for the protocol is same for our group and hence certain classes/methods
      which are common to all protocols is part of the intial setup. The other members of the group are
      Parag Gupta, Karthik Reddy, Garima Gehlot and Paul Mathew.
      Particularly for MOESI protocol, I am working for Karthik Reddy for MESI protocol implementation
      as their are some minor changes to be done to convert MESI->MOESI protocol.
      So, majorly the code with Karthik Reddy will be same excluding the explicit changes I need to do 
      to make it MOESI protocol.
"""
import pydoc
import sys
import time

ENOTSUPP = 2
CACHE_SIZE = 512
p = ""
s = ""
d = ""
addr = ""

def createProtocolObjects(name):
  if name == "MOESI":
    return (eval("MOESI_Cache"), eval("MOESI_Directory"))
  else:
    exit(-ENOTSUPP)


## MOESI Cache Protocol Classes
class MOESI_Cache():
  """
  This class denotes the object for the local- cache corresponding a particular processor.
  It contains the main logic for handling 5 states of the protocol and is responsible for the state 
  transitions for the cache data entries.
  The implementation is based on the state transitions as explained in the following mentioned book (Chapter 8).
  Reference : Sorin, Daniel J., Mark D. Hill, and David A. Wood. "A primer on memory consistency and 
  cache coherence." Synthesis Lectures on Computer Architecture 6.3 (2011): 1-212.
  Book doesn't contain the state diagram/machine for MOESI protocol, but understanding the MESI and MOSI protocol 
  clearly helped me to create a state machine for MOESI protocol together with some brain-storming sessions with 
  Karthik Reddy.
  """
  def setup(mem_ctrl_protocol_obj, other_protocol_obj, size):
    self.memory = []
    self.get_from_caches = False
    self.wait_for_caches = False
    self.wait_for_memory = False
    self.get_from_memory = False
    
  def run():
    await(False)

  def CacheUpdate(addr):
    """ We implemented LRU cache for managing the data in the Cache.
        Based on whether the data is present in Cache or not, update the cache Entries.
        If the data is there in the cache and not the head of list, remove from its current location and put at front.
        Otherwise, insert directly at the head of the list.
    """
    if (1, addr) in self.memory: 
      self.memory.remove((1, addr))
    else:
      """ Check if the cache is full """
      if len(self.memory) == size:
        print("Cache is FULL")
        (state, last_addr) = self.memory.pop()
        if state == 1:
          send(('flush', last_addr), to=mem_ctrl_protocol_obj)
    
    self.memory.insert(0, (1, addr))


  def Transition_from_I_to_S(addr):
    """ 
    We have some cases when transitioning from state 'I' based on the state of data in directory class.
    If State of same data in Directory is :-
      a) S : Directory state will remain in S state and I->S transition will occur in Cache.
      b) M : Directory will forward the load msg to Owner Cache of data entry, Owner state from M/E -> S and 
             it will reply to Dir and current Cache with "DatafromOwner" msg.
      c) O : Directory will forward the load msg to Owner Cache of data entry, Owner state from M/O -> O and 
             it will reply to Dir and current Cache with "DatafromOwner" msg.
      
    """

  def Transition_from_I_to_E(addr):
    """
      If the Directory entry is in state 'I',
      Directory transition from I->E and and cache transition from I->E using the "ExclDatafromDir" msg from Directory class.
    """
  

  def Transition_from_I_to_M(addr):
    """
    Processing of the write request.
    If the state of the data entry in Directory is :-
      a) I : Directory transition from I->M and and cache transition from I->M using the "DatafromDirAck0" msg from Directory class.
      b) M : Directory transition from M/E->M with msg forwarding to Owner Cache of data entry, Owner state from M/E -> I and 
             it will reply to Dir and current Cache with "DatafromDirAck0" msg.
      c) S : Directory transition from S->M with Inv broadcast to all the caches having the data entry. Caches will also 
             make transition from S->I and sends Inv-Ack to current Cache with "DatafromOwner" msg.
      d) O : Directory transition from O->M with Inv broadcast to all the caches having the data entry with S state and 
             fwd-GetM message to the previous owner of the data entry. Sharer caches will also  make transition from S->I and
             sends Inv-Ack and Owner cache will send DatafromDirAck0 message to requesting Cache.
    """

  def Transition_from_S_to_M(addr):
    """
    Two Cases :-
      a) Directory transition from S->M with Inv broadcast to all the caches having the data entry. Caches will also 
         make transition from S->I and sends Inv-Ack to current Cache with "DatafromOwner" msg.
      b) Directory transition from O->M with Inv broadcast to all the caches having the data entry with S state and 
         fwd-GetM message to the previous owner of the data entry. Sharer caches will also  make transition from S->I and
         sends Inv-Ack and Owner cache will send DatafromDirAck0 message to requesting Cache.
    """

  def Transition_from_M_to_I(addr):
    """
    Cache entry will be in M state when Directory entry is in M state. This is cause M->I transition for Directory entry as well as 
    this cache entry with a Put-Ack msg from Directory.
    """

  def Transition_from_E_to_I(addr): 
    """
    Cache entry will be in E state when Directory entry is in E state. This will cause E->I transition for Directory entry as well as 
    this cache entry with a Put-Ack msg from Directory.
    """
  
  def Transition_from_O_to_M(addr): 
    """
    Cache entry will be in O state when Directory entry is in O state. This will cause Directory to send Inv request to all sharer caches.
    Sharer caches will make S->I transition and send Inv-Ack to requesting cache. Directory will also send AckCount msg to requesting cache 
    which will help the requesting cache to wait till AckCount.
    """
  

  def Transition_from_S_to_I(addr): 
    """
    Cache entry will be in S state when Directory entry is in S state. This is cause S->I/S transition for Directory entry and S->I 
    for the cache entry with a Put-Ack msg from Directory.
    """

  def Transition_from_O_to_I(addr): 
    """
    Cache entry will be in O state when Directory entry is in O state. This is cause O->I/S transition for Directory entry and O->I 
    for the cache entry with a Put-Ack msg from Directory.
    """



  def receive_ExclDatafromDir(msg= ('ExclDatafromDir',),from_=p):
    """ 
    Exclusive data msg from the Directory to cache when none of the caches contain requesting data entry, hence I->E is done 
    """
    print("Addr received from another cache")
    get_from_caches = True
    wait_for_caches = True

  def receive_DatafromOwner(msg=('DatafromOwner'),from_=p):
    """ Data message from the other caches which are currently the having the data entry in E or M state """
    print("Addr received from memory")
    get_from_memory = True
    wait_for_memory = True

  def receive_fwdGetS(msg=('fwd-GetS'),from_=d):
    """ Directory forwarded msg for sharing of data entry to caches having data currently in M or E state """
    print("Addr received from memory")
    get_from_memory = True
    wait_for_memory = True


  def receive_fwdGetM(msg=('fwd-GetM'),from_=d):
    """ Directory forwarded msg for modifying data entry to caches having data currently in M or E state """
    print("Addr received from memory")
    get_from_memory = True
    wait_for_memory = True


  def receive_Inv(msg= ('Inv', addr), from_= d):
    """ Invalidating request msg from directory """
    new_cache = [(0,addr) if x==(1,addr) else x for x in self.memory]
    self.memory = new_cache

  def receive_AckCount(msg=('AckCount', addr)):
    """ The Directory will send the Count of the acks that requesting cache should receive when O->M transition happens and 
        all sharers need to Invalidate their data entries """
    wait_for_memory = True
    get_addr(addr)


  def receive_InvAck(msg=('Inv-Ack', addr)):
    """ The sharer of a cache entry will send invalidate ack to requesting cache for it to make successful I/S->M transition """
    wait_for_memory = True
    get_addr(addr)

  def receive_load(msg=('load',addr, p), from_=s):
    """ Load request from the processor """
    print("Received LOAD request for addr %s" % addr);
    
    self.reorder(addr)
    print("Sending Ack")
    send('completed', to=s)
  
  def receive_store(msg=('store',addr, p), from_=s):
    """ Store request from the Processor """
    print("Received STORE request for addr %s" % addr);
    if (1,addr) not in self.memory:
      """ Cache miss logic """
      get_addr(addr)
    self.reorder(addr)
    print("Sending Ack")
    send('completed', to=s)
  
  def receive(msg= ('done',)):
    print("Cache Exiting\n")
    exit()


class MOESI_Directory():
  """
  MOESI directory controller class.
  This class simulates the shared directory between caches and is responsible for managing data in the memory.
  This is a single process which handles all access requests from all the processor caches.
  It keeps track of all data entries and their states corresponding to memory.
  Reference : 
  Sorin, Daniel J., Mark D. Hill, and David A. Wood. "A primer on memory consistency and 
  cache coherence." Synthesis Lectures on Computer Architecture 6.3 (2011): 1-212.
  Karthik Reddy : https://github.com/karthikbox/cache_coherence/blob/mesi_protocol/submit_files/mesi_protocol_main.txt
  """

  def setup(cache_protocol_objs):
    self.memory_ref = dict()
  
  def receive_getS(msg=('getS')):
    """ Read Request from caches """
    print("recevied msg\n")

  def receive_getM(msg=('getM')):
    """ Write Request from caches """
    print("recevied msg\n")


  def receive_putM(msg=('putM')):
    """ Write-back Request with data from caches when cache needs to evict this data entry (no write to memory). 
        Will transition from M->O state
    """
    print("recevied msg\n")    

  def receive_putE(msg=('putE')):
    """ Write-back Request from caches when cache needs to evict this data entry (no write to memory)"""
    print("recevied msg\n")    

  def receive_putS(msg=('putS')):
    """ Write-back Request from caches when cache needs to evict this data entry (no write to memory) 
        which can make S->S/I transition.
    """
  def receive_putO(msg=('putO')):
    """ Write-back Request with data from caches when cache needs to evict this data entry (write to memory) 
        which can make S->S/I transition.
    """
    print("recevied msg\n")    

  def receive(msg= ('done',)):
    print("CTRL Exiting\n")
    exit()

  def run():
    await(False)


class ProcessorReq():
  """
  Processor Class:
  This class simulates the read/write requests to a particular processor.
  implementation wise, it makes read/write requests to cache controller one at a time.
  Since this is a part of common platform on which the team will do the evaluations, copied it from following :-
  Reference: Parag Gupta. https://github.com/karthikbox/cache_coherence/tree/p_template/main.da
  """
  def setup(trace, protocol):
    self.keep_waiting = False
    ## self.cache = Cache(protocol, CACHE_SIZE)
  
  def execute(inst):
    type, addr = inst
    if type == "r":
      send(('load', addr, self.id), to=protocol)
   
    elif type == "w":
      send(('store', addr, self.id), to=protocol)
    
    else:
      print("Unexpected instruction:", inst);
  
  def run():
    for inst in trace:
      keep_waiting = False
      execute(inst)
      await(keep_waiting)

    print("Processor Exits")

  def receive(msg= ('completed')):
    print("ACKed\n")
    keep_waiting = True

def ReadTraces(trace_file):
  """
  Temporary implementation to simulate access requests to a processor.
  Generic to all protocol implementations. Copied it from following :-
  Reference: Parag Gupta. https://github.com/karthikbox/cache_coherence/tree/p_template/main.da
  """
  return [
          [
           ('r', '0x11111111'),
           ('r', '0x11111112'),
           ('w', '0x11111113')
          ],

          [
           ('r', '0x11111111'),
           ('w', '0x11111115'),
           ('r', '0x11111112')
          ]
         ]

def main():
  """
  Main driver function to simulate the running behaviour of cache coherence protocol with 
  given number of processors, protocol name and trace file path.
  Command should be passed in the following way :
  dar main.da 'n' "Protocol" "Path",
  where n - # of processors ( local-caches)
        Protocol - Protocol Name (MI/MSI/MESI/MOSI/MOESI)
        Path - Path of the trace file to run with
  Since this is a part of common platform on which the team will do the evaluations, copied it from following :-
  Reference: Parag Gupta. https://github.com/karthikbox/cache_coherence/tree/p_template/main.da
  
  """
  nprocessors = int(sys.argv[1]) if len(sys.argv) > 1 else 2
  proto_name = sys.argv[2] if len(sys.argv) > 2 else 'MI'
  #trace_file = sys.argv[3] if len(sys.argv) > 3 else exit(-1)
  trace_file = sys.argv[3] if len(sys.argv) > 3 else 'none'
  
  trace = get_traces(trace_file)
  Proto_cache, Proto_ctrl = get_proto_class(proto_name)
  
  ## Initialize protocol objs for caches and controller
  mem_ctrl_protocol_obj = new(Proto_ctrl, num=1)
  protocol_objs = new(Proto_cache, num=nprocessors)
  
  ## Setup Protocol for ctrller
  setup(mem_ctrl_protocol_obj, (protocol_objs,))
  start(mem_ctrl_protocol_obj)

  ## Setup Protocols for caches
  for proto_obj in protocol_objs:
    setup(proto_obj, (mem_ctrl_protocol_obj, protocol_objs - {proto_obj}, CACHE_SIZE))
    start(proto_obj)

  ## Setup Processors
  processors = new(Processor, num= nprocessors)
  
  ## temp lists for iterating
  processors_list = list(processors)
  protocol_objs_list = list(protocol_objs)
  for i in range(nprocessors): 
    setup(processors_list[i], (trace[i], protocol_objs_list[i]))
  
  start(processors)
  
  ## Exiting logic  
  for p in processors: 
    p.join()

  da.send(('done',), to= protocol_objs)
  for m in protocol_objs:
    m.join()

  da.send(('done',), to= mem_ctrl_protocol_obj)
  for m in mem_ctrl_protocol_obj:
    m.join()
  print('-----END-----')

