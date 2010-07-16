//
//  AuthentificationState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <CommonCrypto/CommonDigest.h>
#import <Security/Security.h>

#import "AuthentificationState.h"
#import "GUIDState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "AlertPrompt.h"
#import "i18n.h"

@implementation AuthentificationState

- (void)askForPassword
{
	alertState = 0;
	AlertPrompt *prompt = [[AlertPrompt alloc] initWithTitle:_("Please type your password.") message:@"\n" delegate:self cancelButtonTitle:_("Cancel") okButtonTitle:_("OK")];
	[prompt show];
	[prompt release];
}

- (void)activated
{
	myController.label.text = _("Authentication");
	
#if TARGET_IPHONE_SIMULATOR
	[self askForPassword];
#else
	keychain = [[KeychainWrapper alloc] init];
	currentPassword = [[keychain objectForKey:(id)kSecValueData] retain];

	if ([currentPassword length] != 0)
	{
		[myNetwork expect:512];
	}
	else
	{
		[self askForPassword];
	}
#endif
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[AuthentificationState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)dealloc
{
	[currentPassword release];

#if !TARGET_IPHONE_SIMULATOR
	[keychain release];
#endif
	
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
			UIAlertView *view = [[UIAlertView alloc] initWithTitle:_("Error")
													message:_("Incorrect password.")
													delegate:self cancelButtonTitle:_("Retry") otherButtonTitles:nil];
			alertState = 1;
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

- (void)networkDidClose:(Network *)network controller:(SyncViewController *)controller
{
	[super networkDidClose:network controller:controller];
}

// UIAlertViewDelegate

- (void)alertView:(UIAlertView *)alertView didDismissWithButtonIndex:(NSInteger)buttonIndex
{
	switch (alertState)
	{
		case 0:
			switch (buttonIndex)
			{
				case 0: // Cancel
					[myController cancel];
					break;
				case 1: // OK
					[currentPassword release];
					currentPassword = [((AlertPrompt *)alertView).enteredText retain];
					[myNetwork expect:512];
					break;
			}
			break;
		case 1:
			[self askForPassword];
			break;
	}
}

@end
