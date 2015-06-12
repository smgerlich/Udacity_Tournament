-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

create database tournament;
  
\c tournament;

Create table players (
  player_id serial PRIMARY KEY,
  name varchar(75) not null
);

create table tournaments (
  tournament_id serial primary key,
  tournament_name varchar(255)
);

-- This is to keep track of the players registered for each
-- tournament
CREATE TABLE tournament_players (
  tournament_player_id serial primary key,
  tournament_id integer not null references tournaments,
  player_id integer not null references players
);

create table matches (
  match_id    serial PRIMARY KEY,
  tournament_id integer not null references tournaments,
  player_id_1 integer not null references players,
  player_id_2 integer not null references players,
  winner integer not null references players
);

CREATE VIEW player_score
  AS SELECT
    p.player_id,
    t.tournament_id,
    count(CASE WHEN coalesce(m.winner, 0) = p.player_id THEN 1
            ELSE null END)
            AS "wins",
    count(CASE WHEN coalesce(m.winner, p.player_id) != p.player_id THEN 1
            ELSE null END)
            AS "losses",
    count(CASE WHEN coalesce(m.player_id_1, 0) = m.player_id_2 THEN 1
            ELSE null END)
            AS "byes"
  FROM players p
    LEFT JOIN matches m
      ON m.player_id_1 = p.player_id
      OR m.player_id_2 = p.player_id
    LEFT JOIN tournaments t
      ON t.tournament_id = m.tournament_id
  GROUP BY p.player_id, t.tournament_id;

-- This is designed to implement the OMW ranking in the event of ties
CREATE VIEW schedule_strength
  AS SELECT
    p.player_id,
    t.tournament_id,
    coalesce(SUM(ps.wins),0) AS "opp_wins",
    coalesce(SUM(ps.losses),0) AS "opp_losses",
    coalesce(SUM(ps.wins)/(SUM(ps.wins)+SUM(ps.losses)),0) AS "opp_strength"
  FROM players p
    LEFT JOIN matches m
      ON m.player_id_1 = p.player_id
      OR m.player_id_2 = p.player_id
    LEFT JOIN tournaments t
      ON t.tournament_id = m.tournament_id
    LEFT JOIN player_score ps
      ON (ps.player_id = m.player_id_1 OR ps.player_id = m.player_id_2)
      AND ps.player_id != p.player_id
      AND ps.tournament_id = t.tournament_id
    GROUP BY p.player_id, t.tournament_id;

-- This last line just initializes a single value in the tournaments table,
-- as each player will be added to tournament_id 1 by default.
Insert into tournaments (tournament_name) Values ('default_tournament');
