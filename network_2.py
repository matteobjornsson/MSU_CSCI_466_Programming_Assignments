'''
Created on Oct 12, 2016

@author: mwittie
'''
import queue
import threading


## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize)
        self.mtu = None
    
    ##get packet from the queue interface
    def get(self):
        try:
            return self.queue.get(False)
        except queue.Empty:
            return None
        
    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, block=False):
        self.queue.put(pkt, block)
        
        
## Implements a network layer packet (different from the RDT packet 
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    ## packet encoding lengths 
    dst_addr_S_length = 5
    id_length = 5
    offset_length = 13
    flag_len = 1
    header_len = dst_addr_S_length + id_length + offset_length + flag_len 
    
    
    ##@param dst_addr: address of the destination host
    # @param data_S: packet payload
    #dummy comment for purposes of merge conflict practice
    # id: unique id for data to tell that multiple segments belong to same block of data
    # offset: where the bytes are to be inserted
    # flag: 1 is more fragments are coming, 0 is final fragment
    def __init__(self, dst_addr: int, id: int, offset: int, flag: int, data_S: str):
        self.dst_addr = dst_addr
        self.id = id
        self.offset = offset
        self.flag = flag
        self.data_S = data_S
        
    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()
    
    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += str(self.id).zfill(self.id_length)
        byte_S += str(self.offset).zfill(self.offset_length)
        byte_S += str(self.flag)
        byte_S += self.data_S
        return byte_S
    
    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S: str):
        dst_addr = int(byte_S[0 : NetworkPacket.dst_addr_S_length])
        id = int(byte_S[NetworkPacket.dst_addr_S_length:NetworkPacket.dst_addr_S_length + NetworkPacket.id_length])
        offset = int(byte_S[NetworkPacket.dst_addr_S_length + NetworkPacket.id_length: NetworkPacket.dst_addr_S_length + NetworkPacket.id_length + NetworkPacket.offset_length])
        flag = int(byte_S[NetworkPacket.dst_addr_S_length + NetworkPacket.id_length + NetworkPacket.offset_length: NetworkPacket.dst_addr_S_length + NetworkPacket.id_length + NetworkPacket.offset_length + 1])
        data_S = byte_S[NetworkPacket.dst_addr_S_length + NetworkPacket.id_length + NetworkPacket.offset_length + NetworkPacket.flag_len: ]
        return self(dst_addr, id, offset, flag, data_S)
    
    # def fragment(self, )

                    #     if (len(pkt_S) <= out_mtu):
                    #     self.out_intf_L[i].put(p.to_byte_S(), True)
                    #     print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                    #         % (self, p, i, i, out_mtu))
                    # # if outgoing MTU is too small, fragment packet to fit. Send all new fragment packets.
                    # else:
                    #     payload = p.data_S 
                    #     fragList = []
                    #     newPayloadSize = out_mtu - NetworkPacket.header_len
                    #     while (True)):
                    #         fragList.append(payload[0:newPayloadSize - 1])
                    #         payload = payload[newPayloadSize: ]
                    #         if (len(payload) < newPayloadSize):
                    #             fragList.append(payload)
                    #             break
                    #     for fragment in fragList:
                    #         fragPacket = NetworkPacket(p.dst_addr, p.id, p. )
                    #         self.out_intf_L[i].put(p.to_byte_S(), True)
                    #         print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                    #             % (self, p, i, i, out_mtu))

    def print(self):
        return '\n'.join("{k}: {v}".format(k=key,v=val) for (key,val) in self.__dict__.items())

    

# pack = NetworkPacket(5, 1, 0, 0, "meowwwww")
# print(pack)

# byte_S = pack.to_byte_S()
# print(pack_str)
# new_pack = NetworkPacket.from_byte_S(pack_str)
# print(new_pack)


## Implements a network host for receiving and transmitting data
class Host:
    
    ##@param addr: address of this node represented as an integer
    def __init__(self, addr: int):
        self.addr = addr
        self.in_intf_L = [Interface()]
        self.out_intf_L = [Interface()]
        self.stop = False #for thread termination
    
    ## called when printing the object
    def __str__(self):
        return 'Host_%s' % (self.addr)
       
    ## create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst_addr: int, id: int, offset: int, flag: int, data_S: str):
        p = NetworkPacket(dst_addr, id, offset, flag, data_S)
        self.out_intf_L[0].put(p.to_byte_S()) #send packets always enqueued successfully
        print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))
        
    ## receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.in_intf_L[0].get()
        if pkt_S is not None:
            print('%s: received packet "%s" on the in interface' % (self, pkt_S))
       
    ## thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                return
        


## Implements a multi-interface router described in class
class Router:
    
    ##@param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces 
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_count, max_queue_size):
        self.stop = False #for thread termination
        self.name = name
        #create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]

    ## called when printing the object
    def __str__(self):
        return 'Router_%s' % (self.name)

    ## look through the content of incoming interfaces and forward to
    # appropriate outgoing interfaces
    def forward(self):
        for i in range(len(self.in_intf_L)):
            pkt_S = None
            try:
                #get packet from interface i
                pkt_S = self.in_intf_L[i].get()
                #if packet exists make a forwarding decision
                if pkt_S is not None:
                    out_mtu = self.out_intf_L[i].mtu
                    p = NetworkPacket.from_byte_S(pkt_S) #parse a packet out
                    # HERE you will need to implement a lookup into the 
                    # forwarding table to find the appropriate outgoing interface
                    # for now we assume the outgoing interface is also i

                    # if outgoing MTU is big enough, send packet
                    self.out_intf_L[i].put(p.to_byte_S(), True)
                    print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                        % (self, p, i, i, out_mtu))
                        
            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, p, i))
                pass
                
    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return 