import argparse
import time

from Gymnasium.leaky_rule_based_bot import LeakyRuleBasedBot
from Gymnasium.random_bot import RandomBot
from Neuralnetwork_Batch import DTQNTrainer

OPPONENTS = {
    "leaky": LeakyRuleBasedBot,
    "random": RandomBot,
}


def build_opponent(name: str, seed: int):
    if name == "none":
        return None
    return OPPONENTS[name](seed)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a DTQN agent for Krips.")
    parser.add_argument("--rounds", type=int, default=20_000)
    parser.add_argument("--n-envs", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--buffer", type=int, default=200_000)
    parser.add_argument("--sequence-length", type=int, default=8)
    parser.add_argument("--updates-per-round", type=int, default=1)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--discount", type=float, default=0.99)
    parser.add_argument("--target-update", type=int, default=1000)
    parser.add_argument("--tau", type=float, default=None)
    parser.add_argument("--epsilon-start", type=float, default=1.0)
    parser.add_argument("--epsilon-end", type=float, default=0.05)
    parser.add_argument("--decay-rounds", type=int, default=None)
    parser.add_argument("--opponent", choices=["leaky", "random", "none"], default="leaky")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--bc-weight", type=float, default=0.0)
    parser.add_argument("--bc-weight-end", type=float, default=None)
    parser.add_argument("--reward-scale", type=float, default=1.0)
    parser.add_argument("--savestate-name", default="DTQNAgent1.txt")
    parser.add_argument("--log-every", type=int, default=200)
    parser.add_argument("--eval-every", type=int, default=0)
    parser.add_argument("--eval-games", type=int, default=200)
    parser.add_argument("--tensorboard", action="store_true")
    args = parser.parse_args()

    trainer = DTQNTrainer(
        batch_size=args.batch_size,
        buffer_capacity=args.buffer,
        n_envs=args.n_envs,
        seed=args.seed,
        sequence_length=args.sequence_length,
        updates_per_round=args.updates_per_round,
        learning_rate=args.learning_rate,
        discount_factor=args.discount,
        target_update_freq=args.target_update,
        tau=args.tau,
        log_to_tensorboard=args.tensorboard,
        reward_scale=args.reward_scale,
        savestate_name=args.savestate_name,
    )

    started = time.time()
    stats = trainer.train(
        rounds=args.rounds,
        epsilon_start=args.epsilon_start,
        epsilon_end=args.epsilon_end,
        decay_rounds=args.decay_rounds,
        opponent=build_opponent(args.opponent, args.seed + 7),
        log_every=args.log_every,
        eval_every=args.eval_every or None,
        eval_games=args.eval_games,
        bc_weight=args.bc_weight,
        bc_weight_end=args.bc_weight_end,
    )
    elapsed = time.time() - started
    print(
        f"training done in {elapsed:.1f}s "
        f"({args.rounds / elapsed:.2f} rounds/s) | "
        f"a1 {stats['wins1']} / a2 {stats['wins2']} / draw {stats['draws']} | "
        f"mean loss {stats['loss']:.4f} | "
        f"legal actions {stats['legal_actions']:.2f}"
    )

    if args.eval_games > 0 and args.opponent != "none":
        try:
            evaluation = trainer.evaluate(
                build_opponent(args.opponent, args.seed + 11),
                games=args.eval_games,
            )
        except RuntimeError as error:
            print(f"evaluation fehlgeschlagen: {error}")
            evaluation = None
        if evaluation is not None:
            print(
                f"evaluation vs {args.opponent}: {evaluation['wins1']}W / "
                f"{evaluation['wins2']}L / {evaluation['draws']}D over "
                f"{evaluation['games']} games -> winrate {evaluation['winrate']:.3f}"
            )


if __name__ == "__main__":
    main()
