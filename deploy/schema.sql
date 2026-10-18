-- MovieGame schema v2; generated from app/database.py

CREATE TABLE catalog_versions (
	version VARCHAR(24) NOT NULL, 
	PRIMARY KEY (version)
)

;

CREATE TABLE movies (
	id VARCHAR(24) NOT NULL, 
	title TEXT NOT NULL, 
	year INTEGER NOT NULL, 
	category VARCHAR(20) NOT NULL, 
	description TEXT NOT NULL, 
	source_url TEXT NOT NULL, 
	source_verified BOOLEAN NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE schema_versions (
	version SERIAL NOT NULL, 
	PRIMARY KEY (version)
)

;

CREATE TABLE shared_results (
	token VARCHAR(32) NOT NULL, 
	share_key VARCHAR(64) NOT NULL, 
	snapshot JSON NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (token), 
	UNIQUE (share_key)
)

;

CREATE TABLE survey_versions (
	version VARCHAR(32) NOT NULL, 
	questions JSON NOT NULL, 
	PRIMARY KEY (version)
)

;

CREATE TABLE themes (
	name VARCHAR(100) NOT NULL, 
	PRIMARY KEY (name)
)

;

CREATE TABLE characters (
	id VARCHAR(24) NOT NULL, 
	movie_id VARCHAR(24) NOT NULL, 
	name TEXT NOT NULL, 
	identity TEXT NOT NULL, 
	description TEXT NOT NULL, 
	traits JSON NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(movie_id) REFERENCES movies (id)
)

;

CREATE TABLE movie_images (
	movie_id VARCHAR(24) NOT NULL, 
	image JSON NOT NULL, 
	PRIMARY KEY (movie_id), 
	FOREIGN KEY(movie_id) REFERENCES movies (id)
)

;

CREATE TABLE movie_themes (
	movie_id VARCHAR(24) NOT NULL, 
	theme VARCHAR(100) NOT NULL, 
	PRIMARY KEY (movie_id, theme), 
	FOREIGN KEY(movie_id) REFERENCES movies (id), 
	FOREIGN KEY(theme) REFERENCES themes (name)
)

;

CREATE TABLE submissions (
	key_hash VARCHAR(64) NOT NULL, 
	request_hash VARCHAR(64) NOT NULL, 
	survey_version VARCHAR(32) NOT NULL, 
	catalog_version VARCHAR(24) NOT NULL, 
	result JSON NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (key_hash), 
	FOREIGN KEY(survey_version) REFERENCES survey_versions (version)
)

;
CREATE INDEX ix_movies_category ON movies (category);
CREATE INDEX ix_shared_results_expires_at ON shared_results (expires_at);
CREATE INDEX ix_characters_movie_id ON characters (movie_id);
CREATE INDEX ix_submissions_expires_at ON submissions (expires_at);