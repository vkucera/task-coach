//
//  AuthentificationState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "AuthentificationState.h"
#import "GUIDState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"

@implementation AuthentificationState

- initWithNetwork:(Network *)theNetwork controller:(SyncViewController *)controller
{
	if (self = [super init])
	{
		network = theNetwork;

		controller.label.text = NSLocalizedString(@"Authentication", @"Authentication state title");

		controller.password.hidden = NO;
		controller.password.delegate = self;

		[controller.password becomeFirstResponder];
	}
	
	return self;
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[AuthentificationState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)network:(Network *)theNetwork didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	int32_t status = ntohl(*((int32_t *)[data bytes]));
	
	if (status)
	{
		NSLog(@"Password was accepted.");
		controller.state = [GUIDState stateWithNetwork:network controller:controller];
	}
	else
	{
		controller.state = nil;
		[theNetwork close];

		UIAlertView *view = [[UIAlertView alloc] initWithTitle:NSLocalizedString(@"Error", @"Bad password error title")
			  message:NSLocalizedString(@"Incorrect password.", @"Bad password message")
			  delegate:controller cancelButtonTitle:NSLocalizedString(@"Abort", @"Bad password cancel button title") otherButtonTitles:nil];
		[view show];
		[view release];
		[theNetwork release];
		[[Database connection] rollback];
	}
}

// UITextFieldDelegate

- (BOOL)textFieldShouldReturn:(UITextField *)textField
{
	[network expect:4];
	[network appendString:textField.text];
	
	[textField resignFirstResponder];
	textField.hidden = YES;

	return NO;
}

@end
