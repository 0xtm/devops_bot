--Version 6
DROP TABLE IF EXISTS Emails;
DROP TABLE IF EXISTS Phones;

CREATE USER bot_drops WITH PASSWORD '';
CREATE USER repl_user REPLICATION PASSWORD 'P@ssw0rd';
SELECT pg_create_physical_replication_slot('replication_slot');
CREATE TABLE Emails (ID SERIAL PRIMARY KEY, email VARCHAR (100) NOT NULL);
CREATE TABLE Phones (ID SERIAL PRIMARY KEY, phone VARCHAR (100) NOT NULL);

INSERT INTO Emails(email) VALUES ('mail@mail.ru');
INSERT INTO Emails(email) VALUES ('tp@mail.ru');
INSERT INTO Emails(email) VALUES ('dp@mail.ru');
INSERT INTO Emails(email) VALUES ('it@mail.ru');

INSERT INTO Phones(phone) VALUES ('88002000600');
INSERT INTO Phones(phone) VALUES ('88002000601');
INSERT INTO Phones(phone) VALUES ('88002000602');
INSERT INTO Phones(phone) VALUES ('88002000603');


GRANT SELECT,INSERT ON TABLE Emails TO bot_drops;
GRANT USAGE,UPDATE ON SEQUENCE Emails_id_seq TO bot_drops;
GRANT SELECT,INSERT ON TABLE Phones TO bot_drops;
GRANT USAGE,UPDATE ON SEQUENCE Phones_id_seq TO bot_drops;
