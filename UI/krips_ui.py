import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

from board_renderer import (
    CARD_H,
    CARD_W,
    DECK_X,
    DECK_Y_BOTTOM,
    DECK_Y_TOP,
    DEFAULT_STYLE,
    FOUND_X,
    HEIGHT,
    ROW_Y,
    SHOTS,
    STYLES,
    TABLEAU_X,
    TABLEAU_Y,
    TURN_COLORS,
    WIDTH,
    Anim,
    Assets,
    Card,
    build_game,
    draw_animated,
    draw_foundation,
    draw_hud,
    draw_row,
    draw_slots,
    draw_stack,
    horizontal_cards,
    lerp_color,
    pile_anchor,
    save,
    top_card_pos,
)
from Gymnasium.leaky_rule_based_bot import LeakyRuleBasedBot
from Klassen.move import DestinationType, Move, OriginType

OWN_ORDER = ("reserve", "waste", "stock")
OTHER_ORDER = ("stock", "waste", "reserve")
PILE_NAMES = ("stock", "waste", "reserve")
DECK_INDEX = {"stock": 0, "waste": 1, "reserve": 2}
BOT_DELAY_MS = 750
KRIPS_DELAY_MS = 900
KRIPS_WINDOW_MS = 6000
SELECT_LIFT = 26
LIFT_MS = 130
DRAG_THRESHOLD = 5
HIGHLIGHT_RGB = (236, 208, 118)
REJECT_RGB = (214, 62, 62)
STATUS_Y = 1096
UI_HELP = "Klicken oder ziehen     Leertaste Krips     R Haufen umdrehen     F1 F2 F3 Stil     Esc Ende"


class View:
    def __init__(self, game, human=1):
        self.game = game
        self.human = human
        self.other = 3 - human
        self.cache = {}
        self.refresh()

    def demo(self, card, owner):
        entry = self.cache.get(id(card))
        if entry is None:
            entry = Card(card.card_type.value, card.card_rank.value, card.is_face_up, owner)
            self.cache[id(card)] = entry
        entry.face_up = card.is_face_up
        entry.owner = owner
        return entry

    def refresh(self):
        game = self.game
        own = game.player1 if self.human == 1 else game.player2
        rival = game.player2 if self.human == 1 else game.player1
        self.own = {
            "stock": [self.demo(card, self.human) for card in own.player_stock],
            "waste": [self.demo(card, self.human) for card in own.player_waste],
            "reserve": [self.demo(card, self.human) for card in own.player_reserve],
        }
        self.other_piles = {
            "stock": [self.demo(card, self.other) for card in rival.player_stock],
            "waste": [self.demo(card, self.other) for card in rival.player_waste],
            "reserve": [self.demo(card, self.other) for card in rival.player_reserve],
        }
        self.tableau = [
            [self.demo(card, 1 if index < 4 else 2) for card in pile]
            for index, pile in enumerate(game.board.tableau)
        ]
        self.foundations = [
            [self.demo(card, 0) for card in pile] for pile in game.board.foundations
        ]
        self.turn = (
            game.current_player.player_number if game.current_player is not None else self.human
        )

    def own_display(self):
        return [self.own[name] for name in OWN_ORDER]

    def other_display(self):
        return [self.other_piles[name] for name in OTHER_ORDER]


def deck_pos(side, name):
    if side == "own":
        return DECK_X[OWN_ORDER.index(name)], DECK_Y_BOTTOM
    return DECK_X[OTHER_ORDER.index(name)], DECK_Y_TOP


def deck_rect(side, name):
    x, y = deck_pos(side, name)
    return pygame.Rect(x, y, CARD_W, CARD_H)


def tableau_rect(view, index):
    x, y = pile_anchor(index)
    items = horizontal_cards(view.tableau[index], 6, -1 if index < 4 else 1)
    if not items:
        return pygame.Rect(x, y, CARD_W, CARD_H)
    offsets = [offset for _, offset in items]
    return pygame.Rect(x + min(offsets), y, CARD_W + max(offsets) - min(offsets), CARD_H)


def foundation_rect(index):
    row, col = divmod(index, 2)
    return pygame.Rect(FOUND_X[col], ROW_Y[row], CARD_W, CARD_H)


def location_at(view, pos):
    for name in OWN_ORDER:
        if deck_rect("own", name).collidepoint(pos):
            return ("deck", name)
    for name in OTHER_ORDER:
        if deck_rect("other", name).collidepoint(pos):
            return ("opponent_deck", name)
    for index in range(8):
        if foundation_rect(index).collidepoint(pos):
            return ("foundation", index)
    for index in range(8):
        if tableau_rect(view, index).collidepoint(pos):
            return ("tableau", index)
    return None


def source_position(view, loc):
    kind, value = loc
    if kind == "deck":
        return deck_pos("own", value)
    return top_card_pos(view, value)


def source_location(move):
    if move.origin_type == OriginType.PLAYER:
        return ("deck", PILE_NAMES[move.origin_value])
    return ("tableau", move.origin_value)


def target_rect(view, move):
    if move.destination_type == DestinationType.FOUNDATION:
        return foundation_rect(move.destination_value)
    if move.destination_type == DestinationType.TABLEAU:
        return tableau_rect(view, move.destination_value)
    if move.destination_type == DestinationType.OPPONENT:
        return deck_rect("other", "waste")
    if move.destination_type == DestinationType.PLAYER and move.destination_value == 1:
        return deck_rect("own", "waste")
    return None


def side_for(player_number, human):
    return "own" if player_number == human else "other"


def target_position(view, move, actor, human=1):
    if move.destination_type == DestinationType.TABLEAU:
        return top_card_pos(view, move.destination_value)
    if move.destination_type == DestinationType.FOUNDATION:
        rect = foundation_rect(move.destination_value)
        return rect.x, rect.y
    if move.destination_type == DestinationType.PLAYER:
        return deck_pos(side_for(actor, human), PILE_NAMES[move.destination_value])
    return deck_pos(side_for(3 - actor, human), "waste")


def same_origin(move, loc):
    kind, value = loc
    if kind == "deck":
        return move.origin_type == OriginType.PLAYER and move.origin_value == DECK_INDEX[value]
    if kind == "tableau":
        return move.origin_type == OriginType.TABLEAU and move.origin_value == value
    return False


def is_plain_flip(move):
    return (
        move.origin_type == OriginType.PLAYER
        and move.destination_type == DestinationType.PLAYER
        and move.origin_value == move.destination_value
    )


def build_move(source, target):
    if source is None or target is None:
        return None
    kind, value = source
    if kind == "deck":
        origin_type = OriginType.PLAYER
        origin_value = DECK_INDEX[value]
    elif kind == "tableau":
        origin_type = OriginType.TABLEAU
        origin_value = value
    else:
        return None
    tkind, tvalue = target
    if tkind == "foundation":
        return Move(origin_type, origin_value, DestinationType.FOUNDATION, tvalue)
    if tkind == "tableau":
        return Move(origin_type, origin_value, DestinationType.TABLEAU, tvalue)
    if tkind == "opponent_deck" and tvalue == "waste":
        return Move(origin_type, origin_value, DestinationType.OPPONENT, 0)
    if tkind == "deck" and tvalue == value and value in ("stock", "reserve"):
        return Move(origin_type, origin_value, DestinationType.PLAYER, DECK_INDEX[value])
    if tkind == "deck" and value == "stock" and tvalue == "waste":
        return Move(origin_type, origin_value, DestinationType.PLAYER, 1)
    return None


def move_text(move):
    if move.origin_type == OriginType.PLAYER:
        source = ("Stock", "Haufen", "Dreizehner")[move.origin_value]
    else:
        source = f"Tableau {move.origin_value + 1}"
    if move.destination_type == DestinationType.PLAYER:
        target = ("Stock", "Haufen", "Dreizehner")[move.destination_value]
    elif move.destination_type == DestinationType.TABLEAU:
        target = f"Tableau {move.destination_value + 1}"
    elif move.destination_type == DestinationType.FOUNDATION:
        target = f"Foundation {move.destination_value + 1}"
    else:
        target = "Gegner-Haufen"
    return f"{source} -> {target}"


def draw_board(
    surf,
    assets,
    view,
    skip,
    held=None,
    held_pos=None,
    anim=None,
    krips=0.0,
    highlight=(),
    status=None,
    help_surface=None,
    turn_hint=False,
):
    surf.blit(assets.bg, (0, 0))
    draw_slots(surf, assets, view)
    edge = TURN_COLORS.get(view.turn) if turn_hint else None
    own_edge = edge if view.turn == view.human else None
    other_edge = edge if view.turn == view.other else None
    left_edge = edge if view.turn == 1 else None
    right_edge = edge if view.turn == 2 else None
    for index in range(8):
        if view.foundations[index]:
            row, col = divmod(index, 2)
            draw_foundation(
                surf, assets, view.foundations[index], FOUND_X[col], ROW_Y[row], skip
            )
    for row in range(4):
        draw_row(
            surf, assets, view.tableau[row], TABLEAU_X, ROW_Y[row], skip, -1, edge_rgb=left_edge
        )
        draw_row(
            surf, assets, view.tableau[4 + row], TABLEAU_Y, ROW_Y[row], skip, 1, edge_rgb=right_edge
        )
    for x, pile in zip(DECK_X, view.other_display()):
        draw_stack(surf, assets, pile, x, DECK_Y_TOP, skip, 6, 4, 4, edge_rgb=other_edge)
    for x, pile in zip(DECK_X, view.own_display()):
        draw_stack(surf, assets, pile, x, DECK_Y_BOTTOM, skip, 6, 4, 4, edge_rgb=own_edge)
    for rect in highlight:
        pygame.draw.rect(surf, HIGHLIGHT_RGB, rect.inflate(10, 10), 3, border_radius=16)
    if anim is not None and anim.kind == "reject" and anim.duration > 0:
        phase = anim.t / anim.duration
        strength = abs(math.sin(phase * math.pi * 2.0))
        color = lerp_color(assets.style["slot_rgb"], REJECT_RGB, strength)
        pygame.draw.rect(
            surf,
            color,
            pygame.Rect(anim.origin[0] - 5, anim.origin[1] - 5, CARD_W + 10, CARD_H + 10),
            3,
            border_radius=16,
        )
    if held is not None and held_pos is not None:
        draw_animated(surf, assets, held, held_pos[0], held_pos[1], 1.06, 1.0, 1.0, True)
    if anim is not None:
        x, y, scale, shadow_mul, flip, start_face = anim.sample()
        if anim.kind == "flip" and anim.duration > 0:
            start_face = anim.t / anim.duration >= 0.5
        draw_animated(surf, assets, anim.card, x, y, scale, shadow_mul, flip, start_face)
    draw_hud(surf, assets, view, None, krips, help_surface)
    if status is not None:
        plate = pygame.Rect(0, 0, status.get_width() + 44, 40)
        plate.center = (WIDTH // 2, STATUS_Y + 14)
        panel = pygame.Surface(plate.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (*assets.style["panel_rgb"], 216), panel.get_rect(), border_radius=20)
        surf.blit(panel, plate.topleft)
        surf.blit(status, (plate.x + 22, plate.y + 9))


class KripsUI:
    def __init__(self, game, human=1, style_id=DEFAULT_STYLE, bot_seed=0):
        pygame.init()
        if pygame.display.get_surface() is None:
            pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
        self.game = game
        self.human = human
        self.view = View(game, human)
        self.set_style(style_id)
        self.bot = LeakyRuleBasedBot(bot_seed, mistake_rate=0.0, krips_miss_rate=0.0)
        self.held = None
        self.held_source = None
        self.held_pos = None
        self.lift_from = None
        self.lift_to = None
        self.lift_t = LIFT_MS
        self.grab = (0, 0)
        self.press_pos = None
        self.dragging = False
        self.moved = False
        self.highlight = ()
        self.anims = []
        self.last_actor = None
        self.bot_due = 0
        self.krips_deadline = 0
        self.krips_until = 0
        self.message = ""
        self.message_until = 0
        self.status_cache = {}
        self.schedule()

    def set_style(self, style_id):
        self.assets = Assets(style_id)
        self.assets.warm()
        self.help_surface = self.assets.fonts["help"].render(
            UI_HELP, True, self.assets.style["label_rgb"]
        )
        self.status_cache = {}

    @property
    def opponent_number(self):
        return 3 - self.human

    def my_turn(self):
        return (
            self.game.is_running
            and self.game.current_player is not None
            and self.game.current_player.player_number == self.human
        )

    def can_play(self):
        return self.my_turn() and not self.game.is_krips

    def legal_moves(self):
        if not self.game.is_running or self.game.current_player is None:
            return []
        return self.game.rules.get_all_legal_moves()

    def own_top(self, name):
        pile = self.view.own[name]
        return pile[-1] if pile else None

    def source_card(self, loc):
        if loc is None:
            return None
        kind, value = loc
        if kind == "deck":
            return self.own_top(value)
        if kind == "tableau":
            pile = self.view.tableau[value]
            return pile[-1] if pile else None
        return None

    def legal_targets(self, loc):
        rects = []
        for move in self.legal_moves():
            if not same_origin(move, loc) or is_plain_flip(move):
                continue
            rect = target_rect(self.view, move)
            if rect is not None:
                rects.append(rect)
        return rects

    def clear_held(self):
        self.held = None
        self.held_source = None
        self.held_pos = None
        self.lift_from = None
        self.lift_t = LIFT_MS
        self.dragging = False
        self.press_pos = None
        self.moved = False
        self.highlight = ()

    def pick(self, loc, pos):
        card = self.source_card(loc)
        if card is None:
            return False
        x, y = source_position(self.view, loc)
        self.held = card
        self.held_source = loc
        self.held_pos = (x, y)
        self.lift_from = (x, y)
        self.lift_to = (x, y - SELECT_LIFT)
        self.lift_t = 0
        self.grab = (pos[0] - x, pos[1] - y)
        self.press_pos = pos
        self.moved = False
        self.highlight = tuple(self.legal_targets(loc))
        return True

    def push_anim(self, card, kind, origin, target, arc=0.0):
        if card is None or origin is None or target is None:
            return
        duration = {"flip": 260, "drop": 240, "reject": 280}[kind]
        self.anims.append(Anim(kind, duration, origin, target, card, arc))

    def after_action(self, actor):
        self.last_actor = actor
        self.schedule()

    def schedule(self, ignore_krips=False):
        if not self.game.is_running or self.game.current_player is None:
            self.bot_due = 0
            self.krips_deadline = 0
            return
        now = pygame.time.get_ticks()
        if self.game.is_krips and not ignore_krips:
            if self.last_actor == self.human:
                self.bot_due = now + KRIPS_DELAY_MS
                self.krips_deadline = 0
            else:
                self.bot_due = 0
                self.krips_deadline = now + KRIPS_WINDOW_MS
            return
        self.krips_deadline = 0
        if self.game.current_player.player_number != self.human:
            self.bot_due = now + BOT_DELAY_MS
        else:
            self.bot_due = 0

    def apply_move(self, move, source, actor):
        card = self.source_card(source)
        origin = source_position(self.view, source) if source is not None else None
        self.game.play_move(move)
        self.view.refresh()
        if card is not None and origin is not None:
            if is_plain_flip(move):
                self.push_anim(card, "flip", origin, origin)
            else:
                self.push_anim(
                    card, "drop", origin, target_position(self.view, move, actor, self.human), arc=26
                )
        self.after_action(actor)

    def apply_flip(self, move, actor):
        player = self.game.current_player
        name = "reserve" if move.origin_value == 2 else "stock"
        pile = player.player_reserve if name == "reserve" else player.player_stock
        card = self.view.demo(pile[-1], actor) if pile else None
        side = "own" if player.player_number == self.human else "other"
        position = deck_pos(side, name)
        self.game.play_move(move)
        self.view.refresh()
        if card is not None:
            self.push_anim(card, "flip", position, position)
        self.after_action(actor)

    def reject(self, loc):
        card = self.held
        origin = self.held_pos if self.held_pos is not None else (0, 0)
        rect = None
        if loc is not None:
            kind, value = loc
            if kind == "tableau":
                origin = top_card_pos(self.view, value)
            elif kind == "foundation":
                rect = foundation_rect(value)
            elif kind == "deck":
                rect = deck_rect("own", value)
            elif kind == "opponent_deck":
                rect = deck_rect("other", value)
        if rect is not None:
            origin = (rect.x, rect.y)
        if card is not None and self.held_source is not None:
            back = source_position(self.view, self.held_source)
            self.push_anim(card, "reject", origin, back)
        self.flash("Zug nicht erlaubt")
        self.clear_held()

    def handle_target(self, loc):
        if (
            not self.can_play()
            or self.held_source is None
            or self.source_card(self.held_source) is not self.held
        ):
            self.reject(loc)
            return
        move = build_move(self.held_source, loc)
        if move is not None and move in self.legal_moves():
            source = self.held_source
            self.clear_held()
            self.apply_move(move, source, self.human)
        else:
            self.reject(loc)

    def flash(self, text):
        self.message = text
        self.message_until = pygame.time.get_ticks() + 1400

    def press(self, pos):
        if self.anims:
            return
        loc = location_at(self.view, pos)
        if self.held is not None:
            if not self.can_play() or self.source_card(self.held_source) is not self.held:
                self.reject(loc)
                return
            if loc is not None and loc == self.held_source:
                self.clear_held()
                return
            self.handle_target(loc)
            return
        if not self.can_play():
            if loc is not None:
                self.flash("Krips steht aus" if self.my_turn() else "Du bist nicht am Zug")
            return
        if loc is None:
            return
        if loc in (("deck", "stock"), ("deck", "reserve")):
            name = loc[1]
            top = self.own_top(name)
            if top is not None and not top.face_up:
                value = DECK_INDEX[name]
                self.apply_flip(
                    Move(OriginType.PLAYER, value, DestinationType.PLAYER, value), self.human
                )
                return
        if self.pick(loc, pos):
            self.dragging = True

    def motion(self, pos):
        if not self.dragging or self.held is None or self.press_pos is None:
            return
        if abs(pos[0] - self.press_pos[0]) > DRAG_THRESHOLD or abs(pos[1] - self.press_pos[1]) > DRAG_THRESHOLD:
            self.moved = True
            self.lift_t = LIFT_MS
        self.held_pos = (pos[0] - self.grab[0], pos[1] - self.grab[1] - SELECT_LIFT)

    def release(self, pos):
        if not self.dragging:
            return
        self.dragging = False
        if not self.moved:
            return
        loc = location_at(self.view, pos)
        if loc is not None and loc == self.held_source:
            self.clear_held()
            return
        self.handle_target(loc)

    def flip_waste(self):
        if not self.can_play():
            return
        move = Move(OriginType.PLAYER, 0, DestinationType.PLAYER, 0)
        if not self.view.own["stock"] and self.own_top("waste") and move in self.legal_moves():
            self.clear_held()
            self.apply_flip(move, self.human)
        else:
            self.flash("Haufen kann nicht umgedreht werden")

    def human_krips(self):
        call = Move(OriginType.KRIPS, 1, DestinationType.KRIPS, 1)
        if self.last_actor == self.human:
            self.flash("Den Fehler entscheidet der Gegner")
            return
        if not self.game.is_krips or call not in self.game.rules.get_legal_moves_when_not_playing():
            self.flash("Kein Krips moeglich")
            return
        self.clear_held()
        self.game.play_move_off_turn(call)
        self.view.refresh()
        self.krips_until = pygame.time.get_ticks() + 1100
        self.after_action(self.human)

    def opponent_krips(self):
        call = Move(OriginType.KRIPS, 1, DestinationType.KRIPS, 1)
        if call not in self.game.rules.get_legal_moves_when_not_playing():
            return False
        self.clear_held()
        self.game.play_move_off_turn(call)
        self.view.refresh()
        self.krips_until = pygame.time.get_ticks() + 1100
        self.after_action(self.opponent_number)
        return True

    def bot_turn(self):
        move = self.bot.act(self.game, self.game.rules.get_all_legal_moves())
        actor = self.game.current_player.player_number
        card = None
        position = None
        if move.origin_type == OriginType.PLAYER:
            player = self.game.player1 if actor == 1 else self.game.player2
            pile = player.player_piles[move.origin_value]
            if pile:
                card = self.view.demo(pile[-1], actor)
                side = "own" if actor == self.human else "other"
                position = deck_pos(side, PILE_NAMES[move.origin_value])
        else:
            pile = self.game.board.tableau[move.origin_value]
            if pile:
                card = self.view.demo(pile[-1], 1 if move.origin_value < 4 else 2)
                position = top_card_pos(self.view, move.origin_value)
        self.game.play_move(move)
        self.view.refresh()
        if card is not None and position is not None:
            if is_plain_flip(move):
                self.push_anim(card, "flip", position, position)
            else:
                self.push_anim(
                    card, "drop", position, target_position(self.view, move, actor, self.human), arc=26
                )
        self.after_action(actor)

    def update(self, dt):
        if self.held is not None and self.lift_from is not None and self.lift_t < LIFT_MS and not self.moved:
            self.lift_t = min(LIFT_MS, self.lift_t + dt)
            progress = self.lift_t / LIFT_MS
            eased = 1.0 - (1.0 - progress) ** 3
            self.held_pos = (
                self.lift_from[0] + (self.lift_to[0] - self.lift_from[0]) * eased,
                self.lift_from[1] + (self.lift_to[1] - self.lift_from[1]) * eased,
            )
        if self.anims:
            head = self.anims[0]
            head.advance(dt)
            if head.finished:
                self.anims.pop(0)
            return
        if not self.game.is_running:
            return
        now = pygame.time.get_ticks()
        if self.krips_deadline and now >= self.krips_deadline:
            self.schedule(ignore_krips=True)
            return
        if not self.bot_due or now < self.bot_due:
            return
        self.bot_due = 0
        if self.game.is_krips and self.last_actor == self.human:
            if not self.opponent_krips():
                self.schedule()
            return
        if self.game.current_player is not None and self.game.current_player.player_number != self.human:
            self.bot_turn()

    def status(self):
        if self.message and pygame.time.get_ticks() < self.message_until:
            text = self.message
        elif not self.game.is_running:
            if self.game.player1.won:
                text = "Spiel beendet - Spieler 1 gewinnt"
            elif self.game.player2.won:
                text = "Spiel beendet - Spieler 2 gewinnt"
            else:
                text = "Spiel beendet - Patz"
        elif self.game.is_krips and self.last_actor == self.opponent_number:
            text = "Fehler des Gegners - Leertaste fuer Krips"
        elif self.game.is_krips:
            text = "Fehler gemacht - der Gegner kann Krips rufen"
        elif self.my_turn():
            text = "Du bist am Zug"
        else:
            text = "Gegner ist am Zug ..."
        cached = self.status_cache.get(text)
        if cached is None:
            cached = self.assets.fonts["ui_bold"].render(
                text, True, self.assets.style["label_rgb"]
            )
            self.status_cache[text] = cached
        return cached

    def render(self, surf):
        anim = self.anims[0] if self.anims else None
        if self.held is not None:
            skip = self.held
        elif anim is not None:
            skip = anim.card
        else:
            skip = None
        krips = max(0.0, (self.krips_until - pygame.time.get_ticks()) / 1100.0)
        draw_board(
            surf,
            self.assets,
            self.view,
            skip,
            self.held,
            self.held_pos,
            anim,
            krips,
            self.highlight,
            self.status(),
            self.help_surface,
        )

    def run(self):
        pygame.init()
        screen = pygame.display.get_surface()
        if screen is None:
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
        pygame.display.set_caption("Krips")
        clock = pygame.time.Clock()
        surf = pygame.Surface((WIDTH, HEIGHT))
        running = True
        while running:
            dt = clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.human_krips()
                    elif event.key == pygame.K_r:
                        self.flip_waste()
                    elif event.key in (pygame.K_F1, pygame.K_F2, pygame.K_F3):
                        self.set_style(
                            {pygame.K_F1: "F1", pygame.K_F2: "F2", pygame.K_F3: "F3"}[event.key]
                        )
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.press(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.motion(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.release(event.pos)
            self.update(dt)
            self.render(surf)
            screen.blit(surf, (0, 0))
            pygame.display.flip()
        pygame.quit()


def run_screenshots(human, seed, bot_seed, moves):
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT))
    out = pygame.Surface((WIDTH, HEIGHT))
    paths = []

    def make_app():
        return KripsUI(build_game(seed, bot_seed, moves), human, DEFAULT_STYLE, bot_seed)

    def first_move(app, allow_flip=False):
        for move in app.legal_moves():
            if allow_flip or not is_plain_flip(move):
                return move
        return None

    app = make_app()
    app.render(out)
    paths.append(save(out, "ui_01_board"))

    flight = first_move(app)
    if app.my_turn() and flight is not None:
        source = source_location(flight)
        app.pick(source, source_position(app.view, source))
        app.update(200)
        app.render(out)
        paths.append(save(out, "ui_02_selected"))

        app.clear_held()
        app.apply_move(flight, source, human)
        app.anims[0].t = app.anims[0].duration * 0.45
        app.render(out)
        paths.append(save(out, "ui_03_flight"))

    reject_app = make_app()
    reject_move = first_move(reject_app)
    if reject_app.my_turn() and reject_move is not None:
        source = source_location(reject_move)
        reject_app.pick(source, source_position(reject_app.view, source))
        reject_app.update(200)
        reject_app.reject(("foundation", 3))
        reject_app.anims[0].t = reject_app.anims[0].duration * 0.5
        reject_app.render(out)
        paths.append(save(out, "ui_04_reject"))

    krips_app = make_app()
    krips_app.krips_until = pygame.time.get_ticks() + 5000
    krips_app.render(out)
    paths.append(save(out, "ui_05_krips"))
    pygame.quit()
    return paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", default=DEFAULT_STYLE, choices=list(STYLES))
    parser.add_argument("--player", type=int, default=1, choices=(1, 2))
    parser.add_argument("--seed", type=int, default=170)
    parser.add_argument("--bot-seed", type=int, default=5170)
    parser.add_argument("--moves", type=int, default=0)
    parser.add_argument("--screenshots", action="store_true")
    args = parser.parse_args()

    if args.screenshots:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.makedirs(SHOTS, exist_ok=True)
        for path in run_screenshots(args.player, args.seed, args.bot_seed, 118):
            print(path)
        return
    KripsUI(build_game(args.seed, args.bot_seed, args.moves), args.player, args.style, args.bot_seed).run()


if __name__ == "__main__":
    main()
