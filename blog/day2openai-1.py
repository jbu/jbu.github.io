# Define the games and the inventory
import requests

url = 'https://adventofcode.com/2023/day/2/input'
response = requests.get(url)
data = response.text

games = {}
for line in open('day2.in').readlines()[:2]:
    if line:
        print('xx', line)
        n, plays = line.split(': ')

        game = [
            [
              # [
              #   [p.split(' ') for p in pull]
                # for pull in attempt.split(',')
                # ] 
              (int(pull.strip().split(' ')[0]), pull.strip().split(' ')[1])
              for pull in attempt.strip().split(',')
            ]
            for attempt in plays.split(';')
        ]
        print(game)
        games[n.split()[1]]=game

# games = {
#     1: [("blue", 3, "red", 4), ("red", 1, "green", 2, "blue", 6), ("green", 2)],
#     2: [("blue", 1, "green", 2), ("green", 3, "blue", 4, "red", 1), ("green", 1, "blue", 1)],
#     3: [("green", 8, "blue", 6, "red", 20), ("blue", 5, "red", 4, "green", 13), ("green", 5, "red", 1)],
#     4: [("green", 1, "red", 3, "blue", 6), ("green", 3, "red", 6), ("green", 3, "blue", 15, "red", 14)],
#     5: [("red", 6, "blue", 1, "green", 3), ("blue", 2, "red", 1, "green", 2)]
# }
# print(games)
inventory = {"red": 12, "green": 13, "blue": 14}

# Function to check if a game is possible with the given inventory
def is_game_possible(reveals, inventory):
    for reveal in reveals:
        # Create a dictionary from the reveal tuples for easier comparison
        reveal_dict = {reveal[i]: reveal[i+1] for i in range(0, len(reveal), 2)}
        # Check if any of the revealed cubes exceed the inventory
        for color in reveal_dict:
            if reveal_dict[color] > inventory.get(color, 0):
                return False
    return True

# Determine which games are possible and sum their IDs
possible_games_sum = sum(game_id for game_id, reveals in games.items() if is_game_possible(reveals, inventory))

print(possible_games_sum)
