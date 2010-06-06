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

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[ProtocolNegotiationState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	myController.label.text = _("Protocol negotiation...");
	[self startWithFormat:"i" count:NOCOUNT];
}

- (void)onNewObject:(NSArray *)value
{
	NSInteger version = [[value objectAtIndex:0] intValue];
	NSInteger result = 0;
	
	// Starting with 3.0, protocols 1-4 aren't supported anymore
	
	switch (version)
	{
		case 5:
			result = 1;
			break;
	}
	
	[self sendFormat:"i" values:[NSArray arrayWithObject:[NSNumber numberWithInt:result]]];
	
	// The other end will close the connection eventually.
	
	if (result)
	{
		NSLog(@"Accepted version %d", version);
		
		myController.protocolVersion = version;
		myController.state = [AuthentificationState stateWithNetwork:myNetwork controller:myController];
	}
	else
	{
		if (version > 5)
		{
			// Keep trying
			myController.state = [ProtocolNegotiationState stateWithNetwork:myNetwork controller:myController];
		}
		else
		{
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error")
															message:_("The version of the desktop Task Coach is too old. Please upgrade it and retry.")
														   delegate:self
												  cancelButtonTitle:_("OK")
												  otherButtonTitles:nil];
			[alert show];
			[alert release];
		}
	}
}

- (void)onFinished
{
}

/*
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
		case 5:
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
		if (version <= 3)
		{
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("The version of the desktop Task Coach is too old. Please upgrade it and retry.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
			[alert show];
		}
		else
		{
			[myNetwork expect:4];
		}
	}
}
*/

#pragma mark UIAlertViewDelegate.

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex
{
	[myController finished:NO];
	[myNetwork close];
	[self cancel];
}

@end
