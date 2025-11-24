import os
import argparse
import importlib.util
import time
from tqdm import tqdm

INVALID_MOVE = 1
TIMEOUT = 2
NORMAL = -1
MAX_TIME = 24

from utils_coord import coord_to_idx, idx_to_coord, apply_move, build_board_lines_from_state_vec

def load_agent(agent_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    agent_dir = os.path.join(base_dir, "agents", agent_name)
    module_path = os.path.join(agent_dir, "main.py")

    if not os.path.exists(module_path):
        raise FileNotFoundError(f"Agent '{agent_name}' not found at {module_path}")

    spec = importlib.util.spec_from_file_location(f"agent_{agent_name}", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "init"):
        raise AttributeError(f"Agent '{agent_name}' has no init() function")
    if not hasattr(module, "run"):
        raise AttributeError(f"Agent '{agent_name}' has no run() function")

    module.init()
    return module

def agent_choose_move(agent_module, state_vec, xsize=5, ysize=5):
    board_lines = build_board_lines_from_state_vec(state_vec, xsize, ysize)
    move_coord = agent_module.run(board_lines, xsize, ysize)

    if not isinstance(move_coord, (list, tuple)) or len(move_coord) != 3:
        raise ValueError(f"Agent run() must return (x, y, z), got: {move_coord}")

    x, y, z = int(move_coord[0]), int(move_coord[1]), int(move_coord[2])
    move_idx = coord_to_idx(x, y, z)
    return move_idx

def play_one_game(agents, print_log=False, xsize=5, ysize=5):
    players = [
        {
            "agent" : agents[0]["agent"],
            "time" : 0,
            "score" : 0
        },
        {
            "agent" : agents[1]["agent"],
            "time" : 0,
            "score" : 0
        }
    ]

    replay_data = [xsize, ysize]
    log_data = []

    state_vec = [0.0] * 60          
    square_owner = [[0] * ysize for _ in range(xsize)]

    forced_winner = -1
    reason = 0

    current_player = 0 

    while True:
        legal_moves = [i for i, v in enumerate(state_vec) if v == 0]
        if not legal_moves:
            break 

        start = time.perf_counter()
        move = agent_choose_move(players[current_player]["agent"], state_vec, xsize, ysize)
        elapsed = time.perf_counter() - start
        players[current_player]["time"] += elapsed

        if players[current_player]["time"] > MAX_TIME:
            forced_winner = 1 - current_player
            reason = TIMEOUT
            break

        replay_data.append(current_player)
        replay_data.extend(idx_to_coord(move))

        if move is None or not (0 <= move < 60) or state_vec[move] != 0:
            forced_winner = not current_player
            reason = INVALID_MOVE
            break 

        completed = apply_move(state_vec, square_owner, move, current_player)

        if completed > 0:
            players[current_player]["score"] += completed
        else:
            current_player = 1 - current_player

    if print_log:
        print(",".join(map(str,replay_data)))
        print(players[0]["score"], players[1]["score"])

    return players[0]["score"], players[1]["score"], forced_winner, reason

def evaluate_agents(agents, num_games=1000, xsize=5, ysize=5, print_log=False):
    players = [
        {
            "agent": agents[0]["agent"],
            "name": agents[0]["name"],
            "wins": 0,
            "total_score": 0,
        }, 
        {
            "agent": agents[1]["agent"],
            "name": agents[1]["name"],
            "wins": 0,
            "total_score": 0,
        }
    ]
    
    for i in range(2):
        players[0]["wins"] = 0
        players[1]["wins"] = 0
        players[0]["total_score"] = 0
        players[1]["total_score"] = 0

        for game_idx in tqdm(range(num_games),
                             desc=f"{players[0]['name']} vs {players[1]['name']}",
                             disable=print_log):
            p1_score, p2_score, forced_winner, reason = play_one_game(
                agents,
                print_log=print_log,
                xsize=xsize,
                ysize=ysize
            )

            players[0]["total_score"] += p1_score
            players[1]["total_score"] += p2_score

            if forced_winner == -1:
                if p1_score > p2_score:
                    players[0]["wins"] += 1
                    last_result = "win"
                    last_reason = "normal"
                elif p1_score < p2_score:
                    players[1]["wins"] += 1
                    last_result = "lose"
                    last_reason = "normal"
            elif forced_winner == 0:
                players[0]["wins"] += 1
                last_result = "win"
                last_reason = "opponent timeout" if reason == TIMEOUT else "opponent invalid move"
                tqdm.write(
                    f"{players[0]['name']} won because opponent "
                    f"{'timeout' if reason == TIMEOUT else 'wrong move'}"
                )
            elif forced_winner == 1:
                players[1]["wins"] += 1
                last_result = "lose"
                last_reason = "timeout" if reason == TIMEOUT else "invalid move"
                tqdm.write(
                    f"{players[1]['name']} won because opponent "
                    f"{'timeout' if reason == TIMEOUT else 'wrong move'}"
                )

            games_played = game_idx + 1
            win_rate = players[0]["wins"] / games_played * 100

            tqdm.write(
                f"[{games_played}/{num_games}] "
                f"{players[0]['name']} as first: {last_result} "
                f"({last_reason}), current win rate = {win_rate:.2f}%"
            )

        print(f"==== {players[0]['name']} plays first ====")
        print(f"Games             : {num_games}")
        print(f"{players[0]['name']} wins      : {players[0]['wins']} ({players[0]['wins']/num_games*100:.2f}%)")
        print(f"{players[1]['name']} wins      : {players[1]['wins']} ({players[1]['wins']/num_games*100:.2f}%)")
        print(f"Avg Player1 score : {players[0]['total_score'] / num_games:.3f}")
        print(f"Avg Player2 score : {players[1]['total_score'] / num_games:.3f}")
        print("")

        players[0], players[1] = players[1], players[0]
        agents[0], agents[1] = agents[1], agents[0]

def main():
    parser = argparse.ArgumentParser(
        description="Dots and Boxes agent vs agent evaluator"
    )
    parser.add_argument("agent1", help="agents/ 디렉토리 안의 선공 에이전트 이름")
    parser.add_argument("agent2", help="agents/ 디렉토리 안의 후공 에이전트 이름")
    parser.add_argument("--num-games", "-n", type=int, default=100,
                        help="대국 판수 (default: 100)")
    parser.add_argument("--log", action="store_true",
                        help="게임 로그 출력")

    args = parser.parse_args()

    a1 = load_agent(args.agent1)
    a2 = load_agent(args.agent2)

    agents = [
        {
            "agent": a1,
            "name": args.agent1
        }, {
            "agent" : a2,
            "name": args.agent2
        }
    ]

    evaluate_agents(agents, num_games=args.num_games, print_log=args.log)

if __name__ == "__main__":
    main()
