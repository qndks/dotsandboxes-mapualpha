import os
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, simpledialog
import importlib.util

XSIZE = 5
YSIZE = 5
NUM_EDGES = 60   # 5x5 기준

PLAYER1_EDGE_COLOR = "#087CA7"
PLAYER2_EDGE_COLOR = "#D72638"
PLAYER1_BOX_COLOR = "#A5D8F3"
PLAYER2_BOX_COLOR = "#FFC9C9"


# ======================
# 좌표 계산 함수
# ======================
def coord_to_idx(x, y, z):
    return (x * 6 + y) if z == 0 else (30 + x * 5 + y)

def idx_to_coord(idx):
    z = idx >= 30
    base = 6 - z
    i = idx - 30*z
    return [i // base, i % base, int(z)]

def get_box_edges(x, y):
    top    = coord_to_idx(x,   y,   0)
    bottom = coord_to_idx(x,   y+1, 0)
    left   = coord_to_idx(x,   y,   1)
    right  = coord_to_idx(x+1, y,   1)
    return [top, bottom, left, right]

def get_edge_squares(idx):
    x, y, z = idx_to_coord(idx)
    squares = []

    if z == 0:  # horizontal
        if y <= 4:
            squares.append((x, y))
        if 1 <= y <= 5:
            squares.append((x, y-1))
    else:       # vertical
        if x <= 4:
            squares.append((x, y))
        if 1 <= x <= 5:
            squares.append((x-1, y))

    return squares
    
def apply_move(state_vec, square_owner, move_idx, player_id):
    state_vec[move_idx] = player_id + 1
    completed = 0

    for (bx, by) in get_edge_squares(move_idx):
        if square_owner[bx][by] != 0:
            continue
        edges = get_box_edges(bx, by)
        if all(state_vec[e] != 0 for e in edges):
            square_owner[bx][by] = (player_id + 1)
            completed += 1

    return completed

def build_board_lines_from_state_vec(state_vec, xsize=5, ysize=5):
    board_lines = [[[0, 0] for _ in range(6)] for _ in range(6)]

    for idx, v in enumerate(state_vec):
        x, y, z = idx_to_coord(idx)
        if (z == 0 and x < xsize) or (z == 1 and y < ysize):
            board_lines[x][y][z] = 1 if v != 0 else 0

    return board_lines


# =====================================================
#                      GUI (반응형 버전)
# =====================================================
class DotsAndBoxesGUI:
    def __init__(self, root, agent_name="MapuAlpha", human_first=True):

        # 화면 크기 기반 scaling
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        self.window_size = int(min(sw, sh) * 0.75)
        self.canvas_size = int(self.window_size * 0.9)

        self.font_size = max(12, int(self.window_size * 0.014))

        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=self.font_size)

        self.root = root
        self.root.title(f"Dots and Boxes - Human vs {agent_name}")

        root.geometry(f"{self.window_size}x{self.window_size}")

        # 반응형 핵심: 간격 자동 계산
        self.margin = int(self.canvas_size * 0.06)
        self.unit = (self.canvas_size - 2*self.margin) / XSIZE

        # --- 선공 선택 ---
        choice = simpledialog.askstring(
            "First Move",
            "Who plays first? (human/agent)",
            parent=root
        )
        self.human_first = not (choice and choice.lower().startswith("a"))

        # load agent
        self.agent_module = load_agent(agent_name)

        # state
        self.state_vec = [0] * NUM_EDGES
        self.square_owner = [[0] * YSIZE for _ in range(XSIZE)]
        self.current_player = 0
        self.scores = [0, 0]

        # 🔒 입력 잠금 플래그
        self.input_locked = False

        # Canvas
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.pack()

        self.info_label = tk.Label(
            root,
            text="",
            font=("Arial", self.font_size)
        )
        self.info_label.pack(pady=5)

        self.edge_items = {}
        self.box_items = {}

        self._create_board()

        # 메뉴
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        game_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="Restart", command=self.reset_board)

        self.update_info()

        # 선공이 AI인 경우: 시작부터 입력 잠금 + AI 호출 예약
        if not self.human_first:
            self.input_locked = True
            self.root.after(500, self.ai_move)

    # ====================================================
    #  반응형: 좌표 계산
    # ====================================================
    def px(self, x):
        return self.margin + x * self.unit

    def _create_board(self):
        # Boxes
        for x in range(XSIZE):
            for y in range(YSIZE):
                x1 = self.px(x)
                y1 = self.px(y)
                x2 = self.px(x+1)
                y2 = self.px(y+1)
                item = self.canvas.create_rectangle(x1, y1, x2, y2, outline="", fill="")
                self.box_items[(x, y)] = item

        # Horizontal edges
        for y in range(YSIZE + 1):
            for x in range(XSIZE):
                move_idx = coord_to_idx(x, y, 0)
                x1 = self.px(x)
                y1 = self.px(y)
                x2 = self.px(x+1)
                item = self.canvas.create_line(
                    x1, y1, x2, y1,
                    width=max(3, int(self.unit * 0.10)),
                    fill="#dddddd"
                )
                self.canvas.tag_bind(item, "<Button-1>", lambda e, idx=move_idx: self.on_edge_click(idx))
                self.edge_items[item] = move_idx

        # Vertical edges
        for y in range(YSIZE):
            for x in range(XSIZE + 1):
                move_idx = coord_to_idx(x, y, 1)
                x1 = self.px(x)
                y1 = self.px(y)
                y2 = self.px(y+1)
                item = self.canvas.create_line(
                    x1, y1, x1, y2,
                    width=max(3, int(self.unit * 0.10)),
                    fill="#dddddd"
                )
                self.canvas.tag_bind(item, "<Button-1>", lambda e, idx=move_idx: self.on_edge_click(idx))
                self.edge_items[item] = move_idx

        # Dots
        for y in range(YSIZE + 1):
            for x in range(XSIZE + 1):
                cx = self.px(x)
                cy = self.px(y)
                r = max(3, int(self.unit*0.09))
                self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="black", tags="dot")

        self.canvas.tag_raise("dot")

    # ====================================================
    #                 Event / Game Logic
    # ====================================================

    def on_edge_click(self, move_idx):

        # 🔒 입력 잠겨 있으면 클릭 무시
        if self.input_locked:
            return "break"

        if not self.is_human_turn():
            return "break"
        if move_idx < 0 or move_idx >= NUM_EDGES:
            return
        if self.state_vec[move_idx] != 0:
            return

        completed = apply_move(self.state_vec, self.square_owner, move_idx, self.current_player)

        self.update_edges()
        self.update_boxes()

        if completed > 0:
            self.scores[self.current_player] += completed
        else:
            self.current_player = 1 - self.current_player

        self.update_info()

        if self.is_game_over():
            self.end_game()
            return

        if not self.is_human_turn():
            # 이제 AI 턴 → 이 시점부터 들어오는 입력은 전부 잠금
            self.input_locked = True
            self.root.after(200, self.ai_move)

    def ai_move(self):
        if self.is_game_over() or self.is_human_turn():
            return

        board_lines = build_board_lines_from_state_vec(self.state_vec, XSIZE, YSIZE)
        x, y, z = self.agent_module.run(board_lines, XSIZE, YSIZE)
        move_idx = coord_to_idx(int(x), int(y), int(z))

        if move_idx < 0 or move_idx >= NUM_EDGES or self.state_vec[move_idx] != 0:
            messagebox.showerror("Error", f"Agent made a fatal mistake: {(x, y, z)}")
            self.current_player = 1 - self.current_player
            self.update_info()
            # 그래도 사람 차례가 되면 잠금 해제
            if self.is_human_turn() and not self.is_game_over():
                self.root.after(150, self.unlock_input)
            return

        completed = apply_move(self.state_vec, self.square_owner, move_idx, self.current_player)

        self.update_edges()
        self.update_boxes()
        self.highlight_edge(move_idx)

        if completed > 0:
            # AI가 박스를 먹었으면 한 번 더 AI 턴 → 계속 잠금 유지
            self.scores[self.current_player] += completed
            self.update_info()
            if not self.is_game_over():
                self.root.after(200, self.ai_move)
            else:
                self.end_game()
        else:
            # 턴이 넘어감
            self.current_player = 1 - self.current_player
            self.update_info()

            # 이제 사람이면 잠금 풀기 (약간의 딜레이 후)
            if self.is_human_turn() and not self.is_game_over():
                self.root.after(150, self.unlock_input)

    def unlock_input(self):
        print("Input unlocked")
        self.input_locked = False

    def highlight_edge(self, move_idx):
        target_item = None
        for item, idx in self.edge_items.items():
            if idx == move_idx:
                target_item = item
                break
        if target_item is None:
            return

        owner = self.state_vec[move_idx]
        if owner == 1:
            original = PLAYER1_EDGE_COLOR
        elif owner == 2:
            original = PLAYER2_EDGE_COLOR
        else:
            original = "#dddddd"

        def blink(count=6):
            if count == 0:
                self.update_edges()
                return
            cur = self.canvas.itemcget(target_item, "fill")
            new = "yellow" if cur != "yellow" else original
            self.canvas.itemconfig(target_item, fill=new)
            self.root.after(150, blink, count - 1)

        blink()

    def is_human_turn(self):
        return (self.current_player == 0) if self.human_first else (self.current_player == 1)

    def is_game_over(self):
        return all(v != 0 for v in self.state_vec)

    def update_edges(self):
        for item, idx in self.edge_items.items():
            owner = self.state_vec[idx]
            if owner == 0:
                self.canvas.itemconfig(item, fill="#dddddd")
            elif owner == 1:
                self.canvas.itemconfig(item, fill=PLAYER1_EDGE_COLOR)
            elif owner == 2:
                self.canvas.itemconfig(item, fill=PLAYER2_EDGE_COLOR)

    def update_boxes(self):
        for x in range(XSIZE):
            for y in range(YSIZE):
                owner = self.square_owner[x][y]
                item = self.box_items[(x, y)]
                if owner == 0:
                    self.canvas.itemconfig(item, fill="", outline="")
                elif owner == 1:
                    self.canvas.itemconfig(item, fill=PLAYER1_BOX_COLOR, outline="#4444ff")
                elif owner == 2:
                    self.canvas.itemconfig(item, fill=PLAYER2_BOX_COLOR, outline="#ff4444")

    def update_info(self):
        p0 = "Human" if self.human_first else "Agent"
        p1 = "Agent" if self.human_first else "Human"
        s0, s1 = self.scores

        if not self.is_human_turn():
            self.info_label.config(text=f"Agent thinking...", fg="blue")
            return
        turn_name = p0 if self.current_player == 0 else p1
        self.info_label.config(
            text=f"Turn: {turn_name}   |   {p0}: {s0}  |  {p1}: {s1}",
            fg="black"
        )

    def end_game(self):
        # 게임 끝나면 입력 잠궈버리는 것도 안전함
        self.input_locked = True

        p0 = "Human" if self.human_first else "Agent"
        p1 = "Agent" if self.human_first else "Human"
        s0, s1 = self.scores
        if s0 > s1: w = p0
        elif s1 > s0: w = p1
        else: w = "Draw"
        messagebox.showinfo("Game Over", f"{p0}: {s0}  |  {p1}: {s1}\nWinner: {w}")

    def reset_board(self):
        self.state_vec = [0] * NUM_EDGES
        self.square_owner = [[0]*YSIZE for _ in range(XSIZE)]
        self.scores = [0, 0]
        self.current_player = 0

        # 새판에서는 다시 사람부터 입력 가능
        self.input_locked = False

        self.update_edges()
        self.update_boxes()
        self.update_info()


def load_agent(agent_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    agent_dir = os.path.join(base_dir, "agents", agent_name)
    module_path = os.path.join(agent_dir, "main.py")

    if not os.path.exists(module_path):
        raise FileNotFoundError(f"Agent '{agent_name}' not found at {module_path}")

    spec = importlib.util.spec_from_file_location(f"agent_{agent_name}", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.init()
    return module


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", type=str, default="MapuAlpha")
    parser.add_argument("--human-first", action="store_true", default=True)
    args = parser.parse_args()

    root = tk.Tk()
    gui = DotsAndBoxesGUI(root, agent_name=args.agent, human_first=args.human_first)
    root.mainloop()
