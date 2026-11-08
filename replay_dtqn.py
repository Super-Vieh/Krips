import argparse
import os
from collections import deque

import numpy as np
import pygame
import torch as T

from Gymnasium.leaky_rule_based_bot import LeakyRuleBasedBot
from Gymnasium.observation import encode_game
from Gymnasium.random_bot import RandomBot
from Klassen.gameorchestor import GameOrchestor
from Klassen.move import DestinationType, OriginType
from Neuralnetwork_Batch import DTQNAgent, DTQNNetwork, SequenceStorage

CARD_W: int = 75
CARD_H: int = 108
WINDOW: tuple[int, int] = (1540, 860)
BACKGROUND: tuple[int, int, int] = (30, 31, 34)
TEXT: tuple[int, int, int] = (225, 225, 230)
MUTED: tuple[int, int, int] = (150, 152, 160)

SUIT_FILES: dict[str, str] = {
    "Pik": "spades",
    "Coeur": "hearts",
    "Treff": "clubs",
    "Karro": "diamonds",
}
RANK_FILES: dict[int, str] = {1: "ace", 11: "jack", 12: "queen", 13: "king"}


def card_file(rank: int, suit: str) -> str:
    name = RANK_FILES.get(rank, str(rank))
    suffix = "2" if rank in (11, 12, 13) else ""
    return f"Bilder/{name}_of_{suit}{suffix}.png"


def load_images() -> tuple[dict, pygame.Surface]:
    cache: dict = {}
    for suit in SUIT_FILES.values():
        for rank in range(1, 14):
            path = card_file(rank, suit)
            if os.path.exists(path):
                image = pygame.image.load(path)
                cache[(suit, rank)] = pygame.transform.smoothscale(
                    image, (CARD_W, CARD_H)
                )
    back = pygame.image.load("Bilder/Placeholder.png")
    return cache, pygame.transform.smoothscale(back, (CARD_W, CARD_H))


def origin_label(move) -> str:
    if move.origin_type == OriginType.KRIPS:
        return "K"
    if move.origin_type == OriginType.TABLEAU:
        return f"S{move.origin_value + 1}"
    return f"A{move.origin_value}"


def destination_label(move) -> str:
    if move.destination_type == DestinationType.KRIPS:
        return "K"
    if move.destination_type == DestinationType.TABLEAU:
        return f"S{move.destination_value + 1}"
    if move.destination_type == DestinationType.FOUNDATION:
        return f"M{move.destination_value + 1}"
    if move.destination_type == DestinationType.PLAYER:
        return f"A{move.destination_value}"
    return "G0"


def move_label(move) -> str:
    return f"{origin_label(move)}->{destination_label(move)}"


class AgentPlayer:
    def __init__(self, agent: DTQNAgent) -> None:
        self.agent = agent
        self.history: deque = deque(maxlen=agent.nn.sequence_length)

    def act(self, game):
        state = np.array(encode_game(game), copy=True)
        self.history.append(state)
        stacked = np.stack(self.history)
        length = self.agent.nn.sequence_length
        if stacked.shape[0] < length:
            padding = np.repeat(stacked[:1], length - stacked.shape[0], axis=0)
            stacked = np.concatenate([padding, stacked], axis=0)
        window = T.from_numpy(stacked[None].astype(np.float32))
        masks = T.from_numpy(self.agent.legal_mask(game)[None])
        index = self.agent.select_action(0.0, window, masks)[0]
        return self.agent.index_to_move(index)


def record_game(agent_player: AgentPlayer, opponent, seed: int, max_moves: int = 8000):
    game = None
    used_seed = seed
    for attempt in range(500):
        candidate = GameOrchestor(seed + attempt).set_up_game()
        if candidate.current_player is not None:
            game = candidate
            used_seed = seed + attempt
            break
    if game is None:
        raise RuntimeError("Kein spielbares Startdeck gefunden.")
    agent_player.history.clear()

    moves: list[tuple[bool, int, object]] = []
    while game.is_running and len(moves) < max_moves:
        mover = game.current_player.player_number
        move = agent_player.act(game) if mover == 1 else opponent.act(game)
        game.play_move(move)
        moves.append((False, mover, move))
        if game.is_running and game.is_krips:
            responder = 2 if mover == 1 else 1
            response = (
                agent_player.agent.act_off_turn(game)
                if responder == 1
                else opponent.act_off_turn(game)
            )
            game.play_move_off_turn(response)
            moves.append((True, responder, response))
    return used_seed, moves


class Replay:
    def __init__(self, seed: int, moves: list) -> None:
        self.seed = seed
        self.moves = moves
        self.step = 0
        self.game = None
        self.rebuild()

    def rebuild(self) -> None:
        game = GameOrchestor(self.seed).set_up_game()
        for off_turn, _, move in self.moves[: self.step]:
            if off_turn:
                game.play_move_off_turn(move)
            else:
                game.play_move(move)
        self.game = game

    def go_to(self, step: int) -> None:
        step = max(0, min(step, len(self.moves)))
        if step < self.step:
            self.step = step
            self.rebuild()
            return
        game = self.game
        while self.step < step:
            off_turn, _, move = self.moves[self.step]
            if off_turn:
                game.play_move_off_turn(move)
            else:
                game.play_move(move)
            self.step += 1


BADGE_FONT = None


def draw_pile(surface, pile, x, y, images, back, fan=0, top_only=False) -> None:
    global BADGE_FONT
    if BADGE_FONT is None:
        BADGE_FONT = pygame.font.SysFont("dejavusans", 16, bold=True)
    if not pile:
        pygame.draw.rect(surface, (55, 57, 62), (x, y, CARD_W, CARD_H), 2, 8)
        return
    cards = pile[-1:] if top_only else pile
    offset = 0
    if fan and len(cards) > 1:
        offset = min(fan, max(10, 210 // (len(cards) - 1)))
    for position, card in enumerate(cards):
        card_x = x + position * offset
        if card.is_face_up:
            image = images.get((SUIT_FILES[card.card_type.name], card.card_rank.value))
        else:
            image = None
        if image is None:
            surface.blit(back, (card_x, y))
        else:
            surface.blit(image, (card_x, y))
    if len(pile) > len(cards):
        pygame.draw.circle(surface, (230, 230, 235), (x + CARD_W // 2, y + CARD_H // 2), 14)
        count = BADGE_FONT.render(str(len(pile)), True, (40, 40, 45))
        surface.blit(count, count.get_rect(center=(x + CARD_W // 2, y + CARD_H // 2)))


def draw_board(surface, game, images, back, fonts) -> None:
    surface.fill(BACKGROUND)
    small, medium, large = fonts

    for index, pile in enumerate(game.board.foundations):
        x = 350 + index * 100
        draw_pile(surface, pile, x, 175, images, back, top_only=True)

    for index, pile in enumerate(game.board.tableau):
        x = 60 + (index % 4) * 380
        y = 330 if index < 4 else 520
        draw_pile(surface, pile, x, y, images, back, fan=26)

    for player, y, base_x, title in (
        (game.player2, 20, 1240, "Spieler 2 (Bot)"),
        (game.player1, 655, 40, "Spieler 1 (Agent)"),
    ):
        surface.blit(small.render(title, True, MUTED), (base_x, y - 20))
        for offset, pile in enumerate(
            (player.player_stock, player.player_waste, player.player_reserve)
        ):
            draw_pile(
                surface,
                pile,
                base_x + offset * 90,
                y,
                images,
                back,
                top_only=True,
            )


def draw_status(surface, replay: Replay, fonts) -> None:
    small, medium, _ = fonts
    if replay.step == 0:
        description = "Startaufstellung - noch kein Zug"
    else:
        off_turn, mover, move = replay.moves[replay.step - 1]
        who = "Agent" if mover == 1 else "Bot"
        kind = "Krips-Antwort" if off_turn else "Zug"
        description = f"{kind} von Spieler {mover} ({who}): {move_label(move)}"

    status = f"{replay.step} / {len(replay.moves)}   {description}"
    surface.blit(medium.render(status, True, TEXT), (40, 790))
    help_text = (
        "Enter / Pfeil rechts: naechster Zug    Pfeil links: zurueck    "
        "Pos1 / Ende: Anfang / Ende    R: neues Spiel    Esc: beenden"
    )
    surface.blit(small.render(help_text, True, MUTED), (40, 822))


def build_agent(path: str, sequence_length: int) -> DTQNAgent:
    network = DTQNNetwork(1e-3, "DTQNAgent1.txt", sequence_length)
    if os.path.exists(path):
        try:
            network.load_savestate(map_location=network.device)
            print(f"Savestate geladen: {path}")
        except RuntimeError as error:
            print(f"WARNUNG: {path} passt nicht zur aktuellen Beobachtungsgroesse ({error}).")
            print("Es spielt ein untrainiertes Netz - bitte das Training einmal laufen lassen.")
    else:
        print(f"WARNUNG: {path} nicht gefunden - es spielt ein untrainiertes Netz.")
    return DTQNAgent(network, SequenceStorage(1, sequence_length), player_number=1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Zeigt eine Partie des DTQN-Agenten Zug fuer Zug.")
    parser.add_argument("--opponent", choices=["leaky", "random"], default="leaky")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--sequence-length", type=int, default=8)
    parser.add_argument("--savestate", default=os.path.join("Savestates", "DTQNAgent1.txt"))
    args = parser.parse_args()

    agent = build_agent(args.savestate, args.sequence_length)
    player = AgentPlayer(agent)
    opponent = LeakyRuleBasedBot(0) if args.opponent == "leaky" else RandomBot(0)

    pygame.init()
    surface = pygame.display.set_mode(WINDOW)
    pygame.display.set_caption("Krips - DTQN Replay")
    images, back = load_images()
    fonts = (
        pygame.font.SysFont("dejavusans", 16),
        pygame.font.SysFont("dejavusans", 20),
        pygame.font.SysFont("dejavusans", 26),
    )

    seed, moves = record_game(player, opponent, args.seed)
    replay = Replay(seed, moves)
    print(f"Partie mit Seed {seed} aufgezeichnet: {len(moves)} Zuege.")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RIGHT, pygame.K_RETURN, pygame.K_SPACE, pygame.K_DOWN):
                    replay.go_to(replay.step + 1)
                elif event.key in (pygame.K_LEFT, pygame.K_UP):
                    replay.go_to(replay.step - 1)
                elif event.key == pygame.K_HOME:
                    replay.go_to(0)
                elif event.key == pygame.K_END:
                    replay.go_to(len(replay.moves))
                elif event.key == pygame.K_r:
                    seed, moves = record_game(player, opponent, seed + 1)
                    replay = Replay(seed, moves)
                    print(f"Neue Partie (Seed {seed}): {len(moves)} Zuege.")
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False

        draw_board(surface, replay.game, images, back, fonts)
        draw_status(surface, replay, fonts)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
