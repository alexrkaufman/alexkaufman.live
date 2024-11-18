DROP TABLE IF EXISTS post;

CREATE TABLE post (
  id varchar(36) default(uuid()),
  author_id varchar(36) NOT NULL,
);
