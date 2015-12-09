"""
MOESI cache coherence protocol implementation in DistAlgo
based on the transition diagram as explained in 8th Chapter of 
Sorin, Daniel J., Mark D. Hill, and David A. Wood. "A primer on memory consistency and 
cache coherence." Synthesis Lectures on Computer Architecture 6.3 (2011): 1-212.
To implement the protocol in DistAlgo, I used Directory Controller based implementation.

Note: The basic structural view for the protocol is same for our group and hence certain classes/methods
      which are common to all protocols is part of the intial setup. The other members of the group are
      Parag Gupta, Karthik Reddy, Garima Gehlot and Paul Mathew.
      Particularly for MOESI protocol, I worked with Karthik Reddy for MESI protocol implementation
      as MOESI is based on MESI protocol with an additional inclusion of 'Owner' state.
    
      Code is referenced in comments where it has been copied.

"""

import sys
import time
import os
addr = 'addr'
p='process'
s='process'
d='process'
val_rvd='value_received'
ack='ackowledgement'
data='data'
send='send'
monitor_obj='monitor'
value='value_received'
cache_id='cache_id'
lc='logical_clock'
cpu='cpu_time'
elapsed='elapsed_time'

#from termcolor import colored


ENOTSUPP = 2
CACHE_SIZE = 512

def get_proto_class(name):
  """
  Helper function to create class objects. Common to all protocol implementations.
  Reference: Parag Gupta. https://github.com/karthikbox/cache_coherence/tree/p_template/main.da
  """
  if name == "MOESI":
    return (eval("MOESI_Cache"), eval("MOESI_Directory"))
  else:
    exit(-ENOTSUPP)

"""
  MOESI Protocol class:
"""
class MOESI_Cache():
  """
  Each instance of this class represents Cache Controller of CACHE_SIZE corresponding to each Processor's local-cache.
  It contains the main logic for handling 5 states of the protocol and is responsible for the state 
  transitions for the cache data entries.
  The implementation is based on the state transitions as explained in the following mentioned book (Chapter 8).
  Reference : Sorin, Daniel J., Mark D. Hill, and David A. Wood. "A primer on memory consistency and 
  cache coherence." Synthesis Lectures on Computer Architecture 6.3 (2011): 1-212.
  Book doesn't contain the state diagram/machine for MOESI protocol, but understanding the MESI and MOSI protocol 
  clearly helped me to create a state machine for MOESI protocol together with some brain-storming sessions with 
  Karthik Reddy.
  """
  def setup(dir_ctrlr, other_caches, size,monitor_obj):
    self.memory = []
    self.pending_actions=[]
    self.current_state="READY"
    
  def run():
    while(1):
      await(len(self.pending_actions)>0 and current_state=="READY")
      #queue has some pending request and  state is READY
      #process request
      processRequest()

  def processRequest():
    """
    Handler function to take each pending request in the pending_actions queue and process them.
    """
    #deque request
    # (inst,addr,to_process,data)=pending_actions.pop(0)
    t=pending_actions.pop(0)
    inst=t[0]
    addr=t[1]
    to_process=t[2]
    
    if inst=='inv':
      perform_invalidation(addr,to_process)
    elif inst=='load':
      perform_load(addr,to_process)
    elif inst=='store':
      perform_store(addr,to_process,t[3])
    elif inst=='fwd_gets':
      perform_fwd_gets(addr,to_process)
    elif inst=='fwd_getm':
      perform_fwd_getm(addr,to_process,0)
    elif inst=='replace':
      perform_replacement(t[1])
    else:
      assert False, "invalid request = %r" %t[0]    
 

  def perform_replacement(t):
    """
    Cache Eviction requests handler function.
    """
    assert t[1]!='INVALID',"invalid state in replacement"
    # the current_state should be ready for eviction
    assert current_state=='READY', "invalid current_state in replacement"
    assert t==memory[len(memory)-1],"not a valid tuple for eviction tuple=%r"%t
    if t[1]=='SHARED':
      send(('PutS',t[0]), to=dir_ctrlr)
      send(('inc_msg_cnt', 1), to=monitor_obj)
      current_state='SHARED_INVALID_ACK'
      await(current_state=='INVALID' or current_state=='INVALID_INVALID_ACK')
      output('await passed with current_state %r'%current_state)
      if current_state=='INVALID':
        pass
      elif current_state=='INVALID_INVALID_ACK':
       await(current_state=='INVALID')
    elif t[1] in ['MODIFIED','EXCLUSIVE']:
      if t[1]=='MODIFIED':
        send(('PutM',t[0],t[2]), to=dir_ctrlr)
        current_state='MODIFIED_INVALID_ACK'
      elif t[1]=='EXCLUSIVE':
        send(('PutE',t[0]), to=dir_ctrlr)
        current_state='EXCLUSIVE_INVALID_ACK'
      send(('inc_msg_cnt', 1), to=monitor_obj)
      await(current_state=='INVALID' or current_state=='INVALID_INVALID_ACK' or current_state=='SHARED_INVALID_ACK')
      output('await passed with current_state %r'%current_state)
      if current_state=='INVALID':
        pass
      elif current_state=='INVALID_INVALID_ACK':
       await(current_state=='INVALID')
      elif current_state=='SHARED_INVALID_ACK':
       await(current_state=='INVALID')
    # remove this tuple at the end of replacement processing 
    output('removing t=%r from memory' %t)
    memory.remove(t)
    # assert that the size of cache is less than equal to CACHE_SIZE
    assert len(memory)<=CACHE_SIZE,'cache size corrupted, memory size=%r,CACHE_SIZE_PARAM=%r'%(len(memory),CACHE_SIZE) 
    current_state='READY'
         

  def perform_fwd_getm(addr,to_process,ack):
    """
    Fwd_GetM message handler function
    """
    output("in perform_fwd_getm begin: %r" %memory)
    res=[x for x in memory if x[0]==addr]
    assert len(res)>0,'address not in memory. Fwd_getM. addr_rvd=%r' %addr
    assert res[0][1]!='INVALID','address in INVALID state Fwd_getM.'
    assert res[0][1]!='SHARED','address in SHARED state Fwd_getM.'
    # get index of the cache memory tuple from memory
    # pop that tuple, insert new tuple at index again, new tuple's state changed to SHARED
    # mem tuple will not be at the head of the LRU
    index=memory.index(res[0])
    t=memory.pop(index)
    if t[1] in ['MODIFIED','EXCLUSIVE']:
      memory.insert(index,(t[0],'INVALID',t[2]))
    elif t[1] in ['MODIFIED_INVALID_ACK','EXCLUSIVE_INVALID_ACK']:
      memory.insert(index,(t[0],'INVALID_INVALID_ACK',t[2]))
      current_state='INVALID_INVALID_ACK'   
    elif t[1]=='OWNER':
      memory.insert(index,(t[0],'INVALID',t[2]))
    elif t[1]=='OWNER_MODIFIED_ACK_COUNT':
      current_state='INVALID_MODIFIED_ACK_DATA'
      memory.insert(index,(t[0],current_state,t[2]))
    elif t[1]=='OWNER_INVALID_ACK':
      memory.insert(index,(t[0],'INVALID_INVALID_ACK',t[2]))
      current_state='INVALID_INVALID_ACK'   
    else:
      memory.insert(index,t)
    
    # send data to req, set state to INVALID
    if res[0][1] in ['OWNER','OWNER_MODIFIED_ACK_COUNT']:
      send(('data_from_dir',ack,res[0][0],res[0][2]),to=to_process)
    else:
      send(('data_from_owner',res[0][0],res[0][2]),to=to_process)
    send(('inc_msg_cnt', 1), to=monitor_obj)
    output("in perform_fwd_getm : %r" %memory)


  def perform_fwd_gets(addr,to_process):
    """
    Fwd_GetS message handler function
    """
    output("in perform_fwd_getS begin: %r" %memory)
    res=[x for x in memory if x[0]==addr]
    assert len(res)>0,'address not in memory. Fwd_getS. addr_rvd=%r' %addr
    # get index of the cache memory tuple from memory
    # pop that tuple, insert new tuple at index again, 
    # new tuple's state changed to different states as per state transition diagram
    # mem tuple will not be at the head of the LRU
    index=memory.index(res[0])
    t=memory.pop(index)
    if t[1]=='MODIFIED':
      memory.insert(index,(t[0],'OWNER',t[2]))
    elif t[1]=='EXCLUSIVE':
      memory.insert(index,(t[0],'SHARED',t[2]))
    elif t[1]=='MODIFIED_INVALID_ACK':
      memory.insert(index,(t[0],'OWNER_INVALID_ACK',t[2]))
      current_state='OWNER_INVALID_ACK'
    elif t[1]=='EXCLUSIVE_INVALID_ACK':
      memory.insert(index,(t[0],'SHARED_INVALID_ACK',t[2]))
      current_state='SHARED_INVALID_ACK'
    else:
      memory.insert(index,t)
   # send data to req,
    send(('data_from_owner',res[0][0],res[0][2]),to=to_process)
    send(('inc_msg_cnt', 1), to=monitor_obj)
    output("in perform_fwd_gets : %r" %memory)

  def perform_invalidation(addr,to_process):
    """ Invalidate memory, send Inv_Ack to the caches."""
    res=[x for x in memory if x[0]==addr ]
    assert len(res)>0, 'addr_rcvd %r not in cache memory.' % addr
    output('invalidate function. addr_rcvd=%r, state=%r'%(addr,res[0][1]))
    send(('Inv_Ack',addr,to_process),to=to_process)
    send(('inc_msg_cnt', 1), to=monitor_obj)
    index=memory.index(res[0])
    t=memory.pop(index)
    if t[1] == 'SHARED':
      memory.insert(index,(t[0],'INVALID',t[2]))
    elif t[1] == 'SHARED_MODIFIED_ACK_DATA':
      memory.insert(index,(t[0],'INVALID_MODIFIED_ACK_DATA',t[2]))
      current_state='INVALID_MODIFIED_ACK_DATA'
    elif t[1] == 'SHARED_INVALID_ACK':
      memory.insert(index,(t[0],'INVALID_INVALID_ACK',t[2]))
      current_state='INVALID_INVALID_ACK'
    else:
      assert False,"invalid state in perform_invalidation"
    output("in perform_inv %r"%memory)

  def perform_load(addr,to_process):
    """
    Read request handler function for address 'addr'.
    If the cache entry is in Shared, Exclusive or Owner state, then just update the LRU and return the value present.
    If the cache entry is in Invalid, request the Directory Controller with GetS message.
    Depends on the E or S state in Dir Ctrl, entry will be converted to E or S state.
    """
    assert current_state=='READY', "state is not in READY state but in %r" % current_state
    # check state of addr in mem
    # tuple in memory is of the form (addr,status,value)
    res=[x for x in memory if x[0]==addr ]
    if len(res)>0:
      # if addr was present in memory
      assert res[0][0]==addr,"memory should have 'addr' but has %r" % res[0][0]
      if res[0][1]=='INVALID':
        # move this addr to the head of the memory list, update LRU
        update_lru_position_of(res[0])
        # make transition from I to S/E
        current_state='INVALID'
        move_I_to_SorE(addr)
      elif res[0][1] in ['SHARED','MODIFIED','EXCLUSIVE','OWNER']:
        # since state is ANY OF THE ABOVE, update lru and return the value
        update_lru_position_of(res[0])
      else:
        assert False, "invalid state %r" % res[0][2]
    else:
      # addr is not present in memory
      # add addr to memory.
      # add_to_memory, adds new item to the HEAD of memory list with an INVALID state
      add_to_memory((addr,'INVALID',0))
      current_state='INVALID'
      move_I_to_SorE(addr)
    # requested addr should be at the head of the memory
    assert memory[0][0]==addr, "newly loaded memory invariant failed for addr,state= %r, %r" % (memory[0][0],memory[0][1])
    assert memory[0][1]!='INVALID', "newly loaded memory invariant failed for addr,state= %r, %r" % (memory[0][0],memory[0][1])    
    current_state='READY'
    output("Sending Ack")
    send('completed', to=to_process)
    send(('inc_msg_cnt', 1), to=monitor_obj)
    output("in perform_load %r"%memory)
    output("value returned to processor =%r" % memory[0][2])
    output('after perform_load mem state=%r,lc=%r'%(memory,logical_clock()))
    send(('ins', 'load', addr, memory[0][2], self.id,logical_clock()),to=monitor_obj)
    send(('inc_msg_cnt', 1), to=monitor_obj)

  def perform_store(addr,to_process,data):
    """
    Write request handler for address 'addr' with value 'data'
    If the cache entry is in M state, just update the corresponding value and return.
    In all other states, request Dir Ctrl with GetM message. 
    Depending upon the cache entry states in  Directory Controller, following thing happens :-
    If in O state, invalidate all sharers and go to M state, return.
    If in E state, goto M.
    If in S state, invalidate all sharers and Owner, write data to Memory from Owner, goto M state.
    If in I state, request data from memory.
    Having M state guarantees this as the only copy in the system.
    """
    assert current_state=='READY', "state is not in READY state but in %r" % current_state
    #check the state of addr and act accordingly
    res=[x for x in memory if x[0]==addr ]
    if len(res)>0:
      # if address in present in cache
      if res[0][1]=='INVALID':
	      # move this addr to the head of the memory list, update LRU
        update_lru_position_of(res[0])
        # make transition from I to M
        current_state='INVALID'
        move_I_to_M(addr,data)
      elif res[0][1]=='SHARED':
      	# move to head, update LRU
        update_lru_position_of(res[0])
	      # make S to M transition
        current_state='SHARED'
        move_S_to_M(addr,data)
      elif res[0][1] =='MODIFIED':
        update_lru_position_of(res[0])
        # write data to memory
        tx=memory.pop(0)
        memory.insert(0,(tx[0],tx[1],data))
      elif res[0][1] =='OWNER':
        update_lru_position_of(res[0])
        current_state='OWNER'
        move_O_to_M(addr,data)
      elif res[0][1]=='EXCLUSIVE':
        update_lru_position_of(res[0])
        current_state='EXCLUSIVE'
        move_E_to_M(addr,data)
      else:
        assert False,"invalid state %r" %res[0][2]
    else:
      # addr is not in cache
      # add addr in cache
      # add_to_memory, adds new item to the HEAD of memory list with an INVALID state
      add_to_memory((addr,'INVALID',0))
      current_state='INVALID'
      move_I_to_M(addr,data)
    # requested addr should be at the head of the memory
    assert memory[0][0]==addr, "newly loaded memory invariant failed for addr,state= %r, %r" % (memory[0][0],memory[0][1])
    assert memory[0][1]=='MODIFIED', "newly loaded memory invariant failed for addr,state= %r, %r" % (memory[0][0],memory[0][1])    
    current_state='READY'
    output("Sending Ack")
    send('completed', to=to_process)
    output("in perform_store %r"%memory)
    output("value written in cache =%r" % memory[0][2])
    output('after perform_store mem state=%r, lc=%r'%(memory,logical_clock()))
    send(('ins', 'store', addr, memory[0][2], self.id,logical_clock()),to=monitor_obj)
  
  def move_I_to_SorE(addr):
    """ 
    We have some cases when transitioning from state 'I' based on the state of data in directory class.
    If State of same data in Directory is :-
      a) S : Directory state will remain in S state and I->S transition will occur in Cache.
      b) M : Directory will forward the load msg to Owner Cache of data entry, Owner state from M/E -> S and 
             it will reply to Dir and current Cache with "DatafromOwner" msg.
      c) O : Directory will forward the load msg to Owner Cache of data entry, Owner state from M/O -> O and 
             it will reply to Dir and current Cache with "DatafromOwner" msg.      
      d) I : Directory transition from I->E and and cache transition from I->E using the "ExclDatafromDir" msg from Directory Controller.
    """
    res=[x for x in memory if x[0]==addr]
    assert len(res)>0,"couldnt find addr in memory"
    assert memory[0][0]==addr,"current addr request should be at he head of memory LRU, but it isn not"
    assert memory[0][1]==current_state,'memory state corrupted'
    # addr_t,state_t,val_t=memory.pop(0)
    # memory.insert(0,(addr_t,'SHARED',val_t))
    # when in INVALID, on load, send getS to DC and goto ISD
    current_state='INVALID_SHARED_DATA'
    t=memory.pop(0)
    memory.insert(0,(t[0],current_state,t[2]))
    assert memory[0][0]==addr,"current addr request should be at he head of memory LRU, but it isn not"
    # inform DC
    send(('GetS',addr),to=dir_ctrlr)
    send(('inc_msg_cnt', 1), to=monitor_obj)
    # await till state changes
    await(current_state=='SHARED' or current_state=='EXCLUSIVE')
    assert memory[0][1]!='INVALID_SHARED_DATA','memory state corrupted'
    return
  
  def move_I_to_M(addr,data):
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
    res=[x for x in memory if x[0]==addr]
    assert len(res)>0,"couldnt find addr in memory"
    assert memory[0][0]==addr,"current addr request should be at he head of memory LRU, but it isn't not"
    assert memory[0][1]==current_state,'memory state corrupted'
    # addr_t,state_t,val_t=memory.pop(0)
    # memory.insert(0,(addr_t,'SHARED',val_t))
    # when in INVALID, on load, send getS to DC and goto ISD
    current_state='INVALID_MODIFIED_ACK_DATA'
    t=memory.pop(0)
    memory.insert(0,(t[0],current_state,t[2]))
    # inform DC
    send(('GetM',addr),to=dir_ctrlr)
    send(('inc_msg_cnt', 1), to=monitor_obj)
    # await till state changes
    move_IMAD_to_M(addr,data)
    t=memory.pop(0)
    assert t[1]==current_state,'memory state corrupted. ItoM'
    memory.insert(0,(t[0],current_state,data))


  def move_IMAD_to_M(addr,data):
    """
    Transient state handling which can occur in I->M and O->M transitions.
    """
    await(current_state=='INVALID_MODIFIED_ACK' or current_state=='MODIFIED')
    assert memory[0][1]!='INVALID_MODIFIED_ACK_DATA','memory state corrupted'
    if current_state=='MODIFIED':
      pass
    else:
      # in IMA state, wait till modified state(receive all acks)
      await(current_state=='MODIFIED')
    return

  def move_O_to_M(addr,data):
    """
    Cache entry will be in O state when Directory entry is in O state. 
    Transition to M state will cause Directory to send Inv request to all sharer caches.
    Sharer caches will make S->I transition and send Inv-Ack to requesting cache. Directory will also send AckCount msg to requesting cache 
    which will help the requesting cache to wait till AckCount.
    """
    res=[x for x in memory if x[0]==addr]
    assert len(res)>0,"couldnt find addr in memory, OtoM"
    assert memory[0][0]==addr,"current addr request should be at the head of memory LRU, but it isn't not, OtoM"
    assert memory[0][1]==current_state,'memory state corrupted, OtoM'
    current_state='OWNER_MODIFIED_ACK_COUNT'
    t=memory.pop(0)
    memory.insert(0,(t[0],current_state,t[2]))
    # inform DC
    send(('GetM',addr),to=dir_ctrlr)
    send(('inc_msg_cnt', 1), to=monitor_obj)
    # await till state changes
    await(current_state=='OWNER_MODIFIED_ACK' or current_state=='MODIFIED' or current_state=='INVALID_MODIFIED_ACK_DATA')
    assert memory[0][1]!='OWNER_MODIFIED_ACK_COUNT','memory state corrupted, OtoM'
    if current_state=='MODIFIED':
      pass
    elif current_state=='OWNER_MODIFIED_ACK':
      # in OMA state, wait till modified state(receive all acks)
      await(current_state=='MODIFIED')
    elif current_state=='INVALID_MODIFIED_ACK_DATA':
      move_IMAD_to_M(addr,data)
    else:
      assert False,'invalid state=%r in O to M' % current_state
    # write data
    t=memory.pop(0)
    assert t[1]==current_state,'memory state corrupted. OtoM'
    memory.insert(0,(t[0],current_state,data))
    current_state='READY'


  def move_S_to_M(addr,data):
    """
    Two Cases :-
      a) Directory transition from S->M with Inv broadcast to all the caches having the data entry. Caches will also 
         make transition from S->I and sends Inv-Ack to current Cache with "DatafromOwner" msg.
      b) Directory transition from O->M with Inv broadcast to all the caches having the data entry with S state and 
         fwd-GetM message to the previous owner of the data entry. Sharer caches will also  make transition from S->I and
         sends Inv-Ack and Owner cache will send DatafromDirAck0 message to requesting Cache.
    """
    res=[x for x in memory if x[0]==addr]
    assert len(res)>0,"couldnt find addr in memory"
    assert memory[0][0]==addr,"current addr request should be at he head of memory LRU, but it isn't not"
    assert memory[0][1]==current_state,'memory state corrupted'
    current_state='SHARED_MODIFIED_ACK_DATA'
    t=memory.pop(0)
    memory.insert(0,(t[0],current_state,t[2]))
    # inform DC
    send(('GetM',addr),to=dir_ctrlr)
    send(('inc_msg_cnt', 1), to=monitor_obj)
    # await till state changes
    await(current_state=='SHARED_MODIFIED_ACK' or current_state=='MODIFIED' or current_state=='INVALID_MODIFIED_ACK_DATA')
    # output('await passed, addr_rcvd=%r,state=%r'%(addr,current_state))
    assert memory[0][1]!='SHARED_MODIFIED_ACK_DATA','memory state corrupted'
    if current_state=='MODIFIED':
      pass
    elif current_state=='SHARED_MODIFIED_ACK':
      # in SMA state, wait till modified state(receive all acks)
      await(current_state=='MODIFIED')
    elif current_state=='INVALID_MODIFIED_ACK_DATA':
      move_IMAD_to_M(addr,data)
    else:
      assert False,'invalid state=%r in S to M' % current_state
    t=memory.pop(0)
    assert t[1]==current_state,'memory state corrupted. StoM'
    memory.insert(0,(t[0],current_state,data))
    current_state='READY'

  def move_E_to_M(addr,data):
    """ Simple transition to M state as both state guarantees only copy in the system """
    # goto MODIFIED state. no other actions
    res=[x for x in memory if x[0]==addr]
    assert len(res)>0,"couldnt find addr in memory"
    assert memory[0][0]==addr,"current addr request should be at he head of memory LRU, but it isn't not"
    assert memory[0][1]==current_state,'memory state corrupted'
    current_state='MODIFIED'
    t=memory.pop(0)
    memory.insert(0,(t[0],current_state,data))
    return
  


  def add_to_memory(t):
    """ 
    add tuple t to the head of cache memory list data structure. 
    format of tuple t = (address,state,value) 
    """
    # check size of memory, if size>= CACHE_SIZE, pop the last element and add the new tuple at the head
    # otherwise, insert at head directly
    if len(memory) >= CACHE_SIZE:
      popped=memory[len(memory)-1]
      # if state of popped is SHARED, MODIFIED, EXCLUSIVE
      if popped[1] in ['SHARED', 'MODIFIED', 'EXCLUSIVE']:
        # queue it at the head of pending request so that it will be the next instruction to be executed
        # any message requesting action on the evicted addr will be added to the end of the pending_actions queue,
        # so write back/replacement will happen before the we get to that previously mentioned message on that addr.
        pending_actions.insert(0,('replace',popped,None))
      else:
        # if state is INVALID, just remove the item from the memory(already done with pop), no action needed
        assert popped[1]=='INVALID', "state corrupted for memory item  %r" % popped
    # add tuple t to the head of og the memory list
    memory.insert(0,t)
    

  def update_lru_position_of(t):
    """ 
    LRU cache algorithm handling.
    Move tuple t to the head of the memory list.
    """
    # t should be present int the memory list
    assert t in memory, "tuple %r should exist in memory"
    memory.remove(t)
    memory.insert(0,t)


  def receive_exclusive_data_from_dir(msg=('exclusive_data_from_dir',addr,val_rvd), from_=s):
    """ 
    Exclusive data msg from the Directory to cache when none of the caches contain requesting data entry, hence I->E is done. 
    """
    if current_state=='INVALID_SHARED_DATA' and addr==memory[0][0]:
      # move to EXCLUSIVE state, update the state in memory for the address
      current_state='EXCLUSIVE'
      t=memory.pop(0)
      memory.insert(0,(t[0],current_state,val_rvd))
      assert t[1]=='INVALID_SHARED_DATA','memory state corrupted'
    else:
      assert False, "received out-of-state message. Should not happen. exclusive_data_from_dir.current_state=%r, addr_rcvd=%r, mem0_addr=%r,val_rcvd=%r" % (current_state,addr,memory[0][0],val_rvd)


  def receive_ackcount_from_dir(msg=('ackcount_from_dir',ack,addr), from_=s):
    """
    The Directory will send the Count of the acks that requesting cache should receive when O->M transition happens and 
    all sharers need to Invalidate their data entries
    """
    res = [ x for x in memory if x[0]==addr]
    assert len(res)>0,"couldnt find addr in memory"
    assert memory[0][0]==addr,"current addr request should be at he head of memory LRU, but it isn't not, ackcount_from_dir"
    assert res[0][1]==current_state,"memory state corrupted, current_state : %r and res[0][0] : %r" %(current_state,res[0][0])
    if current_state=='OWNER_MODIFIED_ACK_COUNT':
      current_state='OWNER_MODIFIED_ACK'
      t=memory.pop(0)
      memory.insert(0,(t[0],current_state,t[2],ack))
    else:
      assert False,'not a valid state for ackcount_from_dir : %r and mem : %r'%(current_state,res[0])

  def receive_data_from_dir(msg=('data_from_dir',ack,addr,val_rvd), from_=s):
    """
    Data from Directory Controller receive handler to receive data and ackcount in some state transitions.
    """
    if current_state=='INVALID_SHARED_DATA' and addr==memory[0][0] and ack==0:
      # move to SHARED state
      current_state='SHARED'
      t=memory.pop(0)
      memory.insert(0,(t[0],current_state,val_rvd))
    elif current_state=='INVALID_MODIFIED_ACK_DATA' and addr==memory[0][0] and ack==0:
      # move to MODIFIED state
      current_state='MODIFIED'
      t=memory.pop(0)
      memory.insert(0,(t[0],current_state,val_rvd))
      assert t[1]=='INVALID_MODIFIED_ACK_DATA','memory state corrupted. data_from_dir.  IMAD'
    elif current_state=='INVALID_MODIFIED_ACK_DATA' and addr==memory[0][0] and ack>0:
      # move to INVALID_MODIFIED_ACK state
      current_state='INVALID_MODIFIED_ACK'
      t=memory.pop(0)
      memory.insert(0,(t[0],current_state,val_rvd,ack))
      assert t[1]=='INVALID_MODIFIED_ACK_DATA','memory state corrupted.data_from_dir. IMA'
    elif current_state=='SHARED_MODIFIED_ACK_DATA' and addr==memory[0][0] and ack==0:
      # move to MODIFIED state
      current_state='MODIFIED'
      t=memory.pop(0)
      memory.insert(0,(t[0],current_state,val_rvd))
      assert t[1]=='SHARED_MODIFIED_ACK_DATA','memory state corrupted. data_from_dir.  SMAD'
    elif current_state=='SHARED_MODIFIED_ACK_DATA' and addr==memory[0][0] and ack>0:
      # move to SHARED_MODIFIED_ACK state
      current_state='SHARED_MODIFIED_ACK'
      t=memory.pop(0)
      memory.insert(0,(t[0],current_state,val_rvd,ack))
      assert t[1]=='SHARED_MODIFIED_ACK_DATA','memory state corrupted.data_from_dir. SMA'
    else:
      assert False, "received out-of-state message. Should not happen. data_from_dir. CURRENT_STATE=%r,ack_count=%r, addr rcvd=%r" % (current_state,ack,addr)

  def receive_data_from_owner(msg=('data_from_owner',addr,val_rvd), from_=s):
    """
    Receive handler for data message from the other caches which are currently the having the data entry in E or M state.
    This message is received in response I->S and S->M state transitions.
    """
    if current_state=='INVALID_SHARED_DATA' and addr==memory[0][0]:
      # move to SHARED state
      current_state='SHARED'
      t=memory.pop(0)
      memory.insert(0,(t[0],current_state,val_rvd))
      assert t[1]=='INVALID_SHARED_DATA','memory state corrupted.data_from_owner.ISD'
    elif current_state=='INVALID_MODIFIED_ACK_DATA' and addr==memory[0][0]:
      # move to MODIFIED state
      current_state='MODIFIED'
      t=memory.pop(0)
      memory.insert(0,(t[0],current_state,val_rvd))
      assert t[1]=='INVALID_MODIFIED_ACK_DATA','memory state corrupted. data_from_owner. IMAD'
    elif current_state=='SHARED_MODIFIED_ACK_DATA' and addr==memory[0][0]:
      # move to MODIFIED state
      current_state='MODIFIED'
      t=memory.pop(0)
      memory.insert(0,(t[0],current_state,val_rvd))
      assert t[1]=='SHARED_MODIFIED_ACK_DATA','memory state corrupted. data_from_owner. SMAD'
    else:
      assert False, "received out-of-state message. Should not happen. data_from_owner. current_state %r, addr %r" %(current_state,addr)

  def receive_PutAck(msg=('Put_Ack',addr,p), from_=s):
    """
    Write to memory message receive handler.
    This message is received when data is evicted from cache to be written to memory in case of evictions while cache entry is in any state.
    """
    res = [ x for x in memory if x==addr]
    assert len(res)>0, "addr not in cache memory %r" %addr
    assert res[1]!='INVALID', "memory state not valid for put-ack"

    if current_state in ['SHARED_INVALID_ACK','INVALID_INVALID_ACK','MODIFIED_INVALID_ACK','EXCLUSIVE_INVALID_ACK','OWNER_INVALID_ACK']:
      index=memory.index(res[0])
      t=memory.pop(index)
      memory.insert(index,(t[0],'INVALID',t[2]))
      current_state='INVALID'
    else:
      assert False,'invalid state for handling put-ack.'

  
  def receive_InvAck(msg=('Inv_Ack',addr,p), from_=s):
    """
    The sharer of a cache entry will send invalidate ack to requesting cache for it to make successful I/S/O->M transition
    """
    # state has to be in INVALID_MODIFIED_ACK
    if current_state=='INVALID_MODIFIED_ACK' and addr==memory[0][0]:
      t=memory.pop(0)
      assert type(t[3]) is int, 'ack_count corrupted'
      assert t[3] >0,'ack count corrupted <=0'
      ack_cnt=t[3]
      ack_cnt-=1      
      if ack_cnt==0:
        current_state='MODIFIED'
      memory.insert(0,(t[0],current_state,t[1],ack_cnt))
    elif current_state=='INVALID_MODIFIED_ACK_DATA' and addr==memory[0][0]:
      ## can occur in the case where cache entry is in S/I->M state and directory is in O->M state.
      # wait till date from owner (faked data_from_dir is arrived, which tells us ack_cnt) 
      await(current_state=='INVALID_MODIFIED_ACK')
      t=memory.pop(0)
      assert type(t[3]) is int, 'ack_count corrupted'
      assert t[3]>0,'ack count corrupted <=0'
      ack_cnt=t[3]
      ack_cnt-=1      
      if ack_cnt==0:
        current_state='MODIFIED'
      memory.insert(0,(t[0],current_state,t[1],ack_cnt))
    
    elif current_state=='SHARED_MODIFIED_ACK' and addr==memory[0][0]:
      t=memory.pop(0)
      assert type(t[3]) is int, 'ack_count corrupted'
      assert t[3] >0,'ack count corrupted <=0'
      ack_cnt=t[3]
      ack_cnt-=1
      if ack_cnt==0:
        current_state='MODIFIED'
      memory.insert(0,(t[0],current_state,t[2],ack_cnt))
    elif current_state=='SHARED_MODIFIED_ACK_DATA' and addr==memory[0][0]:
      assert False,'received inv ack when in SMAD state'
    elif current_state=='OWNER_MODIFIED_ACK' and addr==memory[0][0]:
      t=memory.pop(0)
      assert type(t[3]) is int, 'ack_count corrupted, OMA'
      assert t[3]>0,'ack count corrupted <=0'
      ack_cnt=t[3]
      ack_cnt-=1
      if ack_cnt==0:
        current_state='MODIFIED'
      memory.insert(0,(t[0],current_state,t[2],ack_cnt))
    elif current_state=='OWNER_MODIFIED_ACK_COUNT' and addr==memory[0][0]:
      assert False,'received inv ack when in OMAC state'
    else:
      assert False,'received out-of-state message. Should not happen. Inv-ACK. addr_rcvd=%r, head_memory=%r, state=%r'%(addr,memory[0],memory[0][1])


  def receive_Inv(msg=('Inv',addr,p), from_=s):
    """ Invalidating request message from Directory Controller """
    res=[x for x in memory if x[0]==addr]
    assert len(res)>0,'addr_rcvd=%r not in memory'%addr
    if(res[0][1]=='SHARED'):
      perform_invalidation(addr,p)
    elif(res[0][1]=='SHARED_MODIFIED_ACK_DATA'):
      perform_invalidation(addr,p)
    elif(res[0][1]=='SHARED_INVALID_ACK'):
      perform_invalidation(addr,p)
    else:
      pending_actions.append(('inv',addr,p))
    

  def receive_FwdGetS(msg=('Fwd_GetS',addr,p), from_=s):
    """ Receive handler of fwd-gets messages from the directory controller """
    res=[x for x in memory if x[0]==addr]
    if res[0][1] in ['EXCLUSIVE','MODIFIED','EXCLUSIVE_INVALID_ACK','MODIFIED_INVALID_ACK','OWNER','OWNER_MODIFIED_ACK_COUNT','OWNER_MODIFIED_ACK']:
      perform_fwd_gets(addr,p)
    else:
      pending_actions.append(('fwd_gets',addr,p))

  def receive_FwdGetM(msg=('Fwd_GetM',addr,p), from_=s):
    """ Receive handler of fwd-getm messages from the directory controller """
    res=[x for x in memory if x[0]==addr]
    if res[0][1] in ['EXCLUSIVE','MODIFIED','EXCLUSIVE_INVALID_ACK','MODIFIED_INVALID_ACK','OWNER_MODIFIED_ACK_COUNT']:
      perform_fwd_getm(addr,p,0)
    else:
      pending_actions.append(('fwd_getm',addr,p))

  def receive_FwdGetM_with_ack(msg=('Fwd_GetM',addr,p,ack), from_=s):
    """ 
    Receive handler of fwd-getm messages with acknowledgement from the directory controller 
    This receive handler is created to handler a special case in MOESI protocol when Owner cache needs to forward the ack
    received from the directory controller to the requesting cache.
    """
    res=[x for x in memory if x[0]==addr]
    if res[0][1] in ['OWNER','OWNER_MODIFIED_ACK_COUNT']:
      perform_fwd_getm(addr,p,ack)

  def receive_load(msg=('load',addr, p), from_=s):
    """ Receive handler for the load requests from the Processor class. """      
    self.pending_actions.append(('load',addr, s))
    output("Received LOAD request for addr %s" % addr)
 
  def receive_store(msg=('store',addr, p, data), from_=s):
    """ Receive handler for the store requests from the Processor class. """      
    self.pending_actions.append(('store',addr, s, data))
    output("Received STORE request for addr %s" % addr);
 
  def receive(msg= ('done',)):
    """ Receive handler to terminate this cache controller process whenever this message is received """
    print("Cache Exiting\n")
    exit()

class MOESI_Directory():
  """
  MOESI Directory Controller class.
  This class simulates the centralized directory between caches and is responsible for managing data in the memory.
  This is a single process which handles all access requests from all the processor caches.
  It keeps track of all data entries and their states corresponding to memory.
  Reference : 
  Sorin, Daniel J., Mark D. Hill, and David A. Wood. "A primer on memory consistency and 
  cache coherence." Synthesis Lectures on Computer Architecture 6.3 (2011): 1-212.
  Together implemented with Karthik Reddy. So design and some APIs are same with him (with all the necessary changes required for MOESI protocol):-
  https://github.com/karthikbox/cache_coherence/blob/mesi_implementation/main.da
  """
  def setup(cache_protocol_objs,monitor_obj):
    self.pending_actions=[]
    self.memory = dict()
    memory['0x11111114']=['INVALID',None,[],212]

  def run():
    while(1):
      await(len(self.pending_actions)>0)
      #queue has some pending request and  state is READY
      #process request
      processRequest()

  
  def processRequest():
    """
    Handler function to take each pending request in the pending_actions queue and process them.
    """
    # deque request
    t=pending_actions.pop(0)
    #possible instructions are : loads,stores, invlalidate
    # pending_actions tuple format : (inst,addr,to_process,data)
    # check if addr is in memory, else add it to memory with INVALID state
    if(t[1] not in memory):
      memory[t[1]]=['INVALID',self.id,[],555]

    if(t[0]=='GetS'):
      perform_getS(t[1],t[2])
    elif(t[0]=='GetM'):
      perform_getM(t[1],t[2])
    elif(t[0]=='PutS'):
      perform_putS(t[1],t[2])
    elif(t[0]=='PutM'):
      perform_putM(t[1],t[2],t[3])
    elif(t[0]=='PutE'):
      perform_putE(t[1],t[2])
    elif(t[0]=='PutO'):
      perform_putO(t[1],t[2],t[3])
    else:
      assert False,'invalid request in pending actions queue'



  def perform_putS(addr,to_process):
    """ PutS message handler function """
    # remove req from sharers, send Put-Ack to req, if no sharer after removing this, 
    # go to INVALID state, otherwise S->S.
    assert to_process in memory[addr][2],'to_process not in sharers list'
    memory[addr][2].remove(to_process)
    if(len(memory[addr][2])==0):
      memory[addr][0]='INVALID'
    send(('Put_Ack',addr,self.id),to=to_process)
    send(('inc_msg_cnt', 1), to=monitor_obj)

  def perform_putO(addr,to_process,data):
    """ PutO message handler function """
    assert memory[addr]=='OWNER','memory state corrupted, perform_putO'
    # copy data to memory
    # send put-ack to req
    # clear owner
    # make state INVALID if no sharers OR  SHARED is sharers are there
    memory[addr][3]=data
    memory[addr][1]=None
    if len(memory[addr][2])>0:
      memory[addr][0]='SHARED'
    else:
      memory[addr][0]='INVALID'
    send(('Put_Ack',addr,self.id),to=to_process)
    send(('inc_msg_cnt', 1), to=monitor_obj)

  def perform_putM(addr,to_process,data):
    """ PutM message handler function """
    assert memory[addr]=='MODIFIED','memory state corrupted, perform_putM'
    time.sleep(0.1)
    # copy data to memorry
    # send put-ack to req
    # clear owner
    # make state INVALID
    memory[addr][3]=data
    memory[addr][1]=None
    memory[addr][0]='INVALID'
    send(('Put_Ack',addr,self.id),to=to_process)
    send(('inc_msg_cnt', 1), to=monitor_obj)

  def perform_putE(addr,to_process):
    """ PutE message handler function """
    assert memory[addr]=='EXCLUSIVE','memory state corrupted'
    # send put-ack to req
    # clear owner
    # make state INVALID
    memory[addr][1]=None
    memory[addr][0]='INVALID'
    send(('Put_Ack',addr,self.id),to=to_process)
    send(('inc_msg_cnt', 1), to=monitor_obj) 

  def perform_getS(addr,to_process):
    """ 
    getS message handler function 
    Following cases are there depending upon cache entry state in Directory Controller :-
    I : Data is read from memory (100ms delay is added to simulate this behaviour)
        And returned back to requesting cache with exclusive_data_from_dir message, I->E state changed.
    S : Data is returned to requesting cache using data_from_dir message.
    E : fwd-gets message is sent to exclusive owner and state is changed to shared.
    M : fwd-gets message is sent to owner cache and state is changed to owner.
    O : fwd-gets message is sent to owner cache.
    """
    # key -value : memory_addr, [state,owner,[sharers],value]
    assert addr in memory, "address %r not in memory" % addr
    if memory[addr][0]=='INVALID':
      time.sleep(0.1)
      # send exclusive data to req, 
      # set owner to req, 
      # set state to exclusive
      send(('exclusive_data_from_dir',addr,memory[addr][3]),to=to_process)
      memory[addr][1]=to_process
      memory[addr][0]="EXCLUSIVE"
    elif memory[addr][0]=='SHARED':
      # send data to req with ack=0, 
      # add req to sharers list, 
      # no change to state
      memory[addr][2].append(to_process)
      send(('data_from_dir',0,addr,memory[addr][3]),to=to_process)
    elif memory[addr][0]=='EXCLUSIVE':
      # forward GetS to owner, 
      # add req to sharers
      # make state as OWNER
      send(('Fwd_GetS',addr,to_process),to=memory[addr][1])
      memory[addr][2].append(to_process)
      memory[addr][2].append(memory[addr][1])
      memory[addr][0]='SHARED'
      memory[addr][1]=[]
      #await(memory[addr][0]=='SHARED')
    elif memory[addr][0]=='MODIFIED':
      # forward getS to owner, 
      # add req to sharers, 
      # make state as OWNER
      send(('Fwd_GetS',addr,to_process),to=memory[addr][1])
      memory[addr][2].append(to_process)
      memory[addr][0]='OWNER'
    elif memory[addr][0]=='OWNER':
      # forward getS to owner,
      # add req to sharers, 
      send(('Fwd_GetS',addr,to_process),to=memory[addr][1])
      memory[addr][2].append(to_process)
    else:
      assert False, 'invalid memory state. getS'
    send(('inc_msg_cnt', 1), to=monitor_obj)


  def perform_getM(addr,to_process):
    """ 
    getM message handler function 
    Following cases are there depending upon cache entry state in Directory Controller :-
    I : Data is written to memory (100ms delay is added to simulate this behaviour)
        And data_from_dir message is returned back to requesting cache, I->M state changed.
    S : Data is returned to requesting cache using data_from_dir message and length of sharers as ack.
        Inv message is sent to all sharers, state change S->M.
    E : fwd-getm message is sent to exclusive owner and state is changed to M.
    M : fwd-getm message is sent to owner cache and owner is changed to requesting cache.
    O : fwd-gets message is sent to owner cache with ack count, inv messages to all sharers
        and state change to M.
    """
   # key -value : memory_addr, [state,owner,[sharers],value]
    assert addr in memory, "address %r not in memory, current memory state %r " % (addr,memory[addr][0]) 
    output("addr_rcvd=%r, state in memory=%r"%(addr,memory[addr][0]))
    if memory[addr][0]=='INVALID':
      # send data_from_dir with ack=0 to req, 
      # set owner to req, i
      # set state MODIFIED
      time.sleep(0.1)
      send(('data_from_dir',0,addr,memory[addr][3]),to=to_process)
      send(('inc_msg_cnt', 1), to=monitor_obj)
      memory[addr][1]=to_process
      memory[addr][0]="MODIFIED"
    elif memory[addr][0]=='SHARED':
      # send data to req with ack>0,send INV to sharers
      # clear shareers, set owner to request, set state to MODIFIED
      # check if req is part of the sharers list
      # if so, remove to_process from sharers list      
      if to_process in memory[addr][2]:
        memory[addr][2].remove(to_process)
      send(('data_from_dir',len(memory[addr][2]),addr,memory[addr][3]),to=to_process)
      send(('inc_msg_cnt', 1), to=monitor_obj)
      output('%r sending inv message to %r (in SHARED)'%(to_process,memory[addr][2]))
      send(('Inv',addr,to_process),to={x for x in memory[addr][2]})
      send(('inc_msg_cnt', len(memory[addr][2])), to=monitor_obj)
      memory[addr][2]=[]
      memory[addr][1]=to_process
      memory[addr][0]='MODIFIED'
    elif memory[addr][0]=='EXCLUSIVE':
      # forrward getM to owner, 
      # set owner to req
      # change state to MODIFIED
      send(('Fwd_GetM',addr,to_process),to=memory[addr][1])
      send(('inc_msg_cnt', 1), to=monitor_obj)
      memory[addr][1]=to_process
      memory[addr][0]='MODIFIED'
    elif memory[addr][0]=='MODIFIED':
      # forward getM to owner, 
      # set owner to req
      send(('Fwd_GetM',addr,to_process),to=memory[addr][1])
      send(('inc_msg_cnt', 1), to=monitor_obj)
      memory[addr][1]=to_process
    elif memory[addr][0]=='OWNER':
      #in case owner is the requester
        # send ackcount to req, send inv to sharers,
        # clear sharers, set state to MODIFIED
      #else (in case owner is not the requester)
        # fwd-getm to owner, 
        # send inv to sharers,
        # set owner to req, clear sharers, 
        # send ackcount to req, set state to MODIFIED
      if to_process!=memory[addr][1]:
        if to_process in memory[addr][2]:
          memory[addr][2].remove(to_process)
        send(('Fwd_GetM',addr,to_process,len(memory[addr][2])),to=memory[addr][1])
        send(('inc_msg_cnt', 1), to=monitor_obj)
        memory[addr][1]=to_process
      elif to_process==memory[addr][1]:
        send(('ackcount_from_dir',len(memory[addr][2]),addr),to=to_process)
        send(('inc_msg_cnt', 1), to=monitor_obj)
      output('%r sending inv message to %r (in OWNER)'%(to_process,memory[addr][2]))
      send(('Inv',addr,to_process),to={x for x in memory[addr][2]})
      send(('inc_msg_cnt', len(memory[addr][2])), to=monitor_obj)
      memory[addr][2]=[]
      memory[addr][0]='MODIFIED'
    else:
      assert False, 'invalid memory state for addr_rcvd=%r,state in memory=%r'%(addr,memory[addr][0])


  def receive_GetS(msg=('GetS',addr), from_=p):
    """ Read Request from caches """
    pending_actions.append(('GetS',addr,p))

  def receive_GetM(msg= ('GetM',addr), from_= p):
    """ Write Request from caches """
    pending_actions.append(('GetM',addr,p))

  def receive_PutS(msg= ('PutS',addr), from_= p):
    """ Write-back Request from caches when cache needs to evict this data entry (no write to memory) which can make S->S/I transition.
    Put it in pending queue.
    """
    pending_actions.append(('PutS',addr,p))

  def receive_PutM(msg= ('PutM',addr,data), from_= p):
    """ Write-back Request with data from caches when cache needs to evict this data entry (no write to memory). Will transition from M->O state
    Put it in pending queue.
    """
    pending_actions.append(('PutM',addr,p,data))

  def receive_PutE(msg= ('PutE',addr), from_= p):
    """ Write-back Request from caches when cache needs to evict this data entry (no write to memory)
    Put it in pending queue
    """
    pending_actions.append(('PutE',addr,p))

  def receive_PutO(msg= ('PutO',addr,data), from_= p):
    """ Write-back Request with data from caches when cache needs to evict this data entry (write to memory) which can make S->S/I transition.
    Put it in pending queue
    """
    pending_actions.append(('PutO',addr,p,data))

  def receive(msg= ('done',)):
    print("CTRL Exiting\n")
    exit()

class Processor():
    """
  Processor Class:
  This class simulates the read/write requests of each processor.
  Implementation wise, it makes read/write requests to cache controller one at a time.
  Since this is a part of common platform on which the team will do the evaluations, copied it from following :-
  Reference: Parag Gupta. https://github.com/karthikbox/cache_coherence/tree/p_template/main.da
    """
    def setup(trace, protocol,monitor_obj):
      self.keep_waiting = False
    
    def execute(inst):
      """
      Each load/store requests are made to cache controller one at a time using this function. 
      """
      if inst[0] == "r":
        send(('load',inst[1] , self.id), to=protocol)
        send(('inc_msg_cnt', 1), to=monitor_obj) 
      elif inst[0] == "w":
        send(('store', inst[1], self.id, inst[2]), to=protocol)
        send(('inc_msg_cnt', 1), to=monitor_obj) 
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

def get_traces(trace_dir, nprocs):
  """
  Helper function to read trace files from the trace directory. Common to all the protocol implementations.
  Implemented together with Karthik Reddy.
  """
  trace=[]
  for i in range(nprocs):
    trace_filename='p'+str(i)+'.trace'
    f=open(os.path.join(trace_dir,trace_filename))
    insts=[]
    for line in f:
      insts.append(line.split())
    trace.append(insts)
  return trace  

class Monitor():
  """
    Monitor Class:
    Used for correctness checking and performance analysis measurement.
    Correntness checking : Instructions list will queue the result of all access requests to all caches.
                           It will give us picture of how values are getting accessed/modified. 
                           We are able to verify sequential consistency using this.
    Performance analysis : (i)  Total # of messages used for communication
                           (ii) Elapsed time taken by the protocol
                           (iii)CPU time taken by the protocol

    This part is common to all the protocol implementations. 
    Copied it from following reference with some changes to make colored output :-
    Reference: Paul Mathew. https://github.com/karthikbox/cache_coherence/blob/mi_protocol/mi_protocol.da
  """
  def setup():
    self.instructions = []
    self.total_msgs = 0
    self.cpu_time = 0
    self.elapsed_time = 0
   
  def receive_ins(msg= ('ins', type, addr, value, cache_id,lc)):
    instructions.append((type, addr, value, cache_id,lc))

  def receive_inc_msg_cnt(msg= ('inc_msg_cnt', value)):
    """
    Receive handler for total message count.
    Used to calculate total number of messages used in the protocol for cache coherence.
    """
    total_msgs = total_msgs + value

  def receive_time_taken(msg= ('time_taken', cpu, elapsed)):
    """
    Receive handler to measure CPU and ELAPSED time used by the protocol
    for a given number of Processors and given traces
    """
    cpu_time = cpu
    elapsed_time = elapsed 

  def run():
    await(False)
    
  def receive(msg= ('done',)):
    """
    When all the Processor class are done with processing load/store request, 
    this handler is used to print all the correctness checking invariants and proformance benchmarking numbers.
    """
    print(colored(("===Load/Store global order==="),'blue'))
    for ins in instructions:
      if ins[0]=='load':
        print(ins[3], " : ", ins[0],"", ins[1]," ", ins[2])
      else:
        print(ins[3], " : ", ins[0], ins[1]," ", ins[2])
    print()
    print(colored(("===Benchmarks==="),'blue'))
    print(colored(("Total Message Count:", total_msgs),'red'))
    print(colored(("Elapsed time:", elapsed_time),'green'))
    print(colored(("CPU time:", cpu_time),'cyan'))
    exit()

def main():
    """
  Main driver function to simulate the running behaviour of cache coherence protocol with 
  given number of processors, protocol name and trace file path.
  Command should be passed in the following way :
  dar main.da <num_processors> <protocol_name> <tracefile_path>
  where n - # of processors ( local-caches)
        Protocol - Protocol Name (MI/MSI/MESI/MOSI/MOESI)
        Path - Path of the trace file to run with
  Since this is a part of common platform on which the team will do the evaluations, copied it from following :-
  Reference: Parag Gupta. https://github.com/karthikbox/cache_coherence/tree/p_template/main.da
    """
    nprocessors = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    proto_name = sys.argv[2] if len(sys.argv) > 2 else 'MOESI'
    trace_dir = sys.argv[3] if len(sys.argv) > 3 else './traces'

    config(channel= 'fifo', clock= 'Lamport')
    
    start_cpu_time = time.process_time()
    start_elapsed_time = time.perf_counter()
    
    trace = get_traces(trace_dir,nprocessors)
    print(trace)
    Proto_cache, Proto_ctrl = get_proto_class(proto_name)
    
    print('-----START-----')
    ## Start monitor process
    monitor_obj = new(Monitor, num=1)
    setup(monitor_obj, ())
    start(monitor_obj)

    
    ## Initialize protocol objs for caches and controller
    mem_ctrl_protocol_obj = new(Proto_ctrl, num=1)
    protocol_objs = new(Proto_cache, num=nprocessors)
    
    ## Setup Protocol for ctrller
    setup(mem_ctrl_protocol_obj, (protocol_objs,monitor_obj))
    start(mem_ctrl_protocol_obj)

    ## Setup Protocols for caches
    for proto_obj in protocol_objs:
      setup(proto_obj, (mem_ctrl_protocol_obj, protocol_objs - {proto_obj}, CACHE_SIZE,monitor_obj))
      start(proto_obj)

    ## Setup Processors
    processors = new(Processor, num= nprocessors)
    
    ## temp lists for iterating
    processors_list = list(processors)
    protocol_objs_list = list(protocol_objs)
    for i in range(nprocessors): 
      setup(processors_list[i], (trace[i], protocol_objs_list[i],monitor_obj))
    
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

    end_cpu_time = time.process_time()
    end_elapsed_time = time.perf_counter()

    da.send(('time_taken', end_cpu_time-start_cpu_time, end_elapsed_time-start_elapsed_time), to= monitor_obj)
    da.send(('done',), to= monitor_obj)
    for monitor in monitor_obj:
      monitor.join()
    print('-----END-----')

