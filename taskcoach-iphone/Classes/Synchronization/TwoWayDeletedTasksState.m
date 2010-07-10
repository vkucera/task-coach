//
//  TwoWayDeletedTasksState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TwoWayDeletedTasksState.h"
#import "TwoWayModifiedTasksState.h"
#import "LogUtils.h"

#import "Network.h"
#import "SyncViewController.h"

#import "CDDomainObject+Addons.h"
#import "CDTask.h"

@implementation TwoWayDeletedTasksState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayDeletedTasksState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	JLDEBUG("=== Two way deleted tasks");

	[super activated];
}

- (void)packObject:(CDTask *)task
{
	JLDEBUG("Packing task \"%s\"", [task.name UTF8String]);

	[self sendFormat:"s" values:[NSArray arrayWithObject:task.taskCoachId]];
}

- (void)onFinished
{
	JLDEBUG("=== Finished");

	myController.state = [TwoWayModifiedTasksState stateWithNetwork:myNetwork controller:myController];
}

- (NSString *)entityName
{
	return @"CDTask";
}

- (NSInteger)status
{
	return STATUS_DELETED;
}

- (NSString *)ordering
{
	return @"creationDate";
}

@end
