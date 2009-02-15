//
//  AuthentificationState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <CommonCrypto/CommonDigest.h>
#import <Security/Security.h>

#import "AuthentificationState.h"
#import "GUIDState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"

@implementation AuthentificationState

- (void)activated
{
	myController.label.text = NSLocalizedString(@"Authentication", @"Authentication state title");
	
	myController.password.delegate = self;

#if TARGET_IPHONE_SIMULATOR
	myController.password.hidden = NO;
	myController.cancelButton.hidden = NO;

	[myController.password becomeFirstResponder];
#else
	keychain = [[KeychainWrapper alloc] init];
	currentPassword = [[keychain objectForKey:(id)kSecValueData] retain];

	if ([currentPassword length] != 0)
	{
		[myNetwork expect:512];
	}
	else
	{
		myController.password.hidden = NO;
		myController.cancelButton.hidden = NO;

		[myController.password becomeFirstResponder];
	}
#endif
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[AuthentificationState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)dealloc
{
#if !TARGET_IPHONE_SIMULATOR
	[keychain release];
	[currentPassword release];
#endif
	
	[super dealloc];
}

- (void)cancel
{
	myController.password.delegate = nil;
	[super cancel];
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

#if !TARGET_IPHONE_SIMULATOR
			[keychain setObject:currentPassword forKey:(id)kSecValueData];
#endif

			// Also send device name
			UIDevice *dev = [UIDevice currentDevice];
			NSLog(@"Sending device name: %@", dev.name);
			[network appendString:dev.name];

			controller.state = [GUIDState stateWithNetwork:network controller:controller];
		}
		else
		{
			UIAlertView *view = [[UIAlertView alloc] initWithTitle:NSLocalizedString(@"Error", @"Bad password error title")
													message:NSLocalizedString(@"Incorrect password.", @"Bad password message")
													delegate:self cancelButtonTitle:NSLocalizedString(@"Retry", @"Bad password retry button title") otherButtonTitles:nil];
			[view show];
			[view release];
		}
	}
	else
	{
		// Though MacOS (and so the iPhone simulator) do know how to create data from a string
		// using kCFStringEncodingUTF8, the iPhone itself doesn't. It's able to encode a
		// string in UTF-8 though. Go figure.
		
		NSMutableData *hashData = [[NSMutableData alloc] initWithData:data];
		const char *bf = [currentPassword UTF8String];
		[hashData appendData:[NSData dataWithBytes:bf length:strlen(bf)]];

		CC_SHA1_CTX context;
		CC_SHA1_Init(&context);
		CC_SHA1_Update(&context, [hashData bytes], [hashData length]);
		unsigned char hash[20];
		CC_SHA1_Final(hash, &context);
		
		[hashData release];
		
		[myNetwork expect:4];
		[myNetwork append:[NSData dataWithBytes:hash length:20]];
	}
}

// UITextFieldDelegate

- (BOOL)textFieldShouldReturn:(UITextField *)textField
{
	[textField resignFirstResponder];
	textField.hidden = YES;
	myController.cancelButton.hidden = YES;
	[currentPassword release];
	currentPassword = [textField.text copy];
	[myNetwork expect:512];

	return NO;
}

// UIAlertViewDelegate.

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex
{
	myController.password.hidden = NO;
	myController.cancelButton.hidden = NO;
	[myController.password becomeFirstResponder];
}

@end
