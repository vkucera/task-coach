//
//  ProtocolNegotiationState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "ProtocolNegotiationState.h"
#import "AuthentificationState.h"
#import "Network.h"
#import "SyncViewController.h"

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
			response = 1;
			break;
	}

	[network appendInteger:response];

	if (response)
	{
		NSLog(@"Accepted protocol %d.", version);

		controller.state = [AuthentificationState stateWithNetwork:network controller:controller];
	}
	else
	{
		[network expect:4];
	}
}

@end
