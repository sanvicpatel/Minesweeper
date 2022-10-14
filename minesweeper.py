import itertools
import random
from copy import deepcopy

class Minesweeper():
    """
    Minesweeper game representation
    """

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
        """
        Prints a text-based representation
        of where mines are located.
        """
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
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

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
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        if len(self.cells) == self.count:  # Checks if the length of the set of cells is equal to the count
            return self.cells        # If so, returns the entire set because every cell in the set must be a mine


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:      # Checks if the count of the sentence is 0
            return self.cells    # If so, returns the entire set because every cell in the set must be safe



    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:       # If the cell is in the sentence's set of cells,
            self.cells.remove(cell)    # Then removes the cell from the sentence
            self.count -= 1        # And decreases the count by one as there is one less mine in the set now


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:      # If the cell is in the sentence's set of cells,
            self.cells.remove(cell)  # then removes the cell from the sentence

class MinesweeperAI():
    """
    Minesweeper game player
    """

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
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        self.moves_made.add(cell)  # marks the cell as a move that has been made
        self.mark_safe(cell) # marks the cells as safe

        # Creates a new sentence based on the cell's neighbors and given value of count
        neighbors = set()
        for i in range(cell[0] - 1, cell[0] + 2):      # Traverses every cell one column, row, or diagonal away
            for j in range(cell[1] - 1, cell[1] + 2):   # from the given cell to find its neighbors

                if (i, j) == cell:  # Ignore the cell itself
                    continue

                if 0 <= i < self.height and 0 <= j < self.width:    # Makes sure the row and column are inside the board
                    new_cell = (i, j)   # Creates new cell
                    if new_cell not in self.mines and new_cell not in self.safes and new_cell not in self.moves_made:
                        neighbors.add(new_cell)     # Adds new cell to set only if its state is uncertain
                    if new_cell in self.mines:  # If the new cell is known as a mine, then decreases count
                        count -= 1          # because the cell will not be included in the sentence

        neighbors_sentence = Sentence(neighbors, count)
        self.knowledge.append(neighbors_sentence)   # Adds new sentence to knowledge base

        change = True
        while change:   # Keeps finding subsets and marking cells as safe/mines until no new sentences can be added
            change = False
            for sentence in self.knowledge:

                # Checks if sentence contains mines/safes. If so, marks cells as mines/safes, respectively
                if sentence.known_mines() == sentence.cells and len(sentence.cells) != 0:
                    copy_cells = deepcopy(sentence.cells)       # Uses deepcopy to not change the original iterator
                    for cell in copy_cells:
                        self.mark_mine(cell)
                if sentence.known_safes() == sentence.cells and len(sentence.cells) != 0:
                    copy_cells = deepcopy(sentence.cells)       # Uses deepcopy to not change the original iterator
                    for cell in copy_cells:
                        self.mark_safe(cell)

            # Removes any sentences whose sets are empty (because they have been marked as mines/safes)
            org_knowledge = deepcopy(self.knowledge)    # Uses deepcopy to not change iterator
            for sentence in org_knowledge:
                if len(sentence.cells) == 0:
                    self.knowledge.remove(sentence)

            org_knowledge = deepcopy(self.knowledge)    # Uses deepcopy to not change iterator

            # Takes two sentences at a time from knowledge and checks for subsets
            for sentence in org_knowledge:
                for other_sentence in org_knowledge:
                    if sentence.cells < other_sentence.cells:    # If one sentence is a subset of the other,
                        new_cells = other_sentence.cells.difference(sentence.cells)  # then creates new set
                        new_count = other_sentence.count - sentence.count    # and new count value

                        new_sentence = Sentence(new_cells, new_count)   # Creates new sentence for the subset
                        if new_sentence not in self.knowledge:  # Adds to knowledge if it does not exist already
                            self.knowledge.append(new_sentence)

                        if other_sentence in self.knowledge:    # Removes larger sentence of the two
                            self.knowledge.remove(other_sentence)   # to avoid redundancy and duplicate subsets
                        change = True

        return None



    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Traverses every cell on board
        for row in range(self.height):
            for cell in range(self.width):
                position = (row, cell)
                if position in self.safes and position not in self.moves_made:  # If cell is safe and not already a move
                    return position                 # then returns the cell
        return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possible_cells = []     # Creates empty list of possible moves

        # Traverses every cell on board
        for row in range(self.height):
            for cell in range(self.width):
                position = (row, cell)
                if position not in self.moves_made and position not in self.mines:
                    possible_cells.append(position)     # Adds position to list if not mine and not already a move

        if len(possible_cells) == 0:    # If there are no possible moves, returns None
            return None
        return random.choice(possible_cells)    # Otherwise returns a random move from list
