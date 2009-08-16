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
		// Re-create views
		[[self statementWithSQL:@"DROP VIEW IF EXISTS AllTask"] exec];
		[[self statementWithSQL:@"DROP VIEW IF EXISTS OverdueTask"] exec];
		[[self statementWithSQL:@"DROP VIEW IF EXISTS DueTodayTask"] exec]; // Obsolete anyway
		[[self statementWithSQL:@"DROP VIEW IF EXISTS DueSoonTask"] exec];
		[[self statementWithSQL:@"DROP VIEW IF EXISTS StartedTask"] exec];
		[[self statementWithSQL:@"DROP VIEW IF EXISTS NotStartedTask"] exec];

		[[self statementWithSQL:@"CREATE VIEW AllTask AS SELECT * FROM Task WHERE status != 3 ORDER BY name"] exec];
		[[self statementWithSQL:@"CREATE VIEW OverdueTask AS SELECT * FROM Task WHERE status != 3 AND dueDate < DATE('now') ORDER BY dueDate, startDate DESC"] exec];
		[[self statementWithSQL:[NSString stringWithFormat:@"CREATE VIEW DueSoonTask AS SELECT * FROM Task WHERE status != 3 AND (dueDate >= DATE('now') AND dueDate < DATE('now', '+%d days')) ORDER BY startDate DESC", [Configuration configuration].soonDays]] exec];
		[[self statementWithSQL:[NSString stringWithFormat:@"CREATE VIEW StartedTask AS SELECT * FROM Task WHERE status != 3 AND startDate IS NOT NULL AND startDate <= DATE('now') AND (dueDate >= DATE('now', '+%d days') OR dueDate IS NULL) ORDER BY startDate", [Configuration configuration].soonDays]] exec];
		[[self statementWithSQL:@"CREATE VIEW NotStartedTask AS SELECT * FROM Task WHERE status != 3 AND (startDate IS NULL OR startDate > DATE('now'))"] exec];
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
