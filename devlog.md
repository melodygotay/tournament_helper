# Snipey Devlog
 — 11/03/2024
-updated the !ban command, renamed to !bans and added functionality to tag two users as parameters. first user starts bans.

 — 10/31/2024 3:04 PM
-locked commands "flip", "ban" and "report" so only captains can use it.
-added 60s cooldown to bracket command

 — 10/31/2024 4:48 PM
-added a functionality to the !ban command that saves each team's map bans depending on the roles they have into the database
-added a lock to captains commands to only work in draft channel, same for comp tracking.
-added a cancel input for map bans 

# Version 0.1.4
## 2024-10-29
### Tournament Helper
- Created a bracket save and load state feature that allows the bracket to be populated after closing and reopening the bot.
### General updates
- Updated the `!picks` command to show the heroes picked during the entire tournament rather than have users specify a series ID.

# Version 0.1.31
## 2024-10-28
### Tournament Helper

- Fixed an issue that caused scores to be recorded incorrectly if the `!report` command was used in a different order from the order used when the series was started.
- Added an option to confirm the hero picks were entered correctly and have the bot re-prompt if not.
- Added a functionality that clears hero input cells in the event of a time-out.

# Version 0.1.3
## 2024-10-27
### Tournament Helper
- Added a proper match reporting command for captains to use after a series ends.
- Added a "cancel" functionality during hero inputs.
- Added a functionality that locks scores after being reported to avoid score altering.

# Version 0.1.2
## 2024-10-25
### Tournament Helper!
- Added a tournament commands page.
- Fixed an issue that prevented the next match from being started if the bot was closed and reopened.
- Fixed an issue that added heroes to the database prematurely causing them to come up as duplicate picks.
- Restructured the look of the `!picks` command.
- Added a `!winner` command for match winners.

# Version 0.1.1
## 2024-10-23
### Account Management
- Fixed an issue where case insensitivity causing issues when using the `!update` command.  Users are now able to use mismatched casing when referencing their account names.
- Fixed an issue that prevented two different users to have two accounts with the same name.  One user will still not be able to have two accounts with the same name to avoid creating duplicates.

### Comp Tracker!
- Added a tool to track compositions for draft play.
- Added a !flip command for coin flips.
- Added an interactive `!ban @<other user>` command for map ban phase.
- Added functionality for self closing matches.
- Added team name parsing from abbreviations.

### Visual Updates
- Updated overall look of `!myaccs` command.
- Updated overall look of `!helpme command`.

# Version 0.1.0
## 2024-10-20
### Account Management
- Added a 'Last Played' feature that allows users to track how many days since an account was played.
- This feature will (in the future) remind players after 14 and 21 days of account inactivity.  Additionally, users can check how many days it has been since the last time they played by using the `!lastplayed` command.

### General
- Added more responses to user messages.
"- Added more commands to 'helpme' and 'info'.

### Visual Updates
- Added a Last Played column to the !myaccs table.