#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def createTournament(name, players):
    """Add a new tournament to the database.

    Args:
        name: tournament name
        players: list of player ids to register for tournament

    Returns:
        tournament id (integer)"""

    db = connect()
    c = db.cursor()
    c.execute("""Insert into tournaments (tournament_name)
        values (%s) returning tournament_id;""", (name,))
    tournament_id = c.fetchone()[0]
    for player in players:
        c.execute("""insert into tournament_players (tournament_id,
            player_id) values (%s, %s);""", (tournament_id, player))
    db.commit()
    db.close()
    return tournament_id

def addPlayerToTournament(player, tournament):
    """Adds a player to an existing tournament.

    Args:
        player: the player's id
        tournament: the id of the tournament"""

    db = connect()
    c = db.cursor()
    c.execute("""Insert into tournament_players (tournament_id,
        player_id) values (%s, %s);""", (tournament, player))
    db.commit()
    db.close()

def deleteMatches(tournament = 1):
    """Remove all the match records from the database.

    Args:
        tournament: id of tournament (default = 1)"""

    db = connect()
    c = db.cursor()
    c.execute("delete from matches;")
    db.commit()
    db.close()

def deletePlayers(tournament = 1):
    """Remove all the player records from the database.

    Args:
        tournament: id of tournament (default = 1)"""

    db = connect()
    c = db.cursor()
    c.execute("""select player_id from tournament_players where
        tournament_id = %s;""", (tournament,))
    players = []
    for result in c.fetchall():
        players.append(result[0])
    c.execute("""delete from tournament_players where
        tournament_id = %s;""", (tournament,))
    if len(players)>0:
        q = c.mogrify("""delete from players where player_id
            in %s;""", (tuple(players),))
        c.execute(q)
    db.commit()
    db.close()

def countPlayers(tournament = 1):
    """Returns the number of players currently registered.

    Args:
        tournament: id of tournament (default = 1)"""

    db = connect()
    c = db.cursor()
    c.execute("""select count(*) from tournament_players where
        tournament_id = %s;""", (tournament,))
    count = c.fetchone()[0]
    db.close()
    return count

def registerPlayer(name):
    """Adds a player to the tournament database.

    Args:
      name: the player's full name (need not be unique).

    Returns:
        player_id (int)
    """

    db = connect()
    c = db.cursor()
    c.execute("""insert into players (name) values (%s)
        returning player_id;""", (name,))
    player_id = c.fetchone()[0]
    db.commit()
    db.close()
    addPlayerToTournament(player_id, 1)
    return player_id

def playerStandings(tournament = 1):
    """Returns a list of the players in a tournament and
    their win records, sorted by wins.

    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    Args:
        tournament: id of tournament (default = 1)

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect()
    c = db.cursor()
    c.execute("""select p.player_id, p.name,
        ps.wins, ps.wins + ps.losses from players p
        join player_score ps on ps.player_id = p.player_id
        join schedule_strength ss on ss.player_id = p.player_id
        join tournament_players tp on tp.player_id = ps.player_id
        where tp.tournament_id = %s
        order by ps.wins desc, ss.opp_strength desc;""", (tournament,))
    results = c.fetchall()
    standings = []
    for row in results:
        standings.append((row[0], row[1], row[2], row[3]))
    db.close()
    return standings

def reportMatch(winner, loser, tournament = 1):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      tournament: id of tournament (default = 1)
    """
    db = connect()
    c = db.cursor()
    c.execute("""insert into matches
        (tournament_id, player_id_1, player_id_2, winner)
        VALUES (%s, %s, %s, %s)""", (tournament, winner, loser, winner))
    db.commit()
    db.close()

def swissPairings(tournament = 1):
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Args:
        tournament: id of tournament (default = 1)

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    pairings = []
    standings = playerStandings(tournament)
    if not standings:
        standings = []
    i = len(standings) - 1
    while i >= 0:
        # first deal with highest scorer in odd # player tournament,
        # who should get a bye.
        if i == 0:
            pairings.append((standings[i][0], standings[i][1],
                standings[i][0], standings[i][1]))
            i -= 1
        # everybody else gets paired with the person just above them in
        # the standings
        else:
            pairings.append((standings[i][0], standings[i][1],
                standings[i-1][0], standings[i-1][1]))
            i -= 2

    return pairings
