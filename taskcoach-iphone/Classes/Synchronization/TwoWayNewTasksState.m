//
//  TwoWayNewTasksState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TwoWayNewTasksState.h"
#import "TwoWayDeletedTasksState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "DateUtils.h"

#import "CDDomainObject+Addons.h"
#import "CDTask.h"
#import "CDCategory.h"

@implementation TwoWayNewTasksState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayNewTasksState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)packObject:(CDTask *)task
{
	NSLog(@"Sending task %@", task.name);
	
	[self sendFormat:"ss" values:[NSArray arrayWithObjects:task.name, task.longDescription, nil]];
	[self sendDate:task.startDate];
	[self sendDate:task.dueDate];
	[self sendDate:task.completionDate];
	[self sendDate:task.reminderDate];

	[self sendFormat:"iiii" values:[NSArray arrayWithObjects:
									[NSNumber numberWithInt:task.recPeriod != nil],
									[NSNumber numberWithInt:[task.recPeriod intValue]],
									[NSNumber numberWithInt:[task.recRepeat intValue]],
									[NSNumber numberWithInt:[task.recSameWeekday intValue]],
									nil]];

	if (task.parent)
		[self sendFormat:"s" values:[NSArray arrayWithObject:task.parent.taskCoachId]];
	else
		[self sendFormat:"s" values:[NSArray arrayWithObject:[NSNull null]]];

	[self sendFormat:"i" values:[NSArray arrayWithObject:[NSNumber numberWithInt:[task.categories count]]]];

	for (CDCategory *category in task.categories)
		[self sendFormat:"s" values:[NSArray arrayWithObject:category.taskCoachId]];
}

- (void)onFinished
{
	myController.state = [TwoWayDeletedTasksState stateWithNetwork:myNetwork controller:myController];
}

- (NSString *)entityName
{
	return @"CDTask";
}

- (NSInteger)status
{
	return STATUS_NEW;
}

- (NSString *)ordering
{
	return @"creationDate";
}

@end
