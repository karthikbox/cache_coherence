
import da
PatternExpr_0 = da.pat.TuplePattern([da.pat.ConstantPattern('get'), da.pat.FreePattern('addr')])
PatternExpr_1 = da.pat.FreePattern('p')
PatternExpr_2 = da.pat.TuplePattern([da.pat.ConstantPattern('invalidate'), da.pat.FreePattern('addr')])
PatternExpr_3 = da.pat.FreePattern('p')
PatternExpr_4 = da.pat.TuplePattern([da.pat.ConstantPattern('found_in_cache'), da.pat.FreePattern('addr'), da.pat.FreePattern('value')])
PatternExpr_5 = da.pat.TuplePattern([da.pat.ConstantPattern('get_from_cache'), da.pat.FreePattern('addr')])
PatternExpr_6 = da.pat.TuplePattern([da.pat.ConstantPattern('not_found_in_cache'), da.pat.FreePattern('addr')])
PatternExpr_7 = da.pat.TuplePattern([da.pat.ConstantPattern('found_in_memory'), da.pat.FreePattern('addr'), da.pat.FreePattern('value')])
PatternExpr_8 = da.pat.ConstantPattern('not_found_in_memory')
PatternExpr_9 = da.pat.TuplePattern([da.pat.ConstantPattern('load'), da.pat.FreePattern('addr')])
PatternExpr_10 = da.pat.FreePattern('s')
PatternExpr_11 = da.pat.TuplePattern([da.pat.ConstantPattern('store'), da.pat.FreePattern('addr'), da.pat.FreePattern('value')])
PatternExpr_12 = da.pat.FreePattern('s')
PatternExpr_13 = da.pat.TuplePattern([da.pat.ConstantPattern('done')])
PatternExpr_14 = da.pat.TuplePattern([da.pat.ConstantPattern('get'), da.pat.FreePattern('addr')])
PatternExpr_15 = da.pat.FreePattern('p')
PatternExpr_16 = da.pat.TuplePattern([da.pat.ConstantPattern('flush'), da.pat.FreePattern('addr'), da.pat.FreePattern('value')])
PatternExpr_17 = da.pat.TuplePattern([da.pat.ConstantPattern('done')])
PatternExpr_18 = da.pat.TuplePattern([da.pat.ConstantPattern('completed_load'), da.pat.FreePattern('value')])
PatternExpr_19 = da.pat.ConstantPattern('completed_store')
PatternExpr_20 = da.pat.TuplePattern([da.pat.ConstantPattern('ins'), da.pat.FreePattern('type'), da.pat.FreePattern('addr'), da.pat.FreePattern('value'), da.pat.FreePattern('cache_id')])
PatternExpr_21 = da.pat.TuplePattern([da.pat.ConstantPattern('inc_msg_cnt'), da.pat.FreePattern('value')])
PatternExpr_22 = da.pat.TuplePattern([da.pat.ConstantPattern('time_taken'), da.pat.FreePattern('cpu'), da.pat.FreePattern('elapsed')])
PatternExpr_23 = da.pat.TuplePattern([da.pat.ConstantPattern('done')])
import sys
import time
import os
ENOTSUPP = 2
CACHE_SIZE = 512

def get_proto_class(name):
    '\n        return the corresponding protocol class name and controller name\n        generic to all protocol implementations\n        Reference : Parag Gupta (https://github.com/karthikbox/cache_coherence/tree/p_template/main.da)\n  '
    if (name == 'MI'):
        return (eval('MI_PROTO_CACHE'), eval('MI_PROTO_CTRL'))
    else:
        self.exit((- ENOTSUPP))

class MI_PROTO_CACHE(da.DistProcess):

    def __init__(self, parent, initq, channel, props):
        super().__init__(parent, initq, channel, props)
        self._events.extend([da.pat.EventPattern(da.pat.ReceivedEvent, '_MI_PROTO_CACHEReceivedEvent_0', PatternExpr_0, sources=[PatternExpr_1], destinations=None, timestamps=None, record_history=None, handlers=[self._MI_PROTO_CACHE_handler_0]), da.pat.EventPattern(da.pat.ReceivedEvent, '_MI_PROTO_CACHEReceivedEvent_1', PatternExpr_2, sources=[PatternExpr_3], destinations=None, timestamps=None, record_history=None, handlers=[self._MI_PROTO_CACHE_handler_1]), da.pat.EventPattern(da.pat.ReceivedEvent, '_MI_PROTO_CACHEReceivedEvent_2', PatternExpr_4, sources=None, destinations=None, timestamps=None, record_history=None, handlers=[self._MI_PROTO_CACHE_handler_2]), da.pat.EventPattern(da.pat.ReceivedEvent, '_MI_PROTO_CACHEReceivedEvent_3', PatternExpr_5, sources=None, destinations=None, timestamps=None, record_history=None, handlers=[self._MI_PROTO_CACHE_handler_3]), da.pat.EventPattern(da.pat.ReceivedEvent, '_MI_PROTO_CACHEReceivedEvent_4', PatternExpr_6, sources=None, destinations=None, timestamps=None, record_history=None, handlers=[self._MI_PROTO_CACHE_handler_4]), da.pat.EventPattern(da.pat.ReceivedEvent, '_MI_PROTO_CACHEReceivedEvent_5', PatternExpr_7, sources=None, destinations=None, timestamps=None, record_history=None, handlers=[self._MI_PROTO_CACHE_handler_5]), da.pat.EventPattern(da.pat.ReceivedEvent, '_MI_PROTO_CACHEReceivedEvent_6', PatternExpr_8, sources=None, destinations=None, timestamps=None, record_history=None, handlers=[self._MI_PROTO_CACHE_handler_6]), da.pat.EventPattern(da.pat.ReceivedEvent, '_MI_PROTO_CACHEReceivedEvent_7', PatternExpr_9, sources=[PatternExpr_10], destinations=None, timestamps=None, record_history=None, handlers=[self._MI_PROTO_CACHE_handler_7]), da.pat.EventPattern(da.pat.ReceivedEvent, '_MI_PROTO_CACHEReceivedEvent_8', PatternExpr_11, sources=[PatternExpr_12], destinations=None, timestamps=None, record_history=None, handlers=[self._MI_PROTO_CACHE_handler_8]), da.pat.EventPattern(da.pat.ReceivedEvent, '_MI_PROTO_CACHEReceivedEvent_9', PatternExpr_13, sources=None, destinations=None, timestamps=None, record_history=None, handlers=[self._MI_PROTO_CACHE_handler_9])])

    def setup(self, mem_ctrl_protocol_obj, other_protocol_obj, size, monitor_obj):
        self.mem_ctrl_protocol_obj = mem_ctrl_protocol_obj
        self.other_protocol_obj = other_protocol_obj
        self.size = size
        self.monitor_obj = monitor_obj
        self.memory = []
        self.get_from_caches = False
        self.wait_for_caches = False
        self.wait_for_memory = False
        self.get_from_memory = False
        self.not_found_q = []
        self.pending_actions = []

    def _da_run_internal(self):
        _st_label_23 = 0
        while (_st_label_23 == 0):
            _st_label_23 += 1
            if False:
                _st_label_23 += 1
            else:
                super()._label('_st_label_23', block=True)
                _st_label_23 -= 1

    def reorder(self, addr, value):
        '\n    LRU Caching logic\n    '
        ' Check if the addr is present in the list '
        found = False
        for (state, address, val) in self.memory:
            if ((state == 1) and (address == addr)):
                found = True
                if (value == ''):
                    value = val
                self.memory.remove((1, addr, val))
                break
        if (not found):
            ' Check if the cache is full '
            if (len(self.memory) == self.size):
                print('Cache is full')
                (state, last_addr, value) = self.memory.pop()
                if (state == 1):
                    self._send(('flush', last_addr, value), self.mem_ctrl_protocol_obj)
                    self._send(('inc_msg_cnt', 1), self.monitor_obj)
        self.memory.insert(0, (1, addr, value))
        return value

    def get_addr(self, addr):
        '\n    The load/store address is not in the cache, try\n       (1) snoop other caches \n       (2) if (1) fails then get from memory\n    '
        self.wait_for_caches = False
        self._send(('get', addr), self.other_protocol_obj)
        self._send(('inc_msg_cnt', len(self.other_protocol_obj)), self.monitor_obj)
        _st_label_50 = 0
        while (_st_label_50 == 0):
            _st_label_50 += 1
            if self.wait_for_caches:
                _st_label_50 += 1
            else:
                super()._label('_st_label_50', block=True)
                _st_label_50 -= 1
        if (not self.get_from_caches):
            self.wait_for_memory = False
            self._send(('get', addr), self.mem_ctrl_protocol_obj)
            self._send(('inc_msg_cnt', 1), self.monitor_obj)
            _st_label_55 = 0
            while (_st_label_55 == 0):
                _st_label_55 += 1
                if self.wait_for_memory:
                    _st_label_55 += 1
                else:
                    super()._label('_st_label_55', block=True)
                    _st_label_55 -= 1
            if self.get_from_memory:
                self._send(('invalidate', addr), self.other_protocol_obj)
                self._send(('inc_msg_cnt', len(self.other_protocol_obj)), self.monitor_obj)
        else:
            self._send(('invalidate', addr), self.other_protocol_obj)
            self._send(('inc_msg_cnt', len(self.other_protocol_obj)), self.monitor_obj)
        self.get_from_caches = False

    def _MI_PROTO_CACHE_handler_0(self, addr, p):
        '\n    Received request for address from another cache, check local\n    cache and if addr is present, invalidate it and send back the value\n    '
        ' Add time delay here to mimic cache-to-cache latency '
        found = False
        value = ''
        for i in range(len(self.memory)):
            if ((self.memory[i][0] == 1) and (self.memory[i][1] == addr)):
                self.memory[i] = (0, addr, self.memory[i][2])
                found = True
                value = self.memory[i][2]
                break
        if found:
            self._send(('found_in_cache', addr, value), p)
            self._send(('inc_msg_cnt', 1), self.monitor_obj)
        else:
            self._send(('not_found_in_cache', addr), p)
            self._send(('inc_msg_cnt', 1), self.monitor_obj)
    _MI_PROTO_CACHE_handler_0._labels = None
    _MI_PROTO_CACHE_handler_0._notlabels = None

    def _MI_PROTO_CACHE_handler_1(self, addr, p):
        '\n    Invalidate the cache block containing the requested address if present in our cache\n    '
        ' invalidate cache block '
        for i in range(len(self.memory)):
            ' invalidate cache block '
            if ((self.memory[i][0] == 1) and (self.memory[i][1] == addr)):
                self.memory[i] = (0, addr, self.memory[i][2])
                break
    _MI_PROTO_CACHE_handler_1._labels = None
    _MI_PROTO_CACHE_handler_1._notlabels = None

    def _MI_PROTO_CACHE_handler_2(self, addr, value):
        '\n    Received "found in cache" acknowledgement which basically denotes we have found the requested addr in another cache and received the value from that cache.\n    '
        ' Check if the cache is full '
        if (len(self.memory) == self.size):
            print('Cache is full')
            (state, last_addr, v) = self.memory.pop()
            if (state == 1):
                self._send(('flush', last_addr, v), self.mem_ctrl_protocol_obj)
                self._send(('inc_msg_cnt', 1), self.monitor_obj)
        self.memory.append((1, addr, value))
        self.get_from_caches = True
        self.wait_for_caches = True
    _MI_PROTO_CACHE_handler_2._labels = None
    _MI_PROTO_CACHE_handler_2._notlabels = None

    def _MI_PROTO_CACHE_handler_3(self, addr):
        '\n    Data already loaded into a cache. Snoop again\n    '
        self.wait_for_memory = True
        self.get_addr(addr)
    _MI_PROTO_CACHE_handler_3._labels = None
    _MI_PROTO_CACHE_handler_3._notlabels = None

    def _MI_PROTO_CACHE_handler_4(self, addr):
        '\n    Received "found in cache" acknowledgement which basically denotes we have found \n    the requested addr in another cache and received the value from that cache.\n    '
        self.not_found_q.append('recvd_not_found')
        if (len(self.not_found_q) == len(self.other_protocol_obj)):
            self.wait_for_caches = True
    _MI_PROTO_CACHE_handler_4._labels = None
    _MI_PROTO_CACHE_handler_4._notlabels = None

    def _MI_PROTO_CACHE_handler_5(self, addr, value):
        '\n    We have received the requested address/data from the memory controller\n    '
        ' Check if the cache is full '
        if (len(self.memory) == self.size):
            print('Cache is full')
            (state, last_addr, v) = self.memory.pop()
            if (state == 1):
                self._send(('flush', last_addr, v), self.mem_ctrl_protocol_obj)
                self._send(('inc_msg_cnt', 1), self.monitor_obj)
        self.memory.append((1, addr, value))
        self.get_from_memory = True
        self.wait_for_memory = True
    _MI_PROTO_CACHE_handler_5._labels = None
    _MI_PROTO_CACHE_handler_5._notlabels = None

    def _MI_PROTO_CACHE_handler_6(self):
        '\n    Address no found in memory\n    '
        print('Addr not found in memory')
        self.wait_for_memory = True
    _MI_PROTO_CACHE_handler_6._labels = None
    _MI_PROTO_CACHE_handler_6._notlabels = None

    def _MI_PROTO_CACHE_handler_7(self, addr, s):
        '\n    Received load request from processor, load address into cache and send back acknowledgement\n    '
        found = False
        value = ''
        for val in self.memory:
            if ((val[0] == 1) and (val[1] == addr)):
                found = True
                break
        if (not found):
            self.get_addr(addr)
        value = self.reorder(addr, '')
        self.not_found_q.clear()
        self._send(('ins', 'loaded', addr, value, self.id), self.monitor_obj)
        self._send(('completed_load', value), s)
        self._send(('inc_msg_cnt', 1), self.monitor_obj)
    _MI_PROTO_CACHE_handler_7._labels = None
    _MI_PROTO_CACHE_handler_7._notlabels = None

    def _MI_PROTO_CACHE_handler_8(self, addr, value, s):
        '\n    Received store request from processo, store value into cache and send back acknowledgement\n    '
        found = False
        for val in self.memory:
            if ((val[0] == 1) and (val[1] == addr)):
                found = True
                break
        if (not found):
            self.get_addr(addr)
        self.reorder(addr, value)
        self.not_found_q.clear()
        self._send(('ins', 'stored', addr, value, self.id), self.monitor_obj)
        self._send('completed_store', s)
        self._send(('inc_msg_cnt', 1), self.monitor_obj)
    _MI_PROTO_CACHE_handler_8._labels = None
    _MI_PROTO_CACHE_handler_8._notlabels = None

    def _MI_PROTO_CACHE_handler_9(self):
        self.exit()
    _MI_PROTO_CACHE_handler_9._labels = None
    _MI_PROTO_CACHE_handler_9._notlabels = None

class MI_PROTO_CTRL(da.DistProcess):

    def __init__(self, parent, initq, channel, props):
        super().__init__(parent, initq, channel, props)
        self._events.extend([da.pat.EventPattern(da.pat.ReceivedEvent, '_MI_PROTO_CTRLReceivedEvent_0', PatternExpr_14, sources=[PatternExpr_15], destinations=None, timestamps=None, record_history=None, handlers=[self._MI_PROTO_CTRL_handler_10]), da.pat.EventPattern(da.pat.ReceivedEvent, '_MI_PROTO_CTRLReceivedEvent_1', PatternExpr_16, sources=None, destinations=None, timestamps=None, record_history=None, handlers=[self._MI_PROTO_CTRL_handler_11]), da.pat.EventPattern(da.pat.ReceivedEvent, '_MI_PROTO_CTRLReceivedEvent_2', PatternExpr_17, sources=None, destinations=None, timestamps=None, record_history=None, handlers=[self._MI_PROTO_CTRL_handler_12])])

    def setup(self, cache_protocol_objs, monitor_obj):
        self.cache_protocol_objs = cache_protocol_objs
        self.monitor_obj = monitor_obj
        self.memory_ref = dict()
        self.memory_value = dict()

    def _da_run_internal(self):
        _st_label_160 = 0
        while (_st_label_160 == 0):
            _st_label_160 += 1
            if False:
                _st_label_160 += 1
            else:
                super()._label('_st_label_160', block=True)
                _st_label_160 -= 1

    def _MI_PROTO_CTRL_handler_10(self, addr, p):
        '\n    Retrieve the requested address from memory and send it back to the cache\n    '
        ' Add time delay here to mimic cache-to-memory latency '
        if ((addr in self.memory_ref) and (self.memory_ref[addr] > 0)):
            self._send(('get_from_cache', addr), p)
            self._send(('inc_msg_cnt', 1), self.monitor_obj)
        else:
            time.sleep(0.1)
            self.memory_ref[addr] = 1
            if (not (addr in self.memory_value)):
                self.memory_value[addr] = 0
            self._send(('found_in_memory', addr, self.memory_value[addr]), p)
            self._send(('inc_msg_cnt', 1), self.monitor_obj)
    _MI_PROTO_CTRL_handler_10._labels = None
    _MI_PROTO_CTRL_handler_10._notlabels = None

    def _MI_PROTO_CTRL_handler_11(self, addr, value):
        '\n    Write back to memory\n    '
        time.sleep(0.1)
        self.memory_ref[addr] = 0
    _MI_PROTO_CTRL_handler_11._labels = None
    _MI_PROTO_CTRL_handler_11._notlabels = None

    def _MI_PROTO_CTRL_handler_12(self):
        self.exit()
    _MI_PROTO_CTRL_handler_12._labels = None
    _MI_PROTO_CTRL_handler_12._notlabels = None

class Processor(da.DistProcess):

    def __init__(self, parent, initq, channel, props):
        super().__init__(parent, initq, channel, props)
        self._events.extend([da.pat.EventPattern(da.pat.ReceivedEvent, '_ProcessorReceivedEvent_0', PatternExpr_18, sources=None, destinations=None, timestamps=None, record_history=None, handlers=[self._Processor_handler_13]), da.pat.EventPattern(da.pat.ReceivedEvent, '_ProcessorReceivedEvent_1', PatternExpr_19, sources=None, destinations=None, timestamps=None, record_history=None, handlers=[self._Processor_handler_14])])

    def setup(self, trace, protocol, monitor_obj):
        self.trace = trace
        self.protocol = protocol
        self.monitor_obj = monitor_obj
        self.keep_waiting = False

    def _da_run_internal(self):
        for inst in self.trace:
            self.keep_waiting = False
            self.execute(inst)
            _st_label_198 = 0
            while (_st_label_198 == 0):
                _st_label_198 += 1
                if self.keep_waiting:
                    _st_label_198 += 1
                else:
                    super()._label('_st_label_198', block=True)
                    _st_label_198 -= 1
            else:
                if (_st_label_198 != 2):
                    continue
            if (_st_label_198 != 2):
                break

    def execute(self, inst):
        '\n           Execute the instructions in the given execution trace \n           Reference : Parag Gupta (https://github.com/karthikbox/cache_coherence/tree/p_template/main.da)\n      '
        if (inst[0] == 'r'):
            (type, addr) = inst
            self._send(('load', addr), self.protocol)
            self._send(('inc_msg_cnt', 1), self.monitor_obj)
        elif (inst[0] == 'w'):
            (type, addr, value) = inst
            self._send(('store', addr, value), self.protocol)
            self._send(('inc_msg_cnt', 1), self.monitor_obj)
        else:
            print('Unexpected instruction:', inst)

    def _Processor_handler_13(self, value):
        '\n      Receive acknowledgement from the cache controller process.\n      This indicates that the instruction has been executed\n      Reference : Parag Gupta (https://github.com/karthikbox/cache_coherence/tree/p_template/main.da)\n      '
        self.keep_waiting = True
    _Processor_handler_13._labels = None
    _Processor_handler_13._notlabels = None

    def _Processor_handler_14(self):
        '\n      Receive acknowledgement from the cache controller process.\n      This indicates that the instruction has been executed\n      Reference : Parag Gupta (https://github.com/karthikbox/cache_coherence/tree/p_template/main.da)\n      '
        self.keep_waiting = True
    _Processor_handler_14._labels = None
    _Processor_handler_14._notlabels = None

class Monitor(da.DistProcess):

    def __init__(self, parent, initq, channel, props):
        super().__init__(parent, initq, channel, props)
        self._events.extend([da.pat.EventPattern(da.pat.ReceivedEvent, '_MonitorReceivedEvent_0', PatternExpr_20, sources=None, destinations=None, timestamps=None, record_history=None, handlers=[self._Monitor_handler_15]), da.pat.EventPattern(da.pat.ReceivedEvent, '_MonitorReceivedEvent_1', PatternExpr_21, sources=None, destinations=None, timestamps=None, record_history=None, handlers=[self._Monitor_handler_16]), da.pat.EventPattern(da.pat.ReceivedEvent, '_MonitorReceivedEvent_2', PatternExpr_22, sources=None, destinations=None, timestamps=None, record_history=None, handlers=[self._Monitor_handler_17]), da.pat.EventPattern(da.pat.ReceivedEvent, '_MonitorReceivedEvent_3', PatternExpr_23, sources=None, destinations=None, timestamps=None, record_history=None, handlers=[self._Monitor_handler_18])])

    def setup(self):
        self.instructions = []
        self.total_msgs = 0
        self.cpu_time = 0
        self.elapsed_time = 0

    def _da_run_internal(self):
        _st_label_223 = 0
        while (_st_label_223 == 0):
            _st_label_223 += 1
            if False:
                _st_label_223 += 1
            else:
                super()._label('_st_label_223', block=True)
                _st_label_223 -= 1

    def _Monitor_handler_15(self, type, addr, value, cache_id):
        '\n    Collects all load/store instructions executed by the cache controller\n    '
        self.instructions.append((type, addr, value, cache_id))
    _Monitor_handler_15._labels = None
    _Monitor_handler_15._notlabels = None

    def _Monitor_handler_16(self, value):
        '\n    Keeps track of the total message count in the system\n    '
        self.total_msgs = (self.total_msgs + value)
    _Monitor_handler_16._labels = None
    _Monitor_handler_16._notlabels = None

    def _Monitor_handler_17(self, cpu, elapsed):
        '\n    Get the elapsed time and CPU time\n    '
        self.cpu_time = cpu
        self.elapsed_time = elapsed
    _Monitor_handler_17._labels = None
    _Monitor_handler_17._notlabels = None

    def _Monitor_handler_18(self):
        '\n    Simulation has ended, dislay the results of the simulation\n    '
        print('===Load/Store global order===')
        for ins in self.instructions:
            print(ins[3], ': ', ins[0], ins[1], ins[2])
        print()
        print('===Benchmarks===')
        print('Total msg count:', self.total_msgs)
        print('Elapsed time:', self.elapsed_time)
        print('CPU time:', self.cpu_time)
        self.exit()
    _Monitor_handler_18._labels = None
    _Monitor_handler_18._notlabels = None

def get_traces(trace_dir, nprocs):
    '\n  Extracts the execution traces from the given directory.\n  Reference: Karthik Reddy (https://github.com/karthikbox/cache_coherence/blob/mesi_protocol/main.da)\n  '
    trace = []
    for i in range(nprocs):
        trace_filename = (('p' + str(i)) + '.trace')
        f = open(os.path.join(trace_dir, trace_filename))
        insts = []
        for line in f:
            insts.append(line.split())
        trace.append(insts)
    return trace

def main():
    '\n    main routine - generic to all protocol implementations:\n      - spawn DistAlgo processes for n processors, n cache controllers and a memory controller \n      - get execution traces for each of the processors\n    Reference : Parag Gupta (https://github.com/karthikbox/cache_coherence/tree/p_template/main.da)\n    '
    nprocessors = (int(sys.argv[1]) if (len(sys.argv) > 1) else 2)
    proto_name = (sys.argv[2] if (len(sys.argv) > 2) else 'MI')
    trace_dir = (sys.argv[3] if (len(sys.argv) > 3) else './traces')
    da.config(channel='fifo', clock='Lamport')
    start_cpu_time = time.process_time()
    start_elapsed_time = time.perf_counter()
    trace = get_traces(trace_dir, nprocessors)
    (Proto_cache, Proto_ctrl) = get_proto_class(proto_name)
    print('-----START-----')
    monitor_obj = da.new(Monitor, num=1)
    da.setup(monitor_obj, ())
    da.start(monitor_obj)
    mem_ctrl_protocol_obj = da.new(Proto_ctrl, num=1)
    protocol_objs = da.new(Proto_cache, num=nprocessors)
    da.setup(mem_ctrl_protocol_obj, (protocol_objs, monitor_obj))
    da.start(mem_ctrl_protocol_obj)
    for proto_obj in protocol_objs:
        da.setup(proto_obj, (mem_ctrl_protocol_obj, (protocol_objs - {proto_obj}), CACHE_SIZE, monitor_obj))
        da.start(proto_obj)
    processors = da.new(Processor, num=nprocessors)
    processors_list = list(processors)
    protocol_objs_list = list(protocol_objs)
    for i in range(nprocessors):
        da.setup(processors_list[i], (trace[i], protocol_objs_list[i], monitor_obj))
    da.start(processors)
    for p in processors:
        p.join()
    da.send(('done',), to=protocol_objs)
    for m in protocol_objs:
        m.join()
    da.send(('done',), to=mem_ctrl_protocol_obj)
    for m in mem_ctrl_protocol_obj:
        m.join()
    end_cpu_time = time.process_time()
    end_elapsed_time = time.perf_counter()
    da.send(('time_taken', (end_cpu_time - start_cpu_time), (end_elapsed_time - start_elapsed_time)), to=monitor_obj)
    da.send(('done',), to=monitor_obj)
    for monitor in monitor_obj:
        monitor.join()
    print('-----END-----')
