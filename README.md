### Roles

* tracker

  * keep a list of correspondence
    * userid, file list, address
    * map file name to a set of a set of request   
  * multiple processes
    * a process listen and build network (register new nodes)
    * a process handling file request

* user

  * request to join
  * request to leave
  * send file list
  * send file request
  * send transferring request (requesting, start download, finish download)
  * multiple processes
    * a process to listen to the request
    * a new process to request and after get request, add new processes for each node



### Procedure

#### Join:

1. user: request to join
2. tracker: request for file list
3. user: send file list
4. tracker ack to join



#### Maintain:

1. all users preodically send message to tracker, to inform it is still alive.
2. update file list if needed



#### Download

1. user: request a file
2. tracker: check in the list, retrun a request all avaialbale dest IP and request message
3. user:
   1. for all available user in the list, make decision.
   2. Open multiple processes, each for a node to reqeust, and recieve files
   3. After obtaining all files, assemble them.



#### Leave

1. user: request to leave
2. tracker: ack to leave and delete all files related to the user.



### Code Implementation

轮子：收信，发信

tracker：

* 进程1: 收听加入/退出
  * 如果收到了请求，向请求的user要求file list
  * 如果收到了file list，解析file list
  * 发送ack给user
* 进程2:收听文件request
  * 如果收到请求，根据request检索文件，并且将list中符合条件的内容都发回去

user：

* 启动：
  * 获取本地文件列表
  * 向tracker发送加入请求
  * 收到tracker的文件请求之后，发送本地文件列表
* 请求文件：
  * 发送需要的文件名
  * 从tracker接收所有可以获取文件的地方，并且选择分部分获取
  * 对于每一个node，开一个新的进程
    * 发送获取文件请求
    * 接收文件
  * 当所有进程都获取完成之后做assembling，获得完整文件
  * 向tracker更新文件列表
* 进程3：维护一个是否在网络中的状态
  * 如果状态为是：周期性更新，告诉tracker依然在网络中
  * 如果状态设成了否：下一次更新就会告诉tracker已经退出



### 任务分配

1. tracker
   1. 收听和处理加入请求，更新文件列表
   2. 收听更新信息和维护存在的用户和对应的文件列表
   3. 收听获取文件的请求，并向用户返回获取文件的请求
2. user (part 1)：
   1. 获取文件列表并储存
   2. 收到request时发送文件
   3. 文件的assembling
3. user (part 2):
   1. 进网请求部分
   2. 周期性维护状态
   3. report & slides



# 补充信息

seed: 文件名+文件长度+完整文件内容哈希+分部分哈希

下载过程：

1. 假定seed是client已经有的
2. client请求文件的时候会把 seed中文件的哈希部分发给tracker
3. tracker根据哈希返回所有认为可以用的address list
4. client通过"Test"向address list里面的address询问是否还有这个文件
5. 根据strategy确定下载地址，并且用异步io下载



tracker工作逻辑：

1. 启动server，监听收到的信息。如果收到了对应的信息，做处理。信息种类包括：
   1. get_torrent_list : 返回所有一个list，里面的种子
   2. seed_torrent_list：根据发过来的信息更新种子状态
   3. get_seeder_list: 返回一个有请求的种子的address的list
2. 任务2:根据每一个list上一次更新的时间，删除过期的list



当前任务：

1. 最后文件的组装和写入
2. 不同的seed的format的处理逻辑
3. producer + consumer 简化



seed相关函数：

```python
def make_seed(path):
    # format: file_name + '\n' + str(file_len) + '\n' + big_hash \
    #           + '\n' + small_hash[0] + '\n' + ... + '\n' + small_hash[n]
    # notice: convert str above to bytes
    ''' Create a seed file from given path (and related file) 
            -Input: path
            -Output: encoded value 
    '''
    
def make_big_hash(path):
    ''' Make hash for given file '''
    
def make_big_hash(path):
    ''' Make hash for given file '''
```





