# Multiple-Server-Client
Creates n Servers. Each server communicates with each other to find the shortest path to each other.

One thread is the Server (receiver) another thread is the Client (sender). provides in-order, reliable delivery of UDP datagrams in presence of packet loss and corruption. Sender delivers a file to server which verifies the integrity of the file.

Pukar Subedi

## Approach 
Reads the given network.txt files and creates n servers from the file. Servers will communicate with each other and find the shortest
paths from one another using bellman ford algorithm. 

###### Network.txt
provide a 2d array of your network and the lengths between servers/routers. 2 files are provided as examples.

###### Output.txt
Log file, will provide otuput with what happens at each step. Each iteration the next server will send out its Distance Vector (DV)
information. Final output will be the result 2d array with shortest lengths from one server to another.
