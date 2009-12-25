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

- (void)onDatabaseUpgrade:(NSDictionary *)dict
{
	NSInteger version = atoi([(NSString *)[dict valueForKey:@"value"] UTF8String]);
	
	NSLog(@"Database version: %d", version);

	switch (version)
	{
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
			
			// Create the main file, if applicable.
			[[self statementWithSQL:@"SELECT value FROM Meta WHERE name=\"guid\""] execWithTarget:self action:@selector(upgradeFileTable:)];
		}
	}
	
	NSLog(@"Database up to date.");
	
	[[self statementWithSQL:@"UPDATE Meta SET value=\"3\" WHERE name=\"version\""] exec];
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

		// Database upgrade from previous versions
		
		[[self statementWithSQL:@"SELECT value FROM Meta WHERE name=\"version\""] execWithTarget:self action:@selector(onDatabaseUpgrade:)];

		// Re-create views
		[[self statementWithSQL:@"DROP VIEW IF EXISTS CurrentTask"] exec];
		[[self statementWithSQL:@"DROP VIEW IF EXISTS CurrentCategory"] exec];
		[[self statementWithSQL:@"DROP VIEW IF EXISTS AllTask"] exec];
		[[self statementWithSQL:@"DROP VIEW IF EXISTS OverdueTask"] exec];
		[[self statementWithSQL:@"DROP VIEW IF EXISTS DueTodayTask"] exec]; // Obsolete anyway
		[[self statementWithSQL:@"DROP VIEW IF EXISTS DueSoonTask"] exec];
		[[self statementWithSQL:@"DROP VIEW IF EXISTS StartedTask"] exec];
		[[self statementWithSQL:@"DROP VIEW IF EXISTS NotStartedTask"] exec];

		[[self statementWithSQL:@"CREATE VIEW CurrentTask AS SELECT * FROM Task LEFT JOIN TaskCoachFile ON Task.fileId=TaskCoachFile.id WHERE TaskCoachFile.visible OR Task.fileId IS NULL"] exec];
		[[self statementWithSQL:@"CREATE VIEW CurrentCategory AS SELECT * FROM Category LEFT JOIN TaskCoachFile ON Category.fileId=TaskCoachFile.id WHERE TaskCoachFile.visible OR Category.fileId IS NULL"] exec];

		[[self statementWithSQL:@"CREATE VIEW AllTask AS SELECT * FROM CurrentTask WHERE status != 3 ORDER BY name"] exec];
		[[self statementWithSQL:@"CREATE VIEW OverdueTask AS SELECT * FROM CurrentTask WHERE status != 3 AND dueDate < DATE('now') ORDER BY dueDate, startDate DESC"] exec];
		[[self statementWithSQL:[NSString stringWithFormat:@"CREATE VIEW DueSoonTask AS SELECT * FROM CurrentTask WHERE status != 3 AND (dueDate >= DATE('now') AND dueDate < DATE('now', '+%d days')) ORDER BY startDate DESC", [Configuration configuration].soonDays]] exec];
		[[self statementWithSQL:[NSString stringWithFormat:@"CREATE VIEW StartedTask AS SELECT * FROM CurrentTask WHERE status != 3 AND startDate IS NOT NULL AND startDate <= DATE('now') AND (dueDate >= DATE('now', '+%d days') OR dueDate IS NULL) ORDER BY startDate", [Configuration configuration].soonDays]] exec];
		[[self statementWithSQL:@"CREATE VIEW NotStartedTask AS SELECT * FROM CurrentTask WHERE status != 3 AND (startDate IS NULL OR startDate > DATE('now'))"] exec];
	}
	
	return self;
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
