"""
CMSC 141
Multitape Turing Machine - Single Head & Track Per Tape
Author: Sophe Mae Dela Cruz
"""

from typing import List, Tuple

START_HEAD_INDEX = 2
INITIAL_BLANK_SIZE = 5

class Tapes:
	def __init__(self, blank, initial_symbol=''):
		self.blank = blank
		# initial symbol from the user
		# adds two Blank symbols per both ends to make it an infinite tape
		self.tape_symbols = [blank, blank] + list(initial_symbol) + [blank, blank]
		self.head = START_HEAD_INDEX		# current tape head is found at INDEX 2 due to blank symbols

	def read_current_symbols(self):
		return self.tape_symbols[self.head]
	
	def write_next_symbols(self, tape_symbol):
		self.tape_symbols[self.head] = tape_symbol

	def move_direction(self, direction):

		if direction == 'L':
			self.head -= 1

			if self.head < 0:
				self.tape_symbols.insert(0, self.blank)
				self.head = 0

		elif direction == 'R':
			self.head += 1

			if self.head >= len(self.tape_symbols):
				self.tape_symbols.append(self.blank)

		elif direction == 'S':
			pass

	def __str__(self):
		output = ''

		for symbol in range(len(self.tape_symbols)):
			if symbol == self.head:
				output += "." + self.tape_symbols[symbol]
			
			else:
				output += self.tape_symbols[symbol]
		
		return output

class State:
	# transition function
	# next variable
	def __init__(self, state_name):
		self.state_name = state_name	
		"""
		tuple for transition functions
		key: current tape symbols
		values: next state, new tape symbols, and direction
		"""
		self.transitions = {}

	def add_transition(self, current_symbols, next, next_symbols, directions):
		self.transitions[current_symbols] = [next, next_symbols, directions]

	def get_transition(self, current_symbols):
		return self.transitions.get(current_symbols, None)

class MultiTapeTM():
	# two blank symbols per both ends to be infinite tape
	# tapeHead variable - is the current state index
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
				self.tapes[i].head = START_HEAD_INDEX

			else:
				# Sets five (5) blank cells arbitrarily
				self.tapes[i].tape_symbols = [self.blank] * INITIAL_BLANK_SIZE
				self.tapes[i].head = START_HEAD_INDEX

		self.state = self.start_state
		
	def read_symbols(self):
		return tuple(tape.read_current_symbols() for tape in self.tapes)
	
	def move_tape_head(self):
		current_state = self.states[self.state]
		symbols = self.read_symbols()
		transitions = current_state.get_transition(symbols)

		if not transitions:
			print("No transition defined.\nTuring Machine HALTS")
			return False
		
		# dissects the transitions
		next_state, next_tape_symbols, directions = transitions	
		self.state = next_state		# updates the state to the next state

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
			output += "Tape #" + str(tape) + ":" + str(self.tapes[tape]) + "\n"

		return output
	
if __name__ == '__main__':
	# Example 1: Unary complement (1-tape)
	q0 = State('q0')		# Start/current state of the problem
	q0.add_transition(('1',), 'q0', ('0',), ('R',))
	q0.add_transition(('0',), 'q0', ('1',), ('R',))
	q0.add_transition(('#',), 'q_accept', ('#',), ('S',))
	q_accept = State('q_accept')

	tm1 = MultiTapeTM('q0', 'q_accept', blank='#', num_of_tapes=1)
	tm1.add_state(q0)
	tm1.add_state(q_accept)
	accepted = tm1.is_accepted('010101')
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

	tm2 = MultiTapeTM('q_copy', 'q_accept', blank='#', num_of_tapes=2)
	tm2.add_state(q_copy)
	tm2.add_state(q_accept2)
	accepted2 = tm2.is_accepted('hannah')
	print("\nCopy Tape0 -> Tape1 (2-tape):")
	print("Accepted:", accepted2)
	print(tm2)

