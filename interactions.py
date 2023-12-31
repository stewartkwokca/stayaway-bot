import math
import game
import datetime as dt

def respond(message: str, user_id: int, username: str):
    user = game.find_by_id(user_id)
    processed_message = message.lower()
    if processed_message[0] != "!":
        return
    processed_message = processed_message[1:]
    if processed_message == "areas":
        out = ""
        i = 0
        tot = 0
        for area in game.playing:
            i += 1
            out += f"Area {i}: {len(area)}\n"
            tot += len(area)
        out += f"Total: {tot}\n"
        out += f"Eliminated: {len(game.eliminated)}"
        return out
    elif processed_message == "start":
        if not game.user_with_same_id_exists(user_id):
            game.createPlayer(username, user_id)
            return "You have been added to the player list, you will be able to join in the next game!"
        else:
            return "You already have a profile!"
    elif processed_message == "help":
        with open('help.txt') as help_file:
            return help_file.read()
    elif processed_message == "leaderboard":
        game.players.sort(key=lambda player: player.wins, reverse=True)
        out = ""
        ctr = 0
        for player in game.players:
            ctr += 1
            out += f"{ctr}.) `{game.find_by_id(player.id).name}` {player.wins}\n"
            if ctr >= 10:
                break
        return out
    elif processed_message == "score":
        return f"Your score: {user.wins}"
    elif processed_message == "end":
        out = f"This round ends at {game.target_time} UTC"
        out += f"\nThat is {math.floor((game.target_time - dt.datetime.now()).total_seconds()/60)} minutes from now."
        return out
    elif processed_message == "id":
        return f"Your ID: {user_id}"
    elif processed_message == "area":
        return f"You are currently in area {game.in_area(user_id)}"
    elif processed_message[:-2] == "move":
        try:
            if not user.moved:
                if int(processed_message[-1:]) > 5 or int(processed_message[-1:]) < 1:
                    return "When using `move`, please enter an integer from 1-5 after the command!"
                else:
                    for area in game.playing:
                        if user in area:
                            area.remove(user)
                            game.playing[int(processed_message[-1:])-1].append(user)
                            user.moved = True
                            return f"Successfully moved to area {int(processed_message[-1:])}"
                    return "You aren't in a game right now!"
            else:
                return f"You have already moved this round! You will stay in Area {game.in_area(user_id)}."
        except Exception as e:
            return f"When using `move`, please enter an integer from 1-5 after the command!\n{e}"

def game_message(event: str, user_id: int) -> str:
    out = ""
    if event == "Game Over":
        out += "New game is starting, everyone is back in Area 1."
        if game.is_winner(user_id):
            out += f"\nYou won! Your score is now **{game.find_by_id(user_id).wins}**."
        out += "\n**Winners**:"
        for winner in game.winners:
            out += f"\n- `{winner.name}`"
    elif event == "Round Over":
        if game.is_elim(user_id):
            out += "\nYou were eliminated, and you won't be added back until the next game."
        else:
            out += "\nYou are still alive!"
    elif event == "one min":
        out += f"\nThis round ends at {game.target_time} UTC."

    return out
