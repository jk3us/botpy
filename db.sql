BEGIN;
DROP TABLE messages;
DROP TABLE tunes;
DROP TABLE presence;

CREATE TABLE messages (
	message_id INTEGER PRIMARY KEY AUTOINCREMENT,
	resource_id integer,
	tofrom integer,
	time integer,
	message text
);

CREATE TABLE tunes (
	service text,
	node text,
	time real,
	artist text,
	title text,
	source text,
	track text,
	length text
);

CREATE TABLE presence (
	node text,
	domain text,
	resource text,
	priority integer,
	type text,
	status text,
	show text
);

COMMIT;
