import json
import requests
import chess
import chess.pgn

def analyze_with_stockfish_api(fen, depth):
    """
    Sends the FEN and depth to Stockfish API for analysis using a GET request.

    Args:
        fen (str): The FEN string representing the board state.
        depth (int): Depth for Stockfish analysis (must be < 16).

    Returns:
        dict: The response from the Stockfish API or an error message.
    """
    if depth >= 16:
        depth = 15  # Adjust to the max accepted depth

    api_url = "https://stockfish.online/api/s/v2.php"  # Stockfish API endpoint

    params = {
        "fen": fen,
        "depth": depth
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Check for HTTP errors

        if not response.text.strip():
            return {"error": "Empty response from API"}

        try:
            return response.json()
        except ValueError:
            return {"error": "Invalid JSON response"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {e}"}

def process_game_moves_and_analyze(game):
    """
    Process all moves in a chess game, analyze them using Stockfish, and return the results as a dictionary.

    Args:
        game (chess.pgn.Game): The chess game object to analyze.

    Returns:
        dict: A dictionary with detailed analysis of each move.
    """
    game_data = []
    board = game.board()  # Create a new board for each game
    move_counter = 0

    for move in game.mainline_moves():
        board.push(move)  # Apply the move to the board
        move_counter += 1

        # Determine whether the move was made by White or Black
        player = "White" if move_counter % 2 == 1 else "Black"

        # Generate FEN for the current position
        current_fen = board.fen()

        # Call Stockfish API for analysis
        stockfish_output = analyze_with_stockfish_api(current_fen, depth=15)

        # Store the analysis data
        move_data = {
            "Move Number": move_counter,
            "Player": player,
            "Move": move.uci(),
            "FEN": current_fen,
            "Stockfish Analysis": stockfish_output
        }
        game_data.append(move_data)

    return game_data

def parse_pgn_and_generate_json(pgn_file_path, output_json_path):
    """
    Parse a PGN file, analyze all moves, and save the results as a JSON file.

    Args:
        pgn_file_path (str): Path to the .pgn file containing the games.
        output_json_path (str): Path where the output JSON file will be saved.
    """
    with open(pgn_file_path, 'r') as pgn_file:
        games_data = []
        game_counter = 0

        while True:
            # Read each game in the PGN file
            game = chess.pgn.read_game(pgn_file)
            if game is None:  # End of file
                print("End of PGN file reached.")
                break

            game_counter += 1
            print(f"\nAnalyzing Game {game_counter}:")

            # Extract metadata from the game
            game_metadata = {
                "Event": game.headers.get("Event", "Unknown Event"),
                "White": game.headers.get("White", "Unknown Player"),
                "Black": game.headers.get("Black", "Unknown Player"),
                "Result": game.headers.get("Result", "Unknown Result")
            }

            # Process the moves for analysis
            game_moves_data = process_game_moves_and_analyze(game)

            # Combine metadata and moves data
            game_data = {
                "Metadata": game_metadata,
                "Moves": game_moves_data
            }

            # Append this game's data to the list of all games
            games_data.append(game_data)

        # Save all games' data as JSON
        with open(output_json_path, 'w') as json_file:
            json.dump(games_data, json_file, indent=4)

        print(f"\nAll games have been analyzed and saved to {output_json_path}")

# Example Usage
if __name__ == "__main__":
    # Path to your .pgn file containing multiple games
    pgn_file_path = "./datasets/some_games.pgn"  # Replace with the actual path to your .pgn file
    output_json_path = "refined_dataset.json"  # Output path for the JSON file

    # Call the function to parse the PGN file and save analysis as JSON
    parse_pgn_and_generate_json(pgn_file_path, output_json_path)
