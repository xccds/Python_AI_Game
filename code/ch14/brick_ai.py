import numpy as np
from brick_env import Game
from brick_agent import Agent
from helper import plot

def train():
    plot_scores = []
    plot_mean_scores = []
    record = 0
    total_step = 0
    game = Game()
    agent = Agent(game.nS,game.nA)
    state_new = game.get_state()

    while True:
        state_old = state_new
        final_move = agent.get_action(state_old,agent.n_game)
        reward, done, score = game.play_step(final_move)
        state_new = game.get_state()
        if game.ball_near_bat():
            agent.remember(state_old, final_move, reward, state_new, done)
        agent.train_long_memory(batch_size=256)
        total_step += 1

        if total_step % 10 == 0:
            agent.trainer.copy_model()

        if done:
            game.reset()
            agent.n_game += 1
            if score > record:
                record = score
                agent.trainer.model.save()
            print('Game', agent.n_game, 'Score', score, 'Record:', record)
            plot_scores.append(score)
            mean_scores = np.mean(plot_scores[-10:])
            plot_mean_scores.append(mean_scores)
            #plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    train()