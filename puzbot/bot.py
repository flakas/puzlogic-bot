class Bot:
    """ Needs to map vision coordinates to solver coordinates """

    def __init__(self, vision, controls, solver):
        self.vision = vision
        self.controls = controls
        self.solver = solver

    def get_board(self):
        """ Prepares vision cells for solver """
        cells = self.vision.get_cells()
        return list(map(lambda c: (c.y, c.x, -1 if c.content == False else c.content), cells))

    def get_pieces(self):
        """ Prepares vision pieces for solver """
        return list(map(lambda p: p.content, self.vision.get_pieces()))

    def get_constraints(self):
        """ Prepares vision constraints for solver """
        return self.vision.get_constraints()

    def get_moves(self):
        return self.solver.solve(self.get_board(), self.get_pieces(), self.get_constraints())

    def do_moves(self):
        moves = self.get_moves()

        if not moves:
            print('Unable to find a solution')
            return False

        board = self.vision.get_game_board()
        available_pieces = self.vision.get_pieces()

        def get_available_piece(piece, pieces):
            target = list(filter(lambda p: p.content == piece, pieces))[0]
            remaining_pieces = list(filter(lambda p: p != target, pieces))
            return (target, remaining_pieces)

        for (to_y, to_x, required_piece) in moves:
            (piece, available_pieces) = get_available_piece(required_piece, available_pieces)

            # Offset of the game screen within a window + offset of the cell + center of the cell
            move_from = (board.x + piece.x + piece.w/2, board.y + piece.y + piece.h/2)
            move_to = (board.x + to_x + piece.w/2, board.y + to_y + piece.h/2)
            print('Moving', move_from, move_to)

            self.controls.left_mouse_drag(
                move_from,
                move_to
            )

    def refresh(self):
        """ Get a new frame """
        self.vision.source.refresh()
