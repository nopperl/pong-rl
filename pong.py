from net import PolicyNetwork
import numpy as np
import gym


def process_observation(image):
    image = image[34:194]
    image = image[::2, ::2, 0]
    image[image == 144] = 0
    image[image == 92] = 1
    image[image == 213] = 2
    image[image == 236] = 3
    image = image.flatten()
    return image


def expected_return(rewards, gamma):
    r = 0
    for t in range(len(rewards)):
        r += gamma * rewards[t]
    return r


def train(done, reward):
    global current_gradients, observations, rewards, rollouts
    # Bias the policy to take the sampled action -> to take clear actions in general
    dscores = np.full(len(scores), -.5)
    dscores[y] = .5
    current_gradients.append(dscores)
    if done:
        grads = np.array(current_gradients) * reward
        xs = np.array(observations)
        net.backward_pass(xs, grads)
        net.update_parameters(eta, decay ** rollouts)
        current_gradients = []
        observations = []
        rollouts += 1
        if rollouts % 50 == 0:
            net.save()
        env.reset()
        print("Episode", rollouts, "Reward:", reward)
        print(expected_return(rewards, gamma))
        rewards = []


def get_env():
    return gym.make("Pong-v0")


def get_net():
    input_size = 80 * 80
    hidden_sizes = [200, 200]
    out_size = 3
    return PolicyNetwork(input_size, hidden_sizes, out_size)


env = get_env()
net = get_net()
env.reset()
decay = .99
eta = 1e-8
gamma = 0.99
render = False
test = False
rollouts = 0
actions = [0]
observations = []
current_gradients = []
if test:
    net.load()
rewards = []
while True:
    action = actions[-1] + 1
    observation, reward, done, info = env.step(action)
    rewards.append(reward)
    if render or test:
        env.render()
    observation = process_observation(observation)
    observation -= observations[-1] if len(observations) > 0 else 0
    observations.append(observation)
    scores = net.forward_pass(observation)
    y = np.argmax(scores)
    actions.append(y)
    if not test:
        train(done, reward)
