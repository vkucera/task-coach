//
//  BaseState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "BaseState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "i18n.h"

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
	
	UIAlertView *view = [[UIAlertView alloc] initWithTitle:_("Error")
				message:_("The connection was unexpectedly closed.")
				delegate:controller cancelButtonTitle:_("Abort") otherButtonTitles:nil];
	[view show];
	[view release];
	[[Database connection] rollback];
}

- (void)networkDidEncounterError:(Network *)network error:(NSError *)error controller:(SyncViewController *)controller
{
	NSLog(@"Network error.");

	controller.state = nil;

	UIAlertView *view = [[UIAlertView alloc] initWithTitle:_("Error")
												  message:[NSString stringWithFormat:_("A network error occurred: %@"), [error localizedDescription]]
												  delegate:controller cancelButtonTitle:_("Abort") otherButtonTitles:nil];
	[view show];
	[view release];
	[[Database connection] rollback];
}

- (void)cancel
{
	myController.state = nil;
	[myNetwork close];
	[[Database connection] rollback];
}

@end
