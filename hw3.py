import sys
import copy
from decimal import Decimal
import itertools

def compute_probability(query, nodes):
    distribution = compute_probability_distribution(query, nodes)
    return normalize(distribution, query)

def probability(Y,e,BN_structure):

    if BN_structure[Y]['type'] == 'decision':
        return 1.0

    if len(BN_structure[Y]['parents']) == 0:
        if e[Y] == True:
            return float(BN_structure[Y]['prob'])
        else:
            return 1.0-float(BN_structure[Y]['prob'])
    else:
        parentTuple = tuple(e[p] for p in BN_structure[Y]['parents'])

        if e[Y] == True:
            return float(BN_structure[Y]['condprob'][parentTuple])
        else:
            return 1-float(BN_structure[Y]['condprob'][parentTuple])

def order_sorting_network(BN_structure):
    nodes = BN_structure.keys()
    sort_nodes = []

    while len(sort_nodes) < len(nodes):
        for node in nodes:
            if node not in sort_nodes and all(p in sort_nodes for p in BN_structure[node]['parents']):
                sort_nodes.append(node)

    return sort_nodes

def sel_node(evidence,BN_structure,sort_nodes):
    new_node = set(evidence.keys())
    bol = [True if x in new_node else False for x in sort_nodes]
    sort_list = []
    new_list=[]
    count=0
    while len(new_node) != 0:
        count=count+1
        delet = new_node.pop()
        for p in BN_structure[delet]['parents']:
            new_node.add(p)
            parentIndex = sort_nodes.index(p)
            bol[parentIndex] = True

    
    for node in sort_nodes:
        if bol[sort_nodes.index(node)] == True:
            sort_list.append(node)

    return sort_list


def enumeration_ask(evidence, network):
    return enumerate_all(network.keys(), network, evidence)


def enumerate_all(network_vars, network, evidence):
    evidence = evidence.copy()

    if len(network_vars) == 0:
        return Decimal(1.0)

    first, rest = network_vars[0], network_vars[1:]
    node = network[first]

    if not isinstance(node, EventNode):
        return enumerate_all(rest, network, evidence)

    parents = node.parents
    unassigned_parents = [p for p in parents if p not in evidence]
    num_unassigned = len(unassigned_parents)

    if num_unassigned is not 0:
        parents_assignment = generate_assignments(num_unassigned)
        total = Decimal(0.0)
        for assignment in parents_assignment:
            for p, val in zip(unassigned_parents, assignment):
                evidence[p] = val

            if first in evidence:
                possible_child_vals = [evidence[first]]
            else:
                possible_child_vals = [True, False]

            for val in possible_child_vals:
                subevidence = evidence.copy()
                subevidence[first] = val
                total += node.probability(val, subevidence) * enumerate_all(rest, network, subevidence)
        return total
    else:
        if first in evidence:
            possible_child_vals = [evidence[first]]
        else:
            possible_child_vals = [True, False]

        total = Decimal(0.0)
        for val in possible_child_vals:
                subevidence = evidence.copy()
                subevidence[first] = val
                total += node.probability(val, subevidence) * enumerate_all(rest, network, subevidence)
        return total


def dseperate(literal):
    literal = literal.strip()
    num = literal.split(' = ')
    v1 = num[0].strip()
    v2 = num[1].strip()
    v3 = num[1].strip()
    v2 = True if v2 == '+' else False
    return v1,v2

def extract_parents(node, evidence):
    parents = {}
    for p in node.parents:
        if p in evidence:
            parents[p] = evidence[p]
    return parents

def selectNodes(sortedVariables, networkDictionary, observedVariables):

    x = observedVariables.keys()
    newNetwork = []

    bnPresence = [True if a in x else False for a in sortedVariables]

    for i in range (0, pow(len(sortedVariables), 2)):
        for v in sortedVariables:
            if bnPresence[sortedVariables.index(v)]!=True and any(bnPresence[sortedVariables.index(c)]==True for c in networkDictionary[v]['Children']):
                index = sortedVariables.index(v)
                bnPresence[index] = True

    for eachNode in sortedVariables:
        if bnPresence[sortedVariables.index(eachNode)] == True:
            newNetwork.append(eachNode)

    return newNetwork



def enumeration(vars,e,BN_structure):
    if len(vars) == 0:
        return 1.0

    Y = vars[0]

    if Y in e:
        result = probability(Y,e,BN_structure)*enumeration(vars[1:],e,BN_structure)
    else:
        sumProbability = []
        e2 = copy.deepcopy(e)
        for y in [True,False]:
            e2[Y] = y
            sumProbability.append(probability(Y,e2,BN_structure)*enumeration(vars[1:],e2,BN_structure))
        result =sum(sumProbability)

    return result

def parse_name_and_parents(line):
    if " | " not in line:
        name = line
        parents = []
    else:
        name, parents = line.split(" | ")
        parents = parents.split(" ")
    return name, parents

def parse_node_values(lines, num_parents):
    values = [None] * 2**num_parents
    for line in lines:
        value_and_parent_assignments = line.split(" ")
        v2 = Decimal(value_and_parent_assignments[0])

        parent_assignments = value_and_parent_assignments[1:]
        index = 0

        for assignment, i in zip(parent_assignments, xrange(num_parents)):
            if assignment == "+":
                index += 2**(num_parents-1-i)
        values[int(index)] = v2
    return values


c1=0
c2=0

sort_nodes = []
c3=0
c4=0
all_query = []
c11=False
c12=False
BN_structure = {}
#filename = sys.argv[-1]
filename = 'input.txt'
f = open(filename)
o = open('output.txt','w')
line = f.readline().strip()
while line != '******':
    c1=c1+1
    all_query.append(line)
    line = f.readline().strip()

line = ' '
while line != '':
    c2=c2+1
    parents = []

    line = f.readline().strip()

    root_parent = lines = line.split(' | ')
    node = root_parent[0].strip()

    if len(root_parent) != 1:
        parents = root_parent[1].strip().split(' ')

    BN_structure[node] = {}
    BN_structure[node]['parents'] = parents
    BN_structure[node]['children']=[]

    #Insert child for all the parents
    for p in parents:
        c4=c4+1
        BN_structure[p]['children'].append(node)

    if len(parents) == 0:
        c11=True
        line = f.readline().strip()
        if line == 'decision':
            #Decision Node
            BN_structure[node]['type'] = 'decision'
        else:
            #Node with prior probability
            BN_structure[node]['type'] = 'normal'
            BN_structure[node]['prob'] = line
    else:
        #Nodes with conditional probabilies
        condprob = {}
        c12=True
        for i in range(0,pow(2,len(parents))):
            line = f.readline().strip()
            lines = line.split(' ')
            prob = lines[0]
            lines = lines[1:]
            truth = tuple(True if x == '+' else False for x in lines)
            condprob[truth] = prob

        BN_structure[node]['type'] = 'normal'
        BN_structure[node]['condprob'] = condprob

    line = f.readline().strip()

sort_nodes = order_sorting_network(BN_structure)

for query in all_query:
    c3=c3+1
    complete_e = {}
    found_e = {}
    find_e=[]
    eval_e = {}

    action = query[:query.index('(')]
    action = action.strip()

    if action == 'P':
      
        bol1 = False
        result = 1.0

        c = query[query.index('(')+1:query.index(')')]
        inde_of = c.index('|') if '|' in c else -1

        if inde_of != -1:
            bol1 = True
            num = c[:c.index(' | ')]
            index_num=0
            ccc = num.strip()
            ccc = ccc.split(',')
            for x1 in ccc:
                x1=x1.strip()
                xVar,xVal = dseperate(x1)
                complete_e[xVar] = xVal
            num2=num
            num = c[c.index(' | ')+3:]

        else:
            num = c

        c = num.strip()
        c = c.split(',')
        for literal in c:
            literal=literal.strip()
            var,val = dseperate(literal)
            complete_e[var] = val
            eval_e[var] = val

        if bol1 == True:

            lis = sel_node(complete_e,BN_structure,sort_nodes)
            up = enumeration(lis,complete_e,BN_structure)
            
            sort_down = sel_node(eval_e,BN_structure,sort_nodes)
            down = enumeration(sort_down,eval_e,BN_structure)

            result = up/down

        else:
            sort_q_n = sel_node(eval_e,BN_structure,sort_nodes)
            result = enumeration(sort_q_n,eval_e,BN_structure)

        result = Decimal(str(result+1e-8)).quantize(Decimal('.01'))
        #print result
        s1=str(result)
        o.write(s1)
        o.write('\n')


    elif action == 'EU':
        #print 'action EU'
        bol1 = False
        result = 1.0

        c = query[query.index('(')+1:query.index(')')]
        inde_of = c.index('|') if '|' in c else -1

        if inde_of != -1:
            bol1 = True
            num = c[:c.index(' | ')]
            index_of=0
            ccc = num.strip()
            ccc = ccc.split(',')
            for x1 in ccc:
                x1=x1.strip()
                xVar,xVal = dseperate(x1)
                complete_e[xVar] = xVal

            num = c[c.index(' | ')+3:]
        #If only evidence is given
        else:
            num = c

        c = num.strip()
        c = c.split(',')
        for literal in c:
            literal=literal.strip()
            var,val = dseperate(literal)
            complete_e[var] = val
            eval_e[var] = val

        complete_e['utility'] = True

        if bol1 == True:
            
            lis = sel_node(complete_e,BN_structure,sort_nodes)
            up = enumeration(lis,complete_e,BN_structure)

            sort_down = sel_node(eval_e,BN_structure,sort_nodes)
            down = enumeration(sort_down,eval_e,BN_structure)

            result = up/down

        else:
            sort_q_n = sel_node(complete_e,BN_structure,sort_nodes)
            result = enumeration(sort_q_n,complete_e,BN_structure)


        result = int(round(result))
        #print result
        s2=str(result)
        o.write(s2)
        o.write('\n')


    else:

        bol1 = False
        result = {}
        maxi_l = []

        c = query[query.index('(')+1:query.index(')')]
        inde_of = c.index('|') if '|' in c else -1

        if inde_of != -1:
            bol1 = True
            num = c[:c.index(' | ')]

            ccc = num.strip()
            ccc = ccc.split(',')
            for x1 in ccc:
                equalIndex = x1.index('=') if '=' in x1 else -1
                if equalIndex != -1:
                    x1=x1.strip()
                    xVar,xVal = dseperate(x1)
                    complete_e[xVar] = xVal
                else:
                    maxi_l.append(x1.strip())

            num = c[c.index(' | ')+3:]
       
        else:
            num = c

        c = num.strip()
        c = c.split(',')
        for literal in c:
            equalIndex = literal.index('=') if '=' in literal else -1
            if equalIndex != -1:
                literal=literal.strip()
                var,val = dseperate(literal)
                complete_e[var] = val
                eval_e[var] = val
            else:
                maxi_l.append(literal.strip())

        complete_e['utility'] = True

        n = len(maxi_l)
        cpt = list(itertools.product([True, False], repeat=n))

        for i in range(0,len(cpt)):
            evi = copy.deepcopy(complete_e)
            v2 = ''
            j = 0
            for maxLiteral in maxi_l:
                evi[maxLiteral] = cpt[i][j]
                if cpt[i][j] == True:
                    v2 = v2 + '+ '
                else:
                    v2 = v2 + '- '
                j = j+1

            if bol1 == True:
                c12=True
                lis = sel_node(evi,BN_structure,sort_nodes)
                up = enumeration(lis,evi,BN_structure)

                sort_down = sel_node(eval_e,BN_structure,sort_nodes)
                down = enumeration(sort_down,eval_e,BN_structure)

                eachResult = up/down

            else:
                c12=False
                sort_q_n = sel_node(evi,BN_structure,sort_nodes)
                eachResult = enumeration(sort_q_n,evi,BN_structure)

            result[eachResult] = v2

        maxResult = max(result.keys())
        s1=str(result[maxResult])
        s2=str(int(round(maxResult)))
        s3=s1+s2
        #print s3
        #print "$$$"
        #print result[maxResult]+str(int(round(maxResult)))
        #     print best_assignment, int(round(highest_utility))
#                y2=best_assignment
                #print y2
#                y2=str(y2)
#                y3=(y2.find('('))
#                y4=y2[y3+1: -1].strip(' ')
#                y5=y4.split(',')
#                y5=y5.strip()
                
#                s11="(True,False,True)"
#                y64=(s11.find('('))
#                y644=s11[y64+1:-1]
#                y65=y644.split(',')
#                y6=len(y5)
            #    print y5[0]
             #   print y5[1]
                #print y6
#                yy=''
        #                x12=''
#                for i2 in range (len(yy)):
#                    x12=x12+yy[i2]
#                    
                #y66=y65[0]
                #print y66,y65[1],y65[2]
#                sx="Rakesh"
#                print sx[0]
                #print y3
                #print y3[1]
                #y4=y3[1].split(',')
                #print y4[0].strip()
                #print y4[1].strip()

        s3=str(result[maxResult]+str(int(round(maxResult))))
        o.write(s3)
        o.write('\n')