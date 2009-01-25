//
//  BaseState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "BaseState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"

@implementation BaseState

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	if (self = [super init])
	{
		myNetwork = network;
		myController = controller;
	}
	
	return self;
}

- (void)networkDidClose:(Network *)network controller:(SyncViewController *)controller
{
	NSLog(@"Connection closed.");

	controller.state = nil;
	
	UIAlertView *view = [[UIAlertView alloc] initWithTitle:NSLocalizedString(@"Error", @"Connection closed error title")
				message:NSLocalizedString(@"The connection was unexpectedly closed.", @"Connection closed error message")
				delegate:controller cancelButtonTitle:NSLocalizedString(@"Abort", @"Connection closed cancel button title") otherButtonTitles:nil];
	[view show];
	[view release];
	[network release];
	[[Database connection] rollback];
}

- (void)networkDidEncounterError:(Network *)network controller:(SyncViewController *)controller
{
	NSLog(@"Network error.");

	controller.state = nil;

	UIAlertView *view = [[UIAlertView alloc] initWithTitle:NSLocalizedString(@"Error", @"Network error title")
												   message:NSLocalizedString(@"A network error occurred.", @"Network error message")
												  delegate:controller cancelButtonTitle:NSLocalizedString(@"Abort", @"Network error cancel button title") otherButtonTitles:nil];
	[view show];
	[view release];
	[network release];
	[[Database connection] rollback];
}

@end
