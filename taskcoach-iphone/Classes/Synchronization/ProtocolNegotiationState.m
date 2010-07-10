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
#import "LogUtils.h"

#import "i18n.h"

@implementation ProtocolNegotiationState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[ProtocolNegotiationState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	JLDEBUG("=== Protocol negotiation state.");

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

	JLDEBUG("Received protocol %d; response %d", version, result);

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

#pragma mark UIAlertViewDelegate.

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex
{
	[myController finished:NO];
	[myNetwork close];
	[self cancel];
}

@end
