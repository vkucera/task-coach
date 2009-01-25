//
//  AuthentificationState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#include <CommonCrypto/CommonDigest.h>

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
	
	[myNetwork expect:512];
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[AuthentificationState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)dealloc
{
	[hashData release];
	
	[super dealloc];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	if ([data length] == 4)
	{
		int32_t status = ntohl(*((int32_t *)[data bytes]));
	
		if (status)
		{
			NSLog(@"Password was accepted.");
			
			// Also send device name
			UIDevice *dev = [UIDevice currentDevice];
			NSLog(@"Sending device name: %@", dev.name);
			[network appendString:dev.name];

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
	else
	{
		hashData = [[NSMutableData alloc] initWithData:data];
		[myController.password becomeFirstResponder];
	}
}

// UITextFieldDelegate

- (BOOL)textFieldShouldReturn:(UITextField *)textField
{
	[hashData appendData:[textField.text dataUsingEncoding:kCFStringEncodingUTF8]];
	
	CC_SHA1_CTX context;
	CC_SHA1_Init(&context);
	CC_SHA1_Update(&context, [hashData bytes], [hashData length]);
	unsigned char hash[20];
	CC_SHA1_Final(hash, &context);

	[myNetwork append:[NSData dataWithBytes:hash length:20]];
	[myNetwork expect:4];

	[textField resignFirstResponder];
	textField.hidden = YES;

	return NO;
}

@end
