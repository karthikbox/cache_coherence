"""
CSE535 - Cache Coherence Project.

MSI cache coherence protocol implementation in DistAlgo by Parag Gupta.
To implement the protocol in DistAlgo, we are using a combination of snooping 
protocol logic and directory protocol logic.
Certain parts of the implementation are same for our group as they are generic 
classes/methods which are common to all protocols and is part of the intial 
setup. The tead members of the group are:
    Parag Gupta (me)
    Karthik Reddy
    Garima Gehlot
    Amit Kandelwal
    Paul Mathews.

Running :
  python -m da main.da <num_processors> MSI <tracefile>

Reference added wherever necessary.

Reference implementation - 
[1] https://github.com/samuelbritt/CS6290-prj3

The initial setup branch (developed by me) on which the protocols are develop: 
[2] https://github.com/karthikbox/cache_coherence/blob/p_template/main.da

MI protocol implementation by Paul Mathews on top of which MSI is implemented:
[3] https://github.com/karthikbox/cache_coherence/blob/mi_protocol/main.da,
Paul Mathews

Important note:
===============
MI protocol API documentation by Paul Mathews, taken as base for 
MSI documentation: 
[4] https://github.com/karthikbox/cache_coherence/blob/mi_protocol/msi_protocol.py
, Paul Mathews

Protocol State machine reference from Wikipedia:
[5] https://en.wikipedia.org/wiki/MSI_protocol
[6] http://wiki.expertiza.ncsu.edu/index.php/Chp8_my
"""

ENOTSUPP = 2
CACHE_SIZE = 512
addr = ""
p = ""
s = ""

def get_proto_class(name):
  """
    Returns the corresponding protocol class and controller class based on 
    string class name.
  """

  if name == "MSI":
    return (eval("MSI_PROTO_CACHE"), eval("MSI_PROTO_CTRL"))
  else:
    exit(-ENOTSUPP)


class MSI_PROTO_CACHE():
  """
    MSI Protocol Class:
      - This class handles both the caching logic as well as the protocol logic
      - snooping of caches and getting data from memory happens via message passing 
      - Each processor will have a protocol cache process corresponding to it which
        will maintain that processor's cache memory as well as maintain cache coherence
      - Inherits from the process class in DistAlgo
      - This class is based on MI_PROTO_CACHE by Paul Mathews [3][4]
  """

  def setup(mem_ctrl_protocol_obj, other_protocol_obj, size):
    """
      Initialize the cache memory and set the wait flags to false.
      Input: (Memory controller protocol object,
              Protocol objects simulating other caches,
              Size of the cache)
      Output: False
    """
    pass 

  def run():
    """ 
      Run loop for the process
    """
    pass

  def reorder_cache(addr):
    """
      Implements LRU Caching logic 
      Reorders the cache on each addr access
    """
    pass
  
  def receive_load(msg=('load',addr, p), from_=s):
    """
      Receive load request from processor.
      Load address into cache and send back acknowledgement.
      Logic:
        Addr in 'M' state: supply data
        Addr in 'S' state: supply data
        Addr in 'I' state: 
          Other cache have data in 'M'/'S' state: 
            Gets the data from owner
            Goto 'S' state
          Else 
            Gets data from Memory.
            Goto 'S' State
    """
    pass
 
  def receive_load_forward(msg= ('loadF', addr), from_= p):
    """
      Receive load request from another caches.
      Logic:
        Addr in 'M' state: 
          Write-back to Memory
          Goto 'S' state
          Supply data
        
        Addr in 'S' state:
          Supply data

        Addr in 'I' state:
          reply not_found
    """
    pass

 
  def receive_store(msg=('store',addr, p), from_=s):
    """
      Received store request from processor.
      Store value into cache and send back acknowledgement.
      Logic:
        Addr in 'M' state: 
          Modify locally

        Addr in 'S' state: 
          Notify other caches to evict addr (tranx from 'S' to 'I')
          Modify Locally
          Goto to 'M' state 

        Addr in 'I' state:
          Get data from 'M'/'S' cache and notify to evict it.
          If not get from memory.
          Modify locally
          Goto to 'M' state
    """
    pass
  
  def receive_store_forward(msg=('storeF',addr, p), from_=s):
    """
      Received store forward request from other caches.
      Logic: 
        Addr in 'M' state: 
          Write-back to main memory.
          Goto 'I' state
          Supply data

        Addr in 'S' state:
          Goto 'I' state
          Supply Data

        Addr in 'I' state:
          Reply not_found
    """
    pass

  def tranx_M_to_S(addr):
    """
      Transition cache line from Modified to Shared state
    """
    pass

  def tranx_M_to_I(addr):
    """
      Transition cache line from Modified to Invalid state
    """
    pass

  def tranx_S_to_M(addr):
    """
      Transition cache line from Shared to Modified state
    """
    pass
  
  def tranx_S_to_I(addr):
    """
      Transition cache line from Shared to Invalid state
    """
    pass
  
  def tranx_I_to_M(addr):
    """
      Transition cache line from Invalid to Modified state
    """
    pass
  
  def tranx_I_to_S(addr):
    """
      Transition cache line from Invalid to Shared state
    """
    pass
  
  def receive_invalidate_block(msg= ('invalidate', addr), from_= p):
    """
      Invalidate addr if present in our cache.
      Goto 'I' state.
    """
    pass

  def receive_data_from_other_cache(msg=('found_in_cache')):
    """
      Received "found in cache" ack which basically denotes we have found 
      the requested addr in another cache and received the value from that cache.
    """
  
  def receive_snoop_caches(msg=('located_in_cache', addr)):
    """
      This logic is put in to handle the race condition when two caches are requesting for the same
      address in memory. When a cache receives this message, it means that the address it had requested the memory
      controller for has already been loaded by another cache and to snoop the other caches again to get
      the updated address. 
    """
    pass


  def receive_not_found_in_caches(msg=('not_found_in_cache')):
    """
      The requested address/data is not located in a cache. When the number of such messages received
      equals the number of other caches then its safe to assume that the address/data is not present in
      any of the other caches and we need to go to the memory controller 
    """
    pass

  def receive_data_from_memory(msg=('found_in_memory')):
    """
      We have received the requested address/data from the memory controller 
    """
    pass

  def receive_not_found_in_memory(msg=('not_found_in_memory')):
    """
      Address not found in memory, ideally should never happen 
    """
    pass 


  def receive_done(msg= ('done',)):
    """
      Exit the cache process on a done message 
    """
    pass


class MSI_PROTO_CTRL():
  """
    MSI Memory Controller Class: 
      - This class simulates the system bus and memory controller
      - keeps track of all addresses in the caches
      - A standalone process which serves memory requests from the caches
      - Inherits from the process class in DistAlgo
  """
  def setup(cache_protocol_objs):
    """
      Simulate a dictionary for tracking the addresses in the caches 
    """
    pass 

  def run():
    pass

  def receive_get_address(msg= ('get',addr), from_= p):
    """
    Retrieve the requested address from memory and send it back to the cache 
    """
    pass

  def receive_write_back_cache_block(msg= ('flush', addr)):
    """
    Flush the corresponding address back to memory 
    """
    pass


  def receive(msg= ('done',)):
    """
      Exit the memory controller process on a done message 
    """

class Processor():
    """
    Processor Class:
      - This class handles the processor logic
      - reads the execution trace one instruction at a time and executes it
      - All the load/store intstructions will be send to it's cache controller process
      - Inherits from the process class in DistAlgo
      - generic to all protocol implementations
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
    get_traces - generic to all protocol implementations
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
      main routine - generic to all protocol implementations:
        - spawn DistAlgo processes for n processors, n cache controllers and a
          memory controller 
        - get execution traces for each of the processors
    """
    nprocessors = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    proto_name = sys.argv[2] if len(sys.argv) > 2 else 'MSI'
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

