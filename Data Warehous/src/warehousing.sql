CREATE DATABASE IF NOT EXISTS rogerwarehouse;
USE rogerwarehouse;

CREATE TABLE IF NOT EXISTS Dim_Persona (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(67) UNIQUE NOT NULL,
    occupation VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Dim_Episode (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    season TINYINT UNSIGNED NOT NULL,
    episode TINYINT UNSIGNED NOT NULL,
    air_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS Fact_Appearance (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    persona INT UNSIGNED NOT NULL,
    episode INT UNSIGNED NOT NULL,
    is_intro BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (persona) REFERENCES Dim_Persona(id) ON DELETE CASCADE,
    FOREIGN KEY (episode) REFERENCES Dim_Episode(id) ON DELETE CASCADE,
    UNIQUE (persona, episode, is_intro)
);

INSERT INTO Dim_Persona (name, occupation) SELECT name, occupation FROM rogerdodger.persona;
INSERT INTO Dim_Episode (season, episode, air_date) SELECT season, episode, air_date FROM rogerdodger.episode;
INSERT INTO Fact_Appearance (persona, episode, is_intro)
SELECT
    a.persona,
    de.id,
    a.is_intro
FROM rogerdodger.appearance a
JOIN rogerdodger.episode e
    ON a.episode = e.id
JOIN Dim_Episode de
    ON de.season = e.season AND de.episode = e.episode;
