//
//  TwoWayEffortsState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 27/12/09.
//  Copyright 2009 Jérôme Laheurte. All rights reserved.
//

#import "TwoWayNewEffortsState.h"
#import "TwoWayModifiedEffortsState.h"

#import "Network.h"
#import "SyncViewController.h"
#import "DateUtils.h"
#import "LogUtils.h"

#import "CDDomainObject+Addons.h"
#import "CDEffort.h"
#import "CDTask.h"

@implementation TwoWayNewEffortsState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayNewEffortsState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	JLDEBUG("=== Two way new efforts");

	[super activated];
}

- (void)packObject:(CDEffort *)effort
{
	JLDEBUG("Packing effort \"%s\"", [effort.name UTF8String]);

	[self sendFormat:"s" values:[NSArray arrayWithObject:effort.name]];

	if (effort.task)
		[self sendFormat:"s" values:[NSArray arrayWithObject:effort.task.taskCoachId]];
	else
		[self sendFormat:"s" values:[NSArray arrayWithObject:[NSNull null]]];

	[self sendDate:effort.started];
	[self sendDate:effort.ended];
}

- (void)onFinished
{
	JLDEBUG("=== Finished");

	myController.state = [TwoWayModifiedEffortsState stateWithNetwork:myNetwork controller:myController];
}

- (NSString *)entityName
{
	return @"CDEffort";
}

- (NSInteger)status
{
	return STATUS_NEW;
}

@end
