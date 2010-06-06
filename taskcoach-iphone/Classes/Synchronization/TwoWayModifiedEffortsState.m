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

#import "CDDomainObject+Addons.h"
#import "CDEffort.h"

@implementation TwoWayModifiedEffortsState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	/*
	NSObject <State> *next = [FullFromDesktopState stateWithNetwork:network controller:controller];
	
	return [[[TwoWayModifiedEffortsState alloc] initWithNetwork:network controller:controller nextState:next expectIds:NO] autorelease];
	 */
	
	return [[[TwoWayModifiedEffortsState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)packObject:(CDEffort *)effort
{
	[self sendFormat:"ss" values:[NSArray arrayWithObjects:effort.taskCoachId, effort.name, nil]];
	[self sendDate:effort.started];
	[self sendDate:effort.ended];
}

- (void)onFinished
{
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
