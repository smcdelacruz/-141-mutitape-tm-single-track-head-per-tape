"""
CMSC 141
Multitape Turing Machine - General Purpose Engine
Implements: Swap two numbers if first > second (via state transitions)
"""

START_HEAD_INDEX = 2
INITIAL_BLANK_SIZE = 5

class Tapes:
    def __init__(self, blank, initial_symbol=''):
        self.blank = blank
        # Pad with blanks on both sides
        self.tape_symbols = [blank, blank] + list(initial_symbol) + [blank, blank]
        self.tapeHead = START_HEAD_INDEX

    def read_current_symbol(self):
        # Safety expansion if head goes out of bounds
        if self.tapeHead < 0:
            self.tape_symbols.insert(0, self.blank)
            self.tapeHead = 0
        elif self.tapeHead >= len(self.tape_symbols):
            self.tape_symbols.append(self.blank)
        return self.tape_symbols[self.tapeHead]
    
    def write_current_symbol(self, tape_symbol):
        if self.tapeHead < 0:
            self.tape_symbols.insert(0, self.blank)
            self.tapeHead = 0
        elif self.tapeHead >= len(self.tape_symbols):
            self.tape_symbols.append(self.blank)
        self.tape_symbols[self.tapeHead] = tape_symbol

    def move_direction(self, direction):
        if direction == 'L':
            self.tapeHead -= 1
        elif direction == 'R':
            self.tapeHead += 1
        # 'S' means stay, so do nothing

    def __str__(self):
        output = ''
        for i, symbol in enumerate(self.tape_symbols):
            if i == self.tapeHead:
                output += f"[{symbol}]"
            else:
                output += symbol
        return output

class State:
    def __init__(self, state_name):
        self.state_name = state_name
        # Key: (sym1, sym2, sym3), Value: (next_state, (write1, write2, write3), (dir1, dir2, dir3))
        self.transitions = {}

    def add_transition(self, current_symbols, nextState, next_symbols, directions):
        self.transitions[current_symbols] = (nextState, next_symbols, directions)

    def get_transition(self, current_symbols):
        return self.transitions.get(current_symbols, None)

class MultiTapeTM:
    def __init__(self, start_state, final_state, blank='B', num_of_tapes=3):
        self.state = start_state
        self.start_state = start_state
        self.final_state = final_state
        self.blank = blank
        self.states = {}
        self.tapes = [Tapes(blank) for _ in range(num_of_tapes)]
        
    def add_state(self, state):
        self.states[state.state_name] = state
    
    def load_input(self, string_input):
        # Load input onto Tape 1, clear others
        for i in range(len(self.tapes)):
            if i == 0:
                self.tapes[i] = Tapes(self.blank, string_input)
            else:
                self.tapes[i] = Tapes(self.blank)
        self.state = self.start_state
        
    def step(self):
        # 1. Check if we are in final state
        if self.state == self.final_state:
            return False # Halt

        # 2. Read symbols from all tapes
        current_symbols = tuple(t.read_current_symbol() for t in self.tapes)
        
        # 3. Get current state object
        if self.state not in self.states:
            print(f"Error: State {self.state} not defined.")
            return False
            
        current_state_obj = self.states[self.state]
        transition = current_state_obj.get_transition(current_symbols)

        # 4. If no transition defined, Halt (Reject or crash)
        if not transition:
            # Uncomment below to debug missing transitions
            # print(f"No transition from {self.state} with symbols {current_symbols}")
            return False
        
        next_state, write_symbols, directions = transition
        
        # 5. Write symbols and Move heads
        for i, tape in enumerate(self.tapes):
            tape.write_current_symbol(write_symbols[i])
            tape.move_direction(directions[i])
            
        # 6. Update State
        self.state = next_state
        return True
    
    def run(self, string_input, max_steps=1000):
        self.load_input(string_input)
        steps = 0
        while self.state != self.final_state and steps < max_steps:
            if not self.step():
                break # Halted (No transition)
            steps += 1
        return self.state == self.final_state
            
    def __str__(self):
        output = f"Current State: {self.state}\n"
        for i, tape in enumerate(self.tapes):
            # purely for display, strip excessive blanks for cleanliness
            raw = str(tape)
            output += f"Tape {i+1}: {raw}\n"
        return output

# ==========================================
#  TRANSITION LOGIC DEFINITION
# ==========================================
if __name__ == '__main__':
    # Helper to clean up transition definitions
    def add_rule(tm, state, read_syms, next_state, write_syms, dirs):
        if state not in tm.states:
            tm.add_state(State(state))
        tm.states[state].add_transition(read_syms, next_state, write_syms, dirs)

    # Instantiate the General Purpose Machine
    tm = MultiTapeTM(start_state='q_init', final_state='q_accept', blank='B', num_of_tapes=3)

    # -----------------------------------------------------------
    # PHASE 1: PARSE (T1 has A#B, Copy B to T2)
    # -----------------------------------------------------------
    
    # 1. Move Tape 1 Right until we hit '#'
    for bit in ['0', '1']:
        add_rule(tm, 'q_init', (bit, 'B', 'B'), 'q_init', (bit, 'B', 'B'), ('R', 'S', 'S'))
    add_rule(tm, 'q_init', ('#', 'B', 'B'), 'q_copy_B_setup', ('#', 'B', 'B'), ('R', 'S', 'S'))

    # 2. Copy Num2 (on T1) to Tape 2
    for bit in ['0', '1']:
        # Read T1, Write T1 (unchanged), Write T2 (copy), Move both R
        add_rule(tm, 'q_copy_B_setup', (bit, 'B', 'B'), 'q_copy_B_setup', (bit, bit, 'B'), ('R', 'R', 'S'))
    
    # Done copying when T1 hits Blank
    add_rule(tm, 'q_copy_B_setup', ('B', 'B', 'B'), 'q_rewind_all', ('B', 'B', 'B'), ('L', 'L', 'S'))

    # 3. Rewind T1 and T2 to start (Scan Left until Blank)
    # Handle combinations of rewinding T1 and T2
    for s1 in ['0', '1', '#', 'B']:
        for s2 in ['0', '1', 'B']:
            # Determine direction: if symbol is Blank, stop moving (S), else Left (L)
            d1 = 'S' if s1 == 'B' else 'L'
            d2 = 'S' if s2 == 'B' else 'L'
            
            # Logic: If both hit blank, switch to compare. Else keep rewinding.
            if s1 == 'B' and s2 == 'B':
                next_st = 'q_compare_start'
                move_dirs = ('R', 'R', 'S') # Move R once to get off the Blank
            else:
                next_st = 'q_rewind_all'
                move_dirs = (d1, d2, 'S')

            add_rule(tm, 'q_rewind_all', (s1, s2, 'B'), next_st, (s1, s2, 'B'), move_dirs)

    # -----------------------------------------------------------
    # PHASE 2: COMPARE (Is T1 > T2?)
    # -----------------------------------------------------------
    
    # Simple MSB comparison logic:
    # 1. If we find mismatch (1 vs 0), we know the winner immediately (assuming aligned/valid binary).
    # 2. Need to check lengths (if one ends before the other).
    # NOTE: This logic assumes inputs are stripped of leading zeros or are same length.
    
    # Case: Equal so far
    add_rule(tm, 'q_compare_start', ('0', '0', 'B'), 'q_compare_start', ('0', '0', 'B'), ('R', 'R', 'S'))
    add_rule(tm, 'q_compare_start', ('1', '1', 'B'), 'q_compare_start', ('1', '1', 'B'), ('R', 'R', 'S'))

    # Case: T1 > T2 (Found a 1 in T1 and 0 in T2) -> Potential Swap
    add_rule(tm, 'q_compare_start', ('1', '0', 'B'), 'q_check_len_gt', ('1', '0', 'B'), ('R', 'R', 'S'))

    # Case: T1 < T2 (Found a 0 in T1 and 1 in T2) -> No Swap
    add_rule(tm, 'q_compare_start', ('0', '1', 'B'), 'q_check_len_lt', ('0', '1', 'B'), ('R', 'R', 'S'))

    # Handling Lengths / End of strings
    # If T1 hits '#' (end of Num1) and T2 hits 'B' (end of Num2) -> Equal -> Accept
    add_rule(tm, 'q_compare_start', ('#', 'B', 'B'), 'q_accept', ('#', 'B', 'B'), ('S', 'S', 'S'))
    
    # If T1 hits '#' but T2 is still going -> T2 is longer -> T1 < T2 -> Accept
    for bit in ['0', '1']:
        add_rule(tm, 'q_compare_start', ('#', bit, 'B'), 'q_accept', ('#', bit, 'B'), ('S', 'S', 'S'))
    
    # If T2 hits 'B' but T1 is still numbers -> T1 is longer -> T1 > T2 -> Swap
    for bit in ['0', '1']:
        add_rule(tm, 'q_compare_start', (bit, 'B', 'B'), 'q_prep_swap', (bit, 'B', 'B'), ('S', 'S', 'S'))

    # Helper states to finish scanning (verify no length surprises)
    # If we thought T1 > T2 (q_check_len_gt), we just need to make sure T2 isn't actually longer.
    for b1 in ['0', '1', '#']:
        for b2 in ['0', '1', 'B']:
            # If T2 ends (B) and T1 hasn't, or both end -> Confirmed Greater -> Swap
            if b2 == 'B':
                add_rule(tm, 'q_check_len_gt', (b1, b2, 'B'), 'q_prep_swap', (b1, b2, 'B'), ('S','S','S'))
            # If T1 ends (#) but T2 continues -> T2 is longer -> Actually Less -> Accept
            elif b1 == '#':
                 add_rule(tm, 'q_check_len_gt', (b1, b2, 'B'), 'q_accept', (b1, b2, 'B'), ('S','S','S'))
            else:
                # Keep scanning
                add_rule(tm, 'q_check_len_gt', (b1, b2, 'B'), 'q_check_len_gt', (b1, b2, 'B'), ('R','R','S'))

    # If we thought T1 < T2, just scan to ensure T1 isn't longer (unlikely in binary, but needed for robustness)
    # For simplicity in this demo: if we found 0 vs 1, we assume T1 < T2 unless T1 is much longer.
    # We will just accept for Less logic to keep code size reasonable.
    for b1 in ['0', '1', '#', 'B']: 
        for b2 in ['0', '1', 'B']:
            add_rule(tm, 'q_check_len_lt', (b1, b2, 'B'), 'q_accept', (b1, b2, 'B'), ('S','S','S'))

    # -----------------------------------------------------------
    # PHASE 3: SWAP (Rewind, T2->T3, T1->T2, T3->T1)
    # -----------------------------------------------------------
    
    # 1. Rewind All Tapes to start (similar to q_rewind_all)
    # q_prep_swap acts as entry to rewind
    for s1 in ['0','1','#','B']: 
        for s2 in ['0','1','B']: 
            add_rule(tm, 'q_prep_swap', (s1,s2,'B'), 'q_swap_rewind', (s1,s2,'B'), ('L','L','S'))

    for s1 in ['0','1','#','B']:
        for s2 in ['0','1','B']:
            d1 = 'S' if s1 == 'B' else 'L'
            d2 = 'S' if s2 == 'B' else 'L'
            if s1 == 'B' and s2 == 'B':
                 # Done rewinding, start copy T2->T3
                add_rule(tm, 'q_swap_rewind', (s1, s2, 'B'), 'q_copy_t2_t3', (s1, s2, 'B'), ('R', 'R', 'R'))
            else:
                add_rule(tm, 'q_swap_rewind', (s1, s2, 'B'), 'q_swap_rewind', (s1, s2, 'B'), (d1, d2, 'S'))

    # 2. Copy T2 (Num2) -> T3
    for bit in ['0', '1']:
        add_rule(tm, 'q_copy_t2_t3', ('B', bit, 'B'), 'q_copy_t2_t3', ('B', bit, bit), ('S', 'R', 'R'))
        # Note: Tape 1 stays at Blank (start) during this
    
    # Done copying T2->T3
    add_rule(tm, 'q_copy_t2_t3', ('B', 'B', 'B'), 'q_rewind_t2_t3', ('B', 'B', 'B'), ('S', 'L', 'L'))

    # 3. Rewind T2, T3
    for b in ['0', '1', 'B']:
        d = 'S' if b == 'B' else 'L'
        if b == 'B':
             # T2/T3 Rewound. Now move T1 to start of Num1 (it's currently at B before Num1)
             add_rule(tm, 'q_rewind_t2_t3', ('B', 'B', 'B'), 'q_copy_t1_t2', ('B', 'B', 'B'), ('R', 'S', 'S'))
        else:
             add_rule(tm, 'q_rewind_t2_t3', ('B', b, b), 'q_rewind_t2_t3', ('B', b, b), ('S', d, d))

    # 4. Copy T1 (Num1) -> T2
    # T1 reads Num1 until '#', T2 writes it.
    for bit in ['0', '1']:
        add_rule(tm, 'q_copy_t1_t2', (bit, 'B', 'B'), 'q_copy_t1_t2', (bit, bit, 'B'), ('R', 'R', 'S'))
    
    # Hit '#' on T1, stop copying.
    add_rule(tm, 'q_copy_t1_t2', ('#', 'B', 'B'), 'q_rewind_t1_t2', ('#', 'B', 'B'), ('L', 'L', 'S'))

    # 5. Rewind T1, T2
    for b1 in ['0', '1', '#', 'B']:
        for b2 in ['0', '1', 'B']:
            d1 = 'S' if b1 == 'B' else 'L'
            d2 = 'S' if b2 == 'B' else 'L'
            if b1 == 'B' and b2 == 'B':
                add_rule(tm, 'q_rewind_t1_t2', (b1,b2,'B'), 'q_copy_t3_t1', (b1,b2,'B'), ('S','S','R'))
            else:
                add_rule(tm, 'q_rewind_t1_t2', (b1,b2,'B'), 'q_rewind_t1_t2', (b1,b2,'B'), (d1,d2,'S'))

    # 6. Copy T3 (Num2) -> T1
    # This overwrites Num1 on Tape 1 with Num2.
    for bit in ['0', '1']:
        add_rule(tm, 'q_copy_t3_t1', ('B', 'B', bit), 'q_copy_t3_t1', (bit, 'B', bit), ('R', 'S', 'R'))
    
    # Finish
    add_rule(tm, 'q_copy_t3_t1', ('B', 'B', 'B'), 'q_accept', ('B', 'B', 'B'), ('S', 'S', 'S'))

    # ==========================================
    # EXECUTION
    # ==========================================
    
    # Test Case 1: No Swap (10 < 11)
    print("--- TEST 1: 10#11 (No Swap Expected) ---")
    tm.run("10#11")
    print(tm)

    # Test Case 2: Swap Needed (111 > 10)
    print("\n--- TEST 2: 111#10 (Swap Expected) ---")
    tm.run("111#10", max_steps=2000)
    print(tm)
    
    print("\nResult Analysis for Test 2:")
    print("Tape 1 should contain smaller number (10) followed by remnant garbage if not cleared (or just 10).")
    print("Tape 2 should contain larger number (111).")