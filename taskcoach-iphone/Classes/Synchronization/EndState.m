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
#import "LogUtils.h"

@implementation EndState

- (void)activated
{
	JLDEBUG("=== End state.");

	NSError *error;
	if (![getManagedObjectContext() save:&error])
	{
		JLERROR("Could not save: %s", [[error localizedDescription] UTF8String]);
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:[error localizedDescription] delegate:nil cancelButtonTitle:_("OK") otherButtonTitles:nil, nil];
        [alert show];
        [alert release];
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
	JLDEBUG("Connection closed.");

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
