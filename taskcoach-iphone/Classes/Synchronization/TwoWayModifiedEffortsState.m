//
//  TwoWayModifiedEffortsState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 22/01/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TwoWayModifiedEffortsState.h"
#import "FullFromDesktopState.h"
#import "SyncViewController.h"
#import "LogUtils.h"

#import "CDDomainObject+Addons.h"
#import "CDEffort.h"

@implementation TwoWayModifiedEffortsState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayModifiedEffortsState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	JLDEBUG("=== Two way modified efforts");

	[super activated];
}

- (void)packObject:(CDEffort *)effort
{
	JLDEBUG("Packing effort \"%s\"", [effort.name UTF8String]);

	[self sendFormat:"ss" values:[NSArray arrayWithObjects:effort.taskCoachId, effort.name, nil]];
	[self sendDate:effort.started];
	[self sendDate:effort.ended];
}

- (void)onFinished
{
	JLDEBUG("=== Finished");

	myController.state = [FullFromDesktopState stateWithNetwork:myNetwork controller:myController];
}

- (NSString *)entityName
{
	return @"CDEffort";
}

- (NSInteger)status
{
	return STATUS_MODIFIED;
}

@end
