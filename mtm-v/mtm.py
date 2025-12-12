# dtm.py
# Deterministic Multitape Turing Machine simulator
# Author: assistant (adapted for student's use)
from collections import defaultdict
from typing import Tuple, List, Dict, Optional

class Tape:
    """
    Tape implemented with a dictionary mapping integer positions -> symbol.
    This allows infinite tape in both directions without special resizing.
    """
    def __init__(self, blank: str, string: str = '', head: int = 0):
        self.blank = blank
        self.cells = {}  # type: Dict[int,str]
        self.head = head
        self.loadString(string, head)

    def loadString(self, string: str, head: int = 0):
        """Load string onto tape starting at position 0 and set head index."""
        self.cells = {}
        for i, ch in enumerate(string):
            self.cells[i] = ch
        self.head = head

    def readSymbol(self) -> str:
        """Return symbol under head (blank if not set)."""
        return self.cells.get(self.head, self.blank)

    def writeSymbol(self, symbol: str):
        """Write symbol at head position. If symbol == blank, we may keep it for clarity."""
        if symbol == self.blank:
            # Optionally clear cells to keep printing compact; we keep blank stored only if previously set.
            if self.head in self.cells:
                self.cells[self.head] = symbol
        else:
            self.cells[self.head] = symbol

    def moveHead(self, direction: str):
        """Move head: 'L' left, 'R' right, 'S' stay."""
        if direction == 'L':
            self.head -= 1
        elif direction == 'R':
            self.head += 1
        elif direction == 'S':
            pass
        else:
            raise ValueError(f"Invalid direction: {direction}")

    def clone(self) -> 'Tape':
        """Return a deep copy of tape (not used in deterministic machine branching, but handy)."""
        t = Tape(self.blank)
        t.cells = dict(self.cells)
        t.head = self.head
        return t

    def _printed_range(self) -> Tuple[int, int]:
        """Return min and max positions to pretty-print the tape slice."""
        if not self.cells:
            return (self.head, self.head)
        min_pos = min(min(self.cells.keys()), self.head)
        max_pos = max(max(self.cells.keys()), self.head)
        return (min_pos, max_pos)

    def __str__(self) -> str:
        """Return printable view with a dot before the symbol under the head (like ab·cdef)."""
        lo, hi = self._printed_range()
        parts = []
        for pos in range(lo, hi+1):
            sym = self.cells.get(pos, self.blank)
            if pos == self.head:
                parts.append("·" + sym)
            else:
                parts.append(sym)
        return "".join(parts)

class DTM:
    """
    Deterministic Multitape Turing Machine.
    Transition table structure:
      key: (state: str, read_symbols: tuple(symbols...))
      value: (next_state: str, write_symbols: tuple(symbols...), moves: tuple('L'/'R'/'S'...))
    Exactly one entry per key is allowed (determinism enforced).
    """
    def __init__(self, start: str, final: str, blank: str = '#', ntapes: int = 1):
        self.start = self.state = start
        self.final = final
        self.blank = blank
        self.ntapes = ntapes
        self.tapes: List[Tape] = [Tape(blank) for _ in range(ntapes)]
        # deterministic transitions: dict -> single tuple
        self.trans: Dict[Tuple[str, Tuple[str, ...]], Tuple[str, Tuple[str, ...], Tuple[str, ...]]] = {}

    def restart(self, string: str):
        """Reset machine to start state and load input into tape 0; clear other tapes."""
        self.state = self.start
        # load input on tape 0
        self.tapes[0].loadString(string, 0)
        # clear other tapes
        for tape in self.tapes[1:]:
            tape.loadString('', 0)

    def readSymbols(self) -> Tuple[str, ...]:
        """Return tuple of symbols currently under each tape head."""
        return tuple(tape.readSymbol() for tape in self.tapes)

    def addTrans(self, state: str, read_sym: Tuple[str, ...],
                 new_state: str, write_sym: Tuple[str, ...], moves: Tuple[str, ...]):
        """
        Add a deterministic transition. Raises an error if a transition for the key already exists.
        read_sym, write_sym, moves must be tuples of length ntapes.
        """
        if len(read_sym) != self.ntapes or len(write_sym) != self.ntapes or len(moves) != self.ntapes:
            raise ValueError("read_sym/write_sym/moves must have length = number of tapes")
        key = (state, read_sym)
        if key in self.trans:
            raise KeyError(f"Transition for key {key} already exists (would be nondeterministic).")
        self.trans[key] = (new_state, write_sym, moves)

    def getTrans(self) -> Optional[Tuple[str, Tuple[str, ...], Tuple[str, ...]]]:
        """Return applicable transition (single) or None."""
        key = (self.state, self.readSymbols())
        return self.trans.get(key, None)

    def step(self) -> bool:
        """
        Perform one transition step.
        Returns True if a transition was executed, False if no transition found (halting configuration).
        """
        trans = self.getTrans()
        if trans is None:
            return False
        next_state, write_syms, moves = trans
        # write and move for each tape
        for tape, w, m in zip(self.tapes, write_syms, moves):
            tape.writeSymbol(w)
            tape.moveHead(m)
        self.state = next_state
        return True

    def run(self, max_steps: int = 10000) -> Tuple[bool, int]:
        """
        Run the machine until it halts or accepts or exceeds max_steps.
        Returns (accepted: bool, steps_executed: int)
        """
        steps = 0
        while steps < max_steps:
            if self.state == self.final:
                return (True, steps)
            progressed = self.step()
            if not progressed:
                # no transition available -> halting (reject unless in final state handled above)
                return (self.state == self.final, steps)
            steps += 1
        # max steps exceeded -> consider as non-termination for practical runs
        return (False, steps)

    def __str__(self) -> str:
        out_lines = []
        for i, tape in enumerate(self.tapes):
            out_lines.append(f"Tape {i}: {str(tape)}")
        out_lines.append(f"State: {self.state}")
        return "\n".join(out_lines)


# ---------------------------
# Example usage (unary complement)
# ---------------------------
def example_unary_complement():
    """
    This DTM flips each '1' to '0' and each '0' to '1' on a single tape, then halts in final state when blank seen.
    Alphabet: {'0', '1'}
    Blank symbol is '#'
    """
    tm = DTM(start='q0', final='q_accept', blank='#', ntapes=1)

    # transitions:
    # if read '1' -> write '0', move right, stay in q0
    tm.addTrans('q0', ('1',), 'q0', ('0',), ('R',))
    # if read '0' -> write '1', move right, stay in q0
    tm.addTrans('q0', ('0',), 'q0', ('1',), ('R',))
    # if read blank -> accept (stay, don't change)
    tm.addTrans('q0', ('#',), 'q_accept', ('#',), ('S',))

    input_str = '11011101'
    tm.restart(input_str)
    accepted, steps = tm.run()
    print("=== Unary complement ===")
    print(f"Input: {input_str}")
    print(f"Accepted: {accepted} (steps={steps})")
    print(tm)
    print()

# ---------------------------
# Example usage (2-tape copy)
# ---------------------------
def example_copy_tape1_to_tape2():
    """
    2-tape machine: copies every symbol from tape0 to tape1 then halts.
    Alphabet used here: {'a','b'} and blank '#'.
    Algorithm:
      - On tape0 read symbol:
          - if 'a' or 'b': write same symbol on tape1, move both heads right, stay in q_copy
          - if blank: go to q_accept
    """
    tm = DTM(start='q_copy', final='q_accept', blank='#', ntapes=2)

    # copy transitions for 'a' and 'b'
    tm.addTrans('q_copy', ('a', '#'), 'q_copy', ('a', 'a'), ('R', 'R'))
    tm.addTrans('q_copy', ('b', '#'), 'q_copy', ('b', 'b'), ('R', 'R'))
    # when tape0 finds blank, accept (don't change tapes)
    tm.addTrans('q_copy', ('#', '#'), 'q_accept', ('#', '#'), ('S', 'S'))

    # load input on tape0, tape1 initially blank
    tm.restart('abba')
    accepted, steps = tm.run()
    print("=== Copy tape0 -> tape1 (2-tape example) ===")
    print("Input (tape0): abba")
    print(f"Accepted: {accepted} (steps={steps})")
    print(tm)
    print()

# Allow running examples when this file executed directly
if __name__ == "__main__":
    example_unary_complement()
    example_copy_tape1_to_tape2()
