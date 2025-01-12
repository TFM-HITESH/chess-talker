import os
import csv
import chess.pgn

def extract_game_details(pgn_files_directory):
    # Prepare the CSV file
    with open('chess_games_summary.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['gameNumber', 'game heading', 'discussion', 'link to game'])

        # Loop through all .pgn files in the given directory
        for i in range(1, 21):  # 20 games
            pgn_filename = f'{pgn_files_directory}/game{i}.pgn'

            # Check if the file exists
            if os.path.exists(pgn_filename):
                try:
                    with open(pgn_filename) as pgn_file:
                        game = chess.pgn.read_game(pgn_file)
                        game_number = f"game{i}"

                        # Extract the game heading (opponent names + event info)
                        white_player = game.headers.get('White', 'N/A')
                        black_player = game.headers.get('Black', 'N/A')
                        event = game.headers.get('Event', 'N/A')
                        site = game.headers.get('Site', 'Unknown')
                        game_heading = f"{white_player} vs. {black_player} ({event})"

                        # Create a discussion paragraph from the PGN metadata
                        result = game.headers.get('Result', 'N/A')
                        white_elo = game.headers.get('WhiteElo', 'N/A')
                        black_elo = game.headers.get('BlackElo', 'N/A')
                        white_rating_diff = game.headers.get('WhiteRatingDiff', 'N/A')
                        black_rating_diff = game.headers.get('BlackRatingDiff', 'N/A')
                        eco = game.headers.get('ECO', 'N/A')
                        opening = game.headers.get('Opening', 'N/A')

                        discussion = (f"Result: {result}. White's Elo: {white_elo} (Change: {white_rating_diff}), "
                                      f"Black's Elo: {black_elo} (Change: {black_rating_diff}). "
                                      f"ECO: {eco}, Opening: {opening}.")

                        # Link construction based on the site (event location)
                        link_to_game = f"https://www.google.com/maps/search/{site.replace(' ', '+')}"

                        # Write the row to CSV
                        writer.writerow([game_number, game_heading, discussion, link_to_game])

                except Exception as e:
                    print(f"Error reading {pgn_filename}: {e}")

    print("CSV file 'chess_games_summary.csv' created successfully!")

# Call the function with the directory path where your .pgn files are stored
extract_game_details('./datasets')  # Replace with your actual path if different
