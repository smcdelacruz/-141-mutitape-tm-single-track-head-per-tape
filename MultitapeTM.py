"""
CMSC 141
Multitape Turing Machine - Single Head & Track Per Tape
Authored by: Sophe Mae C. Dela Cruz
"""

START_HEAD_INDEX = 2
INITIAL_BLANK_SIZE = 5

class Tapes:
    def __init__(self, blank, initial_symbol=''):
        # initial symbol from the user
		# adds two Blank symbols per both ends to make it an infinite tape
        self.blank = blank
        self.tape_symbols = [blank, blank] + list(initial_symbol) + [blank, blank]
        self.tapeHead = START_HEAD_INDEX    # current tape head is found at INDEX 2 due to blank symbols

    def read_current_symbols(self):
        """Reads the current tape symbol/s under the tape head."""
        return self.tape_symbols[self.tapeHead]
    
    def write_next_symbols(self, tape_symbol):
        """Writes the symbol/s on the current cell."""
        self.tape_symbols[self.tapeHead] = tape_symbol

    def move_direction(self, direction):
        """Moves the tape head on either L = left, R = right, or S = Stay."""
        if direction == 'L':
            self.tapeHead -= 1

            # Insert a blank cell in the tape if tapehead goes past the left end
            if self.tapeHead < 0:
                self.tape_symbols.insert(0, self.blank)
                self.tapeHead = 0

        elif direction == 'R':
            self.tapeHead += 1

            # Insert a blank cell in the tape if tapehead goes past the right end
            if self.tapeHead >= len(self.tape_symbols):
                self.tape_symbols.append(self.blank)

        elif direction == 'S':
            pass

    def __str__(self):
        output = ''
        for i, symbol in enumerate(self.tape_symbols):
            if i == self.tapeHead:
                # Square brackets marker to show the current tape head position
                output += "[" + symbol + "]"
            
            else:
                output += symbol
        return output

class State:
    """
	State class - for adding transition functions and update next state symbols \n
	Parameter/s:
		state_name -> start state of the TM
	"""

    def __init__(self, state_name):
        self.state_name = state_name    
        """
		tuple for transition functions
			key: current tape symbols
			values: next state, new tape symbols, and direction
		"""
        self.transitions = {}

    def add_transition(self, current_symbols, nextState, next_symbols, directions):
        """
		Adds new transition function in the TM. \n
		Parameter/s:
			current_symbols -> key of self.transitions; tuple of current tape symbols
			nextState -> next state; a string
			next_symbols -> tuple of new/next tape symbols
			directions -> tuple of direction of next tape symbols (L/R/S)
		"""
        self.transitions[current_symbols] = [nextState, next_symbols, directions]

    def get_transition(self, current_symbols):
        """Returns the transition for current tape symbols"""
        return self.transitions.get(current_symbols, None)

class MultiTapeTM:
    def __init__(self, start_state, final_state, blank='B', num_of_tapes=1):
        self.state = start_state            # current state
        self.start_state = start_state      # copy the original start state
        self.final_state = final_state      # accept state
        self.blank = blank
        self.states = {}                    # dictionary of all states
        self.tapes = [Tapes(blank) for _ in range(num_of_tapes)]    # creates Tapes
        
    def add_state(self, state):
        """Adds state to the TM"""
        self.states[state.state_name] = state
    
    def input_cell(self, string_input):
        """Loads the string input in tape 1 and sets up other tapes."""

        for i in range(len(self.tapes)):
            if i == 0:      # input will go in the first tape
                self.tapes[i].tape_symbols = [self.blank, self.blank] + list(string_input) + [self.blank, self.blank]
                self.tapes[i].tapeHead = START_HEAD_INDEX
            
            else:           # other tapes will be initially blank
                # Sets five (5) blank cells arbitrarily
                self.tapes[i].tape_symbols = [self.blank] * INITIAL_BLANK_SIZE
                self.tapes[i].tapeHead = START_HEAD_INDEX

        self.state = self.start_state  # resets machine to start state
        
    def read_symbols(self):
        """Reads the symbol under each tape head on all tapes; Returns a tuple of symbols"""
        return tuple(tape.read_current_symbols() for tape in self.tapes)
    
    def move_tape_head(self):
        """Moves tape head in one transition step"""

        current_state = self.states[self.state]     # get the current State object
        symbols = self.read_symbols()       # reads symbols on all tapes
        transitions = current_state.get_transition(symbols)

        if not transitions:
            # TM will halt if no transition defined
            print(f"No transition for state '{self.state}' with symbols {symbols}.\n TM HALTS.")
            return False
        
        # Dissects the transitions
        next_state, next_tape_symbols, directions = transitions
        self.state = next_state     # updates the state to the next state

        # Writes and moves for each tape
        for i in range(len(self.tapes)):
            self.tapes[i].write_next_symbols(next_tape_symbols[i])
            self.tapes[i].move_direction(directions[i])
        
        return True
    
    def is_accepted(self, string_input):
        """Runs the MTM until it accepts or rejects."""
        self.input_cell(string_input)
        
        while True:
            if self.state == self.final_state:
                return True
            
            if not self.move_tape_head():
                return False
            
    def __str__(self):
        """Returns a readable print of all tapes in MTM"""
        output = "State: " + self.state + "\n"

        # Prints each tape
        for i, tape in enumerate(self.tapes):
            output += f"Tape #{i+1}: {str(tape)}\n"
        return output

if __name__ == '__main__':
    # State names for the transitions
    state_names = ['q0', 'q1', 'q2', 'q3', 'q4','q5','q6','q7','q8','q9','q10','q11',
                    'q_final']

    states = {name: State(name) for name in state_names}

    def get_swap_transitions():
        transitions = []

        # ==== q0 - Find the second number until it reaches the separator '#'
        transitions.append(('q0', ('0','B','B'), 'q0', ('0','B','B'), ('R','S','S')))
        transitions.append(('q0', ('1','B','B'), 'q0', ('1','B','B'), ('R','S','S')))

        # If separator is found, erase it in the cell
        transitions.append(('q0', ('#','B','B'), 'q1', ('B','B','B'), ('R','S','S')))

        # ==== q1 - Transfer num2 on Tape 1
        transitions.append(('q1', ('0','B','B'), 'q1', ('B','0','B'), ('R','R','S')))
        transitions.append(('q1', ('1','B','B'), 'q1', ('B','1','B'), ('R','R','S')))
        transitions.append(('q1', ('B','B','B'), 'q2', ('B','B','B'), ('S','L','S')))

        # ==== q2 - Find the leftmost B symbol of num2 on Tape 2
        transitions.append(('q2', ('B','0','B'), 'q2', ('B','0','B'), ('S','L','S')))
        transitions.append(('q2', ('B','1','B'), 'q2', ('B','1','B'), ('S','L','S')))
        transitions.append(('q2', ('B','B','B'), 'q3', ('B','B','B'), ('L','R','S')))

        # ==== q3 - Find the rightmost symbol of num1 on Tape 1

        # Tape 2 symbols for t2 in ['0','1','B']
        # t2 = '0'
        transitions.append(('q3', ('B','0','B'), 'q3', ('B','0','B'), ('L','S','S')))
        transitions.append(('q3', ('0','0','B'), 'q4', ('0','0','B'), ('L','S','S')))
        transitions.append(('q3', ('1','0','B'), 'q4', ('1','0','B'), ('L','S','S')))

        # t2 = '1'
        transitions.append(('q3', ('B','1','B'), 'q3', ('B','1','B'), ('L','S','S')))
        transitions.append(('q3', ('0','1','B'), 'q4', ('0','1','B'), ('L','S','S')))
        transitions.append(('q3', ('1','1','B'), 'q4', ('1','1','B'), ('L','S','S')))

        # t2 = 'B'
        transitions.append(('q3', ('B','B','B'), 'q3', ('B','B','B'), ('L','S','S')))
        transitions.append(('q3', ('0','B','B'), 'q4', ('0','B','B'), ('L','S','S')))
        transitions.append(('q3', ('1','B','B'), 'q4', ('1','B','B'), ('L','S','S')))

        # ==== q4 - Find the leftmost symbol on Tape 1

        # t2 = '0'
        transitions.append(('q4', ('0','0','B'), 'q4', ('0','0','B'), ('L','S','S')))
        transitions.append(('q4', ('1','0','B'), 'q4', ('1','0','B'), ('L','S','S')))
        transitions.append(('q4', ('B','0','B'), 'q5', ('B','0','B'), ('R','S','S')))

        # t2 = '1'
        transitions.append(('q4', ('0','1','B'), 'q4', ('0','1','B'), ('L','S','S')))
        transitions.append(('q4', ('1','1','B'), 'q4', ('1','1','B'), ('L','S','S')))
        transitions.append(('q4', ('B','1','B'), 'q5', ('B','1','B'), ('R','S','S')))

        # t2 = 'B'
        transitions.append(('q4', ('0','B','B'), 'q4', ('0','B','B'), ('L','S','S')))
        transitions.append(('q4', ('1','B','B'), 'q4', ('1','B','B'), ('L','S','S')))
        transitions.append(('q4', ('B','B','B'), 'q5', ('B','B','B'), ('R','S','S')))

        # ===== q5 - Compare symbols on Tape 1 and Tape 2 if num1 > num2

        # If symbols are EQUAL, Move R
        transitions.append(('q5', ('0','0','B'), 'q5', ('0','0','B'), ('R','R','S')))
        transitions.append(('q5', ('1','1','B'), 'q5', ('1','1','B'), ('R','R','S')))
        # num1 > num2 -> SWAP
        transitions.append(('q5', ('1','0','B'), 'q6', ('1','0','B'), ('L','L','S')))
        transitions.append(('q5', ('1','B','B'), 'q6', ('1','B','B'), ('L','L','S')))
        
        # num1 > num2 when second number exhausted
        # If second number exhausted and first number still has digits, so A > B
        transitions.append(('q5', ('0','B','B'), 'q6', ('0','B','B'), ('L','L','S')))

        # num1 < num2 -> NO SWAP
        transitions.append(('q5', ('0','1','B'), 'q_final', ('0','1','B'), ('S','S','S')))
        transitions.append(('q5', ('B','1','B'), 'q_final', ('B','1','B'), ('S','S','S')))
        transitions.append(('q5', ('B','B','B'), 'q_final', ('B','B','B'), ('S','S','S')))

        # ==== q6 - Find the leftmost symbol on Tape 1 and Tape 2
        transitions.append(('q6', ('0','0','B'), 'q6', ('0','0','B'), ('L','L','S')))
        transitions.append(('q6', ('0','1','B'), 'q6', ('0','1','B'), ('L','L','S')))
        transitions.append(('q6', ('0','B','B'), 'q6', ('0','B','B'), ('L','L','S')))

        transitions.append(('q6', ('1','0','B'), 'q6', ('1','0','B'), ('L','L','S')))
        transitions.append(('q6', ('1','1','B'), 'q6', ('1','1','B'), ('L','L','S')))
        transitions.append(('q6', ('1','B','B'), 'q6', ('1','B','B'), ('L','L','S')))

        transitions.append(('q6', ('B','0','B'), 'q6', ('B','0','B'), ('L','L','S')))
        transitions.append(('q6', ('B','1','B'), 'q6', ('B','1','B'), ('L','L','S')))

        # If both Tape heads point to Blank, move to next state
        transitions.append(('q6', ('B','B','B'), 'q7', ('B','B','B'), ('S','R','R')))

        # ==== q7 - Transfer num2 from Tape 2 to Tape 3 (if num 1 > num 2)
        # (Tape 3 is temporary tape for copying)
        transitions.append(('q7', ('B','0','B'), 'q7', ('B','B','0'), ('S','R','R')))
        transitions.append(('q7', ('B','1','B'), 'q7', ('B','B','1'), ('S','R','R')))
        transitions.append(('q7', ('B','B','B'), 'q8', ('B','B','B'), ('S','L','L')))

        #  ==== q8 - Find the leftmost symbol on Tapes 2 and 3
        transitions.append(('q8', ('B','B','0'), 'q8', ('B','B','0'), ('S','L','L')))
        transitions.append(('q8', ('B','B','1'), 'q8', ('B','B','1'), ('S','L','L')))
        transitions.append(('q8', ('B','B','B'), 'q9', ('B','B','B'), ('R','R','S')))

        #  ==== q9 - Transfer num1 from Tape 1 to Tape 2 (if num 1 > num 2)
        transitions.append(('q9', ('0','B','B'), 'q9', ('B','0','B'), ('R','R','S')))
        transitions.append(('q9', ('1','B','B'), 'q9', ('B','1','B'), ('R','R','S')))
        transitions.append(('q9', ('B','B','B'), 'q10', ('B','B','B'), ('L','L','S')))

        #  ==== q10 - Find the leftmost symbol on Tapes 1 and 2
        transitions.append(('q10', ('B','0','B'), 'q10', ('B','0','B'), ('L','L','S')))
        transitions.append(('q10', ('B','1','B'), 'q10', ('B','1','B'), ('L','L','S')))
        transitions.append(('q10', ('B','B','B'), 'q11', ('B','B','B'), ('R','S','R')))

        #  ==== q11 - Transfer num2 from Tape 3 to Tape 1
        transitions.append(('q11', ('B','B','0'), 'q11', ('0','B','B'), ('R','S','R')))
        transitions.append(('q11', ('B','B','1'), 'q11', ('1','B','B'), ('R','S','R')))
        transitions.append(('q11', ('B','B','B'), 'q_final', ('B','B','B'), ('S','S','S')))

        return transitions

    def add_transition_func(state_dict, transitions):
        for state_name, current_symbols, next_state, new_symbols, direction in transitions:
            if state_name in state_dict:
                state_dict[state_name].add_transition(current_symbols, next_state, new_symbols, direction)

    def full_tape_str(tape):
        """Converts tapes into a clean string of symbols."""
        return ''.join(tape.tape_symbols).replace(tape.blank, '').strip()

    # Initialize MTM
    mtm = MultiTapeTM('q0', 'q_final', blank = 'B', num_of_tapes = 3)
    for state in states.values():
        mtm.add_state(state)

    transition_func = get_swap_transitions()
    add_transition_func(states, transition_func)

    input_string = "1011#1000"
    print("\nSwap A and B if A > B. Otherwise, do not swap.")
    print(f"Running MultiTape TM on the two binary numbers on tape 1: \n{input_string.rjust(14)}")

    accepted = mtm.is_accepted(input_string)

    for i, tape in enumerate(mtm.tapes, start=1):
        print(f" Tape ({i}): '{tape}'")

    print("\nMTM result:")
    for i, tape in enumerate(mtm.tapes, start = 1):
        print(f" Tape ({i}): '{full_tape_str(tape)}'")

    print("\n")
    