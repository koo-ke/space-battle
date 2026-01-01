import pyxel
import random

class Game:
    def __init__(self):
        pyxel.init(160, 120, title="Space Battle")

        # リソースファイルを読み込む
        pyxel.load("space_battle.pyxres")

        # ゲーム状態（TITLE, PLAYING, GAME_OVER）
        self.game_state = "TITLE"

        # 背景の星を初期化
        self.stars = []
        for _ in range(50):
            self.stars.append({
                'x': random.randint(0, 160),
                'y': random.randint(0, 120),
                'speed': random.uniform(0.2, 0.5),
                'brightness': random.choice([5, 6, 7])
            })

        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.player_x = 80
        self.player_y = 100
        self.player_size = 8
        self.player_sprite = 16  # デフォルトのスプライト位置

        self.enemies = []
        self.spawn_timer = 0

        self.score = 0

    def update(self):
        # 背景の星を更新（常に動き続ける）
        for star in self.stars:
            star['y'] += star['speed']
            # 画面外に出たら上に戻す
            if star['y'] > 120:
                star['y'] = 0
                star['x'] = random.randint(0, 160)

        # タイトル画面
        if self.game_state == "TITLE":
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.reset_game()
                self.game_state = "PLAYING"
            return

        # ゲームオーバー画面
        if self.game_state == "GAME_OVER":
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.game_state = "TITLE"
            return

        # プレイ中（PLAYING）
        # 宇宙船移動
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player_x = max(self.player_x - 2, 0)
            self.player_sprite = 24  # 左移動スプライト
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x = min(self.player_x + 2, 160 - self.player_size)
            self.player_sprite = 32  # 右移動スプライト
        else:
            self.player_sprite = 16  # デフォルトスプライト

        # エイリアンの生成
        # スコアが高いほど出現間隔を短く（最小10フレーム）
        spawn_interval = max(1, 30 - (self.score // 100))

        self.spawn_timer += 1
        if self.spawn_timer >= spawn_interval:
            # スコアが100を超えるたびにエイリアンの種類が増える
            # スコア0-99: 1種類, 100-199: 2種類, 200-299: 3種類, 300-399: 4種類, 400以上: 5種類
            max_alien_types = min((self.score // 100) + 1, 5)
            alien_type = random.randint(0, max_alien_types - 1)

            # エイリアンタイプごとの初速度を設定
            # type 0: 通常の速度, type 1: 早い, type 2: より早い,
            # type 3: ゆっくりから早くなる, type 4: かなり遅い
            if alien_type == 0:
                speed = 2.0
            elif alien_type == 1:
                speed = 3.0
            elif alien_type == 2:
                speed = 4.0
            elif alien_type == 3:
                speed = 0.3  # 非常にゆっくりスタート
            else:  # alien_type == 4
                speed = 0.5  # かなり遅い

            self.enemies.append({
                'x': random.randint(0, 160),
                'y': 0,
                'radius': 4,
                'type': alien_type,
                'speed': speed
            })
            self.spawn_timer = 0

        # エイリアンの移動
        for enemy in self.enemies:
            # type 3（色違い3）は加速する
            if enemy['type'] == 3:
                enemy['speed'] += 0.12  # 加速度（緩急を強く）

            enemy['y'] += enemy['speed']

        # 当たり判定
        for enemy in self.enemies:
            if self.check_collision(enemy):
                self.game_state = "GAME_OVER"

        # 画面外のエイリアンを削除
        self.enemies = [e for e in self.enemies if e['y'] < 120]

        # スコア加算
        self.score += 1

    def check_collision(self, enemy):
        # 円と矩形の当たり判定（簡易版）
        player_center_x = self.player_x + self.player_size / 2
        player_center_y = self.player_y + self.player_size / 2

        distance = ((player_center_x - enemy['x']) ** 2 +
                   (player_center_y - enemy['y']) ** 2) ** 0.5

        return distance < (enemy['radius'] + self.player_size / 2)

    def draw(self):
        pyxel.cls(0)

        # 背景の星を描画
        for star in self.stars:
            pyxel.pset(star['x'], int(star['y']), star['brightness'])

        # タイトル画面
        if self.game_state == "TITLE":
            # 中央揃え: x = (160 - テキスト長 * 4) / 2
            title = "SPACE BATTLE"
            pyxel.text((160 - len(title) * 4) // 2, 40, title, 10)

            # 点滅するテキスト
            if (pyxel.frame_count // 2) % 2 == 0:
                start_text = "PRESS SPACE TO START"
                pyxel.text((160 - len(start_text) * 4) // 2, 60, start_text, 7)
            return

        # ゲームオーバー画面
        if self.game_state == "GAME_OVER":
            # 中央揃え
            game_over_text = "GAME OVER"
            pyxel.text((160 - len(game_over_text) * 4) // 2, 50, game_over_text, 8)

            score_text = f"SCORE: {self.score}"
            pyxel.text((160 - len(score_text) * 4) // 2, 60, score_text, 7)

            retry_text = "PRESS SPACE TO TITLE"
            pyxel.text((160 - len(retry_text) * 4) // 2, 70, retry_text, 7)
            return

        # プレイ中（PLAYING）
        # 宇宙船描画（ドット絵を使用）
        # 移動状態に応じてスプライトを切り替え
        pyxel.blt(self.player_x, self.player_y, 0, self.player_sprite, 0, 8, 8, 0)

        # エイリアン描画（ドット絵を使用）
        # アニメーション: 5フレームごとに画像を切り替え
        anim_frame = (pyxel.frame_count // 5) % 2
        sprite_x = anim_frame * 8  # 0または8

        for enemy in self.enemies:
            # エイリアンのタイプに応じてy座標を変更
            # type 0: y=0 (通常), type 1: y=8 (色違い1), type 2: y=16 (色違い2),
            # type 3: y=24 (色違い3), type 4: y=32 (色違い4)
            sprite_y = enemy['type'] * 8
            # pyxel.blt(描画先x, 描画先y, 画像バンク, 画像内x, 画像内y, 幅, 高さ, 透明色)
            pyxel.blt(enemy['x'] - 4, enemy['y'] - 4, 0, sprite_x, sprite_y, 8, 8, 0)

        # スコア表示
        pyxel.text(5, 5, f"SCORE: {self.score}", 7)

Game()
