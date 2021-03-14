import discord
from Chess import *

client = discord.Client()

hist = None
searcher = None


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    # await client.fetch_channel("748656392868462695").send('Hello')
    global hist, searcher
    if message.author == client.user:
        return

    if message.content.startswith('!commands'):
        await message.channel.send(
            'List of Basic Commands:\n' + '!newgame:[black/white]\nEx.!newgame:white (if no arguments are given, '
                                          'defaults to level 10)\n' + '!move:[initial position-final position]\nEx.!move:e2-e4\n' + '!snapshot')
    elif (message.content.startswith('!move:')):
        user_move = message.content[6:]
        user_move = user_move.replace(" ", "")
        user_move = user_move.replace("-", "")
        if user_move == 'resign':
            await message.channel.send('Too bad, better luck next time. Start a new game with the !newgame command')
            return

        if hist[-1].score <= -MATE_LOWER:
            await message.channel.send("You lost! Start a new game with !newgame command")
        # We query the user until she enters a (pseudo) legal move.
        move = None
        while move not in hist[-1].gen_moves():
            match = re.match('([a-h][1-8])' * 2, user_move)
            if match:
                move = parse(match.group(1)), parse(match.group(2))
            else:
                # Inform the user when invalid input (e.g. "help") is entered
                await message.channel.send("Please enter a move like g8f6")
        hist.append(hist[-1].move(move))

        # After our move we rotate the board and print it again.
        # This allows us to see the effect of our move.
        # print_pos(hist[-1].rotate())

        if hist[-1].score <= -MATE_LOWER:
            await message.channel.send("You won! Congratulations! Start a new game with the !newgame command")
        # Fire up the engine to look for a move.
        start = time.time()
        for _depth, move, score in searcher.search(hist[-1], hist):
            if time.time() - start > 1:
                break

        if score == MATE_UPPER:
            await message.channel.send("Checkmate! You win! To start a new game use the !newgame function")

        # The black player moves from a rotated position, so we have to
        # 'back rotate' the move before printing it.
        await message.channel.send("My move:" + render(119 - move[0]) + '-' + render(119 - move[1]))
        hist.append(hist[-1].move(move))


    elif (message.content.startswith('!newgame:')):
        game = message.content[9:].lower()
        game = game.replace(" ", "")
        init_board = initial if game == 'white' else initial_black
        hist = [Position(init_board, 0, (True, True), (True, True), 0, 0)]
        searcher = Searcher()
        await message.channel.send('Game with ' + game + ' created')
        if game == 'black':
            start = time.time()
            for _depth, move, score in searcher.search(hist[-1], hist):
                if time.time() - start > 1:
                    break
            await message.channel.send("My move:" + render(119 - move[0]) + '-' + render(119 - move[1]))
            hist.append(hist[-1].move(move))

    elif (message.content.startswith('!snapshot')):
        await message.channel.send(print_pos(hist[-1]))


client.run('NzUwOTAzMTE0NzA1NjY2MTc4.X1BTBQ.WhyhwdO2wWGpxiZdF3R30DQvEoM')
