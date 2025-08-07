import tkinter as tk
from tkinter import messagebox
from functools import partial

# 전역 변수
players = {}
pot_value = 0
current_bets = {}

# --- 애니메이션 및 게임 로직 함수 ---
def animate_chip_transfer(player_name, bet_amount, callback):
    """칩이 팟으로 이동하는 애니메이션을 구현합니다."""
    # 플레이어 위치 찾기 (임의 위치)
    try:
        player_index = list(players.keys()).index(player_name)
        listbox_y = listbox_players.winfo_y() + listbox_players.winfo_rooty()
        listbox_item_y = listbox_y + player_index * 20
        start_x, start_y = listbox_players.winfo_x() + listbox_players.winfo_rootx(), listbox_item_y
    except ValueError:
        # 플레이어가 삭제되었거나 찾을 수 없을 때 기본 위치 설정
        start_x, start_y = 50, 50
    
    # 팟 위치 찾기
    end_x = label_pot.winfo_rootx() + label_pot.winfo_width() / 2
    end_y = label_pot.winfo_rooty() + label_pot.winfo_height() / 2
    
    chip_label = tk.Label(root, text=f"{bet_amount}개", font=("Helvetica", 14, "bold"), bg="orange", fg="white", relief="raised")
    chip_label.place(x=start_x - root.winfo_x(), y=start_y - root.winfo_y())
    
    steps = 30
    for i in range(1, steps + 1):
        x = start_x + (end_x - start_x) * (i / steps)
        y = start_y + (end_y - start_y) * (i / steps)
        root.after(i * 10, lambda x=x, y=y: chip_label.place(x=x - root.winfo_x(), y=y - root.winfo_y()))
    
    # 애니메이션 종료 후 콜백 함수 실행
    root.after(steps * 10 + 100, lambda: [chip_label.destroy(), callback()])


def update_game_state():
    """모든 GUI 요소를 업데이트하는 함수."""
    listbox_players.delete(0, tk.END)
    listbox_winner.delete(0, tk.END)
    for name, data in players.items():
        listbox_players.insert(tk.END, f"{name}: {data['chips']}개" + (" (FOLD)" if data['is_folded'] else ""))
        listbox_winner.insert(tk.END, name)
    
    listbox_current_bets.delete(0, tk.END)
    for name, bet in current_bets.items():
        listbox_current_bets.insert(tk.END, f"{name}: {bet}개")

    total_chips_value = sum(data['chips'] for data in players.values())
    label_total_chips.config(text=f"전체 플레이어 칩: {total_chips_value}개")
    label_pot.config(text=f"팟 (Pot): {pot_value}개")


def add_player():
    """새로운 플레이어를 추가하는 함수."""
    player_name = entry_player_name.get()
    if not player_name:
        messagebox.showerror("오류", "플레이어 이름을 입력해주세요.")
        return

    if player_name in players:
        messagebox.showerror("오류", "이미 존재하는 플레이어 이름입니다.")
        return

    try:
        initial_chips = int(entry_initial_chips.get())
        if initial_chips <= 0:
            messagebox.showerror("오류", "초기 칩 개수는 0보다 커야 합니다.")
            return

        players[player_name] = {'chips': initial_chips, 'is_folded': False}
        current_bets[player_name] = 0
        update_game_state()
        entry_player_name.delete(0, tk.END)
        entry_initial_chips.delete(0, tk.END)

    except ValueError:
        messagebox.showerror("오류", "초기 칩 개수는 숫자로 입력해주세요.")


def make_bet():
    """플레이어가 배팅하는 함수."""
    selected_index = listbox_players.curselection()
    if not selected_index:
        messagebox.showerror("오류", "배팅할 플레이어를 선택해주세요.")
        return

    selected_player_name = list(players.keys())[selected_index[0]]
    if players[selected_player_name]['is_folded']:
        messagebox.showinfo("다이", f"{selected_player_name}님은 이미 다이했습니다. 배팅할 수 없습니다.")
        return

    try:
        bet_amount = int(entry_bet_amount.get())
        if bet_amount <= 0:
            messagebox.showerror("오류", "배팅 금액은 0보다 커야 합니다.")
            return

        if players[selected_player_name]['chips'] < bet_amount:
            messagebox.showerror("오류", f"{selected_player_name}님의 칩이 부족합니다.")
            return

        def update_after_animation():
            global pot_value
            players[selected_player_name]['chips'] -= bet_amount
            pot_value += bet_amount
            current_bets[selected_player_name] = current_bets.get(selected_player_name, 0) + bet_amount
            update_game_state()
            entry_bet_amount.delete(0, tk.END)

        # 애니메이션 실행 후 칩 상태 업데이트
        animate_chip_transfer(selected_player_name, bet_amount, update_after_animation)

    except ValueError:
        messagebox.showerror("오류", "배팅 금액은 숫자로 입력해주세요.")

def player_folds():
    """플레이어가 다이(Fold)하는 함수."""
    selected_index = listbox_players.curselection()
    if not selected_index:
        messagebox.showerror("오류", "다이할 플레이어를 선택해주세요.")
        return

    selected_player_name = list(players.keys())[selected_index[0]]

    if not players[selected_player_name]['is_folded']:
        players[selected_player_name]['is_folded'] = True
        messagebox.showinfo("다이", f"{selected_player_name}님이 이번 라운드에서 다이했습니다.")
    else:
        messagebox.showinfo("정보", f"{selected_player_name}님은 이미 다이했습니다.")
    
    update_game_state()
    entry_bet_amount.delete(0, tk.END)


def end_round():
    """한 라운드를 종료하고 승자에게 팟을 분배하는 함수."""
    global pot_value, current_bets

    selected_index = listbox_winner.curselection()
    if not selected_index:
        messagebox.showerror("오류", "승자를 선택해주세요.")
        return
        
    winner_name = listbox_winner.get(selected_index[0])
    
    messagebox.showinfo("라운드 종료", f"'{winner_name}'님이 팟을 가져갑니다!\n획득 칩: {pot_value}개")
    
    players[winner_name]['chips'] += pot_value
    
    pot_value = 0
    current_bets.clear()
    for name in players:
        players[name]['is_folded'] = False
    
    update_game_state()
    entry_bet_amount.delete(0, tk.END)

def keypad_press(number):
    """키패드 버튼 클릭 시 입력창에 숫자를 추가하는 함수."""
    current_text = entry_bet_amount.get()
    entry_bet_amount.delete(0, tk.END)
    entry_bet_amount.insert(0, current_text + str(number))

def clear_bet_amount():
    """배팅 금액 입력창을 비우는 함수."""
    entry_bet_amount.delete(0, tk.END)

def backspace_bet_amount():
    """배팅 금액 입력창에서 마지막 문자를 지우는 함수."""
    current_text = entry_bet_amount.get()
    entry_bet_amount.delete(len(current_text) - 1, tk.END)


# --- GUI 설정 ---
root = tk.Tk()
root.title("포커 칩 카운터")
root.geometry("800x600")

# --- 레이아웃 프레임 ---
frame_top = tk.Frame(root)
frame_top.pack(fill=tk.X, padx=10, pady=10)

frame_middle = tk.Frame(root)
frame_middle.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

frame_bottom = tk.Frame(root)
frame_bottom.pack(fill=tk.X, padx=10, pady=10)

# --- 플레이어 추가 (상단) ---
player_add_frame = tk.LabelFrame(frame_top, text="플레이어 추가", padx=10, pady=10)
player_add_frame.pack(side=tk.LEFT, padx=10)
tk.Label(player_add_frame, text="이름:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="w", padx=5, pady=2)
entry_player_name = tk.Entry(player_add_frame, font=("Helvetica", 12))
entry_player_name.grid(row=0, column=1, padx=5, pady=2)
tk.Label(player_add_frame, text="초기 칩:", font=("Helvetica", 12)).grid(row=1, column=0, sticky="w", padx=5, pady=2)
entry_initial_chips = tk.Entry(player_add_frame, font=("Helvetica", 12))
entry_initial_chips.grid(row=1, column=1, padx=5, pady=2)
entry_initial_chips.insert(0, "1000")
tk.Button(player_add_frame, text="추가", command=add_player, font=("Helvetica", 12)).grid(row=2, column=0, columnspan=2, pady=5)

# --- 팟 및 전체 칩 정보 (상단) ---
info_frame = tk.LabelFrame(frame_top, text="게임 정보", padx=10, pady=10)
info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
label_pot = tk.Label(info_frame, text="팟 (Pot): 0개", font=("Helvetica", 16, "bold"))
label_pot.pack(pady=5)
label_total_chips = tk.Label(info_frame, text="전체 플레이어 칩: 0개", font=("Helvetica", 14, "bold"))
label_total_chips.pack(pady=5)

# --- 플레이어 목록 및 턴 배팅 현황 (중앙) ---
player_info_frame = tk.LabelFrame(frame_middle, text="플레이어 목록", padx=10, pady=10)
player_info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
listbox_players = tk.Listbox(player_info_frame, height=15, font=("Helvetica", 12))
listbox_players.pack(fill=tk.BOTH, expand=True)

current_bets_frame = tk.LabelFrame(frame_middle, text="이번 턴 배팅 현황", padx=10, pady=10)
current_bets_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
listbox_current_bets = tk.Listbox(current_bets_frame, height=15, font=("Helvetica", 12))
listbox_current_bets.pack(fill=tk.BOTH, expand=True)

# --- 배팅 & 라운드 종료 (하단) ---
betting_frame = tk.LabelFrame(frame_bottom, text="배팅 & 라운드 종료", padx=10, pady=10)
betting_frame.pack(fill=tk.X, expand=True)

# 배팅 금액 입력 및 버튼
bet_input_frame = tk.Frame(betting_frame)
bet_input_frame.pack(side=tk.LEFT, padx=10, pady=5)
tk.Label(bet_input_frame, text="배팅 금액:", font=("Helvetica", 12)).pack()
entry_bet_amount = tk.Entry(bet_input_frame, width=15, font=("Helvetica", 14))
entry_bet_amount.pack(pady=5)
tk.Button(bet_input_frame, text="배팅", command=make_bet, font=("Helvetica", 14, "bold"), width=8, height=2).pack(pady=5)
tk.Button(bet_input_frame, text="다이", command=player_folds, font=("Helvetica", 14, "bold"), width=8, height=2, bg="red", fg="white").pack(pady=5)

# 키패드
keypad_frame = tk.Frame(betting_frame)
keypad_frame.pack(side=tk.LEFT, padx=20)
keypad_buttons = [
    ('1', '2', '3'), ('4', '5', '6'), ('7', '8', '9'), ('C', '0', '⌫')
]
for row, buttons in enumerate(keypad_buttons):
    for col, button_text in enumerate(buttons):
        if button_text == 'C':
            cmd = clear_bet_amount
        elif button_text == '⌫':
            cmd = backspace_bet_amount
        else:
            cmd = partial(keypad_press, button_text)
        
        btn = tk.Button(keypad_frame, text=button_text, font=("Helvetica", 18, "bold"), width=4, height=2, command=cmd)
        btn.grid(row=row, column=col, padx=5, pady=5)

# 라운드 종료
end_round_frame = tk.LabelFrame(betting_frame, text="라운드 종료", padx=10, pady=10)
end_round_frame.pack(side=tk.LEFT, padx=20, fill=tk.BOTH, expand=True)
tk.Label(end_round_frame, text="승자 선택:", font=("Helvetica", 12)).pack(pady=5)
listbox_winner = tk.Listbox(end_round_frame, height=5, font=("Helvetica", 12), exportselection=False)
listbox_winner.pack(fill=tk.BOTH, expand=True)
tk.Button(end_round_frame, text="팟 분배", command=end_round, font=("Helvetica", 14, "bold")).pack(pady=5)

root.mainloop()