import game

def respond(message: str, user_id: str, username: str):
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
            out += f"{ctr} {game.find_by_id(player.id).name} {player.wins}\n"
            if ctr >= 10:
                break
        return out
    elif processed_message == "score":
        return f"Your score: {game.find_by_id(user_id).wins}"
    elif processed_message == "end":
        return f"This round ends at {game.target_time} UTC"
    elif processed_message == "id":
        return f"Your ID: {user_id}"
    elif processed_message == "area":
        return f"You are currently in area {game.in_area(user_id)}"
    elif processed_message[:-2] == "move":
        try:
            if int(processed_message[-1:]) > 5 or int(processed_message[-1:]) < 1:
                return "When using `move`, please enter an integer from 1-5 after the command!"
            else:
                for area in game.playing:
                    if game.find_by_id(user_id) in area:
                        area.remove(game.find_by_id(user_id))
                        game.playing[int(processed_message[-1:])-1].append(game.find_by_id(user_id))
                        return f"Successfully moved to area {int(processed_message[-1:])}"
                return "You aren't in a game right now!"
        except Exception as e:
            return f"When using `move`, please enter an integer from 1-5 after the command!\n{e}"

def game_message(event: str, user_id: str) -> str:
    out = ""
    if event == "Game Over":
        out += "Game Over! New game is starting, everyone is back in area 1."
        if game.is_winner(user_id):
            out += f"\nYou won! Your score is now {game.find_by_id(user_id).wins}."
            out += "\nWinners:"
            for winner in game.winners:
                out += f"\n - {winner.name}"
    elif event == "Round Over":
        out += "Round Over."
        if game.is_elim(user_id):
            out += "\nYou were eliminated, and you won't be added back until the next game."
        else:
            out += "\nYou are still alive!"
    elif event == "one min":
        out += "One minute warning!"
    out += f"\nNext round ends at {game.target_time} UTC."

    return out
