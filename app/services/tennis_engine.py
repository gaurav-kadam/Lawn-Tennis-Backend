
PLAYER1 = "PLAYER1"
PLAYER2 = "PLAYER2"


def _other(player):
    return PLAYER2 if player == PLAYER1 else PLAYER1


def create_initial_state(match_format: str, first_server: str):
    return {
        "match_format": match_format,
        "server": first_server,
        "player1_points": 0,
        "player2_points": 0,
        "is_tiebreak": False,
        "tiebreak_player1_points": 0,
        "tiebreak_player2_points": 0,
        "player1_games": 0,
        "player2_games": 0,
        "completed_sets": [],  # list of dicts
        "player1_sets": 0,
        "player2_sets": 0,
        "winner": None,
    }


def _check_game_win(p1, p2):
    if p1 >= 4 and p1 - p2 >= 2:
        return PLAYER1
    if p2 >= 4 and p2 - p1 >= 2:
        return PLAYER2
    return None


def _check_tiebreak_win(p1, p2):
    if p1 >= 7 and p1 - p2 >= 2:
        return PLAYER1
    if p2 >= 7 and p2 - p1 >= 2:
        return PLAYER2
    return None


def _check_set_win(g1, g2):
    if g1 >= 6 and g1 - g2 >= 2:
        return PLAYER1
    if g2 >= 6 and g2 - g1 >= 2:
        return PLAYER2
    if g1 == 6 and g2 == 6:
        return "TIEBREAK"
    return None


def _check_match_win(s1, s2, match_format):
    needed = 2 if match_format == "BEST_OF_3" else 3
    if s1 >= needed:
        return PLAYER1
    if s2 >= needed:
        return PLAYER2
    return None


def _server_for_tiebreak(current_server, points_played_before):
    if points_played_before == 0:
        return current_server
    should_switch = (points_played_before - 1) % 2 == 0
    return _other(current_server) if should_switch else current_server


def _finish_set(state, winner, was_tiebreak):
    state["completed_sets"].append({
        "player1_games": state["player1_games"],
        "player2_games": state["player2_games"],
        "was_tiebreak": was_tiebreak,
        "tiebreak_player1_points": state["tiebreak_player1_points"] if was_tiebreak else None,
        "tiebreak_player2_points": state["tiebreak_player2_points"] if was_tiebreak else None,
    })

    if winner == PLAYER1:
        state["player1_sets"] += 1
    else:
        state["player2_sets"] += 1

    state["player1_games"] = 0
    state["player2_games"] = 0
    state["player1_points"] = 0
    state["player2_points"] = 0
    state["is_tiebreak"] = False
    state["tiebreak_player1_points"] = 0
    state["tiebreak_player2_points"] = 0

    match_winner = _check_match_win(state["player1_sets"], state["player2_sets"], state["match_format"])
    if match_winner:
        state["winner"] = match_winner

    return state


def _finish_game(state, winner):
    if winner == PLAYER1:
        state["player1_games"] += 1
    else:
        state["player2_games"] += 1

    state["player1_points"] = 0
    state["player2_points"] = 0
    state["server"] = _other(state["server"])

    set_result = _check_set_win(state["player1_games"], state["player2_games"])

    if set_result == "TIEBREAK":
        state["is_tiebreak"] = True
        state["tiebreak_player1_points"] = 0
        state["tiebreak_player2_points"] = 0
    elif set_result:
        state = _finish_set(state, set_result, was_tiebreak=False)

    return state


def _handle_normal_point(state, winner):
    if winner == PLAYER1:
        state["player1_points"] += 1
    else:
        state["player2_points"] += 1

    game_winner = _check_game_win(state["player1_points"], state["player2_points"])
    if game_winner:
        state = _finish_game(state, game_winner)

    return state


def _handle_tiebreak_point(state, winner):
    points_before = state["tiebreak_player1_points"] + state["tiebreak_player2_points"]

    if winner == PLAYER1:
        state["tiebreak_player1_points"] += 1
    else:
        state["tiebreak_player2_points"] += 1

    state["server"] = _server_for_tiebreak(state["server"], points_before + 1)

    tb_winner = _check_tiebreak_win(state["tiebreak_player1_points"], state["tiebreak_player2_points"])
    if tb_winner:
        if tb_winner == PLAYER1:
            state["player1_games"] += 1
        else:
            state["player2_games"] += 1
        state = _finish_set(state, tb_winner, was_tiebreak=True)

    return state


def apply_point(state: dict, winner: str) -> dict:
    if state.get("winner"):
        return state  # match already over, ignore further points

    if state["is_tiebreak"]:
        return _handle_tiebreak_point(state, winner)
    return _handle_normal_point(state, winner)


def compute_match_state(match_format: str, first_server: str, point_winners: list[str]) -> dict:
    state = create_initial_state(match_format, first_server)
    for winner in point_winners:
        state = apply_point(state, winner)
    return state


def display_points(p1: int, p2: int):
    names = ["0", "15", "30", "40"]
    if p1 < 3 and p2 < 3:
        return names[p1], names[p2]
    if p1 == p2:
        return "40", "40"
    if p1 > p2:
        return "AD", "40"
    return "40", "AD"
