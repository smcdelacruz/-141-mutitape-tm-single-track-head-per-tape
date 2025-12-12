# ---------------------------
# Tape class
# ---------------------------
class Tape:
    def __init__(self, blank, initial=''):
        self.blank = blank
        self.symbols = [blank, blank] + list(initial) + [blank, blank]
        self.head = 2

    def read(self):
        return self.symbols[self.head]

    def write(self, symbol):
        self.symbols[self.head] = symbol

    def move(self, direction):
        if direction == 'L':
            self.head -= 1
            if self.head < 0:
                self.symbols.insert(0, self.blank)
                self.head = 0
        elif direction == 'R':
            self.head += 1
            if self.head >= len(self.symbols):
                self.symbols.append(self.blank)
        elif direction == 'S':
            pass

    def __str__(self):
        result = ''
        for i in range(len(self.symbols)):
            if i == self.head:
                result += '.' + self.symbols[i]
            else:
                result += self.symbols[i]
        return result

# ---------------------------
# State class
# ---------------------------
class State:
    def __init__(self, name):
        self.name = name
        self.transitions = {}  # key: symbols tuple -> value: [next_state, write_symbols, moves]

    def add_Transition(self, read_symbols, next_state, write_symbols, moves):
        self.transitions[read_symbols] = [next_state, write_symbols, moves]

    def get_Transition(self, read_symbols):
        return self.transitions.get(read_symbols, None)

# ---------------------------
# Multitape TM class
# ---------------------------
class multitape_tm:
    def __init__(self, start_state, final_state, blank='#', num_tapes=1):
        self.blank = blank
        self.num_tapes = num_tapes
        self.tapes = [Tape(blank) for _ in range(num_tapes)]
        self.states = {}
        self.start_state = start_state
        self.final_state = final_state
        self.state = start_state

    def add_state(self, state):
        self.states[state.name] = state

    def load_input(self, string):
        for i in range(len(self.tapes)):
            if i == 0:
                self.tapes[i].symbols = [self.blank, self.blank] + list(string) + [self.blank, self.blank]
                self.tapes[i].head = 2
            else:
                self.tapes[i].symbols = [self.blank]*5
                self.tapes[i].head = 2
        self.state = self.start_state

    def read_symbols(self):
        return tuple(t.read() for t in self.tapes)

    def step(self):
        current_state = self.states[self.state]
        symbols = self.read_symbols()
        trans = current_state.get_Transition(symbols)
        if not trans:
            return False
        next_state, write_symbols, moves = trans
        self.state = next_state
        for i in range(len(self.tapes)):
            self.tapes[i].write(write_symbols[i])
            self.tapes[i].move(moves[i])
        return True

    # ---------------------------
    # Proper accepts method
    # ---------------------------
    def accepts(self, string, max_steps=1000):
        self.load_input(string)
        steps = 0
        while steps < max_steps:
            if self.state == self.final_state:
                return True
            if not self.step():
                break  # halted
            steps += 1
        return False

    def __str__(self):
        out = 'State: ' + self.state + '\n'
        for i in range(len(self.tapes)):
            out += 'Tape ' + str(i) + ': ' + str(self.tapes[i]) + '\n'
        return out

# ---------------------------
# Main examples
# ---------------------------
if __name__ == '__main__':
    # Example 1: Unary complement (1-tape)
    q0 = State('q0')
    q0.add_Transition(('1',), 'q0', ('0',), ('R',))
    q0.add_Transition(('0',), 'q0', ('1',), ('R',))
    q0.add_Transition(('#',), 'q_accept', ('#',), ('S',))
    q_accept = State('q_accept')

    tm1 = multitape_tm('q0', 'q_accept', blank='#', num_tapes=1)
    tm1.add_state(q0)
    tm1.add_state(q_accept)
    accepted = tm1.accepts('000000')
    print("Unary Complement (1-tape):")
    print("Accepted:", accepted)
    print(tm1)

    # Example 2: Copy tape0 -> tape1 (2-tape)
    q_copy = State('q_copy')
    q_copy.add_transition(('a','#'), 'q_copy', ('a','a'), ('R','R'))
    q_copy.add_transition(('h','#'), 'q_copy', ('h','h'), ('R','R'))
    q_copy.add_transition(('n','#'), 'q_copy', ('n','n'), ('R','R'))
    q_copy.add_transition(('#','#'), 'q_accept', ('#','#'), ('S','S'))
    q_accept2 = State('q_accept')

    tm2 = multitape_tm('q_copy', 'q_accept', blank='#', num_tapes=2)
    tm2.add_state(q_copy)
    tm2.add_state(q_accept2)
    accepted2 = tm2.accepts('hannah')
    print("\nCopy Tape0 -> Tape1 (2-tape):")
    print("Accepted:", accepted2)
    print(tm2)
