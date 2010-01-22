
-- Status is:

-- 0: None
-- 1: new
-- 2: modified
-- 3: deleted

CREATE TABLE TaskCoachFile
(
	id INTEGER PRIMARY KEY,
	name VARCHAR(255),
	guid CHAR(40) NOT NULL,
	visible BOOLEAN NOT NULL DEFAULT 0
);

CREATE INDEX idxTaskCoachFileGUID ON TaskCoachFile (guid);
CREATE INDEX idxTaskCoachFileName ON TaskCoachFile (name);
CREATE INDEX idxTaskCoachFileVisible ON TaskCoachFile (visible);

CREATE TABLE Category
(
	id INTEGER PRIMARY KEY,
	fileId INTEGER NULL DEFAULT NULL,
	name VARCHAR(255) NOT NULL,
	status INTEGER NOT NULL DEFAULT 1,
	taskCoachId VARCHAR(255) NULL DEFAULT NULL,
	parentId INTEGER NULL DEFAULT NULL
);

CREATE INDEX idxCategoryFile ON Category (fileId);
CREATE INDEX idxCategoryStatus ON Category (status);
CREATE INDEX idxCategoryName ON Category (name);
CREATE INDEX idxCategoryTaskCoachId ON Category (taskCoachId);
CREATE INDEX idxCategoryParentId ON Category (parentId);

CREATE TABLE Task
(
	id INTEGER PRIMARY KEY,
	fileId INTEGER NULL DEFAULT NULL,
	name VARCHAR(2048) NOT NULL,
	status INTEGER NOT NULL DEFAULT 1,
	taskCoachId VARCHAR(255) NULL DEFAULT NULL,

	-- Task-specific fields

	description TEXT NOT NULL DEFAULT '',
	
	-- Dates are represented as YYYY-MM-DD strings
	
	startDate CHAR(10) NULL DEFAULT NULL,
	dueDate CHAR(10) NULL DEFAULT NULL,
	completionDate CHAR(10) NULL DEFAULT NULL,

	parentId INTEGER NULL DEFAULT NULL
);

CREATE INDEX idxTaskFile ON Task (fileId);
CREATE INDEX idxTaskStatus ON Task (status);
CREATE INDEX idxTaskName ON Task (name);
CREATE INDEX idxTaskTaskCoachId ON Task (taskCoachId);
CREATE INDEX idxTaskParentId ON Task (parentId);

CREATE TABLE TaskHasCategory
(
	idTask INTEGER,
	idCategory INTEGER
);

CREATE INDEX idxTaskHasCategoryTask ON TaskHasCategory (idTask);
CREATE INDEX idxTaskHasCategoryCategory ON TaskHasCategory (idCategory);

CREATE TABLE Effort
(
	id INTEGER PRIMARY KEY,
	fileId INTEGER NULL DEFAULT NULL,
	name VARCHAR(2048) NOT NULL,
	status INTEGER NOT NULL DEFAULT 1,
	taskCoachId VARCHAR(255) NULL DEFAULT NULL,

	taskId INTEGER,
	started CHAR(19),
	ended CHAR(19) NULL DEFAULT NULL
);

CREATE INDEX idxEffortTask ON Effort (taskId);
CREATE INDEX idxEffortFile ON Effort (fileId);
CREATE INDEX idxEffortName ON Effort (name);
CREATE INDEX idxEffortStatus ON Effort (status);
CREATE INDEX idxEffortTaskCoachId ON Effort (taskCoachId);
CREATE INDEX idxEffortStarted ON Effort (started);
CREATE INDEX idxEffortEnded ON Effort (ended);

CREATE TABLE Meta
(
	name VARCHAR(255) NOT NULL,
	value VARCHAR(255)
);

CREATE UNIQUE INDEX idxMetaName ON Meta (name);

-- Initial data

INSERT INTO Meta (name, value) VALUES ('version', '3');
