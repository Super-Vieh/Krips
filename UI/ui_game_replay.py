import argparse
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

from board_renderer import (
    DEFAULT_STYLE,
    HEIGHT,
    SHOTS,
    STYLES,
    TURN_COLORS,
    WIDTH,
    Anim,
    Assets,
    save,
    top_card_pos,
)
from krips_ui import (
    PILE_NAMES,
    View,
    deck_pos,
    draw_board,
    is_plain_flip,
    move_text,
    side_for,
    target_position,
)
from Gymnasium.leaky_rule_based_bot import LeakyRuleBasedBot
from Klassen.game_factory import GameFactory
from Klassen.move import DestinationType, Move, OriginType

REPLAY_HELP = (
    "Links/Rechts Zug     Enter weiter     A Auto     M Info     Leiste klicken     Esc Ende"
)
START_HELP = "Enter Replay starten     Esc Beenden"
END_HELP = "Enter von vorn     Links zurueck     Esc Ende"
DROP_MS = 260
END_MS = 600
SLIDER_TRACK = pygame.Rect(80, 1145, WIDTH - 160, 6)
SLIDER_HIT = pygame.Rect(60, 1136, WIDTH - 120, 24)
INFO_BUTTON = pygame.Rect(WIDTH - 122, 66, 108, 32)
INFO_PANEL = pygame.Rect(WIDTH - 360, 104, 340, 286)


def is_off_turn(move):
    return move.origin_type == OriginType.KRIPS or move.destination_type == DestinationType.KRIPS


def is_krips_call(move):
    return is_off_turn(move) and move.origin_value == 1


def normalize_moves(moves):
    if len(moves) == 1 and isinstance(moves[0], (list, tuple)):
        return list(moves[0])
    return list(moves)


def make_game(seed):
    for offset in range(1000):
        game = GameFactory().set_up_game(seed + offset)
        if game.current_player is not None:
            return game, seed + offset
    raise RuntimeError("kein gueltiger Startspieler gefunden")


def record_game(seed, bot_seed, limit=80, call_krips=True):
    game, actual_seed = make_game(seed)
    bots = {1: LeakyRuleBasedBot(bot_seed), 2: LeakyRuleBasedBot(bot_seed + 7)}
    moves = []
    while game.is_running and len(moves) < limit and game.current_player is not None:
        actor = game.current_player.player_number
        move = bots[actor].act(game)
        moves.append(move)
        game.play_move(move)
        if game.is_running and game.is_krips and call_krips:
            call = Move(OriginType.KRIPS, 1, DestinationType.KRIPS, 1)
            if call in game.rules.get_legal_moves_when_not_playing():
                moves.append(call)
                game.play_move_off_turn(call)
    return moves, actual_seed


def move_actor(game, move):
    if game.current_player is None:
        return None
    if is_off_turn(move):
        return game.current_player.opponent.player_number
    return game.current_player.player_number


def status_text(actor, move, index, total):
    if is_krips_call(move):
        body = "Krips gerufen"
    elif is_off_turn(move):
        body = "Nichts"
    else:
        body = move_text(move)
    return f"{index}/{total}   Spieler {actor}   {body}"


def apply_move(game, view, move):
    if is_off_turn(move):
        game.play_move_off_turn(move)
        view.refresh()
        return None
    actor = game.current_player.player_number
    card = None
    origin = None
    if move.origin_type == OriginType.PLAYER:
        player = game.player1 if actor == 1 else game.player2
        pile = player.player_piles[move.origin_value]
        if pile:
            card = view.demo(pile[-1], actor)
            origin = deck_pos(side_for(actor, view.human), PILE_NAMES[move.origin_value])
    else:
        pile = game.board.tableau[move.origin_value]
        if pile:
            card = view.demo(pile[-1], 1 if move.origin_value < 4 else 2)
            origin = top_card_pos(view, move.origin_value)
    game.play_move(move)
    view.refresh()
    if card is None or origin is None:
        return None
    if is_plain_flip(move):
        return Anim("flip", 260, origin, origin, card)
    return Anim("drop", DROP_MS, origin, target_position(view, move, actor, view.human), card, 26)


def apply_quiet(game, move):
    if is_off_turn(move):
        game.play_move_off_turn(move)
    else:
        game.play_move(move)


def make_state(game, moves, seed, style_id, start_game=None):
    moves = normalize_moves(moves)
    if start_game is None and seed is not None:
        start_game, _ = make_game(seed)
    start = copy.deepcopy(start_game if start_game is not None else game)
    working = copy.deepcopy(start)
    total = len(moves)
    return {
        "start_game": start,
        "game": working,
        "view": View(working, 1),
        "moves": list(moves),
        "total": total,
        "seed": seed,
        "index": 0,
        "anim": None,
        "screen": "start",
        "auto": False,
        "last_auto": 0,
        "krips_until": 0,
        "krips_override": None,
        "info_open": False,
        "slider_drag": False,
        "pending_steps": 0,
        "end_due": 0,
        "status_text": f"0/{total}   Anfangszustand",
        "status_cache": {},
        "text_cache": {},
        "states": {0: copy.deepcopy(start)},
        "actors": {0: None},
        "style": style_id,
    }


def seek(st, target):
    target = max(0, min(st["total"], target))
    base = max(index for index in st["states"] if index <= target)
    game = copy.deepcopy(st["states"][base])
    actor = st["actors"].get(base)
    for position in range(base, target):
        move = st["moves"][position]
        if position == target - 1:
            actor = move_actor(game, move)
        apply_quiet(game, move)
    st["states"][target] = copy.deepcopy(game)
    st["actors"][target] = actor
    st["game"] = game
    st["view"] = View(game, 1)
    st["index"] = target
    st["anim"] = None
    st["krips_until"] = 0
    st["krips_override"] = None
    st["end_due"] = 0
    st["auto"] = False
    st["pending_steps"] = 0
    if target == 0:
        st["status_text"] = f"0/{st['total']}   Anfangszustand"
    else:
        st["status_text"] = status_text(actor, st["moves"][target - 1], target, st["total"])


def step_forward(st, now):
    if st["index"] >= st["total"]:
        st["screen"] = "end"
        st["end_due"] = 0
        st["auto"] = False
        st["pending_steps"] = 0
        return
    move = st["moves"][st["index"]]
    actor = move_actor(st["game"], move)
    st["anim"] = apply_move(st["game"], st["view"], move)
    st["index"] += 1
    st["actors"][st["index"]] = actor
    st["states"][st["index"]] = copy.deepcopy(st["game"])
    if is_krips_call(move):
        st["krips_until"] = now + 1100
    st["status_text"] = status_text(actor, move, st["index"], st["total"])
    st["last_auto"] = now
    st["end_due"] = now + END_MS if st["index"] >= st["total"] else 0


def result_text(st):
    game = st["game"]
    if game.player1.won:
        return "Spieler 1 gewinnt"
    if game.player2.won:
        return "Spieler 2 gewinnt"
    if not game.is_running:
        return "Patz"
    return "Ende der Aufzeichnung"


def compact_move(move):
    if move.origin_type == OriginType.PLAYER:
        source = ("Stock", "Haufen", "Dreizehner")[move.origin_value]
    else:
        source = f"T{move.origin_value + 1}"
    if move.destination_type == DestinationType.PLAYER:
        target = ("Stock", "Haufen", "Dreizehner")[move.destination_value]
    elif move.destination_type == DestinationType.TABLEAU:
        target = f"T{move.destination_value + 1}"
    elif move.destination_type == DestinationType.FOUNDATION:
        target = f"F{move.destination_value + 1}"
    else:
        target = "Gegner"
    return f"{source} -> {target}"


def last_move_text(st):
    if st["index"] == 0:
        return "-"
    move = st["moves"][st["index"] - 1]
    if is_krips_call(move):
        return "Krips gerufen"
    if is_off_turn(move):
        return "Nichts"
    return compact_move(move)


def text_surface(assets, st, text, font="help", key="text"):
    cache_key = (font, key, text)
    surface = st["text_cache"].get(cache_key)
    if surface is None:
        surface = assets.fonts[font].render(text, True, assets.style["label_rgb"])
        st["text_cache"][cache_key] = surface
    return surface


def status_surface(assets, st):
    text = st["status_text"]
    surface = st["status_cache"].get(text)
    if surface is None:
        surface = assets.fonts["ui_bold"].render(text, True, assets.style["label_rgb"])
        st["status_cache"][text] = surface
    return surface


def translucent_panel(surf, rect, rgb, alpha=210, radius=18):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (*rgb, alpha), panel.get_rect(), border_radius=radius)
    surf.blit(panel, rect.topleft)


def make_shade(alpha=150):
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((6, 4, 3, alpha))
    return shade


def draw_slider(surf, assets, st):
    track = SLIDER_TRACK
    pygame.draw.rect(surf, assets.style["slot_rgb"], track, border_radius=3)
    color = TURN_COLORS.get(st["view"].turn, (220, 216, 206))
    if st["total"] > 0:
        x = track.x + int(track.width * st["index"] / st["total"])
        if x > track.x:
            pygame.draw.rect(surf, color, (track.x, track.y, x - track.x, track.height), border_radius=3)
        pygame.draw.circle(surf, (250, 247, 240), (x, track.centery), 8)
        pygame.draw.circle(surf, color, (x, track.centery), 5)


def draw_info(surf, assets, st):
    label = text_surface(assets, st, "Info", "ui", "info_button")
    translucent_panel(surf, INFO_BUTTON, assets.style["panel_rgb"], 200, 16)
    surf.blit(label, (INFO_BUTTON.centerx - label.get_width() // 2, INFO_BUTTON.y + 6))
    if not st["info_open"]:
        return
    translucent_panel(surf, INFO_PANEL, assets.style["panel_rgb"], 214, 20)
    title = text_surface(assets, st, "Spielinfo", "ui_bold", "info_title")
    surf.blit(title, (INFO_PANEL.x + 18, INFO_PANEL.y + 12))
    turn = st["view"].turn
    game = st["game"]
    rows = [
        ("Spiel", "Krips"),
        ("Seed", str(st["seed"]) if st["seed"] is not None else "-"),
        ("Zug", f"{st['index']}/{st['total']}"),
        ("Am Zug", f"Spieler {turn} ({'Rot' if turn == 1 else 'Blau'})"),
        ("Letzter Zug", last_move_text(st)),
        ("Status", result_text(st) if not game.is_running else "Spiel laeuft"),
    ]
    if game.is_krips:
        rows.append(("Krips", "ausstehend"))
    y = INFO_PANEL.y + 50
    for name, value in rows:
        surf.blit(text_surface(assets, st, name, "ui_bold", "info"), (INFO_PANEL.x + 18, y))
        surf.blit(text_surface(assets, st, value, "help", "info"), (INFO_PANEL.x + 144, y + 3))
        y += 30


def draw_start(surf, assets, st, shade, help_surface):
    surf.blit(shade, (0, 0))
    panel = pygame.Rect(0, 0, 600, 340)
    panel.center = (WIDTH // 2, HEIGHT // 2)
    translucent_panel(surf, panel, assets.style["panel_rgb"], 228, 24)
    title = text_surface(assets, st, "Krips - Replay", "toast", "start")
    surf.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 30))
    rows = [
        f"Seed: {st['seed'] if st['seed'] is not None else '-'}",
        f"Zuege: {st['total']}",
        "",
        "Enter        Replay starten",
        "Links/Rechts Zug fuer Zug",
        "Klick auf die Leiste springt direkt",
        "Esc          Beenden",
    ]
    y = panel.y + 100
    for row in rows:
        if row:
            image = text_surface(assets, st, row, "ui", "start")
            surf.blit(image, (panel.centerx - image.get_width() // 2, y))
        y += 32


def draw_end(surf, assets, st, shade, help_surface):
    surf.blit(shade, (0, 0))
    panel = pygame.Rect(0, 0, 600, 320)
    panel.center = (WIDTH // 2, HEIGHT // 2)
    translucent_panel(surf, panel, assets.style["panel_rgb"], 228, 24)
    title = text_surface(assets, st, result_text(st), "toast", "end")
    surf.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 30))
    rows = [
        f"Zuege: {st['index']}/{st['total']}",
        f"Seed: {st['seed'] if st['seed'] is not None else '-'}",
        "",
        "Enter   von vorn",
        "Links   zurueck zum Brett",
        "Esc     Ende",
    ]
    y = panel.y + 110
    for row in rows:
        if row:
            image = text_surface(assets, st, row, "ui", "end")
            surf.blit(image, (panel.centerx - image.get_width() // 2, y))
        y += 32


def draw_scene(surf, assets, st, help_surface, shade, now):
    anim = st["anim"]
    if st["krips_override"] is not None:
        krips = st["krips_override"]
    else:
        krips = max(0.0, (st["krips_until"] - now) / 1100.0)
    draw_board(
        surf,
        assets,
        st["view"],
        anim.card if anim is not None else None,
        None,
        None,
        anim,
        krips,
        (),
        status_surface(assets, st),
        help_surface,
        turn_hint=True,
    )
    if st["screen"] == "replay":
        draw_slider(surf, assets, st)
        draw_info(surf, assets, st)
    elif st["screen"] == "start":
        draw_start(surf, assets, st, shade, help_surface)
    else:
        draw_end(surf, assets, st, shade, help_surface)


def seek_from_x(st, x):
    if st["total"] <= 0:
        return
    ratio = (x - SLIDER_TRACK.x) / SLIDER_TRACK.width
    ratio = max(0.0, min(1.0, ratio))
    seek(st, round(ratio * st["total"]))


def play_replay(game, moves, *, seed=None, auto=False, ms_per_action=900, style_id=DEFAULT_STYLE, start_game=None):
    pygame.init()
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
    pygame.display.set_caption("Krips - Replay")
    assets = Assets(style_id)
    assets.warm()
    help_surface = assets.fonts["help"].render(REPLAY_HELP, True, assets.style["label_rgb"])
    st = make_state(game, moves, seed, style_id, start_game=start_game)
    st["auto"] = auto
    st["last_auto"] = pygame.time.get_ticks()
    surf = pygame.Surface((WIDTH, HEIGHT))
    shade = make_shade()
    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60)
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif st["screen"] == "start":
                    if event.key in (
                        pygame.K_RETURN,
                        pygame.K_KP_ENTER,
                        pygame.K_SPACE,
                        pygame.K_RIGHT,
                    ):
                        st["screen"] = "replay"
                        st["last_auto"] = now
                elif st["screen"] == "end":
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        seek(st, 0)
                        st["screen"] = "replay"
                    elif event.key == pygame.K_LEFT:
                        st["screen"] = "replay"
                else:
                    if event.key == pygame.K_LEFT:
                        seek(st, st["index"] - 1)
                    elif event.key == pygame.K_RIGHT:
                        if st["anim"] is None:
                            step_forward(st, now)
                        else:
                            st["pending_steps"] += 1
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        if st["anim"] is None:
                            step_forward(st, now)
                        else:
                            st["pending_steps"] += 1
                    elif event.key == pygame.K_a:
                        st["auto"] = not st["auto"]
                        st["last_auto"] = now
                    elif event.key in (pygame.K_m, pygame.K_i):
                        st["info_open"] = not st["info_open"]
                    elif event.key == pygame.K_HOME:
                        seek(st, 0)
                    elif event.key == pygame.K_END:
                        seek(st, st["total"])
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if st["screen"] == "replay":
                    if INFO_BUTTON.collidepoint(event.pos):
                        st["info_open"] = not st["info_open"]
                    elif st["info_open"] and INFO_PANEL.collidepoint(event.pos):
                        pass
                    elif SLIDER_HIT.collidepoint(event.pos):
                        st["slider_drag"] = True
                        seek_from_x(st, event.pos[0])
                    elif st["info_open"]:
                        st["info_open"] = False
            elif event.type == pygame.MOUSEMOTION and st["slider_drag"]:
                if event.buttons[0]:
                    seek_from_x(st, event.pos[0])
                else:
                    st["slider_drag"] = False
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                st["slider_drag"] = False
        if (
            st["screen"] == "replay"
            and st["auto"]
            and st["anim"] is None
            and st["index"] < st["total"]
            and now - st["last_auto"] >= ms_per_action
        ):
            step_forward(st, now)
        if st["anim"] is not None:
            st["anim"].advance(dt)
            if st["anim"].finished:
                st["anim"] = None
        if (
            st["screen"] == "replay"
            and st["anim"] is None
            and st["pending_steps"]
        ):
            st["pending_steps"] -= 1
            step_forward(st, now)
        if (
            st["screen"] == "replay"
            and st["end_due"]
            and st["anim"] is None
            and now >= st["end_due"]
        ):
            st["screen"] = "end"
            st["end_due"] = 0
            st["auto"] = False
        draw_scene(surf, assets, st, help_surface, shade, now)
        screen.blit(surf, (0, 0))
        pygame.display.flip()
    pygame.quit()


def run_screenshots(seed, bot_seed, limit, style_id=DEFAULT_STYLE):
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT))
    moves, actual_seed = record_game(seed, bot_seed, max(limit, 400))
    game, _ = make_game(actual_seed)
    assets = Assets(style_id)
    assets.warm()
    help_surface = assets.fonts["help"].render(REPLAY_HELP, True, assets.style["label_rgb"])
    st = make_state(game, moves, actual_seed, style_id)
    st["auto"] = False
    shade = make_shade()
    surf = pygame.Surface((WIDTH, HEIGHT))
    now = pygame.time.get_ticks()
    paths = []

    st["screen"] = "start"
    draw_scene(surf, assets, st, help_surface, shade, now)
    paths.append(save(surf, "replay_01_start"))

    st["screen"] = "replay"
    seek(st, max(1, st["total"] // 2))
    draw_scene(surf, assets, st, help_surface, shade, now)
    paths.append(save(surf, "replay_02_board"))

    flight_at = max(1, st["total"] // 2)
    for position in range(flight_at - 1, st["total"]):
        seek(st, position)
        step_forward(st, now)
        if st["anim"] is not None:
            st["anim"].t = st["anim"].duration * 0.45
            st["screen"] = "replay"
            draw_scene(surf, assets, st, help_surface, shade, now)
            paths.append(save(surf, "replay_03_flight"))
            break

    seek(st, max(1, st["total"] // 2))
    st["info_open"] = True
    st["screen"] = "replay"
    draw_scene(surf, assets, st, help_surface, shade, now)
    paths.append(save(surf, "replay_04_info"))

    seek(st, st["total"])
    st["screen"] = "end"
    draw_scene(surf, assets, st, help_surface, shade, now)
    paths.append(save(surf, "replay_05_end"))

    for position, move in enumerate(st["moves"]):
        if is_krips_call(move):
            seek(st, position + 1)
            st["screen"] = "replay"
            st["info_open"] = False
            st["krips_override"] = 1.0
            draw_scene(surf, assets, st, help_surface, shade, now)
            paths.append(save(surf, "replay_06_krips"))
            break
    pygame.quit()
    return paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", default=DEFAULT_STYLE, choices=list(STYLES))
    parser.add_argument("--seed", type=int, default=170)
    parser.add_argument("--bot-seed", type=int, default=5170)
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--auto", action="store_true")
    parser.add_argument("--ms", type=int, default=900)
    parser.add_argument("--screenshots", action="store_true")
    args = parser.parse_args()

    if args.screenshots:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.makedirs(SHOTS, exist_ok=True)
        for path in run_screenshots(args.seed, args.bot_seed, args.limit, args.style):
            print(path)
        return
    moves, actual_seed = record_game(args.seed, args.bot_seed, args.limit)
    game, _ = make_game(actual_seed)
    play_replay(
        game,
        moves,
        seed=actual_seed,
        auto=args.auto,
        ms_per_action=args.ms,
        style_id=args.style,
    )


if __name__ == "__main__":
    main()
