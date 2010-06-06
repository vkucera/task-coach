//
//  TaskFileNameState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/12/09.
//  Copyright 2009 Jérôme Laheurte. All rights reserved.
//

#import "TaskFileNameState.h"
#import "TwoWayState.h"
#import "DayHourState.h"
#import "Network.h"
#import "Configuration.h"
#import "SyncViewController.h"

#import "CDFile.h"

@implementation TaskFileNameState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TaskFileNameState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	[self startWithFormat:"s" count:NOCOUNT];
}

- (void)onNewObject:(NSArray *)value
{
	NSString *filename = [value objectAtIndex:0];
	
	NSLog(@"Filename: %@", filename);
	
	[Configuration configuration].cdCurrentFile.name = filename;
	
	[self sendFormat:"i" values:[NSArray arrayWithObject:[NSNumber numberWithInt:1]]];
	
	myController.state = [DayHourState stateWithNetwork:myNetwork controller:myController];
}

- (void)finished
{
}

@end
