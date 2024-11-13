import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import asyncio
from data.game_data import TEAMS, HEROES, BRACKET
import re
from data.globals import active_series

class HeroMatch:
    def __init__(self, HEROES):
        self.heroes = HEROES

    def normalize(self, hero_name):
        """Normalize hero names for comparison."""
        # Replace spaces with hyphens and remove punctuation, then lower the case
        normalized = re.sub(r'\s+', '-', hero_name)  # Replace spaces with hyphens
        normalized = re.sub(r'[^\w-]', '', normalized)  # Remove punctuation except for hyphens
        return normalized.lower().strip()  # Lowercase and strip spaces

    def match_heroes(self, input_string):
        # Split the input into hero names
        hero_names = [hero.strip() for hero in input_string.split(',')]
        matched_heroes = []
        unmatched_heroes = []

        # Normalize the heroes from the dictionary for comparison
        normalized_heroes = {
            self.normalize(h): h for role, hs in self.heroes.items() for h in hs
        }

        for hero in hero_names:
            # Normalize the hero name for comparison
            normalized_hero = self.normalize(hero)
            print(f"Checking input: '{normalized_hero}'")  # Debug output
            
            # Try to find the normalized hero in the pre-normalized heroes dictionary
            if normalized_hero in normalized_heroes:
                matched_heroes.append(normalized_heroes[normalized_hero])
            else:
                matched_heroes.append("Invalid")

            if normalized_hero not in normalized_heroes:
                unmatched_heroes.append(hero)
            else:
                unmatched_heroes.append("")

        return matched_heroes, unmatched_heroes

# Constants for statuses
ACTIVE_STATUS = 'Active'
CLOSED_STATUS = 'Closed'
EMPTY = ""             
class CompTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sheet = self.auth_google_sheets()
        self.worksheet = self.sheet
        self.teams = TEAMS
        self.heroes = HEROES
        self.hero_matcher = HeroMatch(HEROES)  # Initialize HeroMatch with the HEROES dictionary 
                                    # my testing channel |  comp-tracking
        self.ALLOWED_CHANNELS_MOD = [1290751062256648212, 1301639621582520320]

    @commands.command()
    async def teams(self, ctx: commands.Context):
        embed = discord.Embed(
            title="3k Raviment Teams",
            description="Use these abbreviations when referencing the teams.",
            color=discord.Color.red()
        )
        embed.add_field(name="", value="**`BCH`:**  Barley's Chewies", inline=False)
        embed.add_field(name="", value="**`TMT`:**  Team Two", inline=False)
        embed.add_field(name="", value='**`MRU`:**  Memes "R" Us', inline=False)
        embed.add_field(name="", value="**`CTZ`:**  Confused Time Zoners", inline=False)
        embed.add_field(name="", value="**`FLO`:**  Floccinaucinihilipilification", inline=False)
        embed.add_field(name="", value="**`MVP`:**  MVP on a Loss FeelsAbzeerMan", inline=False)
        embed.add_field(name="", value="**`PBR`:**  Peanut Butter Randos", inline=False)
        embed.add_field(name="", value="**`DOH`:**  Disciples of the Highlord", inline=False)
        await ctx.send(embed=embed)

    def auth_google_sheets(self):
        # Scope for sheets & drive
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Load credentials from .json file
        creds = ServiceAccountCredentials.from_json_keyfile_name("C:\\Users\\LadyD\\AppData\\Local\\Programs\\Python\\Python312\\Projects\\HotsCalc\\snipey-bfcd3543a260.json", scope)
        client = gspread.authorize(creds)  # Authorize client to interact with sheets
        sheet = client.open("Snipey data")  # Open specific sheet
        worksheet = sheet.get_worksheet(1)  # Access the second worksheet
        return worksheet

    def get_active_series(self, team1, team2):
        global active_series
        records = self.worksheet.get_all_records()
        for row in records:
            if (row['Team 1 Name'] == team1 or row['Team 2 Name'] == team1) and \
            (row['Team 1 Name'] == team2 or row['Team 2 Name'] == team2) and \
            row['Series Status'] == ACTIVE_STATUS and row['Match Status'] == ACTIVE_STATUS:
                active_series[(team1, team2)] = {
                    'series_id': row['Series ID'],
                    'current_match_id': row['Match ID'],  # Initialize match_id if needed
                    'team1': team1,
                    'team2': team2
                }
                return row['Series ID'], row['Match ID']
        return None, None

    def start_new_series(self, series_id, team1, team2):
        global active_series
        existing_id, _ = self.get_active_series(team1, team2) # Store the series ID as the active one
        if not existing_id:
            active_series[(team1, team2)] = {
                'series_id': series_id,
                'current_match_id': 0,  # Initialize match_id if needed
                'team1': team1,
                'team2': team2
            }
       
        print(f"Series {series_id} between {team1} and {team2} started.")
    
    def start_new_match(self, team1, team2, match_id):
        global active_series
        print(f"Starting new match for {team1} vs {team2} with match ID {match_id}")
        
        # Check if an active series exists directly
        series_info = active_series.get((team1, team2))
        if series_info is None:
            raise ValueError("No active series. Please start a new series first by using !series.")

        series_id = series_info['series_id'] # Extract series ID and current match ID
        current_match_id = series_info['current_match_id']

        records = self.worksheet.get_all_records()
        match_exists = any(row['Match ID'] == match_id and row['Series ID'] == series_id for row in records)

        if match_exists:
            print(f"Match {match_id} in Series ID {series_id} already exists.")
            return current_match_id  # Return existing match ID if found

        # If no match ID exists, append a new row with match details
        self.worksheet.append_row([
            team1.upper(), team2.upper(), series_id, match_id, ACTIVE_STATUS, ACTIVE_STATUS
        ])
        print(f"New match started for Series ID {series_id} with Match ID {match_id}, Teams: {team1} vs {team2}")
        series_info['current_match_id'] = match_id 
        return match_id

    def can_pick_hero(self, series_id, team_name, hero_name):
        records = self.worksheet.get_all_records()

        # Check if the hero has already been picked by this team in this series
        for row in records:
            if row['Series ID'] == series_id:
                if row['Team 1 Name'] == team_name:
                    if hero_name in [row[col] for col in row.keys() if col.startswith('T1 H')]:
                        return False  # Hero has already been picked by this team

                if row['Team 2 Name'] == team_name:
                    if hero_name in [row[col] for col in row.keys() if col.startswith('T2 H')]:
                        return False  # Hero has already been picked by this team
        return True

    def update_player_pick(self, series_id, match_id, team_name, player_index, hero_name):
        records = self.worksheet.get_all_records()
        for index, row in enumerate(records): 
            if row['Series ID'] == series_id and row['Match ID'] == match_id:
                if team_name == row['Team 1 Name']:
                    column_index = 7 + player_index  # Assuming hero picks for Team 1 start from column 7
                else:
                    column_index = 12 + player_index  # Assuming hero picks for Team 2 start after Team 1

                self.worksheet.update_cell(index + 2, column_index, hero_name)  # Update the cell with hero_name
                return True  # Successfully updated

        return False 

    def clear_team_picks(self, series_id, match_id):
        # Fetch all records to find the target row
        records = self.worksheet.get_all_records()
        target_row = None

        for index, row in enumerate(records): # Find the row that matches both series and match IDs       
            if row['Series ID'] == series_id and row['Match ID'] == match_id:
                target_row = index + 2  # Adjust for header row
                break

        if target_row:           
            for col in range(7, 17):  # Clear columns 7 through 16 for the identified row
                self.worksheet.update_cell(target_row, col, "")
            
            print(f"Cleared picks for series {series_id}, match {match_id} in row {target_row}.")
            return True 
        else:
            print(f"No matching row found for series {series_id} and match {match_id}.")
            return False 

    @commands.command()
    async def series(self, ctx, series_id: int, team1: str, team2: str):
        global active_series
        global BRACKET

        if ctx.channel.id not in self.ALLOWED_CHANNELS_MOD:
            await ctx.send(f"{ctx.author.mention}, this command can only be used in `#-comp-tracking`.")
            return
        
        team1 = team1.upper()
        team2 = team2.upper()
                
        if team1 not in self.teams or team2 not in self.teams: # Check if both teams are valid
            await ctx.send(f"Invalid teams: '{team1}' and/or '{team2}'. Please use the following abbreviations: {', '.join(self.teams.keys())}")
            return

        expected_teams = None
        for round_name, series in BRACKET.items():
            if str(series_id) in series:
                expected_teams = series[str(series_id)]
                break

        if expected_teams is None:
            await ctx.send(f"No series found with ID {series_id}.")
            return

        bracket_team1 = expected_teams['Team 1'].upper()

        if team1 != bracket_team1: # Check if team1 matches the bracket's Team 1
            team1, team2 = team2, team1 # If not, swap team1 and team2

        if (team1, team2) in active_series:
            await ctx.send(f"A series between **{team1}** and **{team2}** is already active.")
            return

        if len(active_series) > 0:
            previous_series_key = next(iter(active_series))  # In case there's more than one series
            del active_series[previous_series_key]  # Clear previous series

        existing_records = self.worksheet.get_all_records()
        series_exists = False
        latest_match_id = 0

        for row in existing_records:
            if (row['Series ID'] == series_id and 
                row['Team 1 Name'].upper() == team1 and 
                row['Team 2 Name'].upper() == team2):
                series_exists = True
                if row['Match ID'] > latest_match_id:
                    latest_match_id = row['Match ID']

        if series_exists:  # If series exists, activate it
            active_series[(team1, team2)] = {
                'series_id': series_id,
                'current_match_id': latest_match_id,  # Initialize match_id if needed
                'team1': team1,
                'team2': team2
            }
            await ctx.send(f"Series {series_id} between **{team1}** and **{team2}** is now active.")
            print(f"Active Series: {active_series}")  # For monitoring
            return
        
        self.start_new_series(series_id, team1, team2) # If the series does not exist, create a new series

        print(f"Active Series: {active_series}")  # For monitoring
        full_team1 = self.teams.get(team1, team1)
        full_team2 = self.teams.get(team2, team2)
        await ctx.send(f"Started new series between **{full_team1}** and **{full_team2}**.")

    @commands.command()
    async def match(self, ctx, match_id: int):
        global active_series
        if ctx.channel.id not in self.ALLOWED_CHANNELS_MOD:
            await ctx.send(f"{ctx.author.mention}, this command can only be used in `#-comp-tracking`.")
            return
        series_info = None
        previous_match_id = match_id - 1

        if match_id == 1:
            if not active_series: # Ensure there's an active series before starting match 1
                await ctx.send("No active series exists. Please start a series first.")
                return

            (team1, team2), info = next(iter(active_series.items()))
            series_id = info['series_id']
            
            series_info = info
        else:
            if match_id > 1:                
                for (team1, team2), info in active_series.items(): # Search for the active series with a matching previous match that is closed
                    series_id = info['series_id']
                    records = self.worksheet.get_all_records()
                    previous_match_closed = False

                    for row in records:
                        if (row['Series ID'] == series_id and
                            row['Match ID'] == previous_match_id and
                            row['Match Status'] == "Closed"):  # Ensure previous match is closed
                            previous_match_closed = True
                            break

                    if previous_match_closed:
                        active_series[(team1, team2)]['current_match_id'] = match_id
                        series_info = active_series[(team1, team2)]
                        break

            if not series_info:
                await ctx.send("Previous match is not closed or does not exist. Please close the previous match or check the match ID.")
                print("No active series found for the given match ID, or previous match is not closed.")
                return

        team1 = series_info['team1']
        team2 = series_info['team2']
        series_id = series_info['series_id']

        full_team1 = self.teams.get(team1, team1)
        full_team2 = self.teams.get(team2, team2)

        print(f"Attempting to start Match ID {match_id} for Series ID {series_id}: Teams - {team1} vs {team2}")
        new_match_id = self.start_new_match(team1, team2, match_id)

        if not new_match_id:
            await ctx.send("There was an error starting the match. Please try again.")
            return

        await ctx.send(f"Started match {new_match_id} in series {series_id}: **{full_team1}** vs **{full_team2}**.")
        print("Match started message sent.")

        async def get_team_composition(ctx, team_name): # Helper function to get team compositions
            full_team_name = self.teams.get(team_name.upper(), team_name)
            while True:
                await ctx.send(f"Please input the hero picks for **{full_team_name} ({team_name})** (5 heroes, comma-separated):")
                print(f"Waiting for {team_name} input...")

                def check(msg):
                    return msg.channel == ctx.channel and msg.author == ctx.author  # Check if the message is from the command invoker

                try:
                    team_comp_msg = await self.bot.wait_for('message', check=check, timeout=90.0)
                    print(f"Received {team_name} composition: {team_comp_msg.content}")
                    if team_comp_msg.content.lower() == "cancel":
                        await ctx.send("Input canceled.")
                        return
                    
                    await ctx.send("One moment...")
                    # Process the hero input
                    matched_heroes, unmatched_heroes = self.hero_matcher.match_heroes(team_comp_msg.content)  # Process the input using HeroMatch

                    if len(matched_heroes) != 5: # Check if we have exactly 5 heroes
                        await ctx.send("You must provide exactly 5 heroes for the composition! Please try again.")
                        print(f"{team_name} provided an invalid number of heroes.")
                        continue  # Prompt the user again

                    if "Invalid" in matched_heroes: # Check for duplicates and validity
                        unmatched_heroes = [hero for hero in unmatched_heroes if hero.strip()]
                        await ctx.send(f"The following heroes did not match or are invalid: {', '.join(unmatched_heroes)}. Please try again.")
                        print(f"{team_name} provided unknown heroes: {', '.join(unmatched_heroes)}")
                        continue  # Prompt the user again
                    
                    duplicates = [] # Check for duplicates in the current series
                    valid_heroes = []
                    for i, hero in enumerate(matched_heroes):
                        if not self.can_pick_hero(series_id, team_name, hero):
                            duplicates.append(hero)
                        else:
                            valid_heroes.append(hero)

                    if duplicates:
                        await ctx.send(f"The following heroes have already been picked by **{team_name}** in this series: {', '.join(duplicates)}! Please try again.")
                        print(f"{team_name} attempted to pick already chosen heroes: {', '.join(duplicates)}")
                        continue  # Prompt the user again
                    
                    for i, hero in enumerate(valid_heroes):
                        self.update_player_pick(series_id, new_match_id, team_name, i, hero)
                    # If everything is valid, send confirmation and return the team composition
                    await ctx.send(f"**{full_team_name}**'s composition has been recorded as:\n" + ', '.join(f"**{hero}**" for hero in matched_heroes) +"\n\nIs this correct? (Yes/No)")
                    try:
                        confirmation_msg = await self.bot.wait_for('message', check=check, timeout=30.0)
                        if confirmation_msg.content.capitalize() == "Y" or confirmation_msg.content.capitalize() == "Yes":
                            return matched_heroes
                        elif confirmation_msg.content.capitalize() == "N" or confirmation_msg.content.capitalize() == "No":
                            self.clear_team_picks(series_id, new_match_id)
                            continue # Clear heroes and prompt the user again
                        else:
                            await ctx.send("Invalid response. Please respond with 'Yes' or 'No'.")
                    except asyncio.TimeoutError:
                        await ctx.send("You took too long to respond! Please try again.")
                        break

                except asyncio.TimeoutError:
                    await ctx.send(f"You took too long to respond! Please try again by using `!match {new_match_id}`.")
                    print(f"{team_name} did not respond in time, clearing hero inputs for match {new_match_id}")
                    self.clear_team_picks(series_id, new_match_id)
                    break

        team1_compositions = await get_team_composition(ctx, team1)
        if team1_compositions is None:
            return  # Exit if there was a timeout
        print("Team 1 comp added to sheets")

        team2_compositions = await get_team_composition(ctx, team2)
        if team2_compositions is None:
            return  # Exit if there was a timeout
        print("Team 2 comp added to sheets")

        await self.closematch(ctx, match_id)
        series_info['current_match_id'] += 1 
        print(f"Match ID incremented. Current Match ID is now {series_info['current_match_id']}.")

    @commands.command()
    async def winner(self, ctx, match_id: int, winner: str):
        global active_series
        winner = winner.upper()

        print(f"Setting winner: '{winner}' for match ID {match_id}")
        full_name = self.teams.get(winner, winner)
        series_id = None
        for (team1, team2), info in active_series.items():
            if info["current_match_id"] - 1 == match_id:
                series_id = info["series_id"]
                break

        if series_id is None:
            await ctx.send(f"No active series found with Match ID {match_id}.")
            return

        if winner not in self.teams.keys():
            await ctx.send(f"Invalid team name '{winner}'. Please enter a valid team name.")
            return

        records = self.worksheet.get_all_records()
        match_found = False

        for row_num, row in enumerate(records, start=2):  # Start from row 2 to account for header
            if row["Series ID"] == series_id and row["Match ID"] == match_id:
                match_found = True
                               
                try:  # Update the winner column in Google Sheets (Column 17)
                    self.worksheet.update_cell(row_num, 17, winner) 
                    await ctx.send(f"Winner for match {match_id} in series {series_id} has been updated to **{full_name}**")
                    print(f"Winner for Match {match_id} in Series {series_id} updated to {winner}.")
                except Exception as e:
                    print("Error updating cell:", e)
                    await ctx.send("There was an error updating the winner. Please try again.")
                break

        if not match_found:
            await ctx.send(f"No match found with Series ID {series_id} and Match ID {match_id}.")

    @commands.command()
    async def endseries(self, ctx, series_id: int):
        global active_series
        if ctx.channel.id not in self.ALLOWED_CHANNELS_MOD:
            await ctx.send(f"{ctx.author.mention}, this command can only be used in #-comp-tracking.")
            return
        
        records = self.worksheet.get_all_records()  # Get all records from the worksheet
        match_found = False  # Track if the match was found

        for i, row in enumerate(records):
            if row['Series ID'] == series_id and row['Series Status'] == 'Active':
                team1 = row['Team 1 Name']
                team2 = row['Team 2 Name']
                full_team1 = self.teams.get(team1, team1)
                full_team2 = self.teams.get(team2, team2)

                try:
                    print(f"Updating Series ID {series_id} status to '{CLOSED_STATUS}' at row {i + 2}...")
                    self.worksheet.update_cell(i + 2, 5, CLOSED_STATUS)  # Assuming column 5 is for Series Status
                    self.worksheet.update_cell(i + 2, 6, CLOSED_STATUS)  # Assuming column 5 is for Match Status
                    print(f"Successfully updated Series ID {series_id} to status '{CLOSED_STATUS}'.")
                    
                    updated_row = self.worksheet.get_all_records()[i]
                    if updated_row['Series Status'] == CLOSED_STATUS:
                        match_found = True
                    else:
                        print(f"Warning: Series ID {series_id} status not updated correctly, found: {updated_row['Series Status']}")
                        
                except Exception as e:
                    print(f"Failed to update the match status for Match ID {series_id}: {e}")
                    await ctx.send("An error occurred while closing the match. Please try again.")

        await ctx.send(f"Closed series between **{full_team1}** and **{full_team2}**.")
        active_series.clear()
        print(f"ACTIVE SERIES AFTER SERIES CLOSE {active_series}")

        if not match_found:
            await ctx.send(f"No active series found with Series ID {series_id}.")
    
    @commands.command()
    async def closematch(self, ctx, match_id: int):
        records = self.worksheet.get_all_records()  # Get all records from the worksheet
        match_found = False  # Track if the match was found
        for i, row in enumerate(records):
            if row['Match ID'] == match_id and row['Match Status'] == 'Active':
                team1 = row['Team 1 Name']
                team2 = row['Team 2 Name']
                try:
                    print(f"Updating Match ID {match_id} status to '{CLOSED_STATUS}' at row {i + 2}...")
                    self.worksheet.update_cell(i + 2, 6, CLOSED_STATUS)  # Assuming column 6 is for Match Status
                    print(f"Successfully updated Match ID {match_id} to status '{CLOSED_STATUS}'.")

                    updated_row = self.worksheet.get_all_records()[i]
                    if updated_row['Match Status'] == CLOSED_STATUS:
                        full_team1 = self.teams.get(team1, team1)
                        full_team2 = self.teams.get(team2, team2)
                        await ctx.send(f"The composition for match {match_id} between **{full_team1}** and **{full_team2}** has been successfully recorded.")
                        match_found = True
                    else:
                        print(f"Warning: Match ID {match_id} status not updated correctly, found: {updated_row['Match Status']}")
                        
                except Exception as e:
                    print(f"Failed to update the match status for Match ID {match_id}: {e}")
                    await ctx.send("An error occurred while closing the match. Please try again.")
                break  # Exit the loop once the match is found and updated

        if not match_found:
            await ctx.send(f"No active match found with ID {match_id}.")

    def get_heroes_for_team_in_tournament(self, team_name):
        records = self.worksheet.get_all_records()

        tournament_picks = {}

        for row in records:
            series_id = row['Series ID']
            match_id = row['Match ID']

            # Check if the row matches the team name (Team 1 or Team 2)
            if row['Team 1 Name'] == team_name:
                heroes = [
                    row['T1 H1'], row['T1 H2'], row['T1 H3'],
                    row['T1 H4'], row['T1 H5']
                ]
            elif row['Team 2 Name'] == team_name:
                heroes = [
                    row['T2 H1'], row['T2 H2'], row['T2 H3'],
                    row['T2 H4'], row['T2 H5']
                ]
            else:
                continue

            heroes = [hero for hero in heroes if hero]

            if series_id not in tournament_picks:
                tournament_picks[series_id] = {}
            tournament_picks[series_id][match_id] = heroes

        return tournament_picks
    
    @commands.command()
    async def picks(self, ctx, team_name: str):
        """Display heroes picked by the team in an embed."""
        full_name = self.teams.get(team_name.upper())
        tournament_picks = self.get_heroes_for_team_in_tournament(team_name.upper())
        
        if tournament_picks:
            embed = discord.Embed(
                title=f"Picks for {full_name}",
                color=discord.Color.red()
            )

            for series_id, picks_by_match in sorted(tournament_picks.items()):
                # Add a main heading for each series
                embed.add_field(
                    name=f"**- Series {series_id} -**",
                    value="",
                    inline=False
                )

                for match_id, heroes in sorted(picks_by_match.items()):
                    formatted_heroes = "- "+"\n- ".join([hero.title() for hero in heroes])
                    embed.add_field(
                        name=f"Match {match_id}",
                        value=formatted_heroes,
                        inline=True  # Inline each match for side-by-side display
                    )

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No picks found for **{full_name}** in the tournament.")
         
# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(CompTracker(bot))