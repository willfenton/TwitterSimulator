CREATE TABLE Tweet (
    id INTEGER,
    body TEXT,
    PRIMARY KEY(id)
);

CREATE TABLE Hashtag (
    id INTEGER,
    hashtag TEXT,
    start_index INTEGER,
    end_index INTEGER,
    FOREIGN KEY(id) REFERENCES Tweet
);

CREATE TABLE Url (
    id INTEGER,
    url TEXT,
    start_index INTEGER,
    end_index INTEGER,
    FOREIGN KEY(id) REFERENCES Tweet
);

CREATE TABLE Mention (
    id INTEGER,
    mention TEXT,
    start_index INTEGER,
    end_index INTEGER,
    FOREIGN KEY(id) REFERENCES Tweet
);

