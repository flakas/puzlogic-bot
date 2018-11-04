from puzbot.vision import ScreenshotSource, Vision
from puzbot.bot import Bot
from puzbot.solver import Solver
from puzbot.controls import Controller

source = ScreenshotSource()
vision = Vision(source)
solver = Solver()
controller = Controller()
bot = Bot(vision, controller, solver)

print('Checking out the game board')
bot.refresh()

print('Calculating the solution')
print('Suggested solution:', bot.get_moves())
print('Performing the solution')
bot.do_moves()
