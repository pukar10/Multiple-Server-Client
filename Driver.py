# Saad Arshad G#00857432
# Pukar Subedi G#00778854
import pickle
import socket
import threading
import time as time

# we will need a lock to protect against concurrent threads
lock = threading.Lock()


def main():
    matrix = []
    nodeTHolder = []
    socketDictionay = {}

    # read network.txt and get matrix
    with open("network1.txt", "r") as f:
        for line in f:
            line = line.split()
            for e in range(len(line)):
                line[e] = int(line[e])
            matrix.append(line)

    calculateBellManFord(matrix)
    print(matrix)
    network_init(matrix, nodeTHolder, socketDictionay)

    # Relinquish control to node threads!? run/start I guess
    # Start all Node Servers
    for x in nodeTHolder:
        with lock:
            print("Node Server: " + str(x.nodeName) + " Listening. . .")
            start_thread = threading.Thread(target=server_thread, args=(socketDictionay[x.nodeName], x,))
            start_thread.start()

    # Send node DV messages to neighbors | order: A B C D E A B C D E
    # A sends message to neighbors
    # A starts 2 threads to send message to neighbors B and E
    roundCounter = 1
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiverIP = '127.0.0.1'

    while True:
        updateResult = 0
        for i in range(len(nodeTHolder)):
            name = nodeTHolder[i].nodeName
            print("\nRound " + str(roundCounter) + ": " + str(name))
            print("Current DV matrix = " + str(nodeTHolder[i].upDV))
            print("Last DV matrix = " + str(nodeTHolder[i].DVs[name]))
            print("Updated from last DV matrix or the same? ")
            with lock:
                x = []
                if nodeTHolder[i].upDV != nodeTHolder[i].DVs[name]:
                    print("Updated \n")
                    updateResult = 0
                    nodeTHolder[i].upDV = nodeTHolder[i].DVs[name].copy()
                else:
                    print("Not Updated \n")
                    updateResult += 1
                    continue
                for j in nodeTHolder[i].neighbor:
                    client_socket.connect((receiverIP, socketDictionay[j]))
                    w = nodeTHolder[i].neighbor[j]
                    x = nodeTHolder[i].upDV.copy()
                    x.append(name)
                    x.append(w)
                    x = pickle.dumps(x)
                    print("Sending DV to node " + str(j))
                    client_socket.sendto(x, (receiverIP, socketDictionay[j]))
                    time.sleep(.3)
            roundCounter += 1

        if updateResult == 5:
            print("\nFinished at Round = " + str(roundCounter))
            for i in range(len(nodeTHolder)):
                print(str(nodeTHolder[i].nodeName) + " = " + str(nodeTHolder[i].upDV))
            stopAll(client_socket, receiverIP, socketDictionay, nodeTHolder)


def server_thread(receiverPort, node):
    reciverAd = ''
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((reciverAd, receiverPort))

    timer = .5
    while True:
        try:
            server_socket.settimeout(timer)
            received_data, recv_addr = server_socket.recvfrom(1000)
            received_data = pickle.loads(received_data)
            if received_data == 'Done':
                break
            weightFromNode = received_data[len(received_data) - 1]
            del received_data[len(received_data) - 1]
            rname = received_data[len(received_data) - 1]
            del received_data[len(received_data) - 1]
            print("Node " + str(node.nodeName) + " received DV from node " + str(rname))
            print(received_data)

            with lock:
                node.DVs.update({rname: received_data})
                if received_data != node.DVs[node.nodeName]:
                    for i in range(len(received_data)):
                        if received_data[i] != 0 and received_data[i] != 999999 and node.DVs[node.nodeName][i] != 0:
                            if node.DVs[node.nodeName][i] == 999999:
                                node.DVs[node.nodeName][i] = received_data[i] + weightFromNode
                            elif received_data[i] + weightFromNode <= node.DVs[node.nodeName][i]:
                                node.DVs[node.nodeName][i] = received_data[i] + weightFromNode
        except socket.timeout:
            continue


def stopAll(client_socket, receiverIP, socketDictionay, nodeTHolder):
    for i in range(len(nodeTHolder)):
        name = nodeTHolder[i].nodeName
        x = 'Done'
        x = pickle.dumps(x)
        client_socket.sendto(x, (receiverIP, socketDictionay[name]))

    print('All Threads Closed')
    exit(0)


def calculateBellManFord(m):
    for i in range(len(m)):
        for j in range(len(m[0])):
            if i == j:
                m[i][j] = 0
            elif m[i][j] == 0:
                m[i][j] = 999999


def network_init(matrix, nodeTHolder, sd):
    # Create N NodeThreads (count columns or rows)
    nodeName = 'A'
    for i in range(len(matrix[0])):
        temp = NodeThread(nodeName)
        temp.DVs.update({nodeName: matrix[i]})
        nodeTHolder.append(temp)
        nodeName = chr(ord(nodeName) + 1)

    # Creating our server sockets and putting them into a dictonary with the corresponding Node
    receiverPort = 2000

    temp2 = 'A'
    for i in range(len(matrix[0])):
        sd.update({temp2: receiverPort})
        temp2 = chr(ord(temp2) + 1)
        receiverPort += 1

    # Send each node and weight to neighbors
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] != 0 and matrix[i][j] != 999999:
                nodeTHolder[i].setNeighbor(nodeTHolder[j].nodeName, matrix[i][j])


# Node class to create an object
class NodeThread(object):
    def __init__(self, nn):
        self.nodeName = nn
        self.neighbor = {}  # Will hold the neighbor as key and weight as value
        self.DVs = {}
        self.upDV = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def setNeighbor(self, n, nWeight):
        self.neighbor.update({n: nWeight})


if __name__ == "__main__":
    main()
