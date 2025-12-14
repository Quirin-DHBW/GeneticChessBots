"""
What we will need:
- Some way to initialize N bots with randomized DNA
- Using the play game code to yeet them at each other (if it's optimized enough perhaps we can have each bot compete multiple times in a generation)
- Fitness definition! :D (Likely just wins, losses, and draws)
- PURGE THE WEAK
- To quote a meme: "And then they fucked" -> Empty population slots are refilled with children, children inherit 50% of their weights from each parent
- And sometimes there is MUTATION
"""

################
## IMPORTS #####
################

import random as rng
from play_a_game import play_game


####################
## DEFINITIONS #####
####################

# This is what the Bot DNA looks like
# They are all floats between -100 and 100
weights={
        "friendly_pawn_count": 1,
        "friendly_knight_count": 1,
        "friendly_bishop_count": 1,
        "friendly_rook_count": 1,
        "friendly_queen_count": 1,
        "friendly_king_count": 1,
        "enemy_pawn_count": 1,
        "enemy_knight_count": 1,
        "enemy_bishop_count": 1,
        "enemy_rook_count": 1,
        "enemy_queen_count": 1,
        "enemy_king_count": 1,
        "we_have_more": 1,
        "friendly_protected_pieces": 1,
        "friendly_in_check": 1,
        "enemy_in_check": 1,
        "friendly_in_checkmate": 1,
        "enemy_in_checkmate": 1,
        "enemy_proximity_to_friendly_king": 1,
        "friendly_proximity_to_enemy_king": 1,
        "friendly_center_control": 1,
        "enemy_center_control": 1,
        "friendly_threatening_unprotected": 1,
        "enemy_threatening_unprotected": 1,
        "friendly_pawn_promotion_distance": 1,
        "enemy_pawn_promotion_distance": 1,
        "can_castle": 1,
        "can_en_passant": 1,
        "num_legal_moves": 1
    }


# :)
def how_is_baby_made(parent_1, parent_2, mutation_chance=0.01, mutation_min=-10, mutation_max=10):
    """
    We grab half of the weights from one parent (at random) and the remaining half from the other! :D
    Then we roll mutation for each weight :)
    """
    child = {}

    # Grab random keys :D
    parent_1_contribution = rng.sample(list(parent_1.keys()), k=len(parent_1)//2)
    # And now the rest from the other parent
    parent_2_contribution = [key for key in parent_2.keys() if key not in parent_1_contribution]

    # CONSTRUCT THE CHILD
    for key in parent_1_contribution:
        child[key] = parent_1[key]
    for key in parent_2_contribution:
        child[key] = parent_2[key]
    
    # And now we expose them to Uranium because it's funny and ethical :3
    for key in child.keys():
        if rng.random() < mutation_chance:
            child[key] += rng.uniform(mutation_min, mutation_max)
            # Clamp to -100, 100
            child[key] = max(-100, min(100, child[key]))

    return child


##############################
## THE GENETIC ALGORITHM #####
##############################

seed = 47 # Seed so we can repeat runs consistently, number suggested by a friend on discord
rng.seed(seed)

# Lets get bots first uwu
bots = []

n_pops = 200 # MUST BE EVEN
n_purged = n_pops // 2 # Acts as more of a "minimum amount purged"
mut_chance = 0.01
mut_min = -10
mut_max = 10

depth = 1
generations = 100
n_fights = 2

# Create history csv with header if it doesn't exist yet, we're using semicolon separation
with open(f"history.csv", "w") as f:
    f.write("Generation;Bot Index;Bot Identifier;Score;Fitness;Overall Ranking;Weights\n")

# We now initialize the population of chess bots
# But we store them as dicts so we can keep track of their scores
# (might be a hassle to reset said scores later, but that is a problem for future quirin)
for _ in range(n_pops):
    bot = {
        "score": {"win":0, "loss":0, "draw":0},
        "weights": {key: rng.uniform(-100, 100) for key in weights.keys()},
        "fitness": 0,
        "ranking": 0, # In case one bot manages to survive multiple generations, we can see it's overall performance uwu
        "ident": rng.randint(0, 1_000_000)
    }
    bots.append(bot)

for gen in range(generations):
    print(f"Generation {gen + 1} / {generations}")

    # To ensure each bot fights a set amount of times, we will fold the list, ensuring each bot only fights once per matchup
    bot_indexes = list(range(len(bots)))
    generation_white_indexes = bot_indexes[::2]
    generation_black_indexes = bot_indexes[1::2]
    folded_population_index = list(zip(generation_white_indexes, generation_black_indexes))
    
    print("Murder is afoot...")
    for fight in range(n_fights):
        rng.shuffle(bots)
        
        for b_1_ind, b_2_ind in folded_population_index:
            result = play_game(bots[b_1_ind]["weights"], bots[b_2_ind]["weights"], search_depth=depth)[0]
            if result == 0:
                bots[b_1_ind]["score"]["win"] += 1
                bots[b_2_ind]["score"]["loss"] += 1
            elif result == 1:
                bots[b_1_ind]["score"]["loss"] += 1
                bots[b_2_ind]["score"]["win"] += 1
                
            else:
                bots[b_1_ind]["score"]["draw"] += 1
                bots[b_2_ind]["score"]["draw"] += 1
    
    # Fitness score time! :D
    for bot in bots:
        fitness = (bot["score"]["win"] * 2) + (bot["score"]["loss"] * -1) + bot["score"]["draw"]
        bot["fitness"] = fitness
        bot["ranking"] += fitness
    
    # Time to cull the population
    bots.sort(key=lambda x: x["fitness"], reverse=True)
    # We could purge all with negative fitness, and then randomly select the remaining bots to be purged :)
    survivors_purge_1 = []
    for bot in bots:
        if bot["fitness"] >= 0:
            survivors_purge_1.append(bot)
    
    # And now the remainder
    if len(survivors_purge_1) > (n_pops - n_purged):
        survivors_purge_2 = rng.sample(survivors_purge_1, k=(n_pops - n_purged))
    
    
    print("The survivors keep living...")
    # Nature is healing (aka time to reproduce UwU)
    bots = survivors_purge_2
    while len(bots) < n_pops:
        parent_1, parent_2 = rng.sample(bots, k=2)
        child_weights = how_is_baby_made(parent_1["weights"], parent_2["weights"], mutation_chance=mut_chance, mutation_min=mut_min, mutation_max=mut_max)
        child_bot = {
            "score": {"win":0, "loss":0, "draw":0},
            "weights": child_weights,
            "fitness": 0,
            "ranking": 0,
            "ident": rng.randint(0, 1_000_000)
        }
        bots.append(child_bot)
    
    assert len(bots) == n_pops

    with open(f"history.csv", "a") as f:
        for index, bot in enumerate(bots):
            f.write(f"{gen + 1};{index};{bot['ident']};{bot['score']};{bot['fitness']};{bot['ranking']};{bot['weights']}\n")
    
    # Now that the generation is over, reset all scores for the next generation
    for bot in bots:
        bot["fitness"] = 0
        bot["score"] = {"win":0, "loss":0, "draw":0}
