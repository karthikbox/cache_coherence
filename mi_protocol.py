"""
MI cache coherence protocol implementation in DistAlgo
based on the online implementation - https://github.com/samuelbritt/CS6290-prj3

To implement the protocol in DistAlgo, we are using a combination of snooping 
protocol logic and directory protocol logic.
"""

ENOTSUPP = 2
CACHE_SIZE = 512
addr = ""
p = ""
s = ""

def get_proto_class(name):
  """
  return the corresponding protocol class name and controller name
  """
  if name == "MI":
    return (eval("MI_PROTO_CACHE"), eval("MI_PROTO_CTRL"))
  else:
    exit(-ENOTSUPP)


class MI_PROTO_CACHE():
  """
    MI Protocol Class:
      - This class handles both the caching logic as well as the protocol logic
      - snooping of caches and getting data from memory happens via message passing 
      - Each processor will have a protocol cache process corresponding to it which
        will maintain that processor's cache memory as well as maintain cache coherence
      - Inherits from the process class in DistAlgo
  """
  def setup(mem_ctrl_protocol_obj, other_protocol_obj, size):
    """
      Initialize the cache memory and set the wait flags to false
    """
    self.memory = []
    self.get_from_caches = False
    self.wait_for_caches = False
    self.wait_for_memory = False
    
  def run():
    await(False)

  def reorder_cache(addr):
    """
      LRU Caching logic
    """

    """ Check if the addr is present in the list """
    if (1, addr) in self.memory: 
      self.memory.remove((1, addr))
    else:
      """ Check if the cache is full """
      if len(self.memory) == size:
        print("Cache is full")
        (state, last_addr) = self.memory.pop()
        if state == 1:
          send(('flush', last_addr), to=mem_ctrl_protocol_obj)
    
    self.memory.insert(0, (1, addr))

  def get_addr(addr):
    """ 
      The load/store address is not in the cache, try
          (1) snoop other caches 
          (2) if (1) fails then get from memory 
    """
    wait_for_caches = False;
    send(('get', addr), to=other_protocol_obj)
    await(wait_for_caches)
    if not get_from_caches:
      wait_for_memory = False
      send(('get', addr), to=mem_ctrl_protocol_obj)
      await(wait_for_memory)

    """ Receive data from cache/memory, invalidate all other copies """
    get_from_caches = False
    send(('invalidate', addr), to=other_protocol_obj)

  def receive_get_address(msg= ('get',addr), from_= p):
    """
      Received request for address from another cache, check local
      cache and if addr is present, invalidate it and send back the value
    """

    """ Add time delay here to mimic cache-to-cache latency """
    time.sleep(1)
    print("Cache request for address: ", addr)
    if (1, addr) in self.memory:
      """ invalidate cache block """
      new_cache = [(0,addr) if x==(1,addr) else x for x in self.memory]
      self.memory = new_cache
      send(('found_in_cache'), to=p)
    else:
      send(('not_found_in_cache'), to=p)

  def receive_invalidate_block(msg= ('invalidate', addr), from_= p):
    """
      Invalidate the cache block containing the requested address if present in our cache
    """
    """ invalidate cache block """
    new_cache = [(0,addr) if x==(1,addr) else x for x in self.memory]
    self.memory = new_cache

  def receive_data_from_other_cache(msg=('found_in_cache')):
    """
      Received "found in cache" acknowledgement which basically denotes we have found 
      the requested addr in another cache and received the value from that cache.
    """
    print("Addr received from another cache")
    get_from_caches = True
    wait_for_caches = True

  def receive_snoop_caches(msg=('located_in_cache', addr)):
    """
      This logic is put in to handle the race condition when two caches are requesting for the same
      address in memory. When a cache receives this message, it means that the address it had requested the memory
      controller for has already been loaded by another cache and to snoop the other caches again to get
      the updated address.
    """
    wait_for_memory = True
    get_addr(addr)

  def receive_not_found_in_cache(msg=('not_found_in_cache')):
    """
      The requested address/data is not located in a cache. When the number of such messages received
      equals the number of other caches then its safe to assume that the address/data is not present in
      any of the other caches and we need to go to the memory controller
    """
    if len(setof(a, received(('not_found_in_cache'), from_ =a))) == len(other_protocol_obj):
      print("Addr not found in the other caches")
      wait_for_caches = True 

  def receive_data_from_memory(msg=('found_in_memory')):
    """
      We have received the requested address/data from the memory controller
    """
    print("Addr received from memory")
    wait_for_memory = True

  def receive_not_found_in_memory(msg=('not_found_in_memory')):
    """
      Address not found in memory, ideally should never happen
    """
    print("Addr not found in memory")
    wait_for_memory = True

  def receive_load(msg=('load',addr, p), from_=s):
    """
      Received load request from processor, load address into cache and send back acknowledgement
    """
    print("Received LOAD request for addr %s" % addr);
    if (1,addr) not in self.memory:
      """ Cache miss logic """
      get_addr(addr)
    self.reorder(addr)
    print("Sending Ack")
    send('completed', to=s)
  
  def receive_store(msg=('store',addr, p), from_=s):
    """
      Received store request from processo, store value into cache and send back acknowledgement
    """
    print("Received STORE request for addr %s" % addr);
    if (1,addr) not in self.memory:
      """ Cache miss logic """
      get_addr(addr)
    self.reorder(addr)
    print("Sending Ack")
    send('completed', to=s)
  
  def receive_done(msg= ('done',)):
    """
      Exit the cache process on a done message
    """
    print("Cache Exiting\n")
    exit()

class MI_PROTO_CTRL():
  """
    MI Memory Controller Class:
      - This class simulates the system bus and memory controller
      - keeps track of all addresses in the caches
      - A standalone process which serves memory requests from the caches
      - Inherits from the process class in DistAlgo
  """
  def setup(cache_protocol_objs):
    """
    Setup a hashmap for tracking the addresses in the caches
    """
    self.memory_ref = dict()
  
  def run():
    await(False)
  
  def receive_get_address(msg= ('get',addr), from_= p):
    """
    Retrieve the requested address from memory and send it back to the cache
    """
    """ Add time delay here to mimic cache-to-memory latency """
    time.sleep(3)
    if addr in self.memory_ref and self.memory_ref[addr] > 0:
      send(('located_in_cache', addr), to=p)
    else:
      self.memory_ref[addr] = 1
      send(('found_in_memory'), to=p)

  def receive_write_back_cache_block(msg= ('flush', addr)):
    """
    Flush the corresponding address back to memory
    """
    self.memory_ref[addr] = 0

  def receive(msg= ('done',)):
    """
      Exit the memory controller process on a done message
    """
    print("CTRL Exiting\n")
    exit()

class Processor():
    """
    Processor Class:
      - This class handles the processor logic
      - reads the execution trace one instruction at a time and executes it
      - All the load/store intstructions will be send to it's cache controller process
      - Inherits from the process class in DistAlgo
    """
    def setup(trace, protocol):
      """
        Intialize the keep waiting flag to false
      """
      self.keep_waiting = False
    
    def execute(inst):
      """
        Execute the instructions in the given execution trace 
      """
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

    def receive_ack(msg= ('completed')):
      """
        Receive acknowledgement from the cache controller process.
        This indicates that the instruction has been executed
      """
      print("ACKed\n")
      keep_waiting = True

def get_traces(trace_file):
  """
    Get the execution trace list for all the processors
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
      main routine:
        - spawn DistAlgo processes for n processors, n cache controllers and a
          memory controller 
        - get execution traces for each of the processors
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

