# -*- coding: utf-8 -*-
"""
俄罗斯方块游戏 - 使用Kivy框架
功能：每消除一行100分，下落速度随分数增加，1000分通关
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.relativelayout import RelativeLayout
import random
import os

# 游戏常量
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = dp(28)
WIN_SCORE = 1000
INITIAL_SPEED = 1.0  # 初始下落速度（秒/格）

# 方块形状定义
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]]
}

# 方块颜色
COLORS = {
    'I': get_color_from_hex('#00FFFF'),
    'O': get_color_from_hex('#FFFF00'),
    'T': get_color_from_hex('#800080'),
    'S': get_color_from_hex('#00FF00'),
    'Z': get_color_from_hex('#FF0000'),
    'J': get_color_from_hex('#0000FF'),
    'L': get_color_from_hex('#FFA500')
}


class TetrisBlock:
    """俄罗斯方块方块类"""

    def __init__(self, shape_type):
        self.shape_type = shape_type
        self.shape = [row[:] for row in SHAPES[shape_type]]
        self.color = COLORS[shape_type]
        # 设置初始位置在顶部中间，确保完全在网格内
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = GRID_HEIGHT - 1  # 从顶部开始

    def rotate(self):
        rotated = []
        for i in range(len(self.shape[0])):
            new_row = []
            for j in range(len(self.shape) - 1, -1, -1):
                new_row.append(self.shape[j][i])
            rotated.append(new_row)
        return rotated

    def get_positions(self):
        """获取方块占用的位置"""
        positions = []
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    # 计算实际y坐标
                    pos_y = self.y - y
                    # 确保坐标在有效范围内
                    if 0 <= pos_y < GRID_HEIGHT and 0 <= self.x + x < GRID_WIDTH:
                        positions.append((self.x + x, pos_y))
        return positions


class SoundManager:
    """音效管理类"""

    def __init__(self):
        self.sounds = {}
        self.bg_music = None
        self.win_music = None
        self.is_win_music_playing = False
        self.load_sounds()

    def get_sound_path(self, filename):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, filename)

    def load_sounds(self):
        try:
            bg_path = self.get_sound_path('background.mp3')
            if os.path.exists(bg_path):
                self.bg_music = SoundLoader.load(bg_path)
                if self.bg_music:
                    self.bg_music.loop = True
                    self.bg_music.volume = 0.3
                    print(f"Loaded background music: {bg_path}")

            win_path = self.get_sound_path('win.mp3')
            if os.path.exists(win_path):
                self.win_music = SoundLoader.load(win_path)
                if self.win_music:
                    self.win_music.loop = False
                    self.win_music.volume = 0.8
                    print(f"Loaded win music: {win_path}")

            sound_files = {
                'move': 'move.wav',
                'rotate': 'rotate.wav',
                'drop': 'drop.wav',
                'clear': 'clear_line.wav',
                'gameover': 'gameover.wav'
            }

            for sound_name, filename in sound_files.items():
                file_path = self.get_sound_path(filename)
                if os.path.exists(file_path):
                    sound = SoundLoader.load(file_path)
                    if sound:
                        sound.volume = 0.5
                        self.sounds[sound_name] = sound
                        print(f"Loaded sound: {file_path}")
        except Exception as e:
            print(f"Sound loading error: {e}")

    def play_move(self):
        if 'move' in self.sounds:
            self.sounds['move'].play()

    def play_rotate(self):
        if 'rotate' in self.sounds:
            self.sounds['rotate'].play()

    def play_drop(self):
        if 'drop' in self.sounds:
            self.sounds['drop'].play()

    def play_clear(self):
        if 'clear' in self.sounds:
            self.sounds['clear'].play()

    def play_gameover(self):
        if 'gameover' in self.sounds:
            self.sounds['gameover'].play()

    def play_win(self):
        if self.win_music and not self.is_win_music_playing:
            self.stop_background_music()
            self.win_music.play()
            self.is_win_music_playing = True
            print("Playing win music")

    def start_background_music(self):
        if self.bg_music:
            if self.win_music and self.win_music.state == 'play':
                self.win_music.stop()
            self.is_win_music_playing = False
            if self.bg_music.state != 'play':
                self.bg_music.play()
                print("Background music started")

    def stop_background_music(self):
        if self.bg_music and self.bg_music.state == 'play':
            self.bg_music.stop()
            print("Background music stopped")

    def stop_all_music(self):
        if self.bg_music and self.bg_music.state == 'play':
            self.bg_music.stop()
        if self.win_music and self.win_music.state == 'play':
            self.win_music.stop()
        self.is_win_music_playing = False
        print("All music stopped")


class StatsPanel(BoxLayout):
    """统计面板 - 显示积分和进度条（使用纯文本）"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (200, 160)
        self.spacing = 5
        self.padding = [10, 10, 10, 10]

        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 0.95)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_bg, size=self.update_bg)

        # 标题 - 使用纯文本
        title_label = Label(
            text='STATISTICS',
            size_hint=(1, 0.15),
            font_size='14sp',
            color=(0, 1, 1, 1),
            font_name='Arial',
            bold=True,
            halign='center',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        self.add_widget(title_label)

        # 积分标签
        self.score_label = Label(
            text='Score: 0',
            size_hint=(1, 0.2),
            font_size='18sp',
            color=(1, 1, 0, 1),
            font_name='Arial',
            bold=True,
            halign='center',
            valign='middle'
        )
        self.score_label.bind(size=self.score_label.setter('text_size'))
        self.add_widget(self.score_label)

        # 进度条
        self.progress_bar = ProgressBar(
            max=WIN_SCORE,
            value=0,
            size_hint=(1, 0.15)
        )
        self.add_widget(self.progress_bar)

        # 进度信息
        progress_info = BoxLayout(size_hint=(1, 0.15))

        self.target_label = Label(
            text=f'0/{WIN_SCORE}',
            size_hint=(0.5, 1),
            font_size='11sp',
            color=(0.8, 0.8, 0.8, 1),
            font_name='Arial',
            halign='left',
            valign='middle'
        )
        self.target_label.bind(size=self.target_label.setter('text_size'))
        progress_info.add_widget(self.target_label)

        self.percent_label = Label(
            text='0%',
            size_hint=(0.5, 1),
            font_size='11sp',
            color=(0, 1, 0, 1),
            font_name='Arial',
            halign='right',
            valign='middle'
        )
        self.percent_label.bind(size=self.percent_label.setter('text_size'))
        progress_info.add_widget(self.percent_label)

        self.add_widget(progress_info)

        # 速度和剩余
        info_row = BoxLayout(size_hint=(1, 0.2))

        self.speed_label = Label(
            text='Speed:1.0x',
            size_hint=(0.5, 1),
            font_size='11sp',
            color=(0, 1, 1, 1),
            font_name='Arial',
            halign='left',
            valign='middle'
        )
        self.speed_label.bind(size=self.speed_label.setter('text_size'))
        info_row.add_widget(self.speed_label)

        self.remaining_label = Label(
            text='Need:1000',
            size_hint=(0.5, 1),
            font_size='11sp',
            color=(1, 0.5, 0, 1),
            font_name='Arial',
            halign='right',
            valign='middle'
        )
        self.remaining_label.bind(size=self.remaining_label.setter('text_size'))
        info_row.add_widget(self.remaining_label)

        self.add_widget(info_row)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_score(self, score, speed):
        self.score_label.text = f'Score: {score}'
        self.progress_bar.value = min(score, WIN_SCORE)
        percent = (score / WIN_SCORE) * 100
        self.percent_label.text = f'{int(percent)}%'
        self.target_label.text = f'{score}/{WIN_SCORE}'
        self.speed_label.text = f'Speed:{speed:.1f}x'

        remaining = max(0, WIN_SCORE - score)
        self.remaining_label.text = f'Need:{remaining}'

        if percent < 30:
            self.percent_label.color = (1, 0, 0, 1)
        elif percent < 70:
            self.percent_label.color = (1, 1, 0, 1)
        else:
            self.percent_label.color = (0, 1, 0, 1)


class PreviewCanvas(RelativeLayout):
    """预览画布 - 用于显示下一个方块（无网格线）"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.block = None
        self.cell_size = 25
        self.bind(pos=self.draw_preview, size=self.draw_preview)

    def set_block(self, block):
        """设置要预览的方块"""
        self.block = block
        self.draw_preview()

    def draw_preview(self, *args):
        """绘制预览（无网格线）"""
        self.canvas.clear()

        if not self.block:
            return

        with self.canvas:
            # 计算方块尺寸
            block_height = len(self.block.shape)
            block_width = len(self.block.shape[0])

            # 计算总尺寸
            total_width = block_width * self.cell_size
            total_height = block_height * self.cell_size

            # 计算居中位置
            start_x = (self.width - total_width) / 2
            start_y = (self.height - total_height) / 2

            # 只绘制方块，不绘制网格线
            for y, row in enumerate(self.block.shape):
                for x, cell in enumerate(row):
                    if cell:
                        Color(*self.block.color)
                        Rectangle(
                            pos=(start_x + x * self.cell_size + 2,
                                 start_y + (block_height - 1 - y) * self.cell_size + 2),
                            size=(self.cell_size - 4, self.cell_size - 4)
                        )


class PreviewPanel(BoxLayout):
    """预览面板 - 显示下一个方块（使用纯文本）"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (200, 200)
        self.spacing = 5
        self.padding = [10, 10, 10, 10]

        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 0.95)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_bg, size=self.update_bg)

        # 标题 - 使用纯文本
        title_label = Label(
            text='NEXT BLOCK',
            size_hint=(1, 0.2),
            font_size='14sp',
            color=(0, 1, 1, 1),
            font_name='Arial',
            bold=True,
            halign='center',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        self.add_widget(title_label)

        # 使用AnchorLayout来居中显示预览
        container = AnchorLayout(
            anchor_x='center',
            anchor_y='center',
            size_hint=(1, 0.8)
        )

        # 预览画布（无网格线）
        self.preview_canvas = PreviewCanvas(
            size_hint=(None, None),
            size=(180, 160)
        )
        container.add_widget(self.preview_canvas)
        self.add_widget(container)

        self.current_block = None

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_preview(self, block):
        """更新预览"""
        self.current_block = block
        self.preview_canvas.set_block(block)


class ControlPanel(BoxLayout):
    """控制面板 - 显示快捷键说明（使用纯文本）"""

    def __init__(self, restart_callback, exit_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (200, 220)
        self.spacing = 5
        self.padding = [10, 10, 10, 10]

        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 0.95)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_bg, size=self.update_bg)

        # 标题 - 使用纯文本
        title_label = Label(
            text='CONTROLS',
            size_hint=(1, 0.15),
            font_size='14sp',
            color=(0, 1, 1, 1),
            font_name='Arial',
            bold=True,
            halign='center',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        self.add_widget(title_label)

        # 控制说明 - 使用纯文本
        controls = [
            ('Left/Right', 'Move'),
            ('Up', 'Rotate'),
            ('Down', 'Speed'),
            ('Space', 'Drop'),
            ('R', 'Restart'),
            ('Esc', 'Exit')
        ]

        for key, desc in controls:
            control_row = BoxLayout(size_hint=(1, 0.12))
            key_label = Label(
                text=key,
                size_hint=(0.4, 1),
                font_size='11sp',
                color=(1, 1, 0, 1),
                font_name='Arial',
                bold=True,
                halign='left',
                valign='middle'
            )
            key_label.bind(size=key_label.setter('text_size'))
            desc_label = Label(
                text=desc,
                size_hint=(0.6, 1),
                font_size='11sp',
                color=(1, 1, 1, 1),
                font_name='Arial',
                halign='left',
                valign='middle'
            )
            desc_label.bind(size=desc_label.setter('text_size'))
            control_row.add_widget(key_label)
            control_row.add_widget(desc_label)
            self.add_widget(control_row)

        # 按钮行
        btn_row = BoxLayout(size_hint=(1, 0.2), spacing=5)

        restart_btn = Button(
            text='Restart (R)',
            size_hint=(0.5, 1),
            background_color=(0.2, 0.6, 1, 1),
            font_size='12sp',
            font_name='Arial'
        )
        restart_btn.bind(on_press=restart_callback)

        exit_btn = Button(
            text='Exit (Esc)',
            size_hint=(0.5, 1),
            background_color=(1, 0.3, 0.3, 1),
            font_size='12sp',
            font_name='Arial'
        )
        exit_btn.bind(on_press=exit_callback)

        btn_row.add_widget(restart_btn)
        btn_row.add_widget(exit_btn)
        self.add_widget(btn_row)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class TetrisGame(FloatLayout):
    """俄罗斯方块游戏主类"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_block = None
        self.next_block = None
        self.score = 0
        self.game_over = False
        self.game_won = False
        self.speed = INITIAL_SPEED
        self.game_started = False
        self.fall_time = 0

        self.sound = SoundManager()

        main_container = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 1),
            spacing=10,
            padding=[10, 10, 10, 10]
        )

        left_panel = BoxLayout(
            orientation='vertical',
            size_hint=(0.22, 1),
            spacing=10
        )

        self.stats_panel = StatsPanel()
        left_panel.add_widget(self.stats_panel)

        self.preview_panel = PreviewPanel()
        left_panel.add_widget(self.preview_panel)

        left_panel.add_widget(Widget())
        main_container.add_widget(left_panel)

        game_panel = BoxLayout(
            orientation='vertical',
            size_hint=(0.56, 1),
            spacing=5
        )

        self.game_container = FloatLayout(size_hint=(1, 1))
        game_panel.add_widget(self.game_container)
        main_container.add_widget(game_panel)

        right_panel = BoxLayout(
            orientation='vertical',
            size_hint=(0.22, 1),
            spacing=10
        )

        self.control_panel = ControlPanel(
            restart_callback=self.restart_game,
            exit_callback=lambda x: App.get_running_app().stop()
        )
        right_panel.add_widget(self.control_panel)
        right_panel.add_widget(Widget())
        main_container.add_widget(right_panel)

        self.add_widget(main_container)

        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)

        Clock.schedule_interval(self.update, 1.0 / 60.0)
        Clock.schedule_once(self.start_game, 0.1)

        self.game_container.bind(on_touch_down=self.on_game_touch)

    def start_game(self, dt):
        self.game_started = True
        self.spawn_new_block()
        self.sound.start_background_music()
        print("Game started")

    def _on_keyboard_closed(self):
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if not self.game_started or self.game_over or self.game_won:
            if keycode[1] == 'r':
                self.restart_game()
                return True
            elif keycode[1] == 'escape':
                App.get_running_app().stop()
                return True
            return

        if keycode[1] == 'left':
            self.move_block(-1, 0)
            self.sound.play_move()
        elif keycode[1] == 'right':
            self.move_block(1, 0)
            self.sound.play_move()
        elif keycode[1] == 'down':
            self.move_block(0, -1)
            self.sound.play_move()
        elif keycode[1] == 'up':
            self.rotate_block()
            self.sound.play_rotate()
        elif keycode[1] == 'spacebar':
            self.hard_drop()
            self.sound.play_drop()
        elif keycode[1] == 'r':
            self.restart_game()
        elif keycode[1] == 'escape':
            App.get_running_app().stop()

        return True

    def on_game_touch(self, instance, touch):
        if not self.game_started or self.game_over or self.game_won:
            return True

        game_x = self.game_container.x
        game_y = self.game_container.y
        game_width = GRID_WIDTH * BLOCK_SIZE
        game_height = GRID_HEIGHT * BLOCK_SIZE

        start_x = game_x + (self.game_container.width - game_width) / 2
        start_y = game_y + (self.game_container.height - game_height) / 2

        if (start_x <= touch.x <= start_x + game_width and
                start_y <= touch.y <= start_y + game_height):

            rel_x = (touch.x - start_x) / game_width
            rel_y = (touch.y - start_y) / game_height

            if rel_x < 0.25:
                self.move_block(-1, 0)
                self.sound.play_move()
            elif rel_x > 0.75:
                self.move_block(1, 0)
                self.sound.play_move()
            elif rel_y < 0.3:
                self.move_block(0, -1)
                self.sound.play_move()
            elif rel_y > 0.7:
                self.rotate_block()
                self.sound.play_rotate()
            else:
                self.hard_drop()
                self.sound.play_drop()

        return True

    def spawn_new_block(self):
        """生成新方块"""
        if not self.game_started:
            return

        # 第一次生成时，创建第一个方块
        if self.next_block is None:
            # 随机选择一个形状作为下一个方块
            shape_type = random.choice(list(SHAPES.keys()))
            self.next_block = TetrisBlock(shape_type)
            print(f"First next block created: {shape_type}")

        # 设置当前方块为下一个方块
        self.current_block = self.next_block

        # 生成新的下一个方块
        shape_type = random.choice(list(SHAPES.keys()))
        self.next_block = TetrisBlock(shape_type)

        # 更新预览
        self.preview_panel.update_preview(self.next_block)

        # 检查新方块是否与已有方块碰撞（游戏结束检查）
        if self.check_collision():
            print(f"Game Over - No space for new block {self.current_block.shape_type}")
            self.game_over = True
            self.sound.stop_all_music()
            self.sound.play_gameover()
            self.show_game_over_popup()
            return

        print(f"New block spawned: {self.current_block.shape_type} at ({self.current_block.x}, {self.current_block.y})")
        self.draw_game()

    def check_collision(self, offset_x=0, offset_y=0, shape=None):
        """检查碰撞"""
        if self.current_block is None:
            return False

        if shape is None:
            shape = self.current_block.shape

        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.current_block.x + x + offset_x
                    new_y = self.current_block.y - y + offset_y

                    # 检查边界
                    if new_x < 0 or new_x >= GRID_WIDTH:
                        return True
                    if new_y < 0:
                        return True
                    if new_y >= GRID_HEIGHT:
                        # 超出顶部不算碰撞，继续检查
                        continue

                    # 检查与其他方块碰撞
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return True
        return False

    def move_block(self, dx, dy):
        """移动方块"""
        if self.current_block is None or self.game_over or self.game_won:
            return False

        if not self.check_collision(dx, dy):
            self.current_block.x += dx
            self.current_block.y += dy
            self.draw_game()
            return True
        elif dy < 0:  # 向下移动时如果碰撞，锁定方块
            self.lock_block()
        return False

    def rotate_block(self):
        """旋转方块"""
        if self.current_block is None or self.game_over or self.game_won:
            return

        rotated = self.current_block.rotate()
        if not self.check_collision(shape=rotated):
            self.current_block.shape = rotated
            self.draw_game()

    def hard_drop(self):
        """硬降"""
        if self.current_block is None or self.game_over or self.game_won:
            return

        while not self.check_collision(0, -1):
            self.current_block.y -= 1
        self.lock_block()
        self.draw_game()

    def lock_block(self):
        """锁定方块"""
        if self.current_block is None:
            return

        # 将当前方块添加到网格
        positions = self.current_block.get_positions()
        for x, y in positions:
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                self.grid[y][x] = self.current_block.color

        # 消除满行
        lines_cleared = self.clear_lines()
        if lines_cleared > 0:
            old_score = self.score
            self.score += lines_cleared * 100
            self.sound.play_clear()
            self.update_speed()
            self.stats_panel.update_score(self.score, self.speed)

            print(f"Score: {old_score} -> {self.score}, Lines cleared: {lines_cleared}")

            # 检查是否通关
            if self.score >= WIN_SCORE and not self.game_won:
                print(f"WIN! Score {self.score} >= {WIN_SCORE}")
                self.game_won = True
                self.sound.stop_all_music()
                self.sound.play_win()
                self.show_win_popup()
                return

        # 生成新方块
        if not self.game_over and not self.game_won:
            self.spawn_new_block()

    def clear_lines(self):
        """消除满行"""
        lines_cleared = 0
        y = GRID_HEIGHT - 1

        while y >= 0:
            if all(self.grid[y][x] != 0 for x in range(GRID_WIDTH)):
                lines_cleared += 1
                # 消除该行
                for y2 in range(y, GRID_HEIGHT - 1):
                    self.grid[y2] = self.grid[y2 + 1][:]
                self.grid[GRID_HEIGHT - 1] = [0 for _ in range(GRID_WIDTH)]
            else:
                y -= 1

        if lines_cleared > 0:
            print(f"Lines cleared: {lines_cleared}")

        return lines_cleared

    def update_speed(self):
        """更新下落速度"""
        speed_multiplier = 1.0 + (self.score // 100) * 0.1
        new_speed = INITIAL_SPEED / max(0.5, 2.0 - speed_multiplier)

        if new_speed != self.speed:
            self.speed = new_speed
            print(f"Speed updated to: {self.speed:.2f}")

    def update(self, dt):
        """更新游戏状态"""
        if not self.game_started or self.game_over or self.game_won or self.current_block is None:
            return

        # 自动下落
        self.fall_time += dt
        if self.fall_time >= self.speed:
            self.fall_time = 0
            if not self.move_block(0, -1):
                self.lock_block()
                self.sound.play_drop()

        self.draw_game()

    def show_game_over_popup(self):
        """显示游戏结束弹窗 - 使用纯文本"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        title_label = Label(
            text='GAME OVER',
            font_size='24sp',
            color=(1, 0, 0, 1),
            font_name='Arial',
            bold=True
        )
        content.add_widget(title_label)

        score_label = Label(
            text=f'Final Score: {self.score}',
            font_size='20sp',
            font_name='Arial'
        )
        content.add_widget(score_label)

        btn_layout = BoxLayout(size_hint=(1, 0.3), spacing=10)
        restart_btn = Button(
            text='Restart (R)',
            background_color=(0.2, 0.6, 1, 1),
            font_name='Arial',
            font_size='16sp'
        )
        restart_btn.bind(on_press=self.restart_game)
        btn_layout.add_widget(restart_btn)
        content.add_widget(btn_layout)

        self.popup = Popup(
            title='Game Over',
            title_font='Arial',
            content=content,
            size_hint=(0.5, 0.35)
        )
        self.popup.open()

    def show_win_popup(self):
        """显示通关弹窗 - 使用纯文本"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        title_label = Label(
            text='YOU WIN!',
            font_size='24sp',
            color=(0, 1, 0, 1),
            font_name='Arial',
            bold=True
        )
        content.add_widget(title_label)

        score_label = Label(
            text=f'Final Score: {self.score}',
            font_size='20sp',
            font_name='Arial'
        )
        content.add_widget(score_label)

        message_label = Label(
            text=f'You reached {WIN_SCORE} points!',
            font_size='16sp',
            font_name='Arial'
        )
        content.add_widget(message_label)

        btn_layout = BoxLayout(size_hint=(1, 0.3), spacing=10)
        restart_btn = Button(
            text='Play Again (R)',
            background_color=(0.2, 0.6, 1, 1),
            font_name='Arial',
            font_size='16sp'
        )
        restart_btn.bind(on_press=self.restart_game)
        btn_layout.add_widget(restart_btn)
        content.add_widget(btn_layout)

        self.popup = Popup(
            title='Victory!',
            title_font='Arial',
            content=content,
            size_hint=(0.5, 0.4)
        )
        self.popup.open()

    def restart_game(self, instance=None):
        print("Restarting game...")
        self.sound.stop_all_music()
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.game_over = False
        self.game_won = False
        self.speed = INITIAL_SPEED
        self.game_started = True
        self.fall_time = 0
        self.stats_panel.update_score(0, self.speed)
        self.sound.start_background_music()
        self.next_block = None
        self.current_block = None
        self.spawn_new_block()
        self.draw_game()
        if hasattr(self, 'popup'):
            self.popup.dismiss()

    def draw_game(self, *args):
        """绘制游戏"""
        self.game_container.canvas.clear()

        game_x = self.game_container.x
        game_y = self.game_container.y
        game_width = GRID_WIDTH * BLOCK_SIZE
        game_height = GRID_HEIGHT * BLOCK_SIZE

        start_x = game_x + (self.game_container.width - game_width) / 2
        start_y = game_y + (self.game_container.height - game_height) / 2

        with self.game_container.canvas:
            Color(0.1, 0.1, 0.1, 1)
            Rectangle(pos=(start_x, start_y), size=(game_width, game_height))

        with self.game_container.canvas:
            Color(0.3, 0.3, 0.3, 1)
            for x in range(GRID_WIDTH + 1):
                Rectangle(pos=(start_x + x * BLOCK_SIZE, start_y), size=(1, game_height))
            for y in range(GRID_HEIGHT + 1):
                Rectangle(pos=(start_x, start_y + y * BLOCK_SIZE), size=(game_width, 1))

        with self.game_container.canvas:
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    if self.grid[y][x]:
                        Color(*self.grid[y][x])
                        Rectangle(pos=(start_x + x * BLOCK_SIZE + 1,
                                       start_y + y * BLOCK_SIZE + 1),
                                  size=(BLOCK_SIZE - 2, BLOCK_SIZE - 2))

        if self.current_block and not self.game_over and not self.game_won and self.game_started:
            with self.game_container.canvas:
                Color(*self.current_block.color)
                for x, y in self.current_block.get_positions():
                    if 0 <= y < GRID_HEIGHT:
                        Rectangle(pos=(start_x + x * BLOCK_SIZE + 1,
                                       start_y + y * BLOCK_SIZE + 1),
                                  size=(BLOCK_SIZE - 2, BLOCK_SIZE - 2))

        if self.game_over:
            with self.game_container.canvas:
                Color(0, 0, 0, 0.7)
                Rectangle(pos=(start_x, start_y), size=(game_width, game_height))

        if self.game_won:
            with self.game_container.canvas:
                Color(0, 0.5, 0, 0.5)
                Rectangle(pos=(start_x, start_y), size=(game_width, game_height))


class TetrisApp(App):
    """应用程序类"""

    def build(self):
        self.title = 'Tetris - Goal: 1000'
        Window.size = (dp(1000), dp(700))

        layout = FloatLayout()
        self.game = TetrisGame(size_hint=(1, 1))
        layout.add_widget(self.game)

        return layout

    def restart_game(self, instance):
        self.game.restart_game()

    def on_stop(self):
        if hasattr(self, 'game') and hasattr(self.game, 'sound'):
            self.game.sound.stop_all_music()


if __name__ == '__main__':
    try:
        TetrisApp().run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()