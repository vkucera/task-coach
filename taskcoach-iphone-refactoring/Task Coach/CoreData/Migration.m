//
//  Migration.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 06/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

/*
 
#import <sqlite3.h>

#import "Task_CoachAppDelegate.h"
#import "Migration.h"
#import "Configuration.h"
#import "DateUtils.h"
#import "i18n.h"

#import "CDFile.h"
#import "CDCategory.h"
#import "CDTask.h"
#import "CDEffort.h"

 */

void migrateOldDatabase(NSString *filename)
{
    /*
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

		const char *s = (const char *)sqlite3_column_text(req, 1);
		if (s)
			file.name = [NSString stringWithUTF8String:s];
		else
			file.name = @"";

		s = (const char *)sqlite3_column_text(req, 2);
		if (s)
			file.guid = [NSString stringWithUTF8String:s];
		else
			file.guid = @""; // Hum

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
		{
			NSManagedObjectID *theId = [mapFiles objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 1)]];
			if (theId)
				category.file = (CDFile *)[getManagedObjectContext() objectWithID:theId];
		}
		
		const char *s = (const char *)sqlite3_column_text(req, 2);
		if (s)
			category.name = [NSString stringWithUTF8String:s];
		else
			category.name = @"";

		category.status = [NSNumber numberWithInt:sqlite3_column_int(req, 3)];
		
		const char *catTCId = (const char *)sqlite3_column_text(req, 4);
		if (catTCId)
			category.taskCoachId = [NSString stringWithUTF8String:catTCId];

		if (sqlite3_column_type(req, 5) != SQLITE_NULL)
		{
			NSManagedObjectID *theId = [mapCategories objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 5)]];
			if (theId)
				category.parent = (CDCategory *)[getManagedObjectContext() objectWithID:theId];
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
		{
			NSManagedObjectID *theId = [mapFiles objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 1)]];
			if (theId)
				task.file = (CDFile *)[getManagedObjectContext() objectWithID:theId];
		}

		const char *s = (const char *)sqlite3_column_text(req, 2);
		if (s)
			task.name = [NSString stringWithUTF8String:s];
		else
			task.name = @"";

		task.status = [NSNumber numberWithInt:sqlite3_column_int(req, 3)];
		
		const char *taskTCId = (const char *)sqlite3_column_text(req, 4);
		if (taskTCId)
			task.taskCoachId = [NSString stringWithUTF8String:taskTCId];

		s = (const char *)sqlite3_column_text(req, 5);
		if (s)
			task.longDescription = [NSString stringWithUTF8String:s];
		else
			task.longDescription = @"";

		task.priority = [NSNumber numberWithInt:0];
		
		if (sqlite3_column_type(req, 6) != SQLITE_NULL)
			task.startDate = [[TimeUtils instance] dateFromString:[[NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 6)] stringByAppendingString:@" 00:00:00"]];
		
		if (sqlite3_column_type(req, 7) != SQLITE_NULL)
			task.dueDate = [[TimeUtils instance] dateFromString:[[NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 7)] stringByAppendingString:@" 23:59:59"]];
		
		if (sqlite3_column_type(req, 8) != SQLITE_NULL)
			task.completionDate = [[TimeUtils instance] dateFromString:[[NSString stringWithUTF8String:(const char *)sqlite3_column_text(req, 8)] stringByAppendingString:@" 00:00:00"]];
		
		if (sqlite3_column_type(req, 9) != SQLITE_NULL)
		{
			NSManagedObjectID *theId = [mapTasks objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 9)]];
			if (theId)
				task.parent = (CDTask *)[getManagedObjectContext() objectWithID:theId];
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
		{
			NSManagedObjectID *theId = [mapFiles objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 1)]];
			if (theId)
				effort.file = (CDFile *)[getManagedObjectContext() objectWithID:theId];
		}

		const char *s = (const char *)sqlite3_column_text(req, 2);
		if (s)
			effort.name = [NSString stringWithUTF8String:s];
		else
			effort.name = @"";

		effort.status = [NSNumber numberWithInt:sqlite3_column_int(req, 3)];
		
		const char *effortTCId = (const char *)sqlite3_column_text(req, 4);
		if (effortTCId)
			effort.taskCoachId = [NSString stringWithUTF8String:effortTCId];

		if (sqlite3_column_type(req, 5) != SQLITE_NULL)
		{
			NSManagedObjectID *theId = [mapTasks objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 5)]];
			if (theId)
				effort.task = (CDTask *)[getManagedObjectContext() objectWithID:theId];
		}

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
		NSManagedObjectID *taskId = [mapTasks objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 0)]];
		NSManagedObjectID *categoryId = [mapCategories objectForKey:[NSNumber numberWithInt:sqlite3_column_int(req, 1)]];
		
		if (taskId && categoryId)
		{
			CDTask *task = (CDTask *)[getManagedObjectContext() objectWithID:taskId];
			CDCategory *category = (CDCategory *)[getManagedObjectContext() objectWithID:categoryId];
			[task addCategoriesObject:category];
		}
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
     */
}
