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
#import "i18n.h"
#import "DateUtils.h"
#import "LogUtils.h"

@implementation BaseState

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	if ((self = [super init]))
	{
		myNetwork = network;
		myController = controller;
	}
	
	return self;
}

- (void)sendDate:(NSDate *)date
{
	if (date)
	{
		[myNetwork appendString:[[TimeUtils instance] stringFromDate:date]];
	}
	else
	{
		[myNetwork appendString:nil];
	}
}

- (NSDate *)parseDate:(id)date
{
	if (date == [NSNull null])
		return nil;

	return [[TimeUtils instance] dateFromString:date];
}

- (void)networkDidClose:(Network *)network controller:(SyncViewController *)controller
{
	JLERROR("Connection closed.");

	controller.state = nil;
	
	UIAlertView *view = [[UIAlertView alloc] initWithTitle:_("Error")
				message:_("The connection was unexpectedly closed.")
				delegate:controller cancelButtonTitle:_("Abort") otherButtonTitles:nil];
	[view show];
	[view release];
	
	// XXXTODO: rollback ?
}

- (void)networkDidEncounterError:(Network *)network error:(NSError *)error controller:(SyncViewController *)controller
{
	JLERROR("Network error: %s", [[error description] UTF8String]);

	controller.state = nil;

	UIAlertView *view = [[UIAlertView alloc] initWithTitle:_("Error")
												  message:[NSString stringWithFormat:_("A network error occurred: %@"), [error localizedDescription]]
												  delegate:controller cancelButtonTitle:_("Abort") otherButtonTitles:nil];
	[view show];
	[view release];
	
	// XXXTODO: rollback ?
}

- (void)cancel
{
	JLDEBUG("Cancelling");

	myController.state = nil;
	[myNetwork close];
	
	// XXXTODO: rollback ?
}

@end
