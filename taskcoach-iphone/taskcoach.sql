
-- Status is:

-- 0: None
-- 1: new
-- 2: modified
-- 3: deleted

CREATE TABLE Category
(
	id INTEGER PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	status INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idxCategoryStatus ON Category (status);
CREATE INDEX idxCategoryName ON Category (name);

CREATE TABLE Task
(
	id INTEGER PRIMARY KEY,
	name VARCHAR(2048) NOT NULL,
	status INTEGER NOT NULL DEFAULT 1,

	categoryId INTEGER NULL DEFAULT NULL
);

CREATE INDEX idxTaskStatus ON Task (status);
CREATE INDEX idxTaskName ON Task (name);
CREATE INDEX idxTaskCategory ON Task (categoryId);

-- XXXTMP: testing data

INSERT INTO Category (name) VALUES ('Test1');
INSERT INTO Category (name) VALUES ('Test2');
INSERT INTO Category (name) VALUES ('Test3');

INSERT INTO Task (name, categoryId) VALUES ('Task1', 1);
