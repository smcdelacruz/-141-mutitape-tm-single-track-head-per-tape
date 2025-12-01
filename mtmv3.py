# simplified_multitape_tm.py

from typing import List, Tuple

# Tape class (simplified for one head and one track)
class Tapes:
    def __init__(self, blank: str):
        self.blank = blank
        self.symbols = []  # list of symbols on tape
        self.head = 0      # head position

    def load_string(self, string: str):
        self.symbols = list(string)
        self.head = 0

    def read(self) -> str:
        if self.head < len(self.symbols):
            return self.symbols[self.head]
        return self.blank

    def write(self, symbol: str):
        if self.head < len(self.symbols):
            self.symbols[self.head] = symbol
        else:
            self.symbols.append(symbol)

    def move(self, direction: str):
        if direction == 'L':
            self.head -= 1
        elif direction == 'R':
            self.head += 1
        elif direction == 'S':
            pass

    def __str__(self):
        """Print tape with dot marker at head."""
        output = ""
        for i, s in enumerate(self.symbols):
            if i == self.head:
                output += "·" + s
            else:
                output += s
        if self.head >= len(self.symbols):
            output += "·" + self.blank
        return output

# Deterministic Multitape TM
class multitape_tm:
    def __init__(self, start: str, final: str, blank: str='B', num_of_tapes: int=1):
        self.start = start
        self.state = start
        self.final = final
        self.blank = blank
        self.tapes = [Tapes(blank) for _ in range(num_of_tapes)]
        self.trans = {}  # deterministic: (state, symbols) -> (new_state, write_symbols, moves)

    def load_input(self, string: str):
        self.state = self.start
        self.tapes[0].load_string(string)
        # clear other tapes
        for t in self.tapes[1:]:
            t.load_string('')

    def read_symbols(self) -> Tuple[str, ...]:
        return tuple(t.read() for t in self.tapes)

    def add_transition(self, state: str, read_symbols: Tuple[str, ...],
                       new_state: str, write_symbols: Tuple[str, ...], moves: Tuple[str, ...]):
        key = (state, read_symbols)
        if key in self.trans:
            raise ValueError("Deterministic TM cannot have multiple transitions for same key.")
        self.trans[key] = (new_state, write_symbols, moves)

    def step(self) -> bool:
        key = (self.state, self.read_symbols())
        if key not in self.trans:
            return False
        new_state, write_syms, moves = self.trans[key]
        self.state = new_state
        for tape, w, m in zip(self.tapes, write_syms, moves):
            tape.write(w)
            tape.move(m)
        return True

    def run(self, max_steps: int=1000) -> bool:
        steps = 0
        while steps < max_steps:
            if self.state == self.final:
                return True
            if not self.step():
                return False
            steps += 1
        return False

    def __str__(self):
        out = f"State: {self.state}\n"
        for i, t in enumerate(self.tapes):
            out += f"Tape {i}: {str(t)}\n"
        return out

# -------------------
# EXAMPLE 1: Unary Complement (1-tape)
# -------------------
tm1 = multitape_tm('q0', 'q_accept', blank='#', num_of_tapes=1)
tm1.add_transition('q0', ('1',), 'q0', ('0',), ('R',))
tm1.add_transition('q0', ('0',), 'q0', ('1',), ('R',))
tm1.add_transition('q0', ('#',), 'q_accept', ('#',), ('S',))

tm1.load_input('11011101')
accepted = tm1.run()
print("Unary Complement (1-tape):")
print(f"Accepted: {accepted}")
print(tm1)

# -------------------
# EXAMPLE 2: Copy Tape0 -> Tape1 (2-tape)
# -------------------
tm2 = multitape_tm('q_copy', 'q_accept', blank='#', num_of_tapes=2)
tm2.add_transition('q_copy', ('a', '#'), 'q_copy', ('a', 'a'), ('R', 'R'))
tm2.add_transition('q_copy', ('b', '#'), 'q_copy', ('b', 'b'), ('R', 'R'))
tm2.add_transition('q_copy', ('#', '#'), 'q_accept', ('#', '#'), ('S', 'S'))

tm2.load_input('abba')
accepted2 = tm2.run()
print("\nCopy Tape0 -> Tape1 (2-tape):")
print(f"Accepted: {accepted2}")
print(tm2)
