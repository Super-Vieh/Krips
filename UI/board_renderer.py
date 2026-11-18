import argparse
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from Gymnasium.leaky_rule_based_bot import LeakyRuleBasedBot
from Klassen.game_factory import GameFactory

WIDTH = 900
HEIGHT = 1400
CARD_W = 108
CARD_H = 150
RADIUS = 11

ROW_Y = (290, 480, 670, 860)
DECK_Y_TOP = 82
DECK_Y_BOTTOM = 1160
DECK_X = (236, 396, 556)
FOUND_X = (336, 456)
TABLEAU_X = 190
TABLEAU_Y = 602
TABLEAU_STEP = 34
TABLEAU_STEP_CLOSED = 14
FOUND_STEP = 4
TOAST_Y = 1030
LABEL_Y = 1086
BAR_Y = 1114

PIK = "Pik"
COEUR = "Coeur"
TREFF = "Treff"
KARRO = "Karro"
SUITS = (PIK, COEUR, TREFF, KARRO)
RED_SUITS = (COEUR, KARRO)
RANK_TEXT = {1: "A", 11: "J", 12: "Q", 13: "K"}
DEFAULT_STYLE = "F1"
TURN_COLORS = {1: (206, 62, 70), 2: (64, 112, 186)}

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots")

STYLES = {
    "F1": {
        "name": "Tisch-photoreal",
        "background": "wood",
        "face_top": (253, 252, 249),
        "face_bottom": (238, 233, 224),
        "face_edge": (172, 163, 150),
        "ink_red": (166, 36, 44),
        "ink_black": (30, 30, 36),
        "shadow_alpha": 70,
        "shadow_grow": 10,
        "shadow_offset": (2, 8),
        "slot_rgb": (176, 158, 138),
        "slot_glyph_rgb": (138, 120, 102),
        "label_rgb": (216, 206, 192),
        "panel_rgb": (22, 16, 12),
        "card_gradient": True,
    },
    "F2": {
        "name": "Flach und modern",
        "background": "flat",
        "face_top": (36, 41, 55),
        "face_bottom": (24, 28, 39),
        "face_edge": (82, 94, 118),
        "ink_red": (232, 88, 100),
        "ink_black": (228, 234, 246),
        "shadow_alpha": 115,
        "shadow_grow": 12,
        "shadow_offset": (0, 11),
        "slot_rgb": (66, 77, 100),
        "slot_glyph_rgb": (50, 58, 76),
        "label_rgb": (152, 165, 190),
        "panel_rgb": (12, 15, 22),
        "card_gradient": True,
    },
    "F3": {
        "name": "Hybrid",
        "background": "hybrid",
        "face_top": (251, 250, 247),
        "face_bottom": (244, 241, 235),
        "face_edge": (184, 176, 164),
        "ink_red": (176, 46, 54),
        "ink_black": (40, 40, 44),
        "shadow_alpha": 58,
        "shadow_grow": 8,
        "shadow_offset": (1, 6),
        "slot_rgb": (168, 152, 134),
        "slot_glyph_rgb": (132, 116, 100),
        "label_rgb": (208, 198, 184),
        "panel_rgb": (24, 18, 14),
        "card_gradient": False,
    },
}

PIP_X0 = 28
PIP_Y0 = 45
PIP_W = 51
PIP_H = 59
PIP_SIZE = 11
ACE_SIZE = 38

PIPS = {
    1: ((0.5, 0.5),),
    2: ((0.5, 0.18), (0.5, 0.82)),
    3: ((0.5, 0.12), (0.5, 0.5), (0.5, 0.88)),
    4: ((0.18, 0.2), (0.82, 0.2), (0.18, 0.8), (0.82, 0.8)),
    5: ((0.18, 0.18), (0.82, 0.18), (0.5, 0.5), (0.18, 0.82), (0.82, 0.82)),
    6: ((0.2, 0.1), (0.8, 0.1), (0.2, 0.5), (0.8, 0.5), (0.2, 0.9), (0.8, 0.9)),
    7: ((0.2, 0.08), (0.8, 0.08), (0.5, 0.3), (0.2, 0.5), (0.8, 0.5), (0.2, 0.92), (0.8, 0.92)),
    8: ((0.2, 0.06), (0.8, 0.06), (0.5, 0.26), (0.2, 0.44), (0.8, 0.44), (0.5, 0.62), (0.2, 0.94), (0.8, 0.94)),
    9: ((0.2, 0.05), (0.8, 0.05), (0.2, 0.33), (0.8, 0.33), (0.5, 0.5), (0.2, 0.67), (0.8, 0.67), (0.2, 0.95), (0.8, 0.95)),
    10: ((0.2, 0.04), (0.8, 0.04), (0.5, 0.16), (0.2, 0.28), (0.8, 0.28), (0.2, 0.72), (0.8, 0.72), (0.5, 0.84), (0.2, 0.96), (0.8, 0.96)),
}

GLYPHS = {}


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(a, b, t):
    return (int(lerp(a[0], b[0], t)), int(lerp(a[1], b[1], t)), int(lerp(a[2], b[2], t)))


def gradient_surface(size, top, bottom):
    strip = pygame.Surface((1, size[1]))
    for y in range(size[1]):
        strip.set_at((0, y), lerp_color(top, bottom, y / max(1, size[1] - 1)))
    return pygame.transform.smoothscale(strip, size)


def rounded_mask(size, radius):
    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, size[0], size[1]), border_radius=radius)
    return mask


def build_wood(seed=23):
    rng = random.Random(seed)
    base = gradient_surface((WIDTH, HEIGHT), (98, 64, 42), (44, 28, 19))
    grain = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for _ in range(190):
        x0 = rng.uniform(-120, WIDTH + 40)
        amp = rng.uniform(2.0, 6.0)
        alpha = rng.randint(10, 30)
        phase = rng.uniform(0.0, 6.283)
        points = []
        for y in range(-10, HEIGHT + 20, 14):
            x = x0 + amp * math.sin(y * 0.009 + phase) + rng.uniform(-1.6, 1.6)
            points.append((x, y))
        pygame.draw.lines(grain, (26, 15, 9, alpha), False, points, rng.choice((1, 1, 2)))
    base.blit(grain, (0, 0))
    return base


def build_vignette(strength):
    small = pygame.Surface((70, 90), pygame.SRCALPHA)
    for y in range(90):
        for x in range(70):
            dx = (x / 69.0 - 0.5) * 2.0
            dy = (y / 89.0 - 0.5) * 2.0
            d = min(1.0, math.hypot(dx * 0.72, dy))
            small.set_at((x, y), (0, 0, 0, int(strength * d ** 2.4)))
    return pygame.transform.smoothscale(small, (WIDTH, HEIGHT))


def build_background(style):
    if style["background"] == "wood":
        base = build_wood()
        base.blit(build_vignette(80), (0, 0))
    elif style["background"] == "flat":
        base = gradient_surface((WIDTH, HEIGHT), (32, 37, 49), (13, 15, 22))
        base.blit(build_vignette(140), (0, 0))
    else:
        base = gradient_surface((WIDTH, HEIGHT), (34, 36, 44), (16, 17, 22))
        base.blit(build_vignette(120), (0, 0))
        frame = build_wood().convert_alpha()
        mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        mask.fill((255, 255, 255, 255))
        pygame.draw.rect(mask, (0, 0, 0, 0), (40, 40, WIDTH - 80, HEIGHT - 80), border_radius=24)
        frame.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        base.blit(frame, (0, 0))
    return base


def suit_glyph(suit, color, size):
    key = (suit, color, size)
    cached = GLYPHS.get(key)
    if cached is not None:
        return cached
    ss = 4
    w = size * ss
    h = size * ss
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    if suit == KARRO:
        pygame.draw.polygon(surf, color, [(w * 0.5, 0), (w, h * 0.5), (w * 0.5, h), (0, h * 0.5)])
    elif suit == COEUR:
        pygame.draw.circle(surf, color, (int(w * 0.30), int(h * 0.33)), int(w * 0.23))
        pygame.draw.circle(surf, color, (int(w * 0.70), int(h * 0.33)), int(w * 0.23))
        pygame.draw.polygon(surf, color, [(w * 0.07, h * 0.36), (w * 0.93, h * 0.36), (w * 0.5, h * 0.97)])
    elif suit == PIK:
        pygame.draw.circle(surf, color, (int(w * 0.30), int(h * 0.68)), int(w * 0.23))
        pygame.draw.circle(surf, color, (int(w * 0.70), int(h * 0.68)), int(w * 0.23))
        pygame.draw.polygon(surf, color, [(w * 0.07, h * 0.65), (w * 0.93, h * 0.65), (w * 0.5, h * 0.02)])
        pygame.draw.polygon(surf, color, [(w * 0.42, h * 0.72), (w * 0.58, h * 0.72), (w * 0.66, h * 0.98), (w * 0.34, h * 0.98)])
    else:
        pygame.draw.circle(surf, color, (int(w * 0.5), int(h * 0.27)), int(w * 0.23))
        pygame.draw.circle(surf, color, (int(w * 0.27), int(h * 0.63)), int(w * 0.23))
        pygame.draw.circle(surf, color, (int(w * 0.73), int(h * 0.63)), int(w * 0.23))
        pygame.draw.polygon(surf, color, [(w * 0.42, h * 0.60), (w * 0.58, h * 0.60), (w * 0.66, h * 0.98), (w * 0.34, h * 0.98)])
    out = pygame.transform.smoothscale(surf, (size, size))
    GLYPHS[key] = out
    return out


def build_shadow(size, grow, alpha):
    pad = 8
    small = (max(1, size[0] // 4), max(1, size[1] // 4))
    surf = pygame.Surface((small[0] + pad * 2, small[1] + pad * 2), pygame.SRCALPHA)
    for i in range(pad, 0, -1):
        a = int(alpha * ((pad - i) / pad) ** 1.4)
        pygame.draw.rect(surf, (0, 0, 0, a), (pad - i, pad - i + 2, small[0] + i * 2, small[1] + i * 2), border_radius=3)
    return pygame.transform.smoothscale(surf, ((small[0] + pad * 2) * 4, (small[1] + pad * 2) * 4))


class Card:
    __slots__ = ("suit", "rank", "face_up", "owner")

    def __init__(self, suit, rank, face_up, owner):
        self.suit = suit
        self.rank = rank
        self.face_up = face_up
        self.owner = owner


class Assets:
    def __init__(self, style_id):
        self.style_id = style_id
        self.style = STYLES[style_id]
        self.mask = rounded_mask((CARD_W, CARD_H), RADIUS)
        self.bg = build_background(self.style)
        self.shadow = build_shadow((CARD_W, CARD_H), self.style["shadow_grow"], self.style["shadow_alpha"])
        self.fonts = {
            "rank": pygame.font.SysFont("dejavusans", 25, bold=True),
            "corner": pygame.font.SysFont("dejavusans", 15, bold=True),
            "court": pygame.font.SysFont("dejavusans", 32, bold=True),
            "ui": pygame.font.SysFont("dejavusans", 20),
            "ui_bold": pygame.font.SysFont("dejavusans", 20, bold=True),
            "help": pygame.font.SysFont("dejavusans", 17),
            "toast": pygame.font.SysFont("dejavusans", 42, bold=True),
        }
        self.faces = {}
        self.backs = {}
        self.shadows = {}
        self.text = self.build_text()

    def build_text(self):
        label = self.style["label_rgb"]
        return {
            "turn1": self.fonts["ui_bold"].render("Zug: Rot — Spieler 1", True, label),
            "turn2": self.fonts["ui_bold"].render("Zug: Blau — Spieler 2", True, label),
            "style": self.fonts["ui"].render(self.style["name"], True, label),
            "krips": self.fonts["toast"].render("Krips!", True, (248, 228, 168)),
            "help": self.fonts["help"].render(
                "1 Lift   2 Hold   3 Drop   4 Flip   5 Reject     F1 F2 F3 Stil     Leertaste Krips     Esc Ende",
                True,
                label,
            ),
            "legend": self.fonts["help"].render("Spieler 1 = Rot     Spieler 2 = Blau", True, label),
            "lab_lift": self.fonts["ui_bold"].render("Lift", True, label),
            "lab_hold": self.fonts["ui_bold"].render("Hold", True, label),
            "lab_drop": self.fonts["ui_bold"].render("Drop", True, label),
            "lab_flip": self.fonts["ui_bold"].render("Flip", True, label),
            "lab_reject": self.fonts["ui_bold"].render("Reject", True, label),
        }

    def shadow_for(self, width, height):
        key = (width, height)
        cached = self.shadows.get(key)
        if cached is None:
            cached = build_shadow((width, height), self.style["shadow_grow"], self.style["shadow_alpha"])
            self.shadows[key] = cached
        return cached

    def warm(self):
        for suit in SUITS:
            for rank in range(1, 14):
                self.face(suit, rank)
        self.back(1)
        self.back(2)

    def face(self, suit, rank):
        key = (suit, rank)
        cached = self.faces.get(key)
        if cached is None:
            cached = self.build_face(suit, rank)
            self.faces[key] = cached
        return cached

    def back(self, owner):
        cached = self.backs.get(owner)
        if cached is None:
            cached = self.build_back(owner)
            self.backs[owner] = cached
        return cached

    def image(self, card):
        return self.face(card.suit, card.rank) if card.face_up else self.back(card.owner)

    def build_face(self, suit, rank):
        style = self.style
        surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        if style["card_gradient"]:
            surf.blit(gradient_surface((CARD_W, CARD_H), style["face_top"], style["face_bottom"]), (0, 0))
        else:
            surf.fill(style["face_top"])
        surf.blit(self.mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pygame.draw.rect(surf, style["face_edge"], (0, 0, CARD_W, CARD_H), 1, border_radius=RADIUS)
        ink = style["ink_red"] if suit in RED_SUITS else style["ink_black"]
        corner = self.build_corner(suit, rank, ink)
        if rank <= 10:
            glyph = suit_glyph(suit, ink, ACE_SIZE if rank == 1 else PIP_SIZE)
            for fx, fy in PIPS[rank]:
                gx = PIP_X0 + int(fx * PIP_W) - glyph.get_width() // 2
                gy = PIP_Y0 + int(fy * PIP_H) - glyph.get_height() // 2
                surf.blit(glyph, (gx, gy))
        else:
            panel = pygame.Rect(26, 24, 58, 74)
            pygame.draw.rect(surf, ink, panel, 1, border_radius=6)
            letter = self.fonts["court"].render(RANK_TEXT[rank], True, ink)
            surf.blit(letter, (panel.centerx - letter.get_width() // 2, panel.y + 5))
            glyph = suit_glyph(suit, ink, 24)
            surf.blit(glyph, (panel.centerx - glyph.get_width() // 2, panel.bottom - 29))
        surf.blit(corner, (8, 6))
        surf.blit(pygame.transform.rotate(corner, 180), (CARD_W - 8 - corner.get_width(), CARD_H - 6 - corner.get_height()))
        return surf

    def build_corner(self, suit, rank, ink):
        text = self.fonts["rank"].render(RANK_TEXT.get(rank, str(rank)), True, ink)
        glyph = suit_glyph(suit, ink, 15)
        width = max(text.get_width(), glyph.get_width())
        surf = pygame.Surface((width, text.get_height() + glyph.get_height()), pygame.SRCALPHA)
        surf.blit(text, ((width - text.get_width()) // 2, 0))
        surf.blit(glyph, ((width - glyph.get_width()) // 2, text.get_height()))
        return surf

    def build_back(self, owner):
        base = (52, 92, 154) if owner == 2 else (150, 44, 54)
        style = self.style
        surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        top = lerp_color(base, (255, 255, 255), 0.16 if style["background"] != "flat" else 0.05)
        bottom = lerp_color(base, (0, 0, 0), 0.24)
        surf.blit(gradient_surface((CARD_W, CARD_H), top, bottom), (0, 0))
        surf.blit(self.mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pygame.draw.rect(surf, lerp_color(base, (255, 255, 255), 0.55), (0, 0, CARD_W, CARD_H), 1, border_radius=RADIUS)
        inner = pygame.Rect(9, 9, CARD_W - 18, CARD_H - 18)
        pygame.draw.rect(surf, lerp_color(base, (255, 255, 255), 0.30), inner, 1, border_radius=7)
        lattice = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
        tint = lerp_color(base, (255, 255, 255), 0.14)
        for i in range(-inner.height, inner.width, 18):
            pygame.draw.line(lattice, tint, (i, 0), (i + inner.height, inner.height), 1)
            pygame.draw.line(lattice, tint, (i, inner.height), (i + inner.height, 0), 1)
        surf.blit(lattice, (inner.x, inner.y))
        emblem = pygame.Rect(inner.centerx - 20, inner.centery - 26, 40, 52)
        pygame.draw.rect(surf, lerp_color(base, (255, 255, 255), 0.65), emblem, 1, border_radius=4)
        pygame.draw.rect(surf, lerp_color(base, (255, 255, 255), 0.24), emblem.inflate(-10, -10), 1, border_radius=3)
        return surf


def to_demo(card, owner):
    return Card(card.card_type.value, card.card_rank.value, card.is_face_up, owner)


def build_game(seed, bot_seed, moves):
    game = GameFactory().set_up_game(seed)
    if moves <= 0:
        return game
    bot = LeakyRuleBasedBot(bot_seed, mistake_rate=0.0, krips_miss_rate=0.0)
    played = 0
    while game.is_running and played < moves:
        if not game.rules.get_all_legal_moves():
            break
        game.play_move(bot.act(game))
        played += 1
        if game.is_krips:
            game.play_move_off_turn(bot.act_off_turn(game))
    return game


def tableau_violations(game):
    bad = []
    for index, pile in enumerate(game.board.tableau):
        for lower, upper in zip(pile, pile[1:]):
            if lower.card_rank.value != upper.card_rank.value + 1 or lower.farbe == upper.farbe:
                bad.append(index)
                break
    return bad


def describe_tableau(game):
    return [
        " ".join(
            f"{c.card_rank.value}{c.card_type.value}({c.farbe[0]})" for c in pile
        ) or "--"
        for pile in game.board.tableau
    ]


class Scene:
    def __init__(self, game, human=1):
        self.game = game
        self.human = human
        self.other = 3 - human
        own = game.player1 if human == 1 else game.player2
        rival = game.player2 if human == 1 else game.player1
        self.own = {
            "reserve": [to_demo(card, human) for card in own.player_reserve],
            "waste": [to_demo(card, human) for card in own.player_waste],
            "stock": [to_demo(card, human) for card in own.player_stock],
        }
        self.other_piles = {
            "reserve": [to_demo(card, self.other) for card in rival.player_reserve],
            "waste": [to_demo(card, self.other) for card in rival.player_waste],
            "stock": [to_demo(card, self.other) for card in rival.player_stock],
        }
        self.tableau = [
            [to_demo(card, 1 if index < 4 else 2) for card in pile]
            for index, pile in enumerate(game.board.tableau)
        ]
        self.foundations = [
            [to_demo(card, 0) for card in pile] for pile in game.board.foundations
        ]
        self.turn = (
            game.current_player.player_number if game.current_player is not None else human
        )
        self.focus_pile = max(
            (index for index, pile in enumerate(self.tableau) if pile),
            key=lambda index: (len(self.tableau[index]), -index),
            default=0,
        )
        self.focus = self.tableau[self.focus_pile][-1]

    def own_display(self):
        return [self.own["reserve"], self.own["waste"], self.own["stock"]]

    def other_display(self):
        return [self.other_piles["stock"], self.other_piles["waste"], self.other_piles["reserve"]]


class Anim:
    def __init__(self, kind, duration, origin, target, card, arc=0.0):
        self.kind = kind
        self.duration = duration
        self.t = 0.0
        self.origin = origin
        self.target = target
        self.card = card
        self.arc = arc

    @property
    def finished(self):
        return self.t >= self.duration

    def advance(self, ms):
        self.t = min(self.duration, self.t + ms)

    def sample(self):
        p = 0.0 if self.duration <= 0 else min(1.0, self.t / self.duration)
        e = 1.0 - (1.0 - p) ** 3
        ox, oy = self.origin
        tx, ty = self.target
        if self.kind == "lift":
            return ox, oy + (ty - oy) * e, 1.0 + 0.06 * e, 0.35 + 0.65 * e, 1.0, True
        if self.kind == "hold":
            bob = math.sin(self.t / 1000.0 * (2.0 * math.pi / 1.6)) * 3.0 if p > 0.12 else 0.0
            return ox, oy + (ty - oy) * e + bob, 1.06, 1.0, 1.0, True
        if self.kind == "drop":
            x = ox + (tx - ox) * e
            y = oy + (ty - oy) * e - self.arc * 4.0 * p * (1.0 - p)
            return x, y, 1.06 - 0.06 * e, 0.35 + 0.65 * e, 1.0, True
        if self.kind == "flip":
            return ox, oy, 1.0, 0.5, abs(math.cos(math.pi * p)), p < 0.5
        if self.kind == "reject":
            x = ox + (tx - ox) * e
            y = oy + (ty - oy) * e
            shake = math.sin(p * math.pi * 8.0) * 8.0 * (1.0 - e)
            return x + shake, y, 1.0, 0.6 + 0.4 * (1.0 - e), 1.0, True
        return ox, oy, 1.0, 1.0, 1.0, True


def deck_cards(pile, max_visible, open_fan, closed_fan):
    count = len(pile)
    visible = min(count, max_visible)
    start = count - visible
    out = []
    offset = 0
    for i in range(visible - 1, -1, -1):
        card = pile[start + i]
        if i != visible - 1:
            offset += open_fan if card.face_up else closed_fan
        out.append((card, offset))
    out.reverse()
    return out


def horizontal_cards(pile, max_visible, direction):
    count = len(pile)
    visible = min(count, max_visible)
    start = count - visible
    out = []
    offset = 0
    for i in range(start, count):
        card = pile[i]
        out.append((card, offset * direction))
        offset += TABLEAU_STEP if card.face_up else TABLEAU_STEP_CLOSED
    return out


def pile_anchor(index):
    return (TABLEAU_X if index < 4 else TABLEAU_Y), ROW_Y[index % 4]


def top_card_pos(scene, index):
    x, y = pile_anchor(index)
    direction = -1 if index < 4 else 1
    items = horizontal_cards(scene.tableau[index], 6, direction)
    if not items:
        return x, y
    return x + items[-1][1], y


def vertical_cards(pile, max_visible, step):
    count = len(pile)
    visible = min(count, max_visible)
    start = count - visible
    out = []
    offset = 0
    for i in range(start, count):
        out.append((pile[i], offset))
        offset += step
    return out


def draw_shadow(surf, assets, x, y, width, height):
    shadow = assets.shadow_for(width, height)
    off = assets.style["shadow_offset"]
    pad_x = (shadow.get_width() - width) // 2
    pad_y = (shadow.get_height() - height) // 2
    surf.blit(shadow, (int(x) - pad_x + off[0], int(y) - pad_y + off[1]))


def draw_stack(surf, assets, pile, x, y, skip, max_visible, open_fan, closed_fan, edge_rgb=None):
    items = deck_cards(pile, max_visible, open_fan, closed_fan)
    if items:
        spread = items[-1][1] - items[0][1]
        draw_shadow(surf, assets, x, y + items[0][1], CARD_W, CARD_H + spread)
    for card, offset in items:
        if card is skip:
            continue
        surf.blit(assets.image(card), (int(x), int(y + offset)))
        if edge_rgb is not None:
            rect = pygame.Rect(int(x), int(y + offset), CARD_W, CARD_H)
            pygame.draw.rect(surf, edge_rgb, rect, 4, border_radius=RADIUS)


def draw_row(surf, assets, pile, x, y, skip, direction, max_visible=6, edge_rgb=None):
    items = horizontal_cards(pile, max_visible, direction)
    if items:
        offsets = [offset for _, offset in items]
        low = min(offsets)
        high = max(offsets)
        draw_shadow(surf, assets, x + min(0, low), y, CARD_W + (high - low), CARD_H)
    for card, offset in items:
        if card is skip:
            continue
        surf.blit(assets.image(card), (int(x + offset), int(y)))
        if edge_rgb is not None:
            rect = pygame.Rect(int(x + offset), int(y), CARD_W, CARD_H)
            pygame.draw.rect(surf, edge_rgb, rect, 4, border_radius=RADIUS)


def draw_foundation(surf, assets, pile, x, y, skip):
    items = vertical_cards(pile, 4, FOUND_STEP)
    if items:
        spread = items[-1][1] - items[0][1]
        draw_shadow(surf, assets, x, y, CARD_W, CARD_H + spread)
    for card, offset in items:
        if card is skip:
            continue
        surf.blit(assets.image(card), (int(x), int(y + offset)))


def draw_animated(surf, assets, card, x, y, scale, shadow_mul, flip, start_face):
    show_front = card.face_up if start_face else not card.face_up
    img = assets.face(card.suit, card.rank) if show_front else assets.back(card.owner)
    width = max(1, int(CARD_W * flip))
    if width != CARD_W:
        img = pygame.transform.smoothscale(img, (width, CARD_H))
    if scale != 1.0:
        img = pygame.transform.smoothscale(img, (max(1, int(width * scale)), max(1, int(CARD_H * scale))))
    sw = max(1, int(assets.shadow.get_width() * scale * flip))
    sh = max(1, int(assets.shadow.get_height() * scale))
    shadow_img = assets.shadow
    if (sw, sh) != assets.shadow.get_size():
        shadow_img = pygame.transform.smoothscale(assets.shadow, (sw, sh))
    if shadow_mul < 0.999:
        shadow_img = shadow_img.copy()
        shadow_img.set_alpha(int(255 * shadow_mul))
    off = assets.style["shadow_offset"]
    center_x = x + CARD_W / 2.0 + off[0]
    center_y = y + CARD_H / 2.0 + off[1]
    surf.blit(shadow_img, (int(center_x - sw / 2.0), int(center_y - sh / 2.0)))
    surf.blit(img, (int(x) - (img.get_width() - CARD_W) // 2, int(y) - (img.get_height() - CARD_H) // 2))


def draw_slots(surf, assets, scene):
    style = assets.style
    for row in range(4):
        for col in range(2):
            index = row * 2 + col
            rect = pygame.Rect(FOUND_X[col], ROW_Y[row], CARD_W, CARD_H)
            pygame.draw.rect(surf, style["slot_rgb"], rect, 1, border_radius=RADIUS)
            if not scene.foundations[index]:
                glyph = suit_glyph(SUITS[row], style["slot_glyph_rgb"], 26)
                surf.blit(glyph, (rect.centerx - 13, rect.centery - 13))
    for row in range(4):
        left = pygame.Rect(TABLEAU_X, ROW_Y[row], CARD_W, CARD_H)
        right = pygame.Rect(TABLEAU_Y, ROW_Y[row], CARD_W, CARD_H)
        pygame.draw.rect(surf, style["slot_rgb"], left, 1, border_radius=RADIUS)
        pygame.draw.rect(surf, style["slot_rgb"], right, 1, border_radius=RADIUS)


def draw_hud(surf, assets, scene, anim, krips, help_surface=None):
    style = assets.style
    pill = pygame.Rect(28, 20, 300, 40)
    pygame.draw.rect(surf, style["panel_rgb"], pill, border_radius=20)
    color = TURN_COLORS[scene.turn]
    pygame.draw.circle(surf, color, (pill.x + 20, pill.centery), 8)
    surf.blit(assets.text["turn1"] if scene.turn == 1 else assets.text["turn2"], (pill.x + 38, pill.y + 9))
    style_text = assets.text["style"]
    surf.blit(style_text, (WIDTH - 30 - style_text.get_width(), 16))
    legend = assets.text["legend"]
    surf.blit(legend, (WIDTH - 30 - legend.get_width(), 42))
    help_text = help_surface if help_surface is not None else assets.text["help"]
    surf.blit(help_text, ((WIDTH - help_text.get_width()) // 2, HEIGHT - 34))
    if krips > 0.01:
        toast = assets.text["krips"]
        image = toast if krips > 0.99 else toast.copy()
        if krips <= 0.99:
            image.set_alpha(int(255 * krips))
        surf.blit(image, ((WIDTH - toast.get_width()) // 2, TOAST_Y))
    if anim is not None:
        label = assets.text["lab_" + anim.kind]
        surf.blit(label, ((WIDTH - label.get_width()) // 2, LABEL_Y))
        bar_width = 260
        progress = 0.0 if anim.duration <= 0 else min(1.0, anim.t / anim.duration)
        x0 = (WIDTH - bar_width) // 2
        pygame.draw.rect(surf, style["slot_rgb"], (x0, BAR_Y, bar_width, 4), border_radius=2)
        pygame.draw.rect(surf, style["label_rgb"], (x0, BAR_Y, int(bar_width * progress), 4), border_radius=2)


def render(surf, assets, scene, anim=None, drag=None, krips=0.0):
    surf.blit(assets.bg, (0, 0))
    draw_slots(surf, assets, scene)
    skip = anim.card if anim is not None else (drag["card"] if drag else None)

    for index in range(8):
        row, col = divmod(index, 2)
        if scene.foundations[index]:
            draw_foundation(surf, assets, scene.foundations[index], FOUND_X[col], ROW_Y[row], skip)

    for row in range(4):
        draw_row(surf, assets, scene.tableau[row], TABLEAU_X, ROW_Y[row], skip, -1)
        draw_row(surf, assets, scene.tableau[4 + row], TABLEAU_Y, ROW_Y[row], skip, 1)

    for x, pile in zip(DECK_X, scene.other_display()):
        draw_stack(surf, assets, pile, x, DECK_Y_TOP, skip, 6, 4, 4)

    for x, pile in zip(DECK_X, scene.own_display()):
        draw_stack(surf, assets, pile, x, DECK_Y_BOTTOM, skip, 6, 4, 4)

    if anim is not None and anim.kind == "reject":
        phase = anim.t / anim.duration if anim.duration else 1.0
        strength = abs(math.sin(phase * math.pi * 2.0))
        color = lerp_color(assets.style["slot_rgb"], (214, 62, 62), strength)
        rect = pygame.Rect(anim.origin[0] - 5, anim.origin[1] - 5, CARD_W + 10, CARD_H + 10)
        pygame.draw.rect(surf, color, rect, 3, border_radius=16)

    if anim is not None:
        x, y, scale, shadow_mul, flip, start_face = anim.sample()
        draw_animated(surf, assets, anim.card, x, y, scale, shadow_mul, flip, start_face)
    elif drag is not None:
        x, y = drag["pos"]
        draw_animated(surf, assets, drag["card"], x, y, 1.06, 1.0, 1.0, True)
        if drag.get("target") is not None:
            pygame.draw.rect(surf, assets.style["slot_rgb"], drag["target"], 2, border_radius=RADIUS + 4)

    draw_hud(surf, assets, scene, anim, krips)


def lab_animation(scene, key):
    card = scene.focus
    rest = top_card_pos(scene, scene.focus_pile)
    lifted = (rest[0], rest[1] - 18)
    held = (rest[0], rest[1] - 38)
    target = (FOUND_X[0], ROW_Y[0])
    if key == pygame.K_1:
        return Anim("lift", 120, rest, lifted, card)
    if key == pygame.K_2:
        return Anim("hold", 1200, rest, held, card)
    if key == pygame.K_3:
        return Anim("drop", 180, held, target, card, arc=24)
    if key == pygame.K_4:
        return Anim("flip", 250, rest, rest, card)
    if key == pygame.K_5:
        return Anim("reject", 260, target, rest, card)
    return None


def run_interactive(style_id, human, game):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
    pygame.display.set_caption("Krips — Portrait Demo")
    assets = Assets(style_id)
    assets.warm()
    scene = Scene(game, human)
    clock = pygame.time.Clock()
    anim = None
    grace = 0.0
    krips_until = 0.0
    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                    anim = lab_animation(scene, event.key)
                    grace = 260.0
                elif event.key == pygame.K_SPACE:
                    krips_until = pygame.time.get_ticks() + 900
                elif event.key in (pygame.K_F1, pygame.K_F2, pygame.K_F3):
                    style_id = {pygame.K_F1: "F1", pygame.K_F2: "F2", pygame.K_F3: "F3"}[event.key]
                    assets = Assets(style_id)
                    assets.warm()
        if anim is not None:
            anim.advance(dt)
            if anim.finished:
                grace -= dt
                if grace <= 0:
                    anim = None
        krips = max(0.0, (krips_until - pygame.time.get_ticks()) / 900.0)
        render(screen, assets, scene, anim, None, krips)
        pygame.display.flip()
    pygame.quit()


def save(surf, name):
    path = os.path.join(SHOTS, name + ".png")
    pygame.image.save(surf, path)
    return path


def style_sheet(game):
    thumbs = []
    for style_id in STYLES:
        assets = Assets(style_id)
        assets.warm()
        canvas = pygame.Surface((WIDTH, HEIGHT))
        render(canvas, assets, Scene(game, 1))
        thumbs.append((style_id, pygame.transform.smoothscale(canvas, (280, 436))))
    sheet = pygame.Surface((900, 620))
    sheet.fill((13, 13, 15))
    title_font = pygame.font.SysFont("dejavusans", 30, bold=True)
    small = pygame.font.SysFont("dejavusans", 18)
    note = pygame.font.SysFont("dejavusans", 15)
    sheet.blit(title_font.render("Krips hochkant — Stilvarianten", True, (232, 230, 236)), (30, 22))
    sheet.blit(small.render("900x1400, auf 280x436 skaliert", True, (130, 130, 140)), (30, 60))
    notes = {
        "F1": ("Holz mit Maserung, Papierton", "weiche kurze Schatten"),
        "F2": ("dunkel und flach", "hellste Tinte auf dunkler Karte"),
        "F3": ("Holz nur als Rahmen", "flache Karten, klarer Rand"),
    }
    for index, (style_id, image) in enumerate(thumbs):
        x = 12 + index * (280 + 14)
        y = 96
        sheet.blit(image, (x, y))
        pygame.draw.rect(sheet, (66, 66, 74), (x - 1, y - 1, 282, 438), 1)
        caption = small.render(f"{style_id} — {STYLES[style_id]['name']}", True, (214, 212, 220))
        sheet.blit(caption, (x, y + 446))
        for line_index, line in enumerate(notes[style_id]):
            text = note.render(line, True, (134, 136, 148))
            sheet.blit(text, (x, y + 472 + line_index * 20))
    return sheet


def run_screenshots(human, game, start_game):
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT))
    paths = []
    out = pygame.Surface((WIDTH, HEIGHT))

    assets = Assets(DEFAULT_STYLE)
    assets.warm()
    scene = Scene(game, human)
    card = scene.focus
    rest = top_card_pos(scene, scene.focus_pile)
    lifted = (rest[0], rest[1] - 18)
    held = (rest[0], rest[1] - 38)
    target = (FOUND_X[0], ROW_Y[0])

    render(out, assets, scene)
    paths.append(save(out, "portrait_01_board"))

    anim = Anim("lift", 120, rest, lifted, card)
    anim.t = 54
    render(out, assets, scene, anim)
    paths.append(save(out, "portrait_02_lift"))

    anim = Anim("hold", 1200, rest, held, card)
    anim.t = 420
    render(out, assets, scene, anim)
    paths.append(save(out, "portrait_03_hold"))

    anim = Anim("drop", 180, held, target, card, arc=24)
    anim.t = 96
    render(out, assets, scene, anim)
    paths.append(save(out, "portrait_04_drop"))

    anim = Anim("flip", 250, rest, rest, card)
    anim.t = 112
    render(out, assets, scene, anim)
    paths.append(save(out, "portrait_05_flip"))

    anim = Anim("reject", 260, held, rest, card)
    anim.t = 150
    render(out, assets, scene, anim, None, 0.85)
    paths.append(save(out, "portrait_06_reject"))

    drag = {"card": card, "pos": (330, 520), "target": pygame.Rect(FOUND_X[0], ROW_Y[0], CARD_W, CARD_H)}
    render(out, assets, scene, None, drag)
    paths.append(save(out, "portrait_07_drag"))

    paths.append(save(style_sheet(game), "portrait_00_styles"))

    start_scene = Scene(start_game, human)
    render(out, assets, start_scene)
    paths.append(save(out, "portrait_08_start"))

    pygame.quit()
    return paths


def run_bench(human, frames, game):
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT))
    assets = Assets(DEFAULT_STYLE)
    assets.warm()
    scene = Scene(game, human)
    surf = pygame.Surface((WIDTH, HEIGHT))
    rest = top_card_pos(scene, scene.focus_pile)
    anim = Anim("hold", 10 ** 9, rest, (rest[0], rest[1] - 38), scene.focus)
    samples = []
    render(surf, assets, scene, anim)
    for i in range(frames):
        anim.t = (i * 16.7) % 1600.0
        start = time.perf_counter()
        render(surf, assets, scene, anim)
        samples.append((time.perf_counter() - start) * 1000.0)
    samples.sort()
    mean = sum(samples) / len(samples)
    p95 = samples[int(len(samples) * 0.95)]
    print(f"frames {frames}  mean {mean:.2f} ms  p95 {p95:.2f} ms  max {samples[-1]:.2f} ms")
    pygame.quit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", default=DEFAULT_STYLE, choices=list(STYLES))
    parser.add_argument("--human", type=int, default=1, choices=(1, 2))
    parser.add_argument("--seed", type=int, default=170)
    parser.add_argument("--bot-seed", type=int, default=5170)
    parser.add_argument("--moves", type=int, default=118)
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--screenshots", action="store_true")
    parser.add_argument("--bench", action="store_true")
    parser.add_argument("--frames", type=int, default=600)
    args = parser.parse_args()

    start_game = build_game(args.seed, args.bot_seed, 0)
    game = start_game if args.start else build_game(args.seed, args.bot_seed, args.moves)

    if args.validate:
        print(f"seed {args.seed}  bot_seed {args.bot_seed}  moves {0 if args.start else args.moves}")
        print(f"turn player {game.current_player.player_number if game.current_player else None}")
        for index, text in enumerate(describe_tableau(game)):
            print(f"  tableau {index}: {text}")
        print(f"empty tableau piles: {[i for i, pile in enumerate(game.board.tableau) if not pile]}")
        print(f"violations: {tableau_violations(game)}")
        return

    if args.screenshots or args.bench:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    if args.screenshots:
        os.makedirs(SHOTS, exist_ok=True)
        for path in run_screenshots(args.human, game, start_game):
            print(path)
        return
    if args.bench:
        run_bench(args.human, args.frames, game)
        return
    run_interactive(args.style, args.human, game)


if __name__ == "__main__":
    main()
