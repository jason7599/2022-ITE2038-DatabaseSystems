import csv;
import sys;

sys.setrecursionlimit(10**5);

DEGREE = 0;
ROOT = None;

class Record:
    def __init__(self, key, value = None, child = None):
        self.key = key;
        self.value = value;
        self.child = child;
    def __str__(self):
        return str(self.key)+","+str(self.value);

class Node:
    def __init__(self):
        self.isLeaf = True;
        self.keyCount = 0;
        self.records = [];
        self.next = None;

    def addRecord(self, pos, record):
        self.keyCount+=1;
        self.records.insert(pos, record);

    def removeRecord(self, pos=0):
        self.keyCount-=1;
        return self.records.pop(pos);

    def getChild(self, pos=0):
        return self.records[pos].child;

    def __str__(self):
        res = "";
        if self.keyCount==0:
            return res;
        for i in range(len(self.records)):
            res+=str(self.records[i].key);
            if self.isLeaf:
                res+=":"+str(self.records[i].value);
            if i != len(self.records)-1: res+=",";
        return res;

def splitNode(node):

    mid = DEGREE // 2;

    newSibling = Node();
    newParent = Node();

    newParent.isLeaf = False;
    newSibling.isLeaf = node.isLeaf;

    newParent.addRecord(0, node.records[mid]);
    newParent.records[0].child = node;
    newParent.next = newSibling;

    # LeafNode들은 LinkedList처럼
    if node.isLeaf: node.next = newSibling;
    else: node.next = node.getChild(mid);

    t = mid if DEGREE%2!=0 else mid-1;

    for i in range(t):
        newSibling.addRecord(i, node.removeRecord(mid+1));
    if node.isLeaf:
        newSibling.addRecord(0, node.records[mid]);
    node.removeRecord(mid);

    return newParent;

def insertKey(node, record):
    
    pos = 0; # 들어갈 위치
    while pos < node.keyCount:
        if node.isLeaf and record.key == node.records[pos].key:
            # Duplicate keys not allowed
            return node;
        if record.key < node.records[pos].key: break;
        pos+=1;

    # Leaf이면 그냥 삽입
    if node.isLeaf:
        node.addRecord(pos, record);
        # leaf이면서 ROOT인 경우에 split.
        if node.keyCount == DEGREE and node == ROOT:
            node = splitNode(node);
        # 그냥 leaf면 부모에서 처리
        
    # non-leaf
    else:
        childNode = None; #삽입 당할 아이
        #맨 오른쪽
        if pos == node.keyCount: childNode = node.next;
        else: childNode = node.getChild(pos);
        
        childNode = insertKey(childNode, record);

        #자식 터짐.
        if childNode.keyCount == DEGREE:

            tempL = childNode.getChild(DEGREE//2);
            tempR = childNode.next;

            childNode = splitNode(childNode);

            childNode.records[0].child.next = tempL;
            childNode.next.next = tempR;

            #맨 오른쪽에 들어갔으면 전체(node)의 next 갱신
            if pos == node.keyCount: node.next = childNode.next;
            #왼쪽 child 갱신
            else: node.records[pos].child = childNode.next;

            # 병합
            node.addRecord(pos, childNode.records[0]);

            #split에서 해줬는데 왜 안되는지 모르겠음
            #leaf node 연결
            if childNode.getChild().isLeaf:
                # print("child is leaf; update linkedlist")
                childNode.records[0].child.next = childNode.next;

        if node.keyCount == DEGREE and node == ROOT:
            # printTree(node, Color.RED);
            # print("ROOT overflow. Splitting:",node);

            tempL = node.getChild(DEGREE//2);
            tempR = node.next;

            node = splitNode(node);

            node.records[0].child.next = tempL;
            node.next.next = tempR;

    return node;

def deleteKey(node, key):
    # 삭제/탐색 위치
    pos = 0;

    if node.isLeaf:

        while pos < node.keyCount:
            if key == node.records[pos].key: break;
            pos+=1;

        if pos == node.keyCount:
            return node;
        # leaf에서 그냥 삭제
        node.removeRecord(pos);


    # child로 내려가서 삭제
    else:
        # non-leaf node에도 존재한다면 이후 지워줘야함 
        inIndexNode = False;

        while pos < node.keyCount:
            if key < node.records[pos].key: break;
            if key == node.records[pos].key: 
                # print("Key to delete found in indexNode",node);
                inIndexNode = True;
            pos+=1;

        # key 지울 childNode
        childNode = None;
        if pos == node.keyCount: childNode = node.next;
        else: childNode = node.getChild(pos);

        childNode = deleteKey(childNode, key);

        minKeys = DEGREE//2-1 if DEGREE%2==0 else DEGREE//2; 

        # 자식 underflow
        if childNode.keyCount < minKeys:
            # print("childNode underflow",childNode);

            leftChild = None;
            rightChild = None;

            if pos > 0: leftChild = node.getChild(pos-1);

            if pos+1 == node.keyCount: rightChild = node.next;
            elif pos+1 < node.keyCount: rightChild = node.getChild(pos+1);

            # 왼쪽에서 Steal
            if leftChild is not None and leftChild.keyCount > minKeys:
                
                if childNode.isLeaf:
                    # print("Stealing",leftChild.records[leftChild.keyCount-1].key,"from leftChild",leftChild);
                    stealKey = leftChild.records[leftChild.keyCount-1].key
                    stealValue = leftChild.removeRecord(leftChild.keyCount-1).value;
                    # 이렇게 새로 Record 안 만들어주면 이상해짐
                    childNode.addRecord(0, Record(stealKey, stealValue));
                    node.records[pos-1] = Record(stealKey, stealValue, leftChild);

                # 부모 통해서 뺏기
                else:
                    # redistribute 전에도 미리 해줘야 한다.
                    if inIndexNode:
                        for i in range(node.keyCount):
                            if key == node.records[i].key:
                                # print("updating indexnode",node);
                                nKey, nVal = getLeftMostKeyAndValue(childNode);
                                node.records[i].key = nKey;
                                node.records[i].value = nVal;
                                # print("updated indexnode",node);
                                break;
                        inIndexNode = False;

                    # print("redistributing with leftChild");

                    # 부모
                    stealKey = node.records[pos-1].key;
                    stealValue = node.removeRecord(pos-1).value;
                    # print(stealKey,"from parent, for",childNode);

                    # 부모에서 childNode로
                    childNode.addRecord(0, Record(stealKey, stealValue, leftChild.next));
                        
                    # leftChild의 new next
                    tempR = leftChild.getChild(leftChild.keyCount-1);

                    # leftChild
                    stealKey = leftChild.records[leftChild.keyCount-1].key;
                    stealValue = leftChild.removeRecord(leftChild.keyCount-1).value;
                    # print(stealKey,"from leftChild, for",node);

                    # leftChild에서 부모로
                    node.addRecord(pos-1, Record(stealKey, stealValue, leftChild));

                    leftChild.next = tempR;

            # 오른쪽에서 Steal
            elif rightChild is not None and rightChild.keyCount > minKeys:

                if childNode.isLeaf:
                    # print("Stealing",rightChild.records[0].key,"from rightChild",rightChild);

                    stealKey= rightChild.records[0].key
                    stealValue = rightChild.removeRecord(0).value;

                    childNode.addRecord(childNode.keyCount, Record(stealKey, stealValue));
                    # 여기선 rightChild에서 successor 찾는게 맞다
                    # node.swapKey(pos, getLeftMostKey(rightChild));
                    # node.records[pos].key = getLeftMostKey(rightChild);
                    stealKey= rightChild.records[0].key
                    stealValue = rightChild.records[0].value;

                    node.records[pos] = Record(stealKey, stealValue, childNode);

                else:
                    # redistribute 전에도 미리 해줘야 한다.
                    if inIndexNode:
                        for i in range(node.keyCount):
                            if key == node.records[i].key:
                                # print("updating indexnode",node);
                                nKey, nVal = getLeftMostKeyAndValue(childNode);
                                node.records[i].key = nKey;
                                node.records[i].value = nVal;
                                # print("updated indexnode",node);
                                break;
                        inIndexNode = False;

                    # print("redistributing with rightChild");

                    stealKey = node.records[pos].key;
                    stealValue = node.removeRecord(pos).value;

                    # 부모에서 childNode로
                    childNode.addRecord(childNode.keyCount, Record(stealKey, stealValue, childNode.next));

                    # childNode의 new next
                    tempR = rightChild.getChild();

                    stealKey = rightChild.records[0].key;
                    stealValue = rightChild.removeRecord(0).value;

                    # rightChild에서 부모로
                    node.addRecord(pos, Record(stealKey, stealValue, childNode));

                    # childNode의 next 갱신
                    childNode.next = tempR;

            # Merge
            else:
                # Merge할땐 이걸 미리 해줘야 할 듯?
                if inIndexNode:
                    for i in range(node.keyCount):
                        if key == node.records[i].key:
                            # print("updating indexnode",node);
                            nKey, nVal = getLeftMostKeyAndValue(childNode);
                            node.records[i].key = nKey;
                            node.records[i].value = nVal;
                            # print("updated indexnode",node);
                            break;
                    inIndexNode = False;

                if leftChild is not None:

                    # print("merging with leftChild", leftChild);

                    temp = leftChild.keyCount;

                    # childNode를 leftChild로 이동
                    for i in range(childNode.keyCount):
                        leftChild.addRecord(leftChild.keyCount+1, childNode.removeRecord(0));
                    
                    # childNode를 가리키던 child포인터 leftChild를 가리키도록 갱신
                    if pos == node.keyCount: node.next = leftChild;
                    else: node.records[pos].child = leftChild;

                    # parentNode에서 빼주기
                    if childNode.isLeaf:
                        # leftChild가 존재하므로 pos-1은 무조건 있
                        node.removeRecord(pos-1);
                    else:
                        # parentNode에서 하나 주기 
                        # print("Getting",node.records[pos-1].key,"from parent")
                        # print("temp =",temp)
                        leftChild.addRecord(temp, node.removeRecord(pos-1));
                        leftChild.records[temp].child = leftChild.next;

                    # leftChild.next 갱신
                    leftChild.next = childNode.next;

                    if node == ROOT and node.keyCount == 0:
                        node = leftChild;

                # 사실상 mergeRight는 childNode가 가장 왼쪽에 있을때만 실행
                else:
                    # print("merging with rightChild", rightChild);

                    # ROOT의 record가 들어갈 위치
                    temp = childNode.keyCount;

                    # rightChild에서 childNode으로 이동
                    for i in range(rightChild.keyCount):
                        childNode.addRecord(temp+i, rightChild.removeRecord(0));

                    # rightChild를 가리키던 포인터 childNode로 갱신
                    if pos+1 == node.keyCount: node.next = childNode;
                    else: node.records[pos+1].child = childNode;

                    if childNode.isLeaf:
                        node.removeRecord(pos);
                    else: 
                        # print("Getting",node.records[pos].key,"from parent")
                        childNode.addRecord(temp, node.removeRecord(pos))
                        childNode.records[temp].child = childNode.next;

                    childNode.next = rightChild.next;

                    if node == ROOT and node.keyCount == 0:
                        # print("fixing empty ROOT.")
                        node = node.next;

                    # printTree(ROOT, Color.BLUE)

        if inIndexNode:
            for i in range(node.keyCount):
                if key == node.records[i].key:
                    # print("updating indexnode",node);
                    nKey, nVal = getLeftMostKeyAndValue(childNode);
                    node.records[i].key = nKey;
                    node.records[i].value = nVal;
                    # print("updated indexnode",node);
                    break;

    return node;

def getLeftMostKeyAndValue(node):

    successor = node;

    while not successor.isLeaf:
        if successor.keyCount != 0: successor = successor.getChild();
        # merge과정 후 node의 child가 1개가 되는 불가피한 상황을 위해서
        else: successor = successor.next;

    if successor.keyCount == 0:
        return None, None;
    else:
        # print("successor key =",successor.records[0].key)
        return successor.records[0].key, successor.records[0].value;

def singleKeySearch(key):

    search = ROOT;
    path = "";

    while not search.isLeaf:

        pos = 0;
        path+=str(search)+"\n";

        while pos < search.keyCount:
            if key <= search.records[pos].key:
                break;
            pos+=1;
        # 일치하면 그 오른쪽으로 들어가야하니까
        if pos < search.keyCount:
            if key == search.records[pos].key:
                pos+=1;

        if pos == search.keyCount:
            search = search.next;
        else:
            search = search.getChild(pos);
    
    pos = 0;
    while pos < search.keyCount:
        if key <= search.records[pos].key:
            break;
        pos+=1;
    
    if pos < search.keyCount and key == search.records[pos].key:
        path+=str(search.records[pos].value);
        print(path);
    
    else: print("NOT FOUND");

def rangedSearch(start, end):

    search = ROOT;
    res = "";

    while not search.isLeaf:
        pos = 0;
        while pos < search.keyCount:
            if start <= search.records[pos].key:
                break;
            pos+=1;
        if pos < search.keyCount:
            if start == search.records[pos].key:
                pos+=1;
        
        if pos == search.keyCount:
            search = search.next;
        else:
            search = search.getChild(pos);
    
    while search is not None:
        for record in search.records:
            if record.key > end:
                if len(res) == 0:
                    res = "NOT FOUND";
                print(res);
                return;
            if start <= record.key:
                res+=str(record)+"\n";
        search = search.next;
    
    if len(res) == 0:
        res = "NOT FOUND";

    print(res);

def saveTree(fileName):
    global ROOT;

    with open(fileName, "w") as file:
        file.write("#"+str(DEGREE)+"\n");
        q = [ROOT];
        while len(q) != 0:
            t = len(q);
            for i in range(t):
                cur = q.pop(0);
                file.write(str(cur));
                if i != t-1:
                    file.write("/");
                if not cur.isLeaf:
                    for record in cur.records:
                        q.append(record.child);
                    q.append(cur.next);
            file.write("\n");
    
def loadTree(fileName):
    global DEGREE, ROOT;

    with open(fileName, "r") as file:
        
        lines = file.readlines();

        # 첫번째 줄
        DEGREE = int(lines.pop(0)[1:]);

        # with open 에서 return해도 close는 자동으로 실행
        if len(lines) == 0:
            ROOT = Node();
            return;
        
        # leafNode 정보, 마지막 줄
        lastLine = lines.pop();
        leafNodes = lastLine.split("/");

        # reverse bfs
        children = [];

        for leafNode in leafNodes:
            new = Node();

            # linkedList 연결
            if len(children) != 0:
                children[len(children)-1].next = new;

            records = leafNode.split(",");

            for record in records:
                key, value = map(int, record.split(":")); 
                new.addRecord(new.keyCount, Record(key, value));
                
            children.append(new);

        # 역순으로 올라가면서 child연결
        for line in reversed(lines):
            nodes = line.split("/");

            for node in nodes:
                new = Node();
                new.isLeaf = False;

                records = node.split(",");

                for record in records:
                    key = int(record);
                    child = children.pop(0);
                    new.addRecord(new.keyCount, Record(key, None, child));

                new.next = children.pop(0);
                children.append(new);

        ROOT = children[0];

def main():
    global ROOT;
    # create
    if sys.argv[1] == "-c":
        with open(sys.argv[2], "w") as file:
            file.write("#"+sys.argv[3]);
    # insert
    elif sys.argv[1] == "-i":
        loadTree(sys.argv[2]);
        with open(sys.argv[3],"r") as file:
            insertList = csv.reader(file, delimiter=",");
            for insert in insertList:
                key = int(insert[0]);
                value = int(insert[1]);
                ROOT = insertKey(ROOT, Record(key, value));
        saveTree(sys.argv[2]);
    # delete
    elif sys.argv[1] == "-d":
        loadTree(sys.argv[2]);
        with open(sys.argv[3], "r") as file:
            deleteList = csv.reader(file);
            for delete in deleteList:
                ROOT = deleteKey(ROOT, int(delete[0]));
        saveTree(sys.argv[2]);
    # singleKeySearch
    elif sys.argv[1] == "-s":
        loadTree(sys.argv[2]);
        singleKeySearch(int(sys.argv[3]));
    # rangedSearch
    elif sys.argv[1] == "-r":
        loadTree(sys.argv[2]);
        start = int(sys.argv[3]);
        end = int(sys.argv[4]);
        rangedSearch(start, end);

main();
