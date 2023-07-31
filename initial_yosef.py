N_ROWS_LIKE_N_COLS = None

def ascii_map(mem_chunk):
	return 


class Table:
	def __init__(self, n_cols:int=8, n_rows:int=N_ROWS_LIKE_N_COLS, default_value:str = '.'):
		if n_rows == N_ROWS_LIKE_N_COLS:
			n_rows = n_cols
		self.n_cols = n_cols
		self.n_rows = n_rows
		self.table = [[default_value for _ in range(n_rows)] for _ in range(n_cols)]
	
	def __str__(self) -> str:
		seperator_row = "+---"*self.n_cols+"+"+"\n"
		res = seperator_row
		for row in self.table:
			res += "|"
			for cell in row:
				res += " "+cell+" |"
			res += "\n"
			res += seperator_row
		return res

	def show(self):
		print(self)

Table().show()