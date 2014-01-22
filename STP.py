import weighted
import random
import pdb
import networkx as nx

#Reference: http://www.lfd.uci.edu/~gohlke/pythonlibs/

switch_gr = nx.Graph() #nx.Graph comes from the networkx python inbuilt library. It is used in dijstra's algo. The module is changed in such a way that weight is made equivalent to the speed used in the code. Mac-address dictionary is added so as to use the MAC-table entries for computing the shortest path in case of equal paths. Also, djkstra's when comes accrosss equal path, takes any path randomly. Nevertheless, STP has to compare MAC hen finds equal cost path to the source. So, that section has been edited from nx.Graph

class Bpdu():
    '''This class contains attributes of bpdu. bpdu is used to determine the rot switch'''
    def __init__(self):
       self.address =""
       self.priority =""
       self.root=""
       self.source_address = ""
       self.destination_address = ""
       self.payload = ""
    #bpdu.cost = ""
    def __str__():
        return 'root='+self.root

class Switch():
    '''This class contains all the attributes a Switch'''
    def __init__(self, name, add, priority):
        ''' To assign default values
        '''
        # self.forwardtable = dict ()
        self.ports = list() #This contains the list of switches that are connected to a switch
        self.forwardtable = dict ()
        self.name = name
        self.address = add
        self.links = list() #This contains a list of links that are connected to a switch
        self.priority = priority
        self.root = self
        self.to_root_cost = int
        self.label = list()
        self.previous = type(Switch)
        #switch_list.append()

    def __repr__(self):
        ''' This method return a string representation of a list of objects'''
        return self.name

    def connect(self, other):
        '''This function is used to connect to switches as per user input'''

        self.ports.append(other) #This connects the two switches in forward direction of the user input
        if isinstance(other,Switch):
             other.ports.append(self) #This connects the two switches in backward direction of the user input

    def send_bpdu(self):   # eg: s1 . s1->s2
         '''This method creates bpdu packets and forwards it to its connected neighbors and the propogation continues until all the switches agree upon making a switch, the rot switch'''
         self.bpdu = Bpdu()
         self.bpdu.address = self.address
         self.bpdu.priority = self.priority
         self.bpdu.root = self.root
         for others in self.ports: #other is basically the connected switch, if the switch is present in the list of the source switch, it will accept the bpdu
             if isinstance(others,Switch):
                others.receive_bpdu(self.bpdu) #s2,s1 bpdu

    def receive_bpdu(other,bpdu): #s2,s1 bpdu
       '''In this method bpdus are accepted. The root is determined by first comparing the priority. It should be the lowest of all for the root switch. If priority is equal, then checks for the lowest MAC addess. It then forwards it to the other switches'''

       if other.root != bpdu.root:
          if bpdu.priority < other.priority: #In this if a sending switch's priority is lower than the receiving switce's priority, then sending switch is accepted as a root switch
              other.root = bpdu.root
              for others in other.ports: #In this if the receiving switch gets a lower priority switch, it forwards an updated bpdu packet to its onnected switches
                   if isinstance(others,Switch):
                        others.receive_bpdu(bpdu)
          elif bpdu.priority == other.priority: #In this if priority is same, then check for the lowest MAC-address and send the updated bpdu packet
            if bpdu.address < other.address:
                other.root = bpdu.root
                for others in other.ports: #s2 sends to their connection -- propogating
                    if isinstance(others,Switch):
                        others.receive_bpdu(bpdu)
            else:
                other.send_bpdu()
                bpdu.root = other.root
          else: #In this if the receiving switch has a lower priority, then it becomes the switch and forwards the bpdu packet to its connected switch
              other.send_bpdu()                  #if s2 wins, send it to their connection
              bpdu.root = other.root

    def forward(self, sender, packet):
        ''' To build the forward table and send the packet to the associated port. Flood in case there is no match.
        '''

        if packet.source_address not in self.forwardtable: # build forward table
            port = self.ports.index(sender)
            self.forwardtable[packet.source_address] = port
            print self.name

        if packet.destination_address in self.forwardtable: #check des add. in forwar_table
            port = self.forwardtable[packet.destination_address]
            print "I am forwarding packet from port -",
            print "%s to device - %s" %(self.forwardtable[packet.destination_address],packet.destination_address)
            host = self.ports[port]
            host.receive(self, packet)
        else: #flood

            for host in self.ports:
                if host.address == packet.source_address or host.address == sender.address:
                    pass
                else:
                    host.receive (self, packet)

    def receive(self, sender, packet):
        '''This function is used to receive the payload from the other connected devices'''


        self.forward(sender, packet)
        #print "received by",self.name

    def print_root_switch(self):
        '''This method exclusively displays the root, switches present in the topology, their MAC-addresses, and prioirity'''

        print self, self.root
        return self.root.name


    def assign_costandprevious (self,cost,previous_switch):
         '''This function assigns cost to reach root'''
         self.to_root_cost = cost
         self.previous = previous_switch
         #print self,self.previous

    def remove_port(self,other):
        '''This function is used to remove the blocking port from the topology'''

        #print self.ports
        self.ports.remove(other)
        other.ports.remove(self)
        print (self.name+" connecting to "+other.name+" is "+"blocked port ")
        print (other.name+" connecting to "+self.name+" is "+"designated port ")
        #print self.ports

    def initialize_labels(self):
        '''This function initializes a label and appends it to itself '''
        for port in self.ports:
            self.label.append("")

    def find_ports(self):
        '''This function is used to find the designated ports and the root ports'''
        if self.to_root_cost == 0:
            for port in self.ports:
                if (isinstance(port,Switch) == True):
                   self.label[self.ports.index(port)]="designated port"
                   print self.name+" connecting to "+port.name+" is designated port"
                   port.label[port.ports.index(self)]="root port"
                   print port.name+" connecting to "+self.name+" is root port"

        if self.to_root_cost != 0:
            if self.previous != self.root:
                while(1):
                    previous = self.previous
                    local_label = False
                    index = 0
                    for port in previous.ports:
                        if port == self.root:
                            local_label = True
                            port_name = previous.label[index]

                        index = index + 1

                    if local_label == False:
                        previous = previous.previous
                    else:
                        break
              #  index = self.name.ports.index(previous)
              #  self.name.label[index] == port_name
                if port_name!="":
                   print self.name+ " connecting to "+self.previous.name+"is "+port_name
                   if port_name == "root port":
                       another_port_name = "designated port"
                   else:
                       another_port_name = "root port"
                   print self.previous.name + " connecting to "+ self.name+"is "+another_port_name






class Host():
    '''This class contains attributes of the hosts'''

    def __init__(self, name, add):
        ''' This function is used to assign default values'''

        self.name = name
        self.address = add
        self.port = None

    def __str__(self):
        ''' This function is used to return a string representation of an object'''
        return self.name

    def __repr__(self):
        ''' This function is used to return a string representation of a list of objects'''
        return self.name

    def send(self, payload, destination_address):
        ''' This function is used to build the packet and call the receive method on the directly connected device'''

        pkt = Bpdu()
        print destination_address
        pkt.destination_address = destination_address
        pkt.source_address = self.address
        pkt.payload = payload
        print "source: "+ self.name
        print "received by "+ self.port.name
        self.port.receive(self,pkt) #port here means switch'''

    def receive(self, sender, packet):
        ''' To check whether the packet is destined to the host and then print the payload'''
        print "received by "+ sender.name
        print "Destination: " + self.name
        print "Checking if " + self.address, "==" + packet.destination_address
        if self.address == packet.destination_address:
              print self.name, "received", packet.payload


    def connect(self, other_host):
        '''This function is used to build the directly connected devices list'''

        self.port = other_host      #here port means switch'''


def generate_mac():
    '''This method generates a random MAC-Addresses for the switches and hosts'''

    mac = ""
    for i in range(0, 6):
        mac += "%02x:" % random.randint(0x00, 0xff)
    return mac.strip(":")


def get_speed(switch1,switch2):
    '''This method takes the speed of each of the connected links from the user and returns it, which is then used to compute cost to root switch and port states'''
    speed_list = ['10Mbps','100Mbps','1Gbps','10Gbps'] #This list consists of the possible speeds of the links
    speed = str(raw_input("Enter speed of the links interms of (10Mbps/100Mbps/1Gbps/10Gbps) for ("+switch1+","+switch2+"):"))
    # for ("+self.name+","+other.name+"):"))
    while(1): #If the user enters invalid speed it goes into loop and after entering the right speed
     if speed not in speed_list:
          speed = str(raw_input("Invalid speed!! Enter again interms of (10Mbps/100Mbps/1Gbps/10Gbps) for ("+switch1+","+switch2+"):"))
          continue
     if speed in speed_list:
          break
    return speed

'''Refernce: http://networkx.github.io/documentation/latest/reference/algorithms.shortest_paths.html'''

def construct_graph(switch):
    '''This method constructs a graph of the topology. In a way consists of a dictionary to save the speed costs and calculates the minimum cost for all the switches to reach the root switch???'''
    speed_dict = {"10Mbps":100,
                  "100Mbps":19,
                  "1Gbps":4,
                  "10Gbps":2}
    number_of_switches = len(switch)

    for count in range(0,number_of_switches,2):
        switch1 = switch[count]
        switch2 = switch[count+1]
        speed = get_speed(switch1,switch2)
        converted_Speed = speed_dict[speed]
        switch_gr.add_edge(switch1,switch2,speed = converted_Speed) #adding links (here edge)

'''Refernce: http://networkx.github.io/documentation/latest/reference/algorithms.shortest_paths.html'''

def findsp_dijkstra(switch,mac_dict,root_switch):
    '''This method performs the dijktras algorith to find the shortest path for all the switches to reach the root switch'''
    construct_graph(switch)

    cost_to_source, path_to_source = weighted.single_source_dijkstra(switch_gr,root_switch,mac_dict=mac_dict,weight='speed') #originally from networkx
    return cost_to_source, path_to_source
  #  print result
def get_data(host_list,mac_dict_host):
    '''This function is used to get the host infomation from user'''
    while(1):
        data = str(raw_input("Enter data to be send[type done to finish]:"))
        if data == 'done':
            break
        sourcehost = host_list[int(str(raw_input("Source hostname:"))[1])]
        desthost = host_list[int(str(raw_input("Destination hostname:"))[1])]
        desthost_address = mac_dict_host[desthost]
        sourcehost.send(data,desthost_address)


def main():
    switches = [] #This contains a list of switches in the topology, which will be filled as per the user input
    mac_dict = {} #This contains the MAC-addresses of the switches and hosts generated from the random MAC function
    hosts = [] #This contains a list of hosts in the topology, which will be filled as per the user input
    switch_pair_list = [] #This contains list of the links of the connected switches
    blocked_links_list = [] #This contains list of the links that are blocking links

    '''User inputs the switches and the priority of all the switches in the n/w'''

    total_switches = int(raw_input("Enter number of switches:"))
    for switch_no in range(0,total_switches):
        priority = str(raw_input("Enter prioirity for s"+str(switch_no)))
        mac = generate_mac()
        switches.append(Switch("s"+str(switch_no),mac,priority)) #every switch gets a random mac address and prioirities as assigned by the user
        switch_gr.add_node("s"+str(switch_no)) #,weight = (mac.replace(":",""),16))
        mac_dict["s"+str(switch_no)] = mac


    switch_connect_input = str(raw_input("Enter switch connection in form of tuple Eg: (s0,s1),(s1,s2)...:")) #User input of how switches are connected,
    switch_connect_input= switch_connect_input.replace("(","").replace(")","")
    switch_split = switch_connect_input.split(",")
    number_of_switches = len(switch_split)


    for count in range(0,number_of_switches,2): #In this the user enters all the swithes, which is stored as a list. So, it is in the jump of two so as to get the next pair
        switch1 = int(switch_split[count][1])
        switch2 = int(switch_split[count+1][1])
        switch_pair_list.append(("s"+str(switch1),"s"+str(switch2)))
    #    speed = get_speed()
        switches[switch1].connect(switches[switch2]) #In this the 1st pair of switches are connected to each other and consequently the rest



    number_of_hosts = int(raw_input("Enter number of hosts:"))  #Asking user for host connections

    for count in range(0,number_of_hosts): #Determines which host is connected to which switch and the hosts gets MAc-address and is appended to the list
         switch = str(raw_input("Enter the switch Host"+str(count)+" is connected to [Eg: s0] : "))
         mac = generate_mac()
         newhost = Host("H"+str(count),mac)
         print "Available hosts are " + str(newhost)
         mac_dict[newhost] = mac
         hosts.append(newhost)
         newhost.connect(switches[int(switch[1])])
         switches[int(switch[1])].connect(newhost)

    for switch in switches:
        Switch.send_bpdu(switch)
    print "switches, Root swich"
    for switch in switches:
        root_switch = Switch.print_root_switch(switch)

    cost_to_root,path_to_source = findsp_dijkstra(switch_split,mac_dict,root_switch)

    print "Cost to reach root"
    for key in cost_to_root:
        print key +" : "+ str(cost_to_root[key])
        path_list = path_to_source [key]
        length_path_list = len(path_list)
        p_node = path_list[length_path_list-2]
        previous_node = switches[int(p_node[1])]
        switches[int(key[1])].assign_costandprevious(cost_to_root[key],previous_node)

    new_graph = nx.Graph()
   # print path_to_source
    for key in path_to_source :
        path_list = path_to_source[key]
        path_length = len(path_list)
        for index1 in range(0,path_length-1):
            node1 = path_list[index1]
            node2 = path_list[index1+1]
            if not (new_graph.has_node(node1)):
                new_graph.add_node(node1)
            if not (new_graph.has_node(node2)):
                new_graph.add_node(node2)
            if not (new_graph.has_edge(node1,node2)):
                new_graph.add_edge(node1,node2)


    for pair in switch_pair_list: #Finds blocked ports
        if not((new_graph.has_edge(pair[0],pair[1]))):
            blocked_links_list.append(pair)
    #print blocked_links_lists

    for pair in blocked_links_list: #Removes the blocked port associated with the switch
        switches[int(pair[0][1])].remove_port(switches[int(pair[1][1])])


    for switch in switches:
        switch.initialize_labels()

    end_switch = switches[int(root_switch[1])]
    end_switch.find_ports()
    for switch in switches:
        if end_switch != switch:
            switch.find_ports()

    #for switch in switches: #calls the find function for all the switches. Designated and Root ports will then be displayed
     #   switch.find_ports()
      #  if end_switch == switch:
       #     break

    get_data(hosts,mac_dict)

if __name__ == '__main__':
    main()