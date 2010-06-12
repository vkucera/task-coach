//
//  Migration.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 06/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <sqlite3.h>

#import "TaskCoachAppDelegate.h"
#import "Migration.h"
#import "Configuration.h"
#import "DateUtils.h"
#import "i18n.h"

#import "CDFile.h"
#import "CDCategory.h"
#import "CDTask.h"
#import "CDEffort.h"

void migrateOldDatabase(NSString *filename)
{
	sqlite3 *cn;
	int rc;

	NSLog(@"Starting CoreData migration.");

	if (sqlite3_open([filename UTF8String], &cn) != SQLITE_OK)
	{
		@throw [NSException exceptionWithName:@"DatabaseError"
									   reason:[NSString stringWithFormat:@"Could not open %@", filename]
									 userInfo:nil];
	}

	sqlite3_stmt *req;

	if (sqlite3_prepare_v2(cn, "SELECT value FROM Meta WHERE name=\"version\"", -1, &req, NULL) != SQLITE_OK)
	{
		@throw [NSException exceptionWithName:@"DatabaseError" reason:[NSString stringWithUTF8String:sqlite3_errmsg(cn)] userInfo:nil];
	}

	NSInteger version = 0;
	if ((rc = sqlite3_step(req)) == SQLITE_ROW)
	{
		version = atoi((const char*)sqlite3_column_text(req, 0));
	}

	if (version != 3)
		@throw [NSException exceptionWithName:@"DatabaseError" reason:_("Database version too old") userInfo:nil];

	sqlite3_finalize(req);

	// Files
	
	NSMutableDictionary *mapFiles = [[NSMutableDictionary alloc] init];
	
	if (sqlite3_prepare_v2(cn, "SELECT id, name, guid, visible FROM TaskCoachFile", -1, &req, NULL) != SQLITE_OK)
	{
		@throw [NSException exceptionWithName:@"DatabaseError" reason:[NSString stringWithUTF8String:sqlite3_errmsg(cn)] userInfo:nil];
	}

	while ((rc = sqlite3_step(req)) == SQLITE_ROW)
	{
		CDFile *file = [NSEntityDescription insertNewObjectForEntityForName:@"CDFile" inManagedObjectContext:getManagedObjectContext()];

		file.name = [NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 1)];
		file.guid = [NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 2)];

		if (sqlite3_column_int(req, 3))
		{
			NSLog(@"Current file: %@", file.name);

			[Configuration configuration].cdCurrentFile = file;
			[[Configuration configuration] save];
		}

		[mapFiles setObject:file.objectID forKey:[NSNumber numberWithInt:sqlite3_column_int(req, 0)]];

		NSLog(@"Migrated file %@", file.name);
	}

	sqlite3_finalize(req);

	// Categories

	NSMutableDictionary *mapCategories = [[NSMutableDictionary alloc] init]; // sqlite id => CoreData id

	if (sqlite3_prepare_v2(cn, "SELECT id, fileId, name, status, taskCoachId, parentId FROM Category ORDER BY id", -1, &req, NULL) != SQLITE_OK)
	{
		@throw [NSException exceptionWithName:@"DatabaseError" reason:[NSString stringWithUTF8String:sqlite3_errmsg(cn)] userInfo:nil];
	}

	while ((rc = sqlite3_step(req)) == SQLITE_ROW)
	{
		CDCategory *category = [NSEntityDescription insertNewObjectForEntityForName:@"CDCategory" inManagedObjectContext:getManagedObjectContext()];

		if (sqlite3_column_type(req, 1) != SQLITE_NULL)
			category.file = (CDFile *)[getManagedObjectContext() objectWithID:[mapFiles objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 1)]]];

		category.name = [NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 2)];
		category.status = [NSNumber numberWithInt:sqlite3_column_int(req, 3)];
		category.taskCoachId = [NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 4)];

		if (sqlite3_column_type(req, 5) != SQLITE_NULL)
		{
			category.parent = (CDCategory *)[getManagedObjectContext() objectWithID:[mapCategories objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 5)]]];
		}

		category.creationDate = [NSDate date];

		[mapCategories setObject:category.objectID forKey:[NSNumber numberWithInt:sqlite3_column_int(req, 0)]];

		NSLog(@"Migrated category %@ (status %@; file %@)", category.name, category.status, category.file.name);
	}

	sqlite3_finalize(req);
	
	// Tasks

	NSMutableDictionary *mapTasks = [[NSMutableDictionary alloc] init];

	if (sqlite3_prepare_v2(cn, "SELECT id, fileId, name, status, taskCoachId, description, startDate, dueDate, completionDate, parentId FROM Task ORDER BY id", -1, &req, NULL) != SQLITE_OK)
	{
		@throw [NSException exceptionWithName:@"DatabaseError" reason:[NSString stringWithUTF8String:sqlite3_errmsg(cn)] userInfo:nil];
	}

	while ((rc = sqlite3_step(req)) == SQLITE_ROW)
	{
		CDTask *task = [NSEntityDescription insertNewObjectForEntityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()];
		
		if (sqlite3_column_type(req, 1) != SQLITE_NULL)
			task.file = (CDFile *)[getManagedObjectContext() objectWithID:[mapFiles objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 1)]]];
		
		task.name = [NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 2)];
		task.status = [NSNumber numberWithInt:sqlite3_column_int(req, 3)];
		task.taskCoachId = [NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 4)];
		task.longDescription = [NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 5)];
		task.priority = [NSNumber numberWithInt:0];
		
		if (sqlite3_column_type(req, 6) != SQLITE_NULL)
			task.startDate = [[TimeUtils instance] dateFromString:[[NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 6)] stringByAppendingString:@" 00:00:00"]];
		
		if (sqlite3_column_type(req, 7) != SQLITE_NULL)
			task.dueDate = [[TimeUtils instance] dateFromString:[[NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 7)] stringByAppendingString:@" 23:59:59"]];
		
		if (sqlite3_column_type(req, 8) != SQLITE_NULL)
			task.completionDate = [[TimeUtils instance] dateFromString:[[NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 8)] stringByAppendingString:@" 00:00:00"]];
		
		if (sqlite3_column_type(req, 9) != SQLITE_NULL)
		{
			task.parent = (CDTask *)[getManagedObjectContext() objectWithID:[mapTasks objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 9)]]];
		}

		task.creationDate = [NSDate date];

		[mapTasks setObject:task.objectID forKey:[NSNumber numberWithInt:sqlite3_column_int(req, 0)]];
	}

	sqlite3_finalize(req);

	// Efforts
	
	if (sqlite3_prepare_v2(cn, "SELECT id, fileId, name, status, taskCoachId, taskId, started, ended FROM Effort ORDER BY id", -1, &req, NULL) != SQLITE_OK)
	{
		@throw [NSException exceptionWithName:@"DatabaseError" reason:[NSString stringWithUTF8String:sqlite3_errmsg(cn)] userInfo:nil];
	}
	
	while ((rc = sqlite3_step(req)) == SQLITE_ROW)
	{
		CDEffort *effort = [NSEntityDescription insertNewObjectForEntityForName:@"CDEffort" inManagedObjectContext:getManagedObjectContext()];
		
		if (sqlite3_column_type(req, 1) != SQLITE_NULL)
			effort.file = (CDFile *)[getManagedObjectContext() objectWithID:[mapFiles objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 1)]]];
		
		effort.name = [NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 2)];
		effort.status = [NSNumber numberWithInt:sqlite3_column_int(req, 3)];
		effort.taskCoachId = [NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 4)];

		if (sqlite3_column_type(req, 5) != SQLITE_NULL)
			effort.task = (CDTask *)[getManagedObjectContext() objectWithID:[mapTasks objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 5)]]];
		
		effort.started = [[TimeUtils instance] dateFromString:[NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 6)]];
		if (sqlite3_column_type(req, 7) != SQLITE_NULL)
			effort.ended = [[TimeUtils instance] dateFromString:[NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 7)]];
		
	}

	sqlite3_finalize(req);
	[mapFiles release];

	// Task <=> Category association
	
	if (sqlite3_prepare_v2(cn, "SELECT idTask, idCategory FROM TaskHasCategory", -1, &req, NULL) != SQLITE_OK)
	{
		@throw [NSException exceptionWithName:@"DatabaseError" reason:[NSString stringWithUTF8String:sqlite3_errmsg(cn)] userInfo:nil];
	}
	
	while ((rc = sqlite3_step(req)) == SQLITE_ROW)
	{
		CDTask *task = (CDTask *)[getManagedObjectContext() objectWithID:[mapTasks objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 0)]]];
		CDCategory *category = (CDCategory *)[getManagedObjectContext() objectWithID:[mapCategories objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 1)]]];
		[task addCategoriesObject:category];
	}

	sqlite3_finalize(req);
	[mapTasks release];
	[mapCategories release];

	NSError *error;
	if (![getManagedObjectContext() save:&error])
	{
		@throw [NSException exceptionWithName:@"DatabaseError" reason:[error localizedDescription] userInfo:nil];
	}
	
	NSLog(@"CoreData migration ended.");
}
