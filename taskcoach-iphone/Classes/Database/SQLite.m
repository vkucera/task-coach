//
//  SQLite.m
//  iBooks
//
//  Created by Jérôme Laheurte on 10/12/08.
//  Copyright 2008 Jérôme Laheurte. See COPYING for details.
//

#import "SQLite.h"
#import "Statement.h"
#import "Configuration.h"

static int collation(void *p, int s1, const void *p1, int s2, const void *p2)
{
	NSString *str1 = [[NSString alloc] initWithBytes:p1 length:s1 encoding:NSUTF8StringEncoding];
	NSString *str2 = [[NSString alloc] initWithBytes:p2 length:s2 encoding:NSUTF8StringEncoding];

	NSComparisonResult result = [str1 localizedCaseInsensitiveCompare:str2];

	[str1 release];
	[str2 release];

	return result;
}

@implementation SQLite

@synthesize inTransaction;

- (void)upgradeParentId:(NSDictionary *)dict
{
	Statement *req = [self statementWithSQL:@"UPDATE Category SET parentId=? WHERE parentTaskCoachId=?"];
	
	[req bindInteger:[(NSNumber *)[dict valueForKey:@"id"] intValue] atIndex:1];
	[req bindString:[dict valueForKey:@"taskCoachId"] atIndex:2];
	[req exec];
}

- (void)upgradeFileTable:(NSDictionary *)dict
{
	Statement *req = [self statementWithSQL:@"INSERT INTO TaskCoachFile (guid) VALUES (?)"];
	[req bindString:[dict objectForKey:@"value"] atIndex:1];
	[req exec];
	
	NSInteger defaultFileId = [self lastRowID];
	[[self statementWithSQL:@"UPDATE TaskCoachFile SET visible=1"] exec];

	req = [self statementWithSQL:@"UPDATE Category SET fileId=?"];
	[req bindInteger:defaultFileId atIndex:1];
	[req exec];
	
	req = [self statementWithSQL:@"UPDATE Task SET fileId=?"];
	[req bindInteger:defaultFileId atIndex:1];
	[req exec];
	
	[[self statementWithSQL:@"DELETE FROM Meta WHERE name=\"guid\""] exec];
}

- (void)upgradeDatabase
{
	NSLog(@"Database version: %d", dbVersion);

	switch (dbVersion)
	{
		// No breaks here, it's intentional.
		case 1:
		{
			NSLog(@"Upgrading to version 2");

			// Add a parentId column to Category.

			[[self statementWithSQL:@"ALTER TABLE Category ADD COLUMN parentId INTEGER"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxCategoryParentId ON Category (parentId)"] exec];
			
			// Fill it.
			[[self statementWithSQL:@"SELECT id, taskCoachId FROM Category WHERE taskCoachId IS NOT NULL"] execWithTarget:self action:@selector(upgradeParentId:)];
			
			// The parentTaskCoachId column is now unused, but sqlite does not support removing a column.
		}
		case 2:
		{
			NSLog(@"Upgrading to version 3");
			
			// Add the TaskCoachFile table and its indexes
			
			[[self statementWithSQL:@"CREATE TABLE TaskCoachFile ( id INTEGER PRIMARY KEY, name VARCHAR(255), guid CHAR(40) NOT NULL, visible BOOLEAN NOT NULL DEFAULT 0 )"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxTaskCoachFileGUID ON TaskCoachFile (guid)"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxTaskCoachFileName ON TaskCoachFile (name)"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxTaskCoachFileVisible ON TaskCoachFile (visible)"] exec];
			
			[[self statementWithSQL:@"ALTER TABLE Category ADD COLUMN fileId INTEGER NULL DEFAULT NULL"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxCategoryFile ON Category (fileId)"] exec];
			
			[[self statementWithSQL:@"ALTER TABLE Task ADD COLUMN fileId INTEGER NULL DEFAULT NULL"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxTaskFile ON Task (fileId)"] exec];
			
			[[self statementWithSQL:@"ALTER TABLE Task ADD COLUMN parentId INTEGER NULL DEFAULT NULL"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxTaskParentId ON Task (parentId)"] exec];

			[[self statementWithSQL:@"CREATE TABLE Effort (id INTEGER PRIMARY KEY, fileId INTEGER NULL DEFAULT NULL, name VARCHAR(2048) NOT NULL, status INTEGER NOT NULL DEFAULT 1, taskCoachId VARCHAR(255) NULL DEFAULT NULL, taskId INTEGER, started CHAR(19), ended CHAR(19))"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxEffortFile ON Effort (fileId)"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxEffortName ON Effort (name)"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxEffortStatus ON Effort (status)"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxEffortTaskCoachId ON Effort (taskCoachId)"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxEffortTask ON Effort (taskId)"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxEffortStarted ON Effort (started)"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxEffortEnded ON Effort (ended)"] exec];

			// Create the main file, if applicable.
			[[self statementWithSQL:@"SELECT value FROM Meta WHERE name=\"guid\""] execWithTarget:self action:@selector(upgradeFileTable:)];
		}
		case 3:
		{
			NSLog(@"Upgrading to version 4");

			// Add day start and end hours, default 8/18
			[[self statementWithSQL:@"ALTER TABLE TaskCoachFile ADD COLUMN startHour INTEGER NOT NULL DEFAULT 8"] exec];
			[[self statementWithSQL:@"ALTER TABLE TaskCoachFile ADD COLUMN endHour INTEGER NOT NULL DEFAULT 18"] exec];

			// Alter date columns to hold date + time. Must use a temp table because
			// alter table does not support this.
			[[self statementWithSQL:@"CREATE TEMPORARY TABLE migTask (id INTEGER, fileId INTEGER, name VARCHAR(2048), status INTEGER, taskCoachId VARCHAR(255), description TEXT, startDate CHAR(10), dueDate CHAR(10), completionDate CHAR(10), parentId INTEGER)"] exec];
			[[self statementWithSQL:@"INSERT INTO migTask SELECT * FROM Task"] exec];
			[[self statementWithSQL:@"DROP TABLE Task"] exec];
			[[self statementWithSQL:@"CREATE TABLE Task (id INTEGER PRIMARY KEY, fileId INTEGER NULL DEFAULT NULL, name VARCHAR(2048) NOT NULL, status INTEGER NOT NULL DEFAULT 1, taskCoachId VARCHAR(255) NULL DEFAULT NULL, description TEXT NOT NULL DEFAULT '', startDate CHAR(19) NULL DEFAULT NULL, dueDate CHAR(19) NULL DEFAULT NULL, completionDate CHAR(19) NULL DEFAULT NULL, parentId INTEGER NULL DEFAULT NULL)"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxTaskFile ON Task (fileId)"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxTaskStatus ON Task (status)"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxTaskName ON Task (name)"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxTaskTaskCoachId ON Task (taskCoachId)"] exec];
			[[self statementWithSQL:@"CREATE INDEX idxTaskParentId ON Task (parentId)"] exec];
			[[self statementWithSQL:@"INSERT INTO Task SELECT * FROM migTask"] exec];
			[[self statementWithSQL:@"DROP TABLE migTask"] exec];
			// Default start and end hours
			[[self statementWithSQL:@"UPDATE Task SET startDate=startDate || ' 08:00:00'"] exec];
			[[self statementWithSQL:@"UPDATE Task SET dueDate=dueDate || ' 18:00:00'"] exec];
		}
	}
	
	NSLog(@"Database up to date.");
	
	[[self statementWithSQL:@"UPDATE Meta SET value=\"4\" WHERE name=\"version\""] exec];
}

- (void)onDatabaseVersion:(NSDictionary *)dict
{
	dbVersion = atoi([[dict objectForKey:@"value"] UTF8String]);
}

- initWithFilename:(NSString *)filename
{
	if (self = [super init])
	{
		if (sqlite3_open([filename UTF8String], &pDb) != SQLITE_OK)
		{
			@throw [NSException exceptionWithName:@"DatabaseError"
								reason:[NSString stringWithFormat:@"Could not open %@", filename]
								userInfo:nil];
		}
		
		if (sqlite3_create_collation(pDb, "CSDIA", SQLITE_UTF8, NULL, collation) != SQLITE_OK)
		{
			NSLog(@"Could not create collation.");
		}
		else
		{
			NSLog(@"Collation created.");
		}
		
		// Database upgrade from previous versions
		
		[[self statementWithSQL:@"SELECT value FROM Meta WHERE name=\"version\""] execWithTarget:self action:@selector(onDatabaseVersion:)];
		[self upgradeDatabase];
		[self recreateViews];
	}
	
	return self;
}

- (void)recreateViews
{
	// Re-create views
	[[self statementWithSQL:@"DROP VIEW IF EXISTS CurrentTask"] exec];
	[[self statementWithSQL:@"DROP VIEW IF EXISTS CurrentCategory"] exec];
	[[self statementWithSQL:@"DROP VIEW IF EXISTS CurrentEffort"] exec];
	[[self statementWithSQL:@"DROP VIEW IF EXISTS AllTask"] exec];
	[[self statementWithSQL:@"DROP VIEW IF EXISTS OverdueTask"] exec];
	[[self statementWithSQL:@"DROP VIEW IF EXISTS DueTodayTask"] exec]; // Obsolete anyway
	[[self statementWithSQL:@"DROP VIEW IF EXISTS DueSoonTask"] exec];
	[[self statementWithSQL:@"DROP VIEW IF EXISTS StartedTask"] exec];
	[[self statementWithSQL:@"DROP VIEW IF EXISTS NotStartedTask"] exec];
	
	[[self statementWithSQL:@"CREATE VIEW CurrentTask AS SELECT * FROM Task LEFT JOIN TaskCoachFile ON Task.fileId=TaskCoachFile.id WHERE TaskCoachFile.visible OR Task.fileId IS NULL"] exec];
	[[self statementWithSQL:@"CREATE VIEW CurrentCategory AS SELECT * FROM Category LEFT JOIN TaskCoachFile ON Category.fileId=TaskCoachFile.id WHERE TaskCoachFile.visible OR Category.fileId IS NULL"] exec];
	[[self statementWithSQL:@"CREATE VIEW CurrentEffort AS SELECT * FROM Effort LEFT JOIN TaskCoachFile ON Effort.fileId=TaskCoachFile.id WHERE (Effort.fileId == TaskCoachFile.id OR (Effort.fileId IS NULL AND TaskCoachFile.id IS NULL)) AND (TaskCoachFile.visible OR TaskCoachFile.id IS NULL)"] exec];
	
	[[self statementWithSQL:@"CREATE VIEW AllTask AS SELECT * FROM CurrentTask WHERE status != 3"] exec];
	[[self statementWithSQL:@"CREATE VIEW OverdueTask AS SELECT * FROM CurrentTask WHERE status != 3 AND dueDate < DATETIME('now', 'localtime')"] exec];
	[[self statementWithSQL:[NSString stringWithFormat:@"CREATE VIEW DueSoonTask AS SELECT * FROM CurrentTask WHERE status != 3 AND (dueDate >= DATETIME('now', 'localtime') AND dueDate < DATETIME('now', 'localtime', '+%d days')) AND startDate < DATETIME('now', 'localtime')", [Configuration configuration].soonDays]] exec];
	[[self statementWithSQL:[NSString stringWithFormat:@"CREATE VIEW StartedTask AS SELECT * FROM CurrentTask WHERE status != 3 AND startDate IS NOT NULL AND startDate <= DATETIME('now', 'localtime') AND (dueDate >= DATETIME('now', 'localtime', '+%d days') OR dueDate IS NULL)", [Configuration configuration].soonDays]] exec];
	[[self statementWithSQL:@"CREATE VIEW NotStartedTask AS SELECT * FROM CurrentTask WHERE status != 3 AND (startDate IS NULL OR startDate > DATETIME('now', 'localtime'))"] exec];
}

- (void)dealloc
{
	sqlite3_close(pDb);
	
	[super dealloc];
}

- (NSString *)errmsg
{
	return [NSString stringWithUTF8String:sqlite3_errmsg(pDb)];
}

- (sqlite3 *)connection
{
	return pDb;
}

- (Statement *)statementWithSQL:(NSString *)sql
{
	return [[[Statement alloc] initWithConnection:self andSQL:sql] autorelease];
}

- (void)begin
{
	[[self statementWithSQL:@"BEGIN"] exec];
	inTransaction = YES;
}

- (void)commit
{
	[[self statementWithSQL:@"COMMIT"] exec];
	inTransaction = NO;
}

- (void)rollback
{
	[[self statementWithSQL:@"ROLLBACK"] exec];
	inTransaction = NO;
}

- (NSInteger)lastRowID
{
	return sqlite3_last_insert_rowid(pDb);
}

@end
