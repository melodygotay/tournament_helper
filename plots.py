import matplotlib.pyplot as plt
import numpy as np
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

def auth_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("C:\\Users\\LadyD\\AppData\\Local\\Programs\\Python\\Python312\\Projects\\HotsCalc\\snipey-bfcd3543a260.json", scope)
    client = gspread.authorize(creds)  # Authorize client to interact with sheets
    sheet = client.open("Snipey data")  # Open specific sheet
    worksheet = sheet.get_worksheet(1)  # Access the second worksheet
    return worksheet

worksheet = auth_google_sheets()

# Get all data as a list of lists
data = worksheet.get_all_values()  
headers = data[0]  # First row is the header
rows = data[1:]    # Remaining rows are the data

# Convert to DataFrame
df = pd.DataFrame(rows, columns=headers)

def calculate_hero_stats(df):  # Now we pass the DataFrame
    hero_stats = {}

    # Iterate through each row in the DataFrame using iterrows()
    for _, row in df.iterrows():
        # Get heroes picked by Team 1 and Team 2
        team1_heroes = [row[f'T1 H{i}'] for i in range(1, 6)]
        team2_heroes = [row[f'T2 H{i}'] for i in range(1, 6)]

        # Determine the winner
        winner_team = row['Winner']
        team1_won = winner_team == row['Team 1 Name']
        team2_won = winner_team == row['Team 2 Name']

        # Update stats for each hero picked by Team 1
        for hero in team1_heroes:
            if hero not in hero_stats:
                hero_stats[hero] = {"pick_count": 0, "win_count": 0}
            hero_stats[hero]["pick_count"] += 1
            if team1_won:
                hero_stats[hero]["win_count"] += 1

        # Update stats for each hero picked by Team 2
        for hero in team2_heroes:
            if hero not in hero_stats:
                hero_stats[hero] = {"pick_count": 0, "win_count": 0}
            hero_stats[hero]["pick_count"] += 1
            if team2_won:
                hero_stats[hero]["win_count"] += 1

    # Calculate the win rate for each hero
    for hero, stats in hero_stats.items():
        if stats["pick_count"] > 0:
            # Calculate win rate as a fraction (not percentage)
            stats["win_rate"] = stats["win_count"] / stats["pick_count"]
            # Convert it to a percentage and round to integer
            stats["win_rate_percentage"] = round(stats["win_rate"] * 100)
        else:
            stats["win_rate"] = 0  # If the hero was never picked, set win rate to 0
            stats["win_rate_percentage"] = 0  # If the hero was never picked, win rate is 0

    # Sort the heroes by pick count in descending order and get the top 15 heroes
    sorted_heroes = sorted(hero_stats.items(), key=lambda x: x[1]["pick_count"], reverse=True)
    top_15_heroes = sorted_heroes[:15]  # Get the top 15 heroes

    # Reorganize the data back into separate lists
    top_15_hero_stats = dict(top_15_heroes)
    heroes = list(top_15_hero_stats.keys())
    pick_counts = [top_15_hero_stats[hero]["pick_count"] for hero in heroes]
    win_rates = [top_15_hero_stats[hero]["win_rate_percentage"] for hero in heroes]

    return heroes, pick_counts, win_rates


# Now, use the `calculate_hero_stats` function to get the stats
heroes, pick_counts, win_rates = calculate_hero_stats(df)  # Correctly unpack the return value

# Now you can call your plot function to visualize this data
def plot_hero_stats(heroes, pick_counts, win_counts):
    x = np.arange(len(heroes))  # Position of each hero on the x-axis
    width = 0.35  # Bar width

    fig, ax = plt.subplots(figsize=(12, 8))

    # Create the total picks bar (Big Bar)
    bars1 = ax.bar(x, pick_counts, width, label="Total Picks", color="skyblue")

    # Create the win rate percentage bar (Small bar inside)
    # The height of the win rate bar is calculated as a fraction of the pick counts
    bars2 = ax.bar(x, [pick_count * (win_rate / 100) for pick_count, win_rate in zip(pick_counts, win_counts)], width, label="Win Rate (%)", color="lightgreen")

    # Set labels and title
    ax.set_xlabel("Heroes")
    ax.set_ylabel("Pick Count / Win Rate (%)")
    ax.set_title("Top 15 Hero Pick Counts with Win Rate Inside (as %)")
    ax.set_xticks(x)
    ax.set_xticklabels(heroes, rotation=45, ha="right")
    ax.legend()

    # Add labels to bars
    for i, (bar, pick_count, win_rate) in enumerate(zip(bars1, pick_counts, win_counts)):
        # Display pick count as a whole number (integer)
        ax.annotate(f'{int(bar.get_height())}',  # Round pick count to integer
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height() + bar.get_y()),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center", va="bottom")

        # Display win rate percentage as an integer (e.g., 33%)
        ax.annotate(f'{win_rate}%', 
                    xy=(bar.get_x() + bar.get_width() / 2, bars2[i].get_height() + bar.get_y()),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center", va="bottom")

    plt.tight_layout()
    plt.show()

# Call the function to plot
plot_hero_stats(heroes, pick_counts, win_rates)
