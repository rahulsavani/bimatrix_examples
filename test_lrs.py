import os
import examples
from fractions import Fraction
import inspect

def get_eq_from_lrs_output(fname='tmp/out'):

    """
    takes as input the output file from lrsnash

    returns equilibria as strings representing fractions
    in eq1 and eq2
    
    and the corresponding payoffs in p1 and p2
    
    in addition returns index1 and index2
    which are needed for the clique enumeration
    needed to get all equilibrium components
    BUT NOT
    just for testing lrs equilibrium output (as we do here)

    for a non-degenerate game index1==index2== 1...#extreme eq
    """

    #file = 'out'
    #file = '../bimatrix/games/out'

    f= open(fname, 'r')
    x={}
    i=1
    for line in f.readlines():
        x[i] = line.split()
        i+=1

    ######################################################
    # Number of extreme equilibria
    ######################################################
    #print x[i-6]
    numberOfEq = int(x[i-6][4])

    # store mixed strategies as arrays of string probabilities 
    e1 = {}
    e2 = {}

    # store payoffs 
    p1 = {}
    p2 = {}

    ######################################################
    # DICTIONARIES for mixed strategies 
    ######################################################
    # Mixed strategies strings as keys
    # strings like '1/2,1/4,1/4'
    # Indices as values

    dict1 = {}
    dict2 = {}

    # store indices for mixed strategies for input to clique algorithm
    index1 = {}
    index2 = {}

    # next index for input to clique algorithm
    c1 = 1
    c2 = 1

    eq = -1 # array index of current equilibrium 
    # (shared by e1,e2,p1,p2,index1,index2) 

    count = 0 # how many equilibria of II to match with one

    for j in range(8,len(x)-6):

        if not x[j]:
            count = 0 # reset count, ready for next set of II's strategies
            continue
        elif x[j][0] == "2": 
            processII = True
            count += 1 # one more of II's strategies to pair with I's
            eq += 1
        elif x[j][0] == "1": 
            processII = False

        l = len(x[j])
        ##########################################
        # Player II
        ##########################################
        if processII : # loop through all mixed strategies of II
            e2[eq] = x[j][1:l-1]
            p1[eq] = x[j][l-1] # payoffs swapped in lrs output

            e2string = ','.join(e2[eq])

            if e2string not in dict2.keys():
                dict2[e2string] = c2
                c2 += 1
            index2[eq] = dict2[e2string] 
        else:
            #################################################
            # Player I
            #################################################
            # Now match all these count-many strategies of II 
            # with # subsequent strategy of I

            e1[eq] = x[j][1:l-1]
            p2[eq] = x[j][l-1] # payoffs swapped in lrs output

            e1string = ','.join(e1[eq])

            if e1string not in dict1.values():
                dict1[e1string] = c1
                c1 += 1
            index1[eq] = dict1[e1string] 

            for i in range(1,count):
                e1[eq-i] = e1[eq] 
                p2[eq-i] = p2[eq]
                index1[eq-i] = index1[eq] 

    # convert (from dict of lists of lists of strings) to lists of lists of fractions
    e1 = [[Fraction(x) for x in e] for e in e1.values()]
    e2 = [[Fraction(x) for x in e] for e in e2.values()]

    # we don't need index1 and index2 for our tests here
    return {'e1': e1, 
            'e2': e2, 
            'p1': p1, 
            'p2': p2}


def check_eq(eq_gen,eq_lrs):
    """

    check that the two sets of equilibria are the same:

    - first check they have the same cardinality
    - then check that all equilibria from eq_gen appear in eq_lrs

    """

    if len(eq_gen['e1']) != len(eq_lrs['e2']):
        "Lengths not equal:", len(eq_gen['e1']), len(eq_lrs['e2'])
        return False

    eq_gen_zipped = zip(eq_gen['e1'],eq_gen['e2'])
    eq_lrs_zipped = zip(eq_lrs['e1'],eq_lrs['e2'])

    for eg in eq_gen_zipped:
        #print "LOOKING FOR"
        #print eg
        #print "========================="
        # have not found eg yet
        found = False
        for el in eq_lrs_zipped:
            #print el
            if eg == el:
                # found eg break
                found = True
                break
        if not found:
            # never found eg
            return False

    # found every eg
    return True

def run_lrs(name,eq_gen=None):
    fname = os.path.join("tmp",name)

    # first use setnash to create input for lrs
    m1 = os.path.join("tmp","m1")
    m2 = os.path.join("tmp","m2")
    os.system("bin/setnash " + fname + " " + m1 + " " + m2 + ">/dev/null")

    # use lrs to solve game
    out = os.path.join("tmp","out") 
    os.system("bin/nash " + m1 + " " + m2 + " >" + out)

    # read lrs output
    eq_lrs = get_eq_from_lrs_output()      

    return eq_lrs 

def check_game(function, *args):
    eq_gen = function(*args) 
    eq_lrs = run_lrs(eq_gen['fname'])
    return check_eq(eq_gen,eq_lrs)

def main():

    print check_game(examples.battle_of_the_sexes)
    print check_game(examples.dual_cyclic_6x6_75)

    for d in range(10,100,10):
        # linear
        print check_game(examples.hide_and_seek,d)
    
    for d in [5,10,30]:
        # quadratic
        print check_game(examples.all_zero,d)

    for d in [5,10,12]:
        # exponential, so careful with d
        print check_game(examples.coordination,d)

if __name__ == "__main__":
    main()
