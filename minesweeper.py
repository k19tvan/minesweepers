import itertools
import random


class Minesweeper():

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):

        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):

        return self.mines_found == self.mines

class Sentence(): 

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()

    def known_safes(self):
        if self.count == 0:
            return self.cells 
        else:
            return set()    

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):

        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):

        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        
        self.moves_made.add(cell)
        self.mark_safe(cell)
        
        neighbors = set()
        know_mines_count = 0
        
        def inside(x, y):
            return 0 <= x < self.height and 0 <= y < self.width
        
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell:
                    continue
                
                if inside(i, j):
                    if (i, j) in self.mines:
                        know_mines_count += 1
                    elif (i, j) not in self.safes:
                        neighbors.add((i, j))
        
        adjusted_count = count - know_mines_count
        
        if neighbors:
            self.knowledge.append(Sentence(neighbors, adjusted_count))
            
        self.update_knowledge()
            
    def update_knowledge(self):
        changed = True
        while changed:
            changed = False
            new_mines = set()
            new_safes = set()

            for sentence in self.knowledge:
                know_mines = sentence.known_mines()
                know_safes = sentence.known_safes()
                
                if know_mines:
                    new_mines.update(know_mines)
                if know_safes:
                    new_safes.update(know_safes)
         
            for mine in new_mines:
                if mine not in self.mines:
                    self.mark_mine(mine)
                    changed = True
            
            for safe in new_safes:
                if safe not in self.safes:
                    self.mark_safe(safe)
                    changed = True
                    
            self.knowledge = [s for s in self.knowledge if s.cells]
            
            new_sentences = []
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    if sentence1 != sentence2 and sentence2.cells.issubset(sentence1.cells) and sentence2.cells:
                        new_cells = sentence1.cells - sentence2.cells
                        new_count = sentence1.count - sentence2.count
                        
                        if new_count >= 0:
                            infered_sentence = Sentence(new_cells, new_count)
                            if infered_sentence not in self.knowledge and infered_sentence not in new_sentences:
                                new_sentences.append(infered_sentence)
                                changed = True
                                
            self.knowledge.extend(new_sentences)
                    
    def make_safe_move(self):
        
        for move in self.safes:
            if move not in self.moves_made:
                return move
        return None

    def make_random_move(self):
        
        all_cells = set(itertools.product(range(self.height), range(self.width)))
        possible_moves = list(all_cells - self.moves_made - self.mines)
        if possible_moves:
            return random.choice(possible_moves)
        else:
            return None
