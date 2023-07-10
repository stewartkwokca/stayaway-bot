import datetime as dt
import pandas as pd
import bot
import asyncio
import interactions

playing = [[],[],[],[],[]]
eliminated = []

winners = []
target_time = ""

MIN = 60

class Player:
    def __init__(self, name, id, wins):
        self.name = name
        self.id = id
        self.wins = wins
    def win(self):
        self.wins += 1
        global winners
        winners.append(self)


with open("./users.csv") as user_data_file:
    players_dict = pd.read_csv(user_data_file).to_dict(orient="records")
    players = [Player(player["name"], player["id"], player["wins"]) for player in players_dict]


def is_game_over():
    for area in playing:
        if len(area) == 0:
            return True
    return False

async def game_over():
    for area in playing:
        for player in area:
            player.win()
        area.clear()
    reset_game()
    for player in players:
        await bot.initiate_message(bot.client.get_user(int(player.id)), interactions.game_message("Game Over", player.id))

def reset_game():
    eliminated.clear()
    for player in players:
        playing[0].append(player)

async def round_over():
    min_count = 2**31 - 1
    clear_areas = []
    min_areas = []
    for area in playing:
        if len(area) > min_count:
            clear_areas.append(area)
        elif len(area) == min_count:
            min_areas.append(area)
        else:
            min_count = len(area)
            for min_area in min_areas:
                clear_areas.append(min_area)
            min_areas.clear()
            min_areas.append(area)
    for area in clear_areas:
        for player in area:
            eliminated.append(player)
        area.clear()

    for player in players:
        await bot.initiate_message(bot.client.get_user(int(player.id)), interactions.game_message("Round Over", player.id))

async def check_at_timeUp():
    if is_game_over():
        await game_over()
    else:
        await round_over()
    update_players()
    await timeUp()

async def timeUp():
    global target_time
    now = dt.datetime.now()
    target_time = now.replace(microsecond=0) + dt.timedelta(minutes=MIN)  # Set the desired time here
    delta_minus_one = target_time - now - dt.timedelta(minutes=1)

    await asyncio.sleep(delta_minus_one.total_seconds())
    for player in players:
        if in_area(player.id)[0] != "N":
            await bot.initiate_message(bot.client.get_user(int(player.id)),
                                       interactions.game_message("one min", player.id))
    await asyncio.sleep(dt.timedelta(minutes=1).total_seconds())
    await check_at_timeUp()

def user_with_same_id_exists(id):
    for player in players:
        if player.id == id:
            return True
    return False

def createPlayer(name, user_id):
    players.append(Player(name, user_id, 0))
    update_players()

def update_players():
    players_dict.clear()
    for player in players:
        players_dict.append({"name": player.name, "id":player.id, "wins": player.wins})
    pd.DataFrame(players_dict).to_csv("./users.csv", index=False)

async def start_game():
    reset_game()
    await timeUp()

def find_by_id(id):
    for player in players:
        if player.id == id:
            return player
    return None

def in_area(id):
    ctr = 0
    for area in playing:
        ctr += 1
        for player in area:
            if player.id == id:
                return str(ctr)
    return "N/A (You aren't in this round)"

def is_elim(id):
    return find_by_id(id) in eliminated and find_by_id(id) != None

def is_winner(id):
    return find_by_id(id) in winners and find_by_id(id) != None