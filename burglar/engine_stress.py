import random

import engine

scores = []

while True:
    e = engine.GameEngine_Easy()
    while not e.game_over:
        if not e.current_bag:
            e.bag()
        e.insert_stone()
        e.where_to_turn(random.choice((1, 2)))
        print('New Round')
        e.new_round()
    scores.append(e.points)
    print('Game Over')
    if len(scores) >= 10000:
        break

print(max(scores))