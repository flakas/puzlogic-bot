from puzbot.vision import ScreenshotSource, Vision
from puzbot.bot import Bot
from puzbot.solvers.z3 import Z3Solver
from puzbot.controls import Controller

source = ScreenshotSource()
vision = Vision(source, templates_path='templates/')
solver = Z3Solver()
controller = Controller()
bot = Bot(vision, controller, solver)

print('Checking out the game board')
bot.refresh()

print('Board:', bot.get_board())
print('Pieces:', bot.get_pieces())
print('Constraints:', bot.get_constraints())

print('Calculating the solution')
print('Suggested solution:', bot.get_moves())
print('Performing the solution')
bot.do_moves()
