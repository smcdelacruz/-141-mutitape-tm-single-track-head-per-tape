class Tape:
    """Represents a single tape with one head."""
    def __init__(self, blank_symbol='#', initial_string=''):
        self.blank = blank_symbol
        self.symbols = list(initial_string)
        self.head = 0

    def read(self):
        """Return symbol under the head."""
        if self.head < 0:
            return self.blank
        if self.head >= len(self.symbols):
            return self.blank
        return self.symbols[self.head]

    def write(self, symbol):
        """Write symbol under the head, extending tape if needed."""
        if self.head < 0:
            # Extend tape to the left
            self.symbols.insert(0, symbol)
            self.head = 0
        elif self.head >= len(self.symbols):
            # Extend tape to the right
            self.symbols.append(symbol)
        else:
            self.symbols[self.head] = symbol

    def move(self, direction):
        """Move head: L, R, or S."""
        if direction == 'L':
            self.head -= 1
        elif direction == 'R':
            self.head += 1
        # else stay still

    def __str__(self):
        """Returns tape with a dot marking the head position."""
        s = ""
        for i, ch in enumerate(self.symbols):
            if i == self.head:
                s += "." + ch
            else:
                s += " " + ch
        return s


class DTM:
    """Simple deterministic multitape TM."""
    def __init__(self, start_state, accept_state, blank='#', num_tapes=1):
        self.start_state = start_state
        self.accept_state = accept_state
        self.blank = blank
        self.num_tapes = num_tapes

        # transition[(state, read_symbols_tuple)] = (new_state, [(write, move), ...])
        self.transition = {}

        # Runtime variables
        self.state = start_state
        self.tapes = [Tape(blank) for _ in range(num_tapes)]

    def set_input(self, input_string):
        """Loads input on tape 0."""
        self.tapes[0] = Tape(self.blank, input_string)
        # remaining tapes start blank
        for i in range(1, self.num_tapes):
            self.tapes[i] = Tape(self.blank, "")

    def add_transition(self, state, read_tuple, new_state, actions):
        """
        read_tuple:    tuple of symbols read from each tape
        actions:       list of (write_symbol, direction) for each tape
        Example for 2 tapes:
            ('0','1') → [('1','R'), ('1','L')]
        """
        self.transition[(state, read_tuple)] = (new_state, actions)

    def step(self):
        """Execute one transition step."""
        read_now = tuple(t.read() for t in self.tapes)

        if (self.state, read_now) not in self.transition:
            return False  # no transition available

        new_state, actions = self.transition[(self.state, read_now)]

        # Update state
        self.state = new_state

        # Apply actions per tape
        for tape, (write_symbol, direction) in zip(self.tapes, actions):
            tape.write(write_symbol)
            tape.move(direction)

        return True

    def run(self, max_steps=1000):
        """Run until accept state or halt."""
        steps = 0
        while steps < max_steps:
            if self.state == self.accept_state:
                print("ACCEPTED")
                return True

            if not self.step():
                print("HALTED (no transition).")
                return False

            steps += 1

        print("DID NOT HALT")
        return False

    def print_tapes(self):
        """Debug print all tapes."""
        for i, t in enumerate(self.tapes):
            print(f"Tape {i}: {t}")
        print(f"Current state: {self.state}")
        print("-" * 40)


# ------------------------------
# EXAMPLE: copy from tape 0 to tape 1 until blank
# ------------------------------
if __name__ == "__main__":
    tm = DTM(start_state="q0", accept_state="q_accept", num_tapes=2)

    # Read 0 → write 0 on tape 1, move both heads R
    tm.add_transition("q0", ('0', '#'),
                      "q0",
                      [('0', 'R'), ('0', 'R')])

    # Read 1 → write 1 on tape 1
    tm.add_transition("q0", ('1', '#'),
                      "q0",
                      [('1', 'R'), ('1', 'R')])

    # End of input → go to accept
    tm.add_transition("q0", ('#', '#'),
                      "q_accept",
                      [('#', 'S'), ('#', 'S')])

    tm.set_input("01011")
    tm.run()
    tm.print_tapes()
