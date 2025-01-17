import json
import requests
import chess
import chess.pgn
import os
import time  # Importing time for sleep functionality


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

def parse_pgn_and_generate_json(dataset_folder, output_folder):
    """
    Parse PGN files from a folder, analyze all moves, and save each game's results as a separate JSON file.

    Args:
        dataset_folder (str): Folder containing the .pgn files.
        output_folder (str): Folder where the output JSON files will be saved.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through all the game files in the datasets folder
    for i in range(6, 21):
        pgn_file_path = os.path.join(dataset_folder, f"game{i}.pgn")
        output_json_path = os.path.join(output_folder, f"processed_game{i}.json")

        with open(pgn_file_path, 'r') as pgn_file:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                print(f"Skipping {pgn_file_path}: Empty game.")
                continue

            # Extract new metadata
            game_metadata = {
                "Event": game.headers.get("Event", "?"),
                "White": game.headers.get("White", "?"),
                "Black": game.headers.get("Black", "?"),
                "Result": game.headers.get("Result", "?"),
                "WhiteElo": game.headers.get("WhiteElo", "?"),
                "BlackElo": game.headers.get("BlackElo", "?"),
                "WhiteRatingDiff": game.headers.get("WhiteRatingDiff", "?"),
                "BlackRatingDiff": game.headers.get("BlackRatingDiff", "?"),
                "ECO": game.headers.get("ECO", "?"),
                "Opening": game.headers.get("Opening", "?"),
                "Termination": game.headers.get("Termination", "?"),
                "Round": game.headers.get("Round", "?")
            }


            # Process the moves for analysis
            game_moves_data = process_game_moves_and_analyze(game)

            # Combine metadata and moves data
            game_data = {
                "Metadata": game_metadata,
                "Moves": game_moves_data
            }

            # Save the game's data to a JSON file
            with open(output_json_path, 'w') as json_file:
                json.dump(game_data, json_file, indent=4)

            print(f"Game {i} analyzed and saved to {output_json_path}")

            # Add a 1-minute sleep after every 2 games processed to avoid overloading the API
            if i % 2 == 0:
                print("Pausing for 60 seconds to avoid overloading the API...")
                time.sleep(60)

# Example Usage
if __name__ == "__main__":
    dataset_folder = "./datasets"  # Folder containing the .pgn files (game1.pgn to game20.pgn)
    output_folder = "./processed_games_JSON"  # Folder to save the JSON files

    # Call the function to parse the PGN files and save analysis as JSON
    parse_pgn_and_generate_json(dataset_folder, output_folder)
