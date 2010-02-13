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
#import "i18n.h"

@implementation ProtocolNegotiationState

- (void)activated
{
	myController.label.text = _("Protocol negotiation...");
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

	// Starting with 2.0, protocols 1, 2 and 3 are not supported any more on the iPhone app.

	switch (version)
	{
		case 4:
			response = 1;
			break;
	}

	[network appendInteger:response];

	if (response)
	{
		NSLog(@"Accepted protocol %d.", version);
		controller.protocolVersion = version;
		controller.state = [AuthentificationState stateWithNetwork:network controller:controller];
	}
	else
	{
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("The version of the desktop Task Coach is too old. Please upgrade it and retry.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
		[alert show];
	}
}

// UIAlertViewDelegate.

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex
{
	[myController finished:NO];
	[myNetwork close];
	[self cancel];
}

@end
