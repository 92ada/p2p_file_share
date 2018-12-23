# P2P download Protocol

### Group Members:

11611601 何海彬

11612325 陆心童

11612326 张思宇



### Architecture

#### Roles

##### **tracker**

In a P2P file sharing system, the main function of the tracker is to manage status of all nodes in the network, and maintain information of all available files for different nodes. The function can be concluded as :

* **Node management**

  * **Handle register/leave request**
    When a node wants to join or leave the network, it will send request to the tracker. The tracker should keep a list of nodes in the network.

  * **Handle periodic status update (including file list update)**
    Each node will periodically send message to tracker to update its status (noticing the tracker it is still in the network, and update its file list if necessary). The tracker need to handle these messages and update the status of all nodes in the network.

* **File sharing **

  * **Maintain a file list of files held by each node in the network.**
    When a node join the network, it will sends its file list to the tracker. When a node requests some file and successfully downloaded the file from seeders, it will update its file list and send it to the tracker. The tracker need to handle these information and maintain a file list with files and corresponding seeders for query.
  * **Handle request for files:**
    When receiving a request for a specific file, the tracker should check the fie list it maintains, and return information about all available seeder to the requesting node.

##### **node**

In a P2P file system, a node in the network might send request to the tracker for seeds of the files, as well as servers as seeder to provide file it holds to other nodes. The function of node can be concluded as:

* **status maintenance**
  * **register to the network**
    A node needs to send request to the tracker to register to a network. This includes obtaining a list of all files it holds and send it to the tracker when requested.
  * **leave the network **
    A node needs to send request to the tracker to leave to a network.
  * update it status (including whether it is still in the network, and update the file list if necessary)
* **file request & sharing**
  * send file request
    A node will send a request for certain file to the tracker and expect a set of available seeds.
  * handle file request
    A node might receive file requests form other nodes, and will need to send requested partial to the requesting nodes.



#### Procedure

##### **Join:**

1. user: request to join
2. tracker: request for the file list
3. user: send file list to tracker
4. tracker: send ack to join



##### **Maintain:**

1. all users periodically send message to tracker, to inform it is still in the network
2. update file list if necessary



##### **Download **

1. user: request a file
2. tracker:  
   1. send a request for the status of all other nodes (whether it's available for file transferring, whether it needs to update the file list)
   2. querying requested file to get seeds, return a request all available dest IP and request message
3. user:
   1. for all available seeds the list, make decision for how much to download from which nodes.
   2. Open multiple processes, each for a node to request, and receive files
   3. After obtaining all contents of files, assemble them.



##### **Leave**

1. user: request to leave
2. tracker: ack to leave and delete all files related to the user.



### Implementation

#### Representation of seeds

**Data Structure:**

**Method of file querying:**



#### Nodes maintenance and update

**Conditional update:**



### References
