import tkinter as tk
import time
from tkinter import messagebox, ttk
from gamepole import GamePole
from engine import SeaBattle


class SeaBattleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("⚓ Морской Бой")
        self.root.geometry("1600x900")
        self.root.configure(bg='#2c3e50')

        self.style = ttk.Style()
        self.style.configure('TFrame', background='#2c3e50')
        self.style.configure('TLabel', background='#2c3e50', foreground='white')
        self.style.configure('TButton', font=('Arial', 12))

        self.game = None
        self.show_ships = False
        self.init_game()
        self.create_interface()
        self.update_display()

    def init_game(self):
        human_pole = GamePole(10)
        human_pole.init()
        bot_pole = GamePole(10)
        bot_pole.init()

        self.game = SeaBattle(10, human_pole.get_ships(), bot_pole.get_ships(), human_pole)

    def create_interface(self):
        main_container = ttk.Frame(self.root, style='TFrame')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)

        header = ttk.Frame(main_container, style='TFrame')
        header.pack(fill='x', pady=(0, 20))

        ttk.Label(header, text="⚓ МОРСКОЙ БОЙ",
                  font=('Arial', 48, 'bold'),
                  foreground='#3498db').pack()

        content = ttk.Frame(main_container, style='TFrame')
        content.pack(fill='both', expand=True)

        left_panel = ttk.Frame(content, style='TFrame')
        left_panel.pack(side='left', fill='both', expand=True, padx=10)

        player_frame = self.create_field_frame(left_panel, "Ваш флот 🚢", 'player')
        self.player_labels = self.create_field_grid(player_frame, 'player')

        right_panel = ttk.Frame(content, style='TFrame')
        right_panel.pack(side='right', fill='both', expand=True, padx=10)

        bot_frame = self.create_field_frame(right_panel, "Флот противника 🏴‍☠️", 'bot')
        self.bot_labels = self.create_field_grid(bot_frame, 'bot')

        control_frame = ttk.Frame(main_container, style='TFrame')
        control_frame.pack(fill='x', pady=20)

        self.create_control_panel(control_frame)

        self.status_var = tk.StringVar()
        self.status_var.set("🎯 Ваш ход! Атакуйте флот противника!")
        status_bar = ttk.Label(main_container, textvariable=self.status_var,
                               font=('Arial', 20), foreground='#f39c12')
        status_bar.pack(side='bottom', pady=10)

        stats_frame = ttk.Frame(main_container, style='TFrame')
        stats_frame.pack(side='bottom', fill='x', pady=5)

        self.shots_var = tk.StringVar()
        self.shots_var.set("Выстрелы: 0")
        ttk.Label(stats_frame, textvariable=self.shots_var,
                  font=('Arial', 20)).pack()

    def create_field_frame(self, parent, title, field_type):
        frame = ttk.LabelFrame(parent, text=title, style='TFrame')
        frame.pack(fill='both', expand=True)
        return frame

    def create_field_grid(self, parent, field_type):
        labels = []
        for i in range(10):
            row = []
            for j in range(10):
                cell = tk.Label(parent, text="~", width=4, height=2,
                                font=('Arial', 12, 'bold'),
                                relief='raised', bd=2,
                                bg='#3498db', fg='white',
                                cursor='hand2' if field_type == 'bot' else 'arrow')

                if field_type == 'bot':
                    cell.bind("<Button-1>", lambda e, x=i, y=j: self.on_bot_cell_click(x, y))
                    cell.bind("<Enter>", lambda e, x=i, y=j: self.on_cell_hover(x, y, 'bot'))
                    cell.bind("<Leave>", lambda e: self.on_cell_leave('bot'))

                cell.grid(row=i, column=j, padx=2, pady=2)
                row.append(cell)
            labels.append(row)
        return labels

    def create_control_panel(self, parent):
        btn_style = {'font': ('Arial', 12), 'width': 25, 'height': 2}

        new_game_btn = tk.Button(parent, text="🔄 Новая игра",
                                 command=self.new_game, bg='#27ae60', fg='white',
                                 **btn_style)
        new_game_btn.pack(side='left', padx=10)

        ships_btn = tk.Button(parent, text="👁️Показать корабли",
                              command=self.toggle_ships, bg='#2980b9', fg='white',
                              **btn_style)
        ships_btn.pack(side='left', padx=10)

        auto_btn = tk.Button(parent, text="🤖 Ход компьютера",
                             command=self.bot_turn, bg='#e74c3c', fg='white',
                             **btn_style)
        auto_btn.pack(side='left', padx=10)

    def on_bot_cell_click(self, x, y):
        if self.game.check_winner():
            return

        if (x, y) in self.game.get_human_shots():
            self.status_var.set("⚠️ Уже стреляли в эту клетку!")
            return

        self.animate_aiming(x, y)

        self.root.after(300, lambda: self.execute_human_shot(x, y))

    def animate_aiming(self, x, y):
        for i in range(3):
            color = '#e74c3c' if i % 2 == 0 else '#f39c12'
            self.bot_labels[x][y].config(bg=color)
            self.root.update()
            time.sleep(0.1)
        self.bot_labels[x][y].config(bg='#3498db')

    def execute_human_shot(self, x, y):
        result = self.game.human_shot_target(x, y)

        self.animate_explosion(x, y, result)

        self.update_display()
        self.game.update_shots_by_human()
        self.shots_var.set(f"Выстрелы: {self.game._shots_by_human}")

        self.handle_shot_result(result, x, y)

    def animate_explosion(self, x, y, result):
        colors = ['#ff0000', '#ff8000', '#ffff00'] if result != 'pass' else ['#666666', '#999999', '#cccccc']

        for color in colors:
            self.bot_labels[x][y].config(bg=color)
            self.root.update()
            time.sleep(0.1)

        final_color = '#e74c3c' if result != 'pass' else '#95a5a6'
        self.bot_labels[x][y].config(bg=final_color)

    def handle_shot_result(self, result, x, y):
        if result == 'hit':
            self.status_var.set("🎯 Попадание! Цель повреждена!")
            self.play_sound('hit')
        elif result == 'destroyed':
            self.status_var.set("💥 Корабль уничтожен! Отличная работа!")
            self.play_sound('destroy')
        elif result == 'pass':
            self.status_var.set("🌊 Промах!")
            self.play_sound('miss')

        winner = self.game.check_winner()
        if winner:
            self.show_winner(winner)
        else:
            self.root.after(1000, self.bot_turn)

    def play_sound(self, sound_type):
        pass

    def bot_turn(self):
        if self.game.check_winner():
            return

        self.status_var.set("🤖 Противник обдумывает ход...")
        self.root.update()

        self.root.after(1500, self.execute_bot_turn)

    def execute_bot_turn(self):
        self.game.bot_shot()
        self.update_display()

        winner = self.game.check_winner()
        if winner:
            self.show_winner(winner)
        else:
            self.status_var.set("🎯 Ваш ход! Атакуйте флот противника!")

    def update_display(self):
        human_pole = self.game._human_game_pole.get_pole()
        for i in range(10):
            for j in range(10):
                cell = human_pole[i][j]
                bg_color = '#3498db'
                text = "~"

                if (i, j) in self.game.get_bot_shots():
                    bg_color = '#e74c3c' if cell == 2 else '#95a5a6'
                    text = "X" if cell == 2 else "•"
                elif self.show_ships and cell == 1:
                    text = "■"
                    bg_color = '#2980b9'

                self.player_labels[i][j].config(text=text, bg=bg_color)

        for i in range(10):
            for j in range(10):
                if (i, j) in self.game.get_human_shots():
                    hit = any((i, j) in self.game.get_ship_coordinates(ship)
                              for ship in self.game.get_bot_ships())
                    self.bot_labels[i][j].config(
                        text="X" if hit else "•",
                        bg='#e74c3c' if hit else '#95a5a6'
                    )
                else:
                    self.bot_labels[i][j].config(text="~", bg='#3498db')

    def show_winner(self, winner):
        if winner == 'human':
            message = "🎉 Победа! Вы уничтожили флот противника!"
            color = '#27ae60'
        else:
            message = "💀 Поражение! Ваш флот уничтожен!"
            color = '#e74c3c'

        self.status_var.set(message)
        for label in self.bot_labels + self.player_labels:
            for cell in label:
                cell.config(bg=color)

        messagebox.showinfo("Игра окончена", message)

    def new_game(self):
        self.init_game()
        self.update_display()
        self.status_var.set("🎯 Новая игра! Ваш ход!")
        self.shots_var.set("Выстрелы: 0")

    def toggle_ships(self):
        self.show_ships = not self.show_ships
        self.update_display()

    def on_cell_hover(self, x, y, field_type):
        if field_type == 'bot' and (x, y) not in self.game.get_human_shots():
            self.bot_labels[x][y].config(bg='#f39c12')

    def on_cell_leave(self, field_type):
        self.update_display()
