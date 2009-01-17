
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

	-- Task-specific fields

	categoryId INTEGER NULL DEFAULT NULL,
	
	-- Dates are represented as number of seconds since the Unix Epoch
	-- TODO: move this to 64 bits to prevent the infamous year 2038 bug :)
	
	startDate INTEGER NULL DEFAULT NULL,
	dueDate INTEGER NULL DEFAULT NULL,
	completionDate INTEGER NULL DEFAULT NULL
);

CREATE INDEX idxTaskStatus ON Task (status);
CREATE INDEX idxTaskName ON Task (name);
CREATE INDEX idxTaskCategory ON Task (categoryId);

-- Views

CREATE VIEW OverdueTask AS SELECT * FROM Task WHERE status != 3 AND dueDate < DATE('now');
CREATE VIEW DueTodayTask AS SELECT * FROM Task WHERE status != 3 AND dueDate == DATE('now');
CREATE VIEW StartedTask AS SELECT * FROM Task WHERE status != 3 AND startDate IS NOT NULL AND startDate <= DATE('now') AND (dueDate > DATE('now') OR dueDate IS NULL);
CREATE VIEW NotStartedTask AS SELECT * FROM Task WHERE status != 3 AND startDate IS NULL;

-- XXXTMP: testing data

INSERT INTO Category (name) VALUES ('Test1');
INSERT INTO Category (name) VALUES ('Test2');
INSERT INTO Category (name) VALUES ('Test3');

-- Not started
INSERT INTO Task (name, categoryId) VALUES ('Task1', 1);
-- Started
INSERT INTO Task (name, categoryId, startDate) VALUES ('Task2', 1, DATE('now', '-1 day'));
-- Due today
INSERT INTO Task (name, categoryId, startDate, dueDate) VALUES ('Task3', 1, DATE('now'), DATE('now'));
-- Overdue
INSERT INTO Task (name, categoryId, startDate, dueDate) VALUES ('Task4', 1, DATE('now', '-1 day'), DATE('now', '-1 day'));
