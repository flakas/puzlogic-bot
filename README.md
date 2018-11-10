# Puzbot

OpenCV bot which plays and solves numeric puzzles in the [Puzlogic](https://www.kongregate.com/games/ejbarreto/puzlogic?haref=HP_HNG_puzlogic) Unity game.

**Puzlogic** is a number based puzzle game with some similarities to Sudoku.
In Puzlogic you get an oddly shaped grid with locations where you can fill in a number, and with some numbers already filled in. You also get a set of numbers you have to put on the board.
The rules are that in no row and no column may there be two or more repeating numbers, and some columns or rows may have a constraint, requiring all numbers on that row/column to sum to a given number.

Goal of Puzbot is to solve these puzzles one by one, going from screen to screen, without any human intervention.

Puzbot has 3 main parts:

- **Vision** - takes the board as it is displayed on screen, finding numbers and required locations, and transforms it into data structures more convenient for the solver to solve;
- **Solver** - takes the machine-readable representation of the situation and produces a list of steps necessary to take to complete the puzzle;
- **Controller** - Operates mouse controls, traversing through UI screens and executing instructions of the Solver.

If you would like to see it in action, here is a quick demo:

[![Basic Puzlogic game bot with OpenCV and Python](https://img.youtube.com/vi/Z8l1TRdUUSM/0.jpg)](https://www.youtube.com/watch?v=Z8l1TRdUUSM)

If you would like to know how it was built, here is a series of posts detailing just that: [Solving Puzlogic puzzle game with Python and OpenCV: Part 1](https://tautvidas.com/blog/2018/09/solving-puzlogic-puzzle-game-with-python-and-opencv-part-1/).
