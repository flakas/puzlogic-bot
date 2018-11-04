class Bot:
    """
    Needs to map vision coordinates to solver coordinates
    """

    def __init__(self, vision, controls, solver):
        self.vision = vision
        self.controls = controls
        self.solver = solver

    def get_board(self):
        """ Prepares vision cells for solver """
        cells = self.vision.get_cells()

        return list(map(lambda c: (c[0], c[1], c[4]), cells))

    def get_pieces(self):
        """ Prepares vision pieces for solver """
        return list(map(lambda p: p[4], self.vision.get_pieces()))

    def get_constraints(self):
        """ Prepares vision constraints for solver """
        return self.vision.get_constraints()

    def get_moves(self):
        return self.solver.solve(self.get_board(), self.get_pieces(), self.get_constraints())

    def do_moves(self):
        moves = self.get_moves()
        (board_x, board_y, board_w, board_h, board_cropped) = self.vision.get_game_board()
        pieces = self.vision.get_pieces()

        def get_available_piece(piece, pieces):
            target = list(filter(lambda p: p[4] == piece, pieces))[0]
            remaining_pieces = list(filter(lambda p: p != target, pieces))
            return (target[0], target[1], target[2], target[3], remaining_pieces)

        for (to_x, to_y, move_piece) in moves:
            (from_x, from_y, width, height, pieces) = get_available_piece(move_piece, pieces)
            move_from = (board_x + from_x + width/2, board_y + from_y + height/2)
            move_to = (board_x + to_x + width/2, board_y + to_y + height/2)
            print('Moving', move_from, move_to)

            self.controls.left_mouse_drag(
                move_from,
                move_to
            )

    def refresh(self):
        self.vision.source.refresh()
