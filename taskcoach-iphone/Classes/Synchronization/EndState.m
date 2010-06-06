//
//  EndState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TaskCoachAppDelegate.h"
#import "EndState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "i18n.h"

@implementation EndState

- (void)activated
{
	NSError *error;
	if (![getManagedObjectContext() save:&error])
	{
		NSLog(@"Could not save: %@", [error localizedDescription]);
		assert(0);
	}
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[EndState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)networkDidClose:(Network *)network controller:(SyncViewController *)controller
{
	controller.state = nil;
	[controller finished:isOK];
}

- (void)networkDidEncounterError:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	// n/a
}

@end
