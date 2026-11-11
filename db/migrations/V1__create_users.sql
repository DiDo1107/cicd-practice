CREATE TABLE users (
    id         SERIAL PRIMARY KEY,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    created_at TIMESTAMP    NOT NULL DEFAULT NOW()
);
