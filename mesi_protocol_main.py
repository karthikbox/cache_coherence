"""
MESI cache coherence protocol implementation in DistAlgo
This is based on a Directory Controller based implementation.

Run as:
        python -m da main.da <num_processors> <protocol_name> <trace_filepath>

Reference: Sorin, Daniel J., Mark D. Hill, and David A. Wood. "A primer on memory consistency and cache coherence." 
Synthesis Lectures on Computer Architecture 6.3 (2011): 1-212.
Note: Certain parts of the implementation are same for our group as they are generic classes/methods
      which are common to all protocols and is part of the intial setup.
      Team Members:
        Karthik Reddy
        Amit Khandelwal
        Paul Mathew
        Garima Gehlot
        Parag Gupta
      Code is referenced where it has been copied.
"""
addr=1234
p="process"
s="set"
ack=""

class MESI_CACHE_CONTROLLER():
  """
  Extends DistAlgo "process" class.
  Each instance of this class represents a Cache controller of size "CACHE_SIZE".
  Cache controller makes local and remote transitions depending on whether data is present in the cache or not.
  Each Cache controller communicates directly with Directory Controller.
  Reference: Sorin, Daniel J., Mark D. Hill, and David A. Wood. "A primer on memory consistency and cache coherence." Synthesis Lectures on Computer Architecture 6.3 (2011): 1-212.
  Amit Khandelwal. https://github.com/karthikbox/cache_coherence/blob/moesi_protocol/MOESI_documentation.txt. Discussed design choices with Amit, but wrote the API independently. Since MOESI and MESI are similar protocols, some of the API, especially state machine transitions may look similar.
  """
  
  def setup(dir_ctrl_obj):
    """ 
    Input: Directory controller object address.
    Output: Return a MI_PROTO_CACHE object.
    Memory is list of tuples (State,Address).
    All action the cache takes depends on the state of an address stored in memory.
    """
    self.memory = []
    
  def run():
    """ Starts the cache processs. """
    await(False)

  def updateLRU(addr):
    """ Update the cache LRU order internal to this cache """
    pass
  
  def doWrite(addr):
    """ 
    Requests Write access to 'addr'.
    If address is present in cache with state Modified, do the write. 
    Otherwise, sends "GetM" message to the directory controller.
    Receives data from the directory controller or from any other cache who is a owner.
    Guarantees that this is the only copy in the system.
    """
    if memory.find(addr).state!='M':
      make_transition_to_M(addr)
    return memory.find(addr)


  def doRead(addr):
    """
    Requests Read access to 'addr'.
    If address already exists in cache with either of the Modified, Exclusive and Shared state, do the read and return.
    If addr state is Invalid, sends "GetShared" message to the directory controller.
    Receives data from the directory controller or from any other cache who is a owner.
    There may or may not be other copies in the system.
    Make transition to Shared state.
    """
    if addr not in memory:
      make_transition_to_S(addr)
    return memory.find(addr)


  def receive_load_address(msg=('load',addr, p), from_=s):
    """ Executes Read instruction on 'addr'
        Input: Memory address. 
        Output: Read to memory address. Ensures cache coherence.
    """
    doWrite(addr)
    updateLRU(addr)
    print("Sending Ack")
    send('completed', to=s)
  
  def receive_store_address(msg=('store',addr, p), from_=s):
    """
    Executes Write instruction on 'addr'
    Input: Memory address. 
    Output: Writes to memory address. Ensures cache coherence.
    """
    doRead(addr)
    updateLRU(addr)
    print("Sending Ack to Processor")
    send('completed', to=s)

  def receive_forward_getS(msg=('Fwd-GetS',addr,p), from_=s):
    """ 
    The cache is one of the sharers/owner of the address. 
    Reply back to Directory controller and to the requesting cache
    """
    pass

  def receive_forward_getM(msg=('Fwd-GetM',addr,p), from_=s):
    """ 
    The cache is the owner of the address. 
    Reply back to the requesting cache.
    """
    pass

  def receive_put_ack(msg=('Put-Ack',addr,p), from_=s):
    """ 
    Acknowledment from directory controller for making a successful transition
    """
    pass

  def receive_data_from_owner(msg=('Data-from-owner',addr,p), from_=s):
    """ 
    Data received from the owner/sharer of the memory address
    """
    pass

  def receive_data_from_dir_with_ack(msg=('Data-from-dir-with-ack',ack,addr,p), from_=s):
    """ 
    Data received from Directory Controller. Cache must wait for "Inv-Acks" from "ack">=0 number of caches.
    If "ack">0: This makes sure that "ack" Sharers have invalidated their data.
    If "ack"=0: No need to wait for any acks from the Sharers.
    """
    pass
    

  def receive_invalid_ack(msg=('Inv-Ack',addr,p), from_=s):
    """
    Count till the Invalid Acknowledgements reach  the required limit.
    Ack--
    """
    pass

  def mak_transition_from_I_to_S(addr):
    """
    Go from Invalid state to Shared state
    """
    pass

  def mak_transition_from_I_to_M(addr):
    """
    Go from Invalid state to Modified state
    Guarentees unique copy in the system
    """
    pass

  def mak_transition_from_S_to_M(addr):
    """
    Go from Shared state to Modified state
    Guarentees unique copy in the system
    """
    pass

  def mak_transition_from_M_to_I(addr):
    """
    Go from Modified state to Invalid state
    Write back to memory.
    Happens due to evictions.
    """
    pass

  def mak_transition_from_E_to_M(addr):
    """
    Go from exclusive state to Modified state. This is a silent transition.
    """
    pass

  def mak_transition_from_X_to_I(addr):
    """
    Go from states M,S,E to Invalid state.
    """
    pass
    

  def receive_done(msg= ('done',)):
    """
    Exit the Cache Controller process.
    """
    print("Cache Exiting\n")
    exit()

class MESI_DIRECTORY_CONTROLLER():
  """
  Encapsulates a the methods and data of a Directory Controller object.
  Directory Controller tracks the status of each Cache Controller.
  Reference: Sorin, Daniel J., Mark D. Hill, and David A. Wood. "A primer on memory consistency and cache coherence." Synthesis Lectures on Computer Architecture 6.3 (2011): 1-212.
  Amit Khandelwal. https://github.com/karthikbox/cache_coherence/blob/moesi_protocol/MOESI_documentation.txt. Discussed design choices with Amit, but wrote the API independently. Since MOESI and MESI are similar protocols, some of the API, especially state machine transitions may look similar.
  """

  
  def setup(cache_protocol_objs):
    """ 
    Inits a dict object to store for each cache line the "status"(eg. Modified/Invalid), 
    "Owner"(Address of the owner cache controller) and "Sharers"(a list of cache controller addresses).
    """
    self.memory_ref = dict()
  
  def run():
    """ Run the Directory Controller process."""
    await(False)
  
  def receive_getS(msg= ('getS',addr), from_= p):
    """
    If current state of addr is:
    I: send Exclusive data to requestor Cahce, set owner to Requestor and status to E
    S: send data to Req, add Req to Sharers, no change to status
    E: forward GetS to Owner, make Owner sharer, add Req to Sharers, clear Owner/S^D
    M: forward GetS to Owner, make Owner sharer, add Req to Shar- ers, clear Owner/S^D
    S^D: Stall or queue. I.E do not interrup the current transaction
    """
    pass

  def receive_getM(msg= ('getM',addr), from_= p):
    """
    If current state of addr is:
    I: send data to Req, set Owner to Req/M
    S: send data to Req, send Inv to Sharers, clear Sharers, set Owner to Req/M
    E: forward GetM to Owner, set Owner to Req/M
    M: forward GetM to owner, set Owner to Req
    S^D: Stall or queue. I.E do not interrup the current transaction
    """
    pass

  def receive_putM_from_owner(msg= ('putM-from-owner',addr), from_= p):
    """
    If current state of addr is:
    E: copy data to mem, send Put- Ack to Req, clear Owner/I
    M: copy data to mem, send Put- Ack to Req, clear Owner/I
    """
    pass

  def receive_putM_from_nonowner(msg= ('putM-from-nonowner',addr), from_= p):
    """
    If current state of addr is:
    I: send Put-Ack to Req
    S: Remove Req from Sharers, send Put-Ack to Req
    E: send Put-Ack to Req
    M: send Put-Ack to Req
    S^D: remove Req from Sharers, send Put-Ack to Req
    """
    pass

  def receive_putE_from_nonowner(msg= ('putE-from-nonowner',addr), from_= p):
    """
    If current state of addr is:
    I: send Put-Ack to Req
    S: Remove Req from Sharers, send Put-Ack to Req
    E: send Put-Ack to Req
    M: send Put-Ack to Req
    S^D: remove Req from Sharers, send Put-Ack to Req
    """
    pass

  def receive_putM_from_owner(msg= ('putM-from-owner',addr), from_= p):
    """
    If current state of addr is:
    E: send Put-Ack to Req, clear Owner/I
    """
    pass
  

  def receive_done(msg= ('done',)):
    """
    Exit the Cache Controller process.
    """
    print("CTRL Exiting\n")
    exit()

class Processor():
  """
  Represents a Processor.
  The Processor reads from a trace file and issues "load"/"store" instructions to Cache controller object. The processor will wait till the cache object acknowledges a successful execution. Then it executes another intruction.
  Copied this method from the following, since it is part of the common platform on which the Team will evaluate the protocols.
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

def get_traces(trace_file):
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

def get_proto_class(name):
  """
  Input: Cache Coherence algorithm string. Eg: "MESI","MI",etc
  Returns: Return Class of the Algorithm. Eg: class MESI_CACHE_CONTROLLER, class MESI_DIRECTORY_CONTROLLER
  Copied this method from the follwing, since it is part of the common platform on which the Team will evaluate the protocols.
  Reference: Parag Gupta. https://github.com/karthikbox/cache_coherence/tree/p_template/main.da
  """
  if name == "MESI":
    return (eval("MESI_CACHE_CONTROLLER"), eval("MESI_DIRECTORY_CONTROLLER"))
  else:
    exit(-ENOTSUPP)


def main():
  """
  The Driver method for the experiments.
  Run as:
  python -m da main.da <num_processors> <protocol_name> <trace_filepath>

  Outputs the performance statistics.

  Copied this method from the follwing, since it is part of the common platform on which the Team will evaluate the protocols.
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

