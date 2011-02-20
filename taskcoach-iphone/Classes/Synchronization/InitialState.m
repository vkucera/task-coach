//
//  InitialState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "InitialState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "ProtocolNegotiationState.h"
#import "Configuration.h"
#import "i18n.h"
#import "LogUtils.h"

// Initial state just waits for the connection to be established.

@implementation InitialState

- (void)activated
{
	LogCreateFile();

	JLDEBUG("=== Initial state.");

	myController.label.text = _("Connecting...");
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[InitialState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	JLDEBUG("Connected.");

	controller.state = [ProtocolNegotiationState stateWithNetwork:network controller:controller];
}

- (void)networkDidClose:(Network *)network controller:(SyncViewController *)controller
{
	JLERROR("Connection closed in initial state!");
}

- (void)networkDidEncounterError:(Network *)network error:(NSError *)error controller:(SyncViewController *)controller
{
	controller.state = nil;

	[Configuration configuration].domain = nil;
	[Configuration configuration].name = nil;
	[[Configuration configuration] save];

	UIAlertView *view = [[UIAlertView alloc] initWithTitle:_("Connection error")
												   message:_("An error occurred while connecting to the remote host. Please check your settings. Also check that Task Coach is running on the remote host. Last, check your firewall settings.")
												  delegate:controller cancelButtonTitle:_("Abort") otherButtonTitles:nil];
	[view show];
	[view release];

	JLERROR("Connection error: %s", [[error description] UTF8String]);
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	// n/a
}

@end
