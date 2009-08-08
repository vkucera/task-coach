//
//  ProtocolNegotiationState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "ProtocolNegotiationState.h"
#import "AuthentificationState.h"
#import "Network.h"
#import "SyncViewController.h"

#import "Database.h"

@implementation ProtocolNegotiationState

- (void)activated
{
	myController.label.text = NSLocalizedString(@"Protocol negotiation...", @"Protocol negotiation title");
	[myNetwork expect:4];
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[ProtocolNegotiationState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	int32_t version = ntohl(*((int32_t *)[data bytes]));
	int32_t response = 0;

	NSLog(@"Protocol version: %d", version);
	
	switch (version)
	{
		case 1:
		case 2:
			response = 1;
			break;
	}

	[network appendInteger:response];

	if (response)
	{
		NSLog(@"Accepted protocol %d.", version);
		controller.protocolVersion = version;

		if (version != 2)
		{
			UIAlertView *view = [[UIAlertView alloc] initWithTitle:NSLocalizedString(@"Warning", @"Protocol version low warning title")
	                               message:[NSString stringWithFormat:NSLocalizedString(@"It seems that the desktop Task Coach version is too old. Please consider upgrading (you may loose some data if you go on anyway).",
																						@"Protocol version low warning message"), version]
														  delegate:self cancelButtonTitle:NSLocalizedString(@"Abort", @"Protocol version low abort button title") otherButtonTitles:nil];
			[view addButtonWithTitle:NSLocalizedString(@"Go on", @"Protocol version go on button title")];
			[view show];
			[view release];
			return;
		}

		controller.state = [AuthentificationState stateWithNetwork:network controller:controller];
	}
	else
	{
		[network expect:4];
	}
}

// UIAlertViewDelegate.

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex
{
	if (buttonIndex == 0) // Abort
	{
		[myController finished:NO];
		[self cancel];
	}
	else
	{
		myController.state = [AuthentificationState stateWithNetwork:myNetwork controller:myController];
	}
}

@end
