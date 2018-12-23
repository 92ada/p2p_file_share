# P2P download Protocol

### Group Members:

11611601 何海彬

11612325 陆心童 

11612326 张思宇



### Architecture

#### Roles



##### **seed** 

A seed is an identifier for a file. It includes:

1. file name
2. file length
3. hash value for the whole file 
4. a list of hash values for each chunk of the file



##### **tracker**

In a P2P file sharing system, the main function of the tracker is to manage status of all nodes in the network, and maintain information of all avaialble files for different nodes. The function can be concluded as :

- **Node management**
  - **Handle periodic status update (including seed list update)**
    Each node will periodically send message to tracker to update the seeds it has. In our design, each seed has its time to live. If a seed hasn't been update by its seeder for a certain time it will be deleted from the seed list held by the tracker. 
- **File sharing **
  - **Maintain a seed list of files held by each node in the network.**
    When a node join the network, it will sends a list of all its nodes to the tracker. When a node send a  and successfully downloaded the file from seeders, it will update its file list and send it to the tracker. The tracker need to handle these information and maintain a file list with files and corresponding seeders for query. 
  - **Handle request for files:**
    When receiving a request for a specific file, the tracker should check the seed list it maintains, and return the address of all available seeders for sharing the requested file. 

##### **node**

In a P2P file system, a node in the network might send request to the tracker for seeds of the files, as well as servers as seeder to provide file it holds to other nodes: 

- **status maintenance**

  - **update status**

    In correspondence to the handle message of tracker, each node acting as a seeder should periodically update all its seeds to the tracker. 

- **file request & sharing**

  - **send download request**
    A node will send a request for certain file to the tracker and expect a set of available seeds.
  - **handle a download request**
    A node might receive file request form other nodes, and will need to send requested partial to the requesting nodes. 



#### Procedure 

##### **Update Status:**

1. node: make seeds for all its available file, and send the seeds to tracker with head *Update*
2. tracker: handling the accepted inform and updated the seed list it kept 



##### **Download **

Before the download procedure, we suppose the node has acquire the seed from somewhere else. In our program, we simply make the seed with a local file, and try to download it from other nodes. 

1. node: obtain the *total file hash*  and send it to the tracker with header *Query*
2. tracker:  check dictionary it held, return ip address of all nodes holding that file to the requesting node 
3. user: 
   1. Send seed with header *Test* to all address obtain from tracker, to see if the nodes with these addresses do have this file (perhaps they do not hold the requested file anymore, but they has not update file list to the tracker)
   2. Download chunks of the file from nodes available. 





### Implementation

#### Representation of seeds

*Seeds* are used to identify a file. It includes:

1. file name
2. file length
3. hash value for the whole file 
4. a list of hash values for each chunk of the file

When a tracker check for requested file, the only message used is the *hash value for the whole file*. 



#### Implementation of asynchronous operations 

In our design, there are a lot of asynchronous operations. Thus, we use the *asynchronous* library for implementation. 

For **tracker**, two tasks are executed in the event loop:

1. Update seed list: Check timestamp in each seed list, and then deleted seeds that are timeout. 
2. Start server and listen for connection: The detail operation depends on the operation code. Specifically 
   1. get_torrent_list : Means to return a list with all the seeds it currently holds
   2. seed_torrent_list：Update the seed list according to update messages
   3. get_seeder_list: Return an address list including requested file. 

For **node** (implemented on *server.py* since its server as a file server for most of its time), only one task is executed in the event loop, i.e. a dispatch function to listen to file request of a user.  

The *download* function, i.e. the function for a node to request and download file with the seed it holds is implanted in *client.py*. The tasks executed are sequential: 

1. update current status of the node to *tracker*
2. get the address list with given *seed* from tracker 
3. check the availability of the addresses in the address list 
4. download the file and make it up. 