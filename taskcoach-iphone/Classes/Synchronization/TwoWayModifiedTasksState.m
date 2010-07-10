//
//  TwoWayModifiedTasksState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TwoWayModifiedTasksState.h"
#import "TwoWayNewEffortsState.h"

#import "DateUtils.h"
#import "Network.h"
#import "SyncViewController.h"
#import "LogUtils.h"

#import "CDDomainObject+Addons.h"
#import "CDTask.h"
#import "CDCategory.h"

@implementation TwoWayModifiedTasksState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayModifiedTasksState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	JLDEBUG("=== Two way modified tasks");

	[super activated];
}

- (void)packObject:(CDTask *)task
{
	JLDEBUG("Packing task \"%s\"", [task.name UTF8String]);

	[self sendFormat:"sss" values:[NSArray arrayWithObjects:task.name, task.taskCoachId, task.longDescription, nil]];
	[self sendDate:task.startDate];
	[self sendDate:task.dueDate];
	[self sendDate:task.completionDate];
	[self sendDate:task.reminderDate];
	
	[self sendFormat:"iiiii" values:[NSArray arrayWithObjects:
									 task.priority,
									[NSNumber numberWithInt:task.recPeriod != nil],
									[NSNumber numberWithInt:[task.recPeriod intValue]],
									[NSNumber numberWithInt:[task.recRepeat intValue]],
									[NSNumber numberWithInt:[task.recSameWeekday intValue]],
									nil]];

	[self sendFormat:"i" values:[NSArray arrayWithObject:[NSNumber numberWithInt:[task.categories count]]]];

	for (CDCategory *category in task.categories)
	{
		JLDEBUG("Sending task category \"%s\"", [category.name UTF8String]);

		[self sendFormat:"s" values:[NSArray arrayWithObject:category.taskCoachId]];
	}
}

- (void)onFinished
{
	JLDEBUG("=== Finished");

	myController.state = [TwoWayNewEffortsState stateWithNetwork:myNetwork controller:myController];
}

- (NSString *)entityName
{
	return @"CDTask";
}

- (NSInteger) status
{
	return STATUS_MODIFIED;
}

- (NSString *)ordering
{
	return @"creationDate";
}

@end
