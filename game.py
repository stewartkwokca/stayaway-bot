import datetime as dt
import pandas as pd
import bot
import asyncio
import interactions

playing = [[], [], [], [], []]
eliminated = []

winners = []
target_time = ""

MIN = 1

class Player:
    def __init__(self, name, player_id, wins):
        self.name = name
        self.id = player_id
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
    winners.clear()
    for area in playing:
        for player in area:
            player.win()
        area.clear()
    reset_game()
    for player in players:
        await bot.initiate_message(bot.client.get_user(int(player.id)), "Game Over", interactions.game_message("Game Over", player.id))

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

    players_left = 0
    for area in min_areas:
        players_left += len(area)
    if players_left < 5:
        await game_over()
        return
    for player in players:
        await bot.initiate_message(bot.client.get_user(player.id), "Round Over", interactions.game_message("Round Over", player.id))

async def check_at_timeUp():
    try:
        if is_game_over():
            await game_over()
        else:
            await round_over()
        update_players()
    except Exception as e:
        await bot.initiate_message(bot.client.get_user(717943669801353300), "Error", e)
    finally:
        await timeUp()

async def timeUp():
    try:
        global target_time
        now = dt.datetime.now()
        target_time = now.replace(microsecond=0) + dt.timedelta(minutes=MIN)  # Set the desired time here
        delta_minus_one = target_time - now - dt.timedelta(minutes=1)

        await asyncio.sleep(delta_minus_one.total_seconds())
        for player in players:
            if in_area(player.id)[0] != "N":
                await bot.initiate_message(bot.client.get_user(player.id), "One Minute Warning!",
                                           interactions.game_message("one min", player.id))
        await asyncio.sleep(dt.timedelta(minutes=1).total_seconds())
    except Exception as e:
        await bot.initiate_message(bot.client.get_user(717943669801353300), "Error", e)
    finally:
        await check_at_timeUp()

def user_with_same_id_exists(user_id):
    for player in players:
        if player.id == user_id:
            return True
    return False

def createPlayer(name, user_id):
    players.append(Player(name, user_id, 0))
    update_players()

def update_players():
    players_dict.clear()
    for player in players:
        players_dict.append({"name": player.name, "id": player.id, "wins": player.wins})
    pd.DataFrame(players_dict).to_csv("./users.csv", index=False)

async def start_game():
    reset_game()
    await timeUp()

def find_by_id(user_id: int):
    for player in players:
        if player.id == user_id:
            return player
    return None

def in_area(user_id: int):
    ctr = 0
    for area in playing:
        ctr += 1
        for player in area:
            if player.id == user_id:
                return str(ctr)
    return "N/A (You aren't in this round)"

def is_elim(user_id: int):
    return (find_by_id(user_id) in eliminated) and (find_by_id(user_id) is not None)

def is_winner(user_id: int):
    return (find_by_id(user_id) in winners) and (find_by_id(user_id) is not None)
