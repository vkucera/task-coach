//
//  FullFromDesktopTaskState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 06/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "FullFromDesktopTaskState.h"
#import "FullFromDesktopEffortState.h"
#import "SyncViewController.h"
#import "Configuration.h"
#import "DateUtils.h"
#import "LogUtils.h"

#import "CDTask.h"
#import "CDTask+Addons.h"
#import "CDDomainObject+Addons.h"

@implementation FullFromDesktopTaskState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[FullFromDesktopTaskState alloc] initWithNetwork:network controller:controller] autorelease];
}

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	if ((self = [super initWithNetwork:network controller:controller]))
	{
		request = [[NSFetchRequest alloc] init];
	}

	return self;
}

- (void)dealloc
{
	[request release];

	[super dealloc];
}

- (void)activated
{
	JLDEBUG("=== Full from desktop task");

	[self startWithFormat:"ssszzzzziiiii[s]" count:myController.taskCount];
}

- (void)onNewObject:(NSArray *)value
{
	CDTask *task = [NSEntityDescription insertNewObjectForEntityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()];

	task.creationDate = [NSDate date];
	task.name = [value objectAtIndex:0];
	task.status = [NSNumber numberWithInt:STATUS_NONE];
	task.taskCoachId = [value objectAtIndex:1];
	task.longDescription = [value objectAtIndex:2];
	task.startDate = [self parseDate:[value objectAtIndex:3]];
	task.dueDate = [self parseDate:[value objectAtIndex:4]];
	task.completionDate = [self parseDate:[value objectAtIndex:5]];
	task.reminderDate = [self parseDate:[value objectAtIndex:6]];
	task.priority = [value objectAtIndex:8];
	
	JLDEBUG("New task from desktop: \"%s\"", [task.name UTF8String]);

	if ([[value objectAtIndex:9] intValue])
	{
		task.recPeriod = [value objectAtIndex:10];
	}
	task.recRepeat = [value objectAtIndex:11];
	task.recSameWeekday = [value objectAtIndex:12];

	[task computeDateStatus];
	task.file = [Configuration configuration].cdCurrentFile;

	if ([value objectAtIndex:7] != [NSNull null])
	{
		[request setEntity:[NSEntityDescription entityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()]];
		[request setPredicate:[NSPredicate predicateWithFormat:@"taskCoachId == %@", [value objectAtIndex:7]]];
		NSError *error;
		NSArray *results = [getManagedObjectContext() executeFetchRequest:request error:&error];

		if (results)
		{
			assert([results count] == 1);
			task.parent = [results objectAtIndex:0];
		}
		else
		{
			JLERROR("Could not find parent task: %s", [[error localizedDescription] UTF8String]);
		}
	}

	if ([[value objectAtIndex:13] count])
	{
		JLDEBUG("Category count: %d", [[value objectAtIndex:13] count]);

		[request setEntity:[NSEntityDescription entityForName:@"CDCategory" inManagedObjectContext:getManagedObjectContext()]];
		[request setPredicate:[NSPredicate predicateWithFormat:@"taskCoachId IN %@", [NSSet setWithArray:[value objectAtIndex:13]]]];
		NSError *error;
		NSArray *results = [getManagedObjectContext() executeFetchRequest:request error:&error];

		if (results)
		{
			[task addCategories:[NSSet setWithArray:results]];
		}
		else
		{
			JLERROR("Could not find task categories: %s", [[error localizedDescription] UTF8String]);
		}
	}

	[myController increment];
	[self sendFormat:"i" values:[NSArray arrayWithObject:[NSNumber numberWithInt:1]]];
}

- (void)onFinished
{
	JLDEBUG("=== Finished");

	myController.state = [FullFromDesktopEffortState stateWithNetwork:myNetwork controller:myController];
}

@end
