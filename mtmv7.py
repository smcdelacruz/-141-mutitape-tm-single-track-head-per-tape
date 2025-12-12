"""
CMSC 141
Multitape Turing Machine - Single Head & Track Per Tape
"""

START_HEAD_INDEX = 2
INITIAL_BLANK_SIZE = 5

class Tapes:
    def __init__(self, blank, initial_symbol=''):
        self.blank = blank
        # Adds padding to make it effectively infinite
        self.tape_symbols = [blank, blank] + list(initial_symbol) + [blank, blank]
        self.tapeHead = START_HEAD_INDEX

    def read_current_symbols(self):
        return self.tape_symbols[self.tapeHead]
    
    def write_next_symbols(self, tape_symbol):
        self.tape_symbols[self.tapeHead] = tape_symbol

    def move_direction(self, direction):
        if direction == 'L':
            self.tapeHead -= 1
            if self.tapeHead < 0:
                self.tape_symbols.insert(0, self.blank)     
                self.tapeHead = 0
        elif direction == 'R':
            self.tapeHead += 1
            if self.tapeHead >= len(self.tape_symbols):
                self.tape_symbols.append(self.blank)
        elif direction == 'S':
            pass

    def __str__(self):
        output = ''
        for symbol in range(len(self.tape_symbols)):
            if symbol == self.tapeHead:
                output += "[" + self.tape_symbols[symbol] + "]"
            else:
                output += self.tape_symbols[symbol]
        return output

class State:
    def __init__(self, state_name):
        self.state_name = state_name    
        self.transitions = {}

    def add_transition(self, current_symbols, nextState, next_symbols, directions):
        self.transitions[current_symbols] = [nextState, next_symbols, directions]

    def get_transition(self, current_symbols):
        return self.transitions.get(current_symbols, None)

class MultiTapeTM():
    def __init__(self, start_state, final_state, blank='B', num_of_tapes=1):
        self.state = start_state
        self.start_state = self.state
        self.final_state = final_state
        self.blank = blank
        self.states = {}
        self.tapes = [Tapes(blank) for _ in range(num_of_tapes)]
        
    def add_state(self, state):
        self.states[state.state_name] = state
    
    def input_cell(self, string_input):
        for i in range(len(self.tapes)):
            if i == 0:
                self.tapes[i].tape_symbols = [self.blank, self.blank] + list(string_input) + [self.blank, self.blank]
                self.tapes[i].tapeHead = START_HEAD_INDEX
            else:
                self.tapes[i].tape_symbols = [self.blank] * INITIAL_BLANK_SIZE
                self.tapes[i].tapeHead = START_HEAD_INDEX
        self.state = self.start_state
        
    def read_symbols(self):
        return tuple(tape.read_current_symbols() for tape in self.tapes)
    
    def move_tape_head(self):
        current_state = self.states[self.state]
        symbols = self.read_symbols()
        transitions = current_state.get_transition(symbols)

        if not transitions:
            print(f"No transition for state '{self.state}' with symbols {symbols}.\n TM HALTS.")
            return False
        
        next_state, next_tape_symbols, directions = transitions 
        self.state = next_state

        for i in range(len(self.tapes)):
            self.tapes[i].write_next_symbols(next_tape_symbols[i])
            self.tapes[i].move_direction(directions[i])
        return True
    
    def is_accepted(self, string_input):
        self.input_cell(string_input)
        while True:
            if self.state == self.final_state:
                return True
            if not self.move_tape_head():
                return False
            
    def __str__(self):
        output = "State: " + self.state + "\n"
        for tape in range(len(self.tapes)):
            output += "Tape #" + str(tape + 1) + ": " + str(self.tapes[tape]) + "\n"
        return output
    

if __name__ == '__main__':

     # Define States
    # state_names = [
    #     'q0', 'qcopy_num2_t2', 'q_rewind_t2_prep', 'q_find_num1_t1', 
    #     'q_rewind_t1_final', 'q_compare', 'q_swap_start_rewind', 
    #     'q_swap_p1_move', 'q_swap_p1_rewind', 'q_swap_p2_move', 
    #     'q_swap_p2_rewind', 'q_swap_p3_move', 'q_accept'
    # ]

    state_names = [
    'q0',                  # initial state, skip leading zeros on A
    'q_skipBzeros',        # skip leading zeros on B
    'q_len_compare',       # compare lengths first
    'qcopy_num2_t2', 
    'q_rewind_t2_prep', 
    'q_find_num1_t1', 
    'q_rewind_t1_final', 
    'q_compare', 
    'q_swap_start_rewind', 
    'q_swap_p1_move', 
    'q_swap_p1_rewind', 
    'q_swap_p2_move', 
    'q_swap_p2_rewind', 
    'q_swap_p3_move', 
    'q_accept'
]
    
    # Dictionary comprehension
    states = {name: State(name) for name in state_names}

    def get_swap_transitions():
        """Returns the list of transition functions for numeric comparison ignoring leading zeros."""
        transitions = []

        symbols = ['0', '1', 'B']

        # 1. Skip leading zeros on A (tape1)
        transitions.append(('q0', ('0','B','B'), 'q0', ('0','B','B'), ('R','S','S')))
        transitions.append(('q0', ('1','B','B'), 'q_skipBzeros', ('1','B','B'), ('S','S','S')))
        transitions.append(('q0', ('#','B','B'), 'q_accept', ('#','B','B'), ('S','S','S')))  # all zeros in A

        # 2. Skip leading zeros on B (tape2)
        for a in ['0','1']:
            transitions.append(('q_skipBzeros', (a,'0','B'), 'q_skipBzeros', (a,'0','B'), ('S','R','S')))
            transitions.append(('q_skipBzeros', (a,'1','B'), 'q_len_compare', (a,'1','B'), ('S','S','S')))
            transitions.append(('q_skipBzeros', (a,'B','B'), 'q_len_compare', (a,'B','B'), ('S','S','S')))

        # 3. Length comparison: if one number ends before the other
        # A > B -> SWAP
        for b in ['0','1']:
            transitions.append(('q_len_compare', ('0','B','B'), 'q_swap_start_rewind', ('0','B','B'), ('L','L','S')))
            transitions.append(('q_len_compare', ('1','B','B'), 'q_swap_start_rewind', ('1','B','B'), ('L','L','S')))
        # A < B -> ACCEPT
        for a in ['0','1']:
            transitions.append(('q_len_compare', ('B',a,'B'), 'q_accept', ('B',a,'B'), ('S','S','S')))
        # Equal length -> compare bits
        transitions.append(('q_len_compare', ('B','B','B'), 'q_compare', ('B','B','B'), ('L','L','S')))

        # 4. Bit-by-bit comparison
        transitions.append(('q_compare', ('0','0','B'), 'q_compare', ('0','0','B'), ('R','R','S')))
        transitions.append(('q_compare', ('1','1','B'), 'q_compare', ('1','1','B'), ('R','R','S')))
        transitions.append(('q_compare', ('1','0','B'), 'q_swap_start_rewind', ('1','0','B'), ('L','L','S')))  # A > B
        transitions.append(('q_compare', ('0','1','B'), 'q_accept', ('0','1','B'), ('S','S','S')))  # A < B
        transitions.append(('q_compare', ('B','B','B'), 'q_accept', ('B','B','B'), ('S','S','S')))   # equal

        # 5. Swap sequence (rewind & copy phases remain same)
        # Rewind
        for t1 in symbols:
            for t2 in symbols:
                if not (t1=='B' and t2=='B'):
                    transitions.append(('q_swap_start_rewind', (t1,t2,'B'), 'q_swap_start_rewind', (t1,t2,'B'), ('L','L','S')))
        transitions.append(('q_swap_start_rewind', ('B','B','B'), 'q_swap_p1_move', ('B','B','B'), ('S','R','R')))

        # Phase1: T2 -> T3
        transitions.append(('q_swap_p1_move', ('B','0','B'), 'q_swap_p1_move', ('B','B','0'), ('S','R','R')))
        transitions.append(('q_swap_p1_move', ('B','1','B'), 'q_swap_p1_move', ('B','B','1'), ('S','R','R')))
        transitions.append(('q_swap_p1_move', ('B','B','B'), 'q_swap_p1_rewind', ('B','B','B'), ('S','L','L')))

        # Rewind T2,T3
        for t3 in ['0','1']:
            transitions.append(('q_swap_p1_rewind', ('B','B',t3), 'q_swap_p1_rewind', ('B','B',t3), ('S','L','L')))
        transitions.append(('q_swap_p1_rewind', ('B','B','B'), 'q_swap_p2_move', ('B','B','B'), ('R','R','S')))

        # Phase2: T1 -> T2
        transitions.append(('q_swap_p2_move', ('0','B','B'), 'q_swap_p2_move', ('B','0','B'), ('R','R','S')))
        transitions.append(('q_swap_p2_move', ('1','B','B'), 'q_swap_p2_move', ('B','1','B'), ('R','R','S')))
        transitions.append(('q_swap_p2_move', ('B','B','B'), 'q_swap_p2_rewind', ('B','B','B'), ('L','L','S')))
        for t2 in ['0','1']:
            transitions.append(('q_swap_p2_rewind', ('B',t2,'B'), 'q_swap_p2_rewind', ('B',t2,'B'), ('L','L','S')))
        transitions.append(('q_swap_p2_rewind', ('B','B','B'), 'q_swap_p3_move', ('B','B','B'), ('R','S','R')))

        # Phase3: T3 -> T1
        transitions.append(('q_swap_p3_move', ('B','B','0'), 'q_swap_p3_move', ('0','B','B'), ('R','S','R')))
        transitions.append(('q_swap_p3_move', ('B','B','1'), 'q_swap_p3_move', ('1','B','B'), ('R','S','R')))
        transitions.append(('q_swap_p3_move', ('B','B','B'), 'q_accept', ('B','B','B'), ('S','S','S')))

        return transitions


    # def get_swap_transitions():
    #     """Returns the list of transition functions 
    #     for the swapping of two binary numbers."""
    #     transitions = []

    #     # q0 - Find the second number until it reaches the separator '#'
    #     transitions.append(('q0', ('0','B','B'), 'q0', ('0','B','B'), ('R','S','S')))
    #     transitions.append(('q0', ('1','B','B'), 'q0', ('1','B','B'), ('R','S','S')))
    #     # Found separator: Erase it (write B) and start copying next step
    #     transitions.append(('q0', ('#','B','B'), 'qcopy_num2_t2', ('B','B','B'), ('R','S','S')))

    #     # 2. COPY T1 -> T2 (and CLEAR T1)
    #     # T1 reads digit of Num2, Writes B (erase). T2 Writes digit.
    #     transitions.append(('qcopy_num2_t2', ('0','B','B'), 'qcopy_num2_t2', ('B','0','B'), ('R','R','S')))
    #     transitions.append(('qcopy_num2_t2', ('1','B','B'), 'qcopy_num2_t2', ('B','1','B'), ('R','R','S')))
    #     # Hit Blank on T1 (End of Input). Start Rewinding T2.
    #     transitions.append(('qcopy_num2_t2', ('B','B','B'), 'q_rewind_t2_prep', ('B','B','B'), ('S','L','S')))

    #     # 3. REWIND T2 (Back to start of Num2)
    #     # T1 waits on the far right (Blank).
    #     transitions.append(('q_rewind_t2_prep', ('B','0','B'), 'q_rewind_t2_prep', ('B','0','B'), ('S','L','S')))
    #     transitions.append(('q_rewind_t2_prep', ('B','1','B'), 'q_rewind_t2_prep', ('B','1','B'), ('S','L','S')))
    #     # T2 hits Left Blank -> T2 Ready. Switch to finding Num1 on T1.
    #     transitions.append(('q_rewind_t2_prep', ('B','B','B'), 'q_find_num1_t1', ('B','B','B'), ('L','R','S')))

    #     symbols = ['0', '1', 'B']

    #     # 4. FIND NUM1 (T1 moves Left)
    #     for t2 in symbols:
    #         # See Blank -> Keep going Left (skipping erased zone)
    #         transitions.append(('q_find_num1_t1', ('B',t2,'B'), 'q_find_num1_t1', ('B',t2,'B'), ('L','S','S')))
    #         # See Digit -> We found the end of Num1! Switch to standard rewind.
    #         transitions.append(('q_find_num1_t1', ('0',t2,'B'), 'q_rewind_t1_final', ('0',t2,'B'), ('L','S','S')))
    #         transitions.append(('q_find_num1_t1', ('1',t2,'B'), 'q_rewind_t1_final', ('1',t2,'B'), ('L','S','S')))
            
    #     # 5. REWIND T1 (Standard)
    #     # Move Left until we hit the Start Blank of Num1.
    #     for t2 in symbols:
    #         transitions.append(('q_rewind_t1_final', ('0',t2,'B'), 'q_rewind_t1_final', ('0',t2,'B'), ('L','S','S')))
    #         transitions.append(('q_rewind_t1_final', ('1',t2,'B'), 'q_rewind_t1_final', ('1',t2,'B'), ('L','S','S')))
    #         # Hit Left Blank -> T1 Ready. Move R to start Compare.
    #         transitions.append(('q_rewind_t1_final', ('B',t2,'B'), 'q_compare', ('B',t2,'B'), ('R','S','S')))

    #     # 6. COMPARE
    #     # Equal -> Move R
    #     transitions.append(('q_compare', ('0','0','B'), 'q_compare', ('0','0','B'), ('R','R','S')))
    #     transitions.append(('q_compare', ('1','1','B'), 'q_compare', ('1','1','B'), ('R','R','S')))
        
    #     # Mismatch: A > B -> SWAP
    #     transitions.append(('q_compare', ('1','0','B'), 'q_swap_start_rewind', ('1','0','B'), ('L','L','S'))) 
    #     transitions.append(('q_compare', ('1','B','B'), 'q_swap_start_rewind', ('1','B','B'), ('L','L','S'))) # A longer

    #     # Mismatch: A < B -> ACCEPT (No Swap)
    #     transitions.append(('q_compare', ('0','1','B'), 'q_accept', ('0','1','B'), ('S','S','S')))
    #     transitions.append(('q_compare', ('B','1','B'), 'q_accept', ('B','1','B'), ('S','S','S'))) # B longer
        
    #     # Equal End -> ACCEPT
    #     transitions.append(('q_compare', ('B','B','B'), 'q_accept', ('B','B','B'), ('S','S','S')))

    #     # 7. SWAP SEQUENCE
        
    #     # 0. Rewind T1 and T2 to Start (Left Blank)
    #     for t1 in symbols:
    #         for t2 in symbols:
    #             if not (t1 == 'B' and t2 == 'B'):
    #                 transitions.append(('q_swap_start_rewind', (t1,t2,'B'), 'q_swap_start_rewind', (t1,t2,'B'), ('L','L','S')))
        
    #     # Both Hit Blank -> Ready for Phase 1
    #     transitions.append(('q_swap_start_rewind', ('B','B','B'), 'q_swap_p1_move', ('B','B','B'), ('S','R','R')))

    #     # PHASE 1: Move T2 -> T3 (Copy & Erase T2)
    #     # T1 is Passive (Sitting on B)
    #     transitions.append(('q_swap_p1_move', ('B','0','B'), 'q_swap_p1_move', ('B','B','0'), ('S','R','R')))
    #     transitions.append(('q_swap_p1_move', ('B','1','B'), 'q_swap_p1_move', ('B','B','1'), ('S','R','R')))
    #     # End of T2 (Blank) -> Rewind T2, T3
    #     transitions.append(('q_swap_p1_move', ('B','B','B'), 'q_swap_p1_rewind', ('B','B','B'), ('S','L','L')))

    #     # Rewind T2, T3 to Left Blank
    #     for t3 in symbols:
    #         if t3 != 'B': 
    #             transitions.append(('q_swap_p1_rewind', ('B','B',t3), 'q_swap_p1_rewind', ('B','B',t3), ('S','L','L')))
        
    #     # Hit Left Blanks -> Ready for Phase 2
    #     transitions.append(('q_swap_p1_rewind', ('B','B','B'), 'q_swap_p2_move', ('B','B','B'), ('R','R','S')))

    #     # PHASE 2: Move T1 -> T2 (Copy & Erase T1)
    #     # T3 is Passive (Sitting on B)
    #     transitions.append(('q_swap_p2_move', ('0','B','B'), 'q_swap_p2_move', ('B','0','B'), ('R','R','S')))
    #     transitions.append(('q_swap_p2_move', ('1','B','B'), 'q_swap_p2_move', ('B','1','B'), ('R','R','S')))
    #     # End of T1 -> Rewind T1, T2
    #     transitions.append(('q_swap_p2_move', ('B','B','B'), 'q_swap_p2_rewind', ('B','B','B'), ('L','L','S')))

    #     # Rewind T1, T2 to Left Blank
    #     for t2 in ['0', '1']:
    #         transitions.append(('q_swap_p2_rewind', ('B',t2,'B'), 'q_swap_p2_rewind', ('B',t2,'B'), ('L','L','S')))
            
    #     # Hit Left Blanks -> Ready for Phase 3
    #     transitions.append(('q_swap_p2_rewind', ('B','B','B'), 'q_swap_p3_move', ('B','B','B'), ('R','S','R')))

    #     # PHASE 3: Move T3 -> T1 (Copy & Erase T3)
    #     # T2 is Passive (Sitting on B)
    #     transitions.append(('q_swap_p3_move', ('B','B','0'), 'q_swap_p3_move', ('0','B','B'), ('R','S','R')))
    #     transitions.append(('q_swap_p3_move', ('B','B','1'), 'q_swap_p3_move', ('1','B','B'), ('R','S','R')))
    #     # End of T3 -> Done!
    #     transitions.append(('q_swap_p3_move', ('B','B','B'), 'q_accept', ('B','B','B'), ('S','S','S')))

    #     return transitions

    def add_transition_func(state_dict, rules):
        for state_name, read, next_state, write, move in rules:
            if state_name in state_dict:
                state_dict[state_name].add_transition(read, next_state, write, move)

    def full_tape_str(t: Tapes):
        """Cleans up the output string"""
        return ''.join(t.tape_symbols).replace(t.blank, '').strip()
    
    # Initialize Machine
    mtm = MultiTapeTM('q0', 'q_accept', blank='B', num_of_tapes=3)
    for s in states.values():
        mtm.add_state(s)
    
    # Load Logic
    transition_func = get_swap_transitions()
    add_transition_func(states, transition_func)

    # Run
    input_string = "1011#1000"
    print("Swap A and B if A > B. Otherwise, do not swap.\n")
    print(f"Running MultiTape TM on the two binary numbers on tape 1: \n{input_string.rjust(20)}")

    accepted = mtm.is_accepted(input_string)
    
    print(f"\nAccepted: {str(accepted).upper()}")
    
    for i, tape in enumerate(mtm.tapes, start=1):
        print(f" Tape #{i}: '{full_tape_str(tape)}'")

    print("\n")