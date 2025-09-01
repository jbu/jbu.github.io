def is_game_possible(game_data, red_limit, green_limit, blue_limit):
    for draw in game_data.split(';'):
        cubes = [int(x) for x in draw.split(', ')]
        if any(count > limit for count, limit in zip(cubes, [red_limit, green_limit, blue_limit])):
            return False  # Impossible if any draw exceeds the limit
    return True  # Possible if no draw exceeds the limit

def calculate_possible_game_ids(data):
  total_id = 0
  for line in data.splitlines():
    if line == '':
        continue
    game_id, game_data = line.split(': ')
    if is_game_possible(game_data, 12, 13, 14):  # Check for 12 red, 13 green, 14 blue limit
        total_id += int(game_id)
  return total_id

# Example usage with your sample data
data = """
Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green
"""

result = calculate_possible_game_ids(data)
print(result)  # Should output 8