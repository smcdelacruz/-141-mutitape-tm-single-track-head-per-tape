"""
CMSC 141
Multitape Turing Machine - Single Head & Track Per Tape
"""

START_HEAD_INDEX = 2
INITIAL_BLANK_SIZE = 5

class Tapes:
    def __init__(self, blank, initial_symbol=''):
        self.blank = blank
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
            print(f"No transition for state '{self.state}' with symbols {symbols}.\nHALTS.")
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
    def add_rules(state_dict, rules):
        for state_name, read, next_state, write, move in rules:
            if state_name in state_dict:
                state_dict[state_name].add_transition(read, next_state, write, move)

    # ---------------------------------------------------------
    # STATE DEFINITIONS
    # ---------------------------------------------------------
    state_names = [
        'q0',                   # Seek '#'
        'q_copy_t1_t2',         # Copy Num2 to T2, Clear T1
        'q_rewind_t2_prep',     # Rewind T2 to start
        'q_find_num1_t1',       # Move T1 Left past blanks to find Num1
        'q_rewind_t1_final',    # Rewind T1 to start of Num1
        'q_compare',            # Compare A vs B
        'q_swap_start_rewind',  # Initialize Swap: Rewind both to start
        'q_swap_p1_move',       # Phase 1: Move T2 -> T3
        'q_swap_p1_rewind',     # Rewind T2, T3
        'q_swap_p2_move',       # Phase 2: Move T1 -> T2
        'q_swap_p2_rewind',     # Rewind T1, T2
        'q_swap_p3_move',       # Phase 3: Move T3 -> T1
        'q_accept'
    ]
    states = {name: State(name) for name in state_names}
    mtm = MultiTapeTM('q0', 'q_accept', blank='B', num_of_tapes=3)
    for s in states.values():
        mtm.add_state(s)

    # ---------------------------------------------------------
    # TRANSITION RULES
    # ---------------------------------------------------------
    rules = []

    # 1. SETUP: Move T1 Right until '#'
    rules.append(('q0', ('0','B','B'), 'q0', ('0','B','B'), ('R','S','S')))
    rules.append(('q0', ('1','B','B'), 'q0', ('1','B','B'), ('R','S','S')))
    # Found separator: Erase it (write B) and start copying next step
    rules.append(('q0', ('#','B','B'), 'q_copy_t1_t2', ('B','B','B'), ('R','S','S')))

    # 2. COPY T1 -> T2 (and CLEAR T1)
    # T1 reads digit of Num2, Writes B (erase). T2 Writes digit.
    rules.append(('q_copy_t1_t2', ('0','B','B'), 'q_copy_t1_t2', ('B','0','B'), ('R','R','S')))
    rules.append(('q_copy_t1_t2', ('1','B','B'), 'q_copy_t1_t2', ('B','1','B'), ('R','R','S')))
    # Hit Blank on T1 (End of Input). Start Rewinding T2.
    rules.append(('q_copy_t1_t2', ('B','B','B'), 'q_rewind_t2_prep', ('B','B','B'), ('S','L','S')))

    # 3. REWIND T2 (Back to start of Num2)
    # T1 waits on the far right (Blank).
    rules.append(('q_rewind_t2_prep', ('B','0','B'), 'q_rewind_t2_prep', ('B','0','B'), ('S','L','S')))
    rules.append(('q_rewind_t2_prep', ('B','1','B'), 'q_rewind_t2_prep', ('B','1','B'), ('S','L','S')))
    # T2 hits Left Blank -> T2 Ready. Switch to finding Num1 on T1.
    rules.append(('q_rewind_t2_prep', ('B','B','B'), 'q_find_num1_t1', ('B','B','B'), ('L','R','S')))

    # 4. FIND NUM1 (T1 moves Left)
    # T1 is currently in the "erased zone". It sees B's. Move Left until we find digits.
    # T2 is parked on the first digit of Num2 (or B). We must handle wildcards for T2.
    for t2 in ['0', '1', 'B']:
        # See Blank -> Keep going Left (skipping erased zone)
        rules.append(('q_find_num1_t1', ('B',t2,'B'), 'q_find_num1_t1', ('B',t2,'B'), ('L','S','S')))
        # See Digit -> We found the end of Num1! Switch to standard rewind.
        rules.append(('q_find_num1_t1', ('0',t2,'B'), 'q_rewind_t1_final', ('0',t2,'B'), ('L','S','S')))
        rules.append(('q_find_num1_t1', ('1',t2,'B'), 'q_rewind_t1_final', ('1',t2,'B'), ('L','S','S')))
        # Edge case: If T1 was empty (no Num1), we hit the Leftmost Blank immediately?
        # That would mean T1 is 'B'. We stay 'B'. 
        
    # 5. REWIND T1 (Standard)
    # Move Left until we hit the Start Blank of Num1.
    for t2 in ['0', '1', 'B']:
        rules.append(('q_rewind_t1_final', ('0',t2,'B'), 'q_rewind_t1_final', ('0',t2,'B'), ('L','S','S')))
        rules.append(('q_rewind_t1_final', ('1',t2,'B'), 'q_rewind_t1_final', ('1',t2,'B'), ('L','S','S')))
        # Hit Left Blank -> T1 Ready. Move R to start Compare.
        rules.append(('q_rewind_t1_final', ('B',t2,'B'), 'q_compare', ('B',t2,'B'), ('R','S','S')))

    # 6. COMPARE
    # Equal -> Move R
    rules.append(('q_compare', ('0','0','B'), 'q_compare', ('0','0','B'), ('R','R','S')))
    rules.append(('q_compare', ('1','1','B'), 'q_compare', ('1','1','B'), ('R','R','S')))
    
    # Mismatch: A > B -> SWAP
    rules.append(('q_compare', ('1','0','B'), 'q_swap_start_rewind', ('1','0','B'), ('L','L','S'))) 
    rules.append(('q_compare', ('1','B','B'), 'q_swap_start_rewind', ('1','B','B'), ('L','L','S'))) # A longer

    # Mismatch: A < B -> ACCEPT (No Swap)
    rules.append(('q_compare', ('0','1','B'), 'q_accept', ('0','1','B'), ('S','S','S')))
    rules.append(('q_compare', ('B','1','B'), 'q_accept', ('B','1','B'), ('S','S','S'))) # B longer
    
    # Equal End -> ACCEPT
    rules.append(('q_compare', ('B','B','B'), 'q_accept', ('B','B','B'), ('S','S','S')))

    # ---------------------------------------------------------
    # SWAP SEQUENCE
    # ---------------------------------------------------------
    
    # 0. Rewind T1 and T2 to Start (Left Blank)
    # We use wildcards for safety as they might be at different lengths
    for t1 in ['0','1','B']:
        for t2 in ['0','1','B']:
            # If not both Blank, move L
            if not (t1 == 'B' and t2 == 'B'):
                 rules.append(('q_swap_start_rewind', (t1,t2,'B'), 'q_swap_start_rewind', (t1,t2,'B'), ('L','L','S')))
    
    # Both Hit Blank -> Ready for Phase 1
    rules.append(('q_swap_start_rewind', ('B','B','B'), 'q_swap_p1_move', ('B','B','B'), ('S','R','R')))

    # PHASE 1: Move T2 -> T3 (Copy & Erase T2)
    # T1 is Passive (Sitting on B)
    rules.append(('q_swap_p1_move', ('B','0','B'), 'q_swap_p1_move', ('B','B','0'), ('S','R','R')))
    rules.append(('q_swap_p1_move', ('B','1','B'), 'q_swap_p1_move', ('B','B','1'), ('S','R','R')))
    # End of T2 (Blank) -> Rewind T2, T3
    rules.append(('q_swap_p1_move', ('B','B','B'), 'q_swap_p1_rewind', ('B','B','B'), ('S','L','L')))

    # Rewind T2, T3 to Left Blank
    # Note: T2 is now all B (erased). T3 has digits.
    for t3 in ['0', '1', 'B']:
        if t3 != 'B': # Optimization: only need rules if not already at B
            rules.append(('q_swap_p1_rewind', ('B','B',t3), 'q_swap_p1_rewind', ('B','B',t3), ('S','L','L')))
    
    # Hit Left Blanks -> Ready for Phase 2
    rules.append(('q_swap_p1_rewind', ('B','B','B'), 'q_swap_p2_move', ('B','B','B'), ('R','R','S')))

    # PHASE 2: Move T1 -> T2 (Copy & Erase T1)
    # T3 is Passive (Sitting on B)
    rules.append(('q_swap_p2_move', ('0','B','B'), 'q_swap_p2_move', ('B','0','B'), ('R','R','S')))
    rules.append(('q_swap_p2_move', ('1','B','B'), 'q_swap_p2_move', ('B','1','B'), ('R','R','S')))
    # End of T1 -> Rewind T1, T2
    rules.append(('q_swap_p2_move', ('B','B','B'), 'q_swap_p2_rewind', ('B','B','B'), ('L','L','S')))

    # Rewind T1, T2 to Left Blank
    for t2 in ['0', '1']:
        rules.append(('q_swap_p2_rewind', ('B',t2,'B'), 'q_swap_p2_rewind', ('B',t2,'B'), ('L','L','S')))
        
    # Hit Left Blanks -> Ready for Phase 3
    rules.append(('q_swap_p2_rewind', ('B','B','B'), 'q_swap_p3_move', ('B','B','B'), ('R','S','R')))

    # PHASE 3: Move T3 -> T1 (Copy & Erase T3)
    # T2 is Passive (Sitting on B)
    rules.append(('q_swap_p3_move', ('B','B','0'), 'q_swap_p3_move', ('0','B','B'), ('R','S','R')))
    rules.append(('q_swap_p3_move', ('B','B','1'), 'q_swap_p3_move', ('1','B','B'), ('R','S','R')))
    # End of T3 -> Done!
    rules.append(('q_swap_p3_move', ('B','B','B'), 'q_accept', ('B','B','B'), ('S','S','S')))


    add_rules(states, rules)

    # ---------------------------------------------------------
    # TEST EXECUTION
    # ---------------------------------------------------------
    input_string = "10#0"
    print("\nRunning MultiTape TM on input:", input_string)
    accepted = mtm.is_accepted(input_string)
    print("\nAccepted:", accepted)
    
    print("Logical contents (trimmed blanks):")
    def full_tape_str(t: Tapes):
        return ''.join(t.tape_symbols).replace(t.blank, '').strip()

    for i, tape in enumerate(mtm.tapes, start=1):
        print(f" Tape{i}: '{full_tape_str(tape)}'")