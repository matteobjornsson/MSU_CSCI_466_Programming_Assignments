'''
Created on Oct 12, 2016

@author: mwittie
'''
import network_1 as network
import link_1 as link
import threading
from time import sleep

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 2 #give the network sufficient time to transfer all packets before quitting
mtu = 50

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads
    
    #create network nodes
    client = network.Host(1)
    object_L.append(client)
    server = network.Host(2)
    object_L.append(server)
    router_a = network.Router(name='A', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_a)
    
    #create a Link Layer to keep track of links between network nodes
    link_layer = link.LinkLayer()
    object_L.append(link_layer)
    
    #add all the links
    #link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu
    link_layer.add_link(link.Link(client, 0, router_a, 0, mtu))
    link_layer.add_link(link.Link(router_a, 0, server, 0, mtu))
    
    
    #start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=client.__str__(), target=client.run))
    thread_L.append(threading.Thread(name=server.__str__(), target=server.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))
    
    thread_L.append(threading.Thread(name="Network", target=link_layer.run))
    
    for t in thread_L:
        t.start()
    
    #create some send events    
    #for i in range(3):
       #client.udt_send(2, 'This is a longer string for simulation_1. This string is too long for this MTU %d' % i)
       #client.udt_send(2, 'This is short string %d' % i)
    
    message = 'This is a longer string for simulation_1. This string is too long for this MTU'
    segMessage = []
    while(True):
        if(len(message) > mtu-5):
            segMessage.append(message[0:mtu-6])
            message = message[mtu:]
        else:
            segMessage.append(message)
            break
        
    
    for m in segMessage:
        client.udt_send(2, m)
    

    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)
    
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
    print("All simulation threads joined")



# writes to host periodically