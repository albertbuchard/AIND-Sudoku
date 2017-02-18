"""
    Non required functions taken from solution code for clarity.
    What has been implemented: constraints on diagonal units, and naked twin strategy.
    Library re is imported for regexp processing.
"""
import re

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

"""
    Here are defined the two new diagonal units required
"""
diagonal_units = [[rows[i]+cols[i] for i in range(len(rows))],
                 [rows[i]+cols[len(rows)-1-i] for i in range(len(rows))]]

unitlist = row_units + column_units + square_units + diagonal_units
unitlist_without_diagonal = row_units + column_units + square_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)



assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def find_twins (values):
    """
    From a dictionary return a dictionary of value:[twins] pair for twins on any size of values.

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        A dictionary of the form {'replicated_value' : [key_twin1, key_twin2, key_twin3...]}
    """
    twin_dictionary = {}

    # Get an array of all keys
    left_keys = [key for key in values]

    # Start iteration for search
    while(len(left_keys)):
        # Pop one item out of the non processed keys array
        key = left_keys.pop()

        # Look for possible twins
        twin_keys = [(i, left_keys[i]) for i in range(len(left_keys)) if values[left_keys[i]] == values[key]]

        # If twins are found
        if len(twin_keys) > 0:
            # update the twin dictionary
            twin_dictionary[values[key]] = [t[1] for t in twin_keys] + [key]

            # delete twin_keys from the key list to process
            left_keys = [k for k in left_keys if k not in twin_dictionary[values[key]]]

    return(twin_dictionary)

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    for unit in unitlist_without_diagonal:
        # Look for twins in the unit {value: [key_twin1, ..., key_twinN], ...}
        twins = find_twins(dict([(k, values[k]) for k in unit]))

        # Make sure there are no twins with lenght 1 values in the unit
        if any([len(k) == 1 for k in twins]):
            return False

        # Look only for valid twins with number of twin equal to number of possible value
        valid_twins = [[k for k in twins[t] if len(t) == len(twins[t])] for t in twins]

        # Get rid of empty arrays
        valid_twins = [x for x in valid_twins if x]

        for twin_group in valid_twins:
            # Get the other boxes of the unit
            non_twin = [k for k in unit if k not in twin_group]

            # Get values to eliminate
            to_eliminate = values[twin_group[0]]

            # Eliminate the naked twins as possibilities for their peers
            for k in non_twin:
                regex = r"[" + re.escape(to_eliminate) + r"]"
                values[k] = re.sub(regex, "",values[k])

    return values


def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Input: A grid in string form.
    Output: A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def reduce_puzzle(values):
    """
    Iterate eliminate(), only_choice(), and naked_twins().

    If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = naked_twins(values)
        values = only_choice(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example:
            '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

    # We suppose it is a diagonal sudoku (although it is unclear since the naked twins are not passing the test on diagonals)

    # Get dict values from grid
    values = grid_values(grid)

    # Start looping until solved
    return(search(values))



if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
