//
//  DayHourState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 16/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "DayHourState.h"
#import "TwoWayState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Configuration.h"
#import "CDFile.h"

@implementation DayHourState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[DayHourState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	[self startWithFormat:"ii" count:NOCOUNT];
}

- (void)onNewObject:(NSArray *)value
{
	[Configuration configuration].cdCurrentFile.startHour = [value objectAtIndex:0];
	[Configuration configuration].cdCurrentFile.endHour = [value objectAtIndex:1];
	
	[self sendFormat:"i" values:[NSArray arrayWithObject:[NSNumber numberWithInt:1]]];
	
	myController.state = [TwoWayState stateWithNetwork:myNetwork controller:myController];
}

- (void)onFinished
{
}

@end
