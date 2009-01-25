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

- (void)activated
{
	myController.label.text = NSLocalizedString(@"Authentication", @"Authentication state title");
	
	myController.password.hidden = NO;
	myController.password.delegate = self;
	
	[myController.password becomeFirstResponder];
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[AuthentificationState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
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
		[network close];

		UIAlertView *view = [[UIAlertView alloc] initWithTitle:NSLocalizedString(@"Error", @"Bad password error title")
			  message:NSLocalizedString(@"Incorrect password.", @"Bad password message")
			  delegate:controller cancelButtonTitle:NSLocalizedString(@"Abort", @"Bad password cancel button title") otherButtonTitles:nil];
		[view show];
		[view release];
		[network release];
		[[Database connection] rollback];
	}
}

// UITextFieldDelegate

- (BOOL)textFieldShouldReturn:(UITextField *)textField
{
	[myNetwork expect:4];
	[myNetwork appendString:textField.text];

	// Also send device name right after the password
	UIDevice *dev = [UIDevice currentDevice];
	[myNetwork appendString:dev.name];

	[textField resignFirstResponder];
	textField.hidden = YES;

	return NO;
}

@end
