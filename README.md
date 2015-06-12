README SQL Tournament

Tournament.sql contains the schema for a PostgreSQL database which keeps
track of players, matches and scores in one or more swiss pairing tournaments.

From within PSQL, run \i tournament.sql to create the database, create
the schema and initialize a single default tournament.

 Tournament.py controls input into and output from the database, with functions
 for registering players, adding tournaments, adding players to tournaments,
 adding match scores, and getting player pairings for the next round (among
 other things).
