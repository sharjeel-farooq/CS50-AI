import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
        constraints; in this case, the length of the word.)
        """
        for variable in self.crossword.variables:
            length = variable.length
            self.domains[variable] = {
                word for word in self.domains[variable] if len(word) == length
            }
            if not self.domains[variable]:
                raise Exception(f"No valid words for variable {variable} with length {length}")
        
            

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        
        if self.crossword.overlaps[x, y] is None:
            return False
        else:
            i, j = self.crossword.overlaps[x, y]
            revised = False
            for word_x in set(self.domains[x]):
                if any(word_x[i] != word_y[j] for word_y in self.domains[y]):
                    self.domains[x].remove(word_x)
                    revised = True
            return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        
        # If no arcs are given, initialize queue with all arcs in the problem
        if arcs is None:
            queue = [
                (x, y)
                for x in self.crossword.variables
                for y in self.crossword.neighbors(x)
            ]
        else:
            queue = list(arcs)
        
        while queue:
            (x, y) = self.Dequeue(queue)
            if self.revise(x, y):
                if self.size(x.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    self.Enqueue(queue, (z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment) == len(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check if all variables are assigned
        if not self.assignment_complete(assignment):
            return False
        
        # Check if all words are unique
        if len(set(assignment.values())) != len(assignment):
            return False
        
        # Check for conflicts in overlaps
        for (x, y) in self.crossword.overlaps:
            if x in assignment and y in assignment:
                i, j = self.crossword.overlaps[x, y]
                if assignment[x][i] != assignment[y][j]:
                    return False
        
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        conflicts = []

        if var not in assignment:
            for value in self.domains[var]:
                count = 0
                for neighbor in self.crossword.neighbors(var):
                    if neighbor not in assignment:
                        overlap = self.crossword.overlaps.get((var, neighbor))
                        if overlap is not None:
                            i, j = overlap
                            for neighbor_value in self.domains[neighbor]:
                                if value[i] != neighbor_value[j]:
                                    count += 1
                conflicts.append((value, count))
            conflicts.sort(key=lambda x: x[1])
            return [value for value, _ in conflicts]

        return list(self.domains[var])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        
        
        unassigned_vars = [
            var for var in self.crossword.variables if var not in assignment
        ]
        
        if not unassigned_vars:
            return None
        
        # Sort by the number of remaining values in the domain, then by degree
        unassigned_vars.sort(key=lambda var: (len(self.domains[var]), -len(self.crossword.neighbors(var))))
        
        return unassigned_vars[0]
    
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        
        if self.assignment_complete(assignment):
            return assignment
        
        # Select an unassigned variable
        var = self.select_unassigned_variable(assignment)
        
        if var is None:
            return None
        
        # Order domain values for the selected variable
        for value in self.order_domain_values(var, assignment):
            # Create a new assignment with the current value
            new_assignment = assignment.copy()
            new_assignment[var] = value
            
            # Check if the new assignment is consistent
            if self.consistent(new_assignment):
                # Recursively backtrack
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
