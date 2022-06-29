"""
author: Konrad Dagiel
"""
import math

class Process:
    """
    Processes only need a size for simulation purposes, and an id to be distinguished
    """
    def __init__(self,id,size):
        self._size=size
        self._id=id

class Node:
    """
    Tree structure means nodes point to their children and parent
    Nodes have a size, and can have a process

    Only leaf nodes are considered to be part of the memory, as
    outlined in the algorithm rundown.
    """
    def __init__(self, size, parent=None, process=None):
        self._left=None
        self._right=None
        self._parent=parent
        self._size=size
        self._process=process

    def split(self):
        """
        create 2 children, each half size. Since the node is no longer
        a leaf, it is not available to take a process in.

        The children are considered as part of the main memory.
        """
        self._left=Node(self._size//2,self)
        self._right=Node(self._size//2,self)
        return self._left

    def merge(self):
        """
        wipe a node and its buddy, meaning the parent is now a leaf and
        considered to be part of the main memory
        """
        self._parent._left=None
        self._parent._right=None
        return self._parent

    def __str__(self):
        return str(self._size)

    def getBuddy(self):
        """
        get the current nodes "buddy" aka sibling
        """
        if not self._parent:
            return None
        if self==self._parent._left:
            return self._parent._right
        elif self==self._parent._right:
            return self._parent._left
        return None

    def isLeaf(self):
        """
        test if a node is a leaf.
        """
        return self._left is None and self._right is None

    def listAvailableLeaves(self):
        """
        list all available spots in the memory
        """
        arr=[]
        self.allAvailableLeaf(arr)
        for i in range(len(arr)):
            arr[i]=arr[i]._size
        return arr


    def allAvailableLeaf(self, arr):
        """
        helper function to list all available memory locations in an array
        """
        if (not self):
            return
    
        # Check if current self is a leaf node and doesnt have a process
        if (not self._left and not self._right):
            if not self._process:
                arr.append(self)
            return
    
        # Traverse the left
        # and right subtree
        self._right.allAvailableLeaf(arr)
        self._left.allAvailableLeaf(arr)

    def minLeaf(self, spaceRequired):
        """
        returns the minimum size leaf that can fit the requested size.
        """
        arr=[]
        self.allAvailableLeaf(arr)
        minNode=Node(memorySize+1) #minNode initially bigger than memory
        for i in arr:
            if i._size>=spaceRequired and i._size<minNode._size:
                minNode=i
        #if found a suitable node, return. if not, return None
        return minNode if minNode._size < memorySize+1 else None 

    def allocate(self, process):
        """
        round space to a power of 2
        find min size suitable block
        split repeatedly until its size is the required space
        allocate the process to that block
        """
        print("Allocating process", process._id)
        #if block size is lower than minimum, set it to minimum
        #else round it to nearest power of 2
        spaceRequired = minBlockSize if process._size < minBlockSize else 2**(math.ceil(math.log(process._size, 2)))
        print("space required = ", spaceRequired)
        print("internal fragmentation = ", spaceRequired-process._size)
        x=self.minLeaf(spaceRequired)
        #if no min found, cannot allocate
        if not x:
            print("not enough space in memory, not allocated")
            print("----------------------------")
            return None

        #split repeatedly
        while x._size // 2 >= spaceRequired:
            print("splitting, new size=", x._size//2)
            x=x.split()
        print("found block, size=",x._size)

        #update allocated dictionary, so we know which process is in which block
        allocatedDict[process]=x

        #finally, allocate process
        x._process=process
        print("available blocks: ", self.listAvailableLeaves())
        print("----------------------------")
        return x

    def deallocate(self, process):
        """
        lookup our dict to find where this process is in memory
        deallocate it, and merge the block it was in if its buddy is free
        merge repeatedy while possible
        """
        print("De-allocating process",process._id)
        #can only de-allocate processes that have been allocated
        if process not in allocatedDict:
            print("no such process exists")
            print("----------------------------")
            return None
        x=allocatedDict[process]
        #update dict
        allocatedDict.pop(process)
        print("deallocated process:",process._id)
        x._process=None
        y=x.getBuddy()
        #repeatedly merge empty leaves
        while not y._process and y.isLeaf():
            print("buddy also empty, merging")
            temp=x._parent
            x.merge()
            x=temp
            y=x.getBuddy()
            if not y:
                print("available blocks: ", self.listAvailableLeaves())
                print("----------------------------")
                return process
        print("available blocks: ", self.listAvailableLeaves())
        print("----------------------------")
        return process


allocatedDict={} #this is used to track where each process is
memorySize=4096 #this is our initial memory size
minBlockSize=512 #this is the smallest allowed size for a block
root=Node(memorySize) #this is how we initialize our memory

p0=Process(0,1000)
p1=Process(1,1000)
p2=Process(2,1000)
p3=Process(3,3000)
p4=Process(4,400)

processList=[p0, p1, p2, p3, p4] #list of processes to be allocated

print("available blocks:", root.listAvailableLeaves())
print("----------------------------")
for process in processList:
    root.allocate(process)

#random order to deallocate
root.deallocate(p3)
root.deallocate(p2)
root.deallocate(p4)
root.deallocate(p1)
root.deallocate(p0)