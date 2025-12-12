from copy import copy

class eNFA:
    def __init__(self):
        # Attributes
        self.qStates = []
        self.sigma = []
        self.final_states = []
        self.initial = None
        self.transitions = {}

    # Displays the transitions after minimization
    def showTransitions(self):
        for state in self.transitions:
            for symbol in self.sigma:
                print(f"State {state} : {symbol} -> {self.transitions[state][symbol]}")

# Instantiate an eNFA object
enfa = eNFA()

# Input the eNFA values
enfa.qStates = ['q0', 'q1', 'q2', 'q3']
enfa.sigma = ['0', '1']
enfa.final_states = ['q3']
enfa.initial = 'q0'
enfa.transitions = {'q0': {'0': 'q1', '1': 'q0'}, 
                    'q1': {'0': 'q3', '1': 'q0'},
                    'q2': {'0': 'q3', '1': 'q0'},
                    'q3': {'0': 'q2', '1': 'q0'} 
                    }

# Initialize variables
new_eNFA = eNFA()
marked = {}
finalEq = []

# Initialize the marked pairs as non-distinguishable = False
def prepMarkedPairs():
    for state1 in enfa.qStates:
        marked[state1] = {}
        for state2 in enfa.qStates:
            marked[state1][state2] = False

# Mark pairs as distinguishable based on final states
def distinguishablePair():
    for state1 in enfa.qStates:
        for state2 in enfa.qStates:
            if (state1 in enfa.final_states) and (state2 not in enfa.final_states):
                marked[state1][state2] = True
            elif (state1 not in enfa.final_states) and (state2 in enfa.final_states):
                marked[state1][state2] = True

# Mark pairs as distinguishable based on transitions
def minimize():
    while True:
        change = False
        for state1 in enfa.qStates:
            for state2 in enfa.qStates:
                if state1 != state2 and not marked[state1][state2]:
                    for symbol in enfa.sigma:
                        t1 = enfa.transitions[state1][symbol]
                        t2 = enfa.transitions[state2][symbol]
                        if enfa.qStates.index(t1) != enfa.qStates.index(t2):
                            if marked[t1][t2]:
                                marked[state1][state2] = True
                                change = True
        if not change:
            break

# Groups the states into equivalence classes
def finalEquivalence():
    for state1 in enfa.qStates:
        for state2 in enfa.qStates:
            if state1 != state2 and not marked[state1][state2]:
                inserted = False
                for newState in finalEq:
                    if state1 in newState and state2 not in newState:
                        newState.append(state2)
                        inserted = True
                        break
                    elif state2 in newState and state1 not in newState:
                        newState.append(state1)
                        inserted = True
                        break
                    elif state1 in newState and state2 in newState:
                        inserted = True
                        break
                if not inserted:
                    finalEq.append([state1, state2])

    # Checks for ungrouped states and place them in a new group
    for state1 in enfa.qStates:
        allmarked = True
        for state2 in enfa.qStates:
            if state1 != state2 and not marked[state1][state2]:
                allmarked = False
        if allmarked:
            inGrp = False
            for grp in finalEq:
                if state1 in grp:
                    inGrp = True
            if not inGrp:
                finalEq.append([state1])

# Constructs the new minimized eNFA
def constructNew_eNFA():
    new_eNFA.sigma = copy(enfa.sigma)
    stateRelations = {}

    # Maps old states to new state group
    for group in finalEq:
        newState = ''.join(group)
        for state in group:
            stateRelations[state] = newState

    new_eNFA.initial = stateRelations[enfa.initial]
    for state in enfa.final_states:
        if stateRelations[state] not in new_eNFA.final_states:
            new_eNFA.final_states.append(stateRelations[state])

    # Adds new states to new eNFA
    new_eNFA.qStates = list(stateRelations.values())

    doneTransition = {}
    for state in new_eNFA.qStates:
        doneTransition[state] = False

    # Sets transitions for new eNFA
    for state in enfa.qStates:
        newState = stateRelations[state]
        if not doneTransition[newState]:
            new_eNFA.transitions[newState] = {}
            for symbol in enfa.sigma:
                new_eNFA.transitions[newState][symbol] = stateRelations[enfa.transitions[state][symbol]]
            doneTransition[newState] = True


def output():
    print(f'\nFollowing is the Minimized eNFA:\n\t{finalEq}\n')
    print('Following is the Minimized Transitions:')
    new_eNFA.showTransitions()

# Function calls
prepMarkedPairs()
distinguishablePair()
minimize()
finalEquivalence()
constructNew_eNFA()
output()