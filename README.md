README SQL Tournament

Tournament.sql contains the schema for a PostgreSQL database which keeps
track of players, matches and scores in one or more swiss pairing tournaments.

A tournament database should be created from the psql command line, then, from
within the tournament database, run \i tournament.sql to create the schema and
initialize a single default tournament.

 Tournament.py controls input into and output from the database, with functions
 for registering players, adding tournaments, adding players to tournaments,
 adding match scores, and getting player pairings for the next round (among
 other things).
