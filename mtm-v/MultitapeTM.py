"""
CMSC 141
Multitape Turing Machine - Single Head & Track Per Tape
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
		self.tapeHead = START_HEAD_INDEX		# current tape head is found at INDEX 2 due to blank symbols

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

		for symbol in range(len(self.tape_symbols)):
			if symbol == self.tapeHead:
				output += "[" + self.tape_symbols[symbol] + "]"	 	# square brackets marker to show the current tape head position
			
			else:
				output += self.tape_symbols[symbol]
		
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

class MultiTapeTM():
	def __init__(self, start_state, final_state, blank='B', num_of_tapes=1):
		self.state = start_state			# current state
		self.start_state = self.state		# copy the original start state
		self.final_state = final_state		# accept state
		self.blank = blank
		self.states = {}					# dictionary of all states
		self.tapes = [Tapes(blank) for _ in range(num_of_tapes)]	# creates Tapes
		
	def add_state(self, state):
		"""Adds state to the TM"""
		self.states[state.state_name] = state
    
	def input_cell(self, string_input):
		"""Loads the string input in tape 1 and sets up other tapes."""

		for i in range(len(self.tapes)):
			if i == 0:		# input will go in the first tape
				self.tapes[i].tape_symbols = [self.blank, self.blank] + list(string_input) + [self.blank, self.blank]
				self.tapes[i].tapeHead = START_HEAD_INDEX

			else: 			# other tapes will be initially blank
				# Sets five (5) blank cells arbitrarily
				self.tapes[i].tape_symbols = [self.blank] * INITIAL_BLANK_SIZE
				self.tapes[i].tapeHead = START_HEAD_INDEX

		self.state = self.start_state 	# resets machine to start state
		
	def read_symbols(self):
		"""Reads all tape heads at once; Returns a tuple of symbols"""
		return tuple(tape.read_current_symbols() for tape in self.tapes)
	
	def move_tape_head(self):
		"""Moves tape head in one transition step"""

		current_state = self.states[self.state]			# get the current State object
		symbols = self.read_symbols()			# reads symbols on all tapes
		transitions = current_state.get_transition(symbols)

		if not transitions:
			# TM will halt is no transition fp
			print("No transition defined.\nTuring Machine HALTS")
			return False
		
		# dissects the transitions
		next_state, next_tape_symbols, directions = transitions	
		self.state = next_state		# updates the state to the next state

		# Writes and moves for each tape
		for i in range(len(self.tapes)):
			self.tapes[i].write_next_symbols(next_tape_symbols[i])
			self.tapes[i].move_direction(directions[i])
		
		return True
	
	def is_accepted(self, string_input):
		"""Runs the MTM until it accepts or halts"""
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
		for tape in range(len(self.tapes)):
			output += "Tape #" + str(tape + 1) + ": " + str(self.tapes[tape]) + "\n"

		return output
	
if __name__ == '__main__':
	# Example 1: Unary complement (1-tape)
	q0 = State('q0')		# Start/current state of the example
	q0.add_transition(('1',), 'q0', ('0',), ('R',))
	q0.add_transition(('0',), 'q0', ('1',), ('R',))
	q0.add_transition(('B',), 'q_accept', ('B',), ('S',))
	q_accept = State('q_accept')

		# ENTRY POINT - Example 1
	mtm1 = MultiTapeTM('q0', 'q_accept', blank='B', num_of_tapes=1)
	mtm1.add_state(q0)
	mtm1.add_state(q_accept)
	accepted = mtm1.is_accepted('010101')
	print("Unary Complement (1-tape):")
	print("Accepted:", accepted)
	print(mtm1)

    # Example 2: Copy tape0 -> tape1 (2-tape MTM)
	q_copy = State('q_copy')
	q_copy.add_transition(('a','B'), 'q_copy', ('a','a'), ('R','R'))
	q_copy.add_transition(('h','B'), 'q_copy', ('h','h'), ('R','R'))
	q_copy.add_transition(('n','B'), 'q_copy', ('n','n'), ('R','R'))
	q_copy.add_transition(('B','B'), 'q_accept', ('B','B'), ('S','S'))
	q_accept2 = State('q_accept')

		# ENTRY POINT - Example 2
	mtm2 = MultiTapeTM('q_copy', 'q_accept', blank='B', num_of_tapes=2)
	mtm2.add_state(q_copy)
	mtm2.add_state(q_accept2)
	accepted2 = mtm2.is_accepted('hannah')
	print("\nCopy Tape 1 -> Tape 2 (2-tape):")
	print("Accepted:", accepted2)
	print(mtm2)

