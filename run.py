from puzbot.vision import ScreenshotSource, Vision
from puzbot.bot import Bot
from puzbot.solver import Solver
from puzbot.controls import Controller

source = ScreenshotSource()
vision = Vision(source)
solver = Solver()
controller = Controller()
bot = Bot(vision, controller, solver)
bot.refresh()

print('Bot moves:', bot.get_moves())
print(bot.do_moves())
