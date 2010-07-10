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
#import "AlertPrompt.h"
#import "LogUtils.h"
#import "i18n.h"

@implementation AuthentificationState

- (void)askForPassword
{
	JLDEBUG("Asking for password.");

	AlertPrompt *prompt = [[AlertPrompt alloc] initWithTitle:_("Please type your password.")
													 message:@"\n"
													delegate:self
										   cancelButtonTitle:_("Cancel")
											   okButtonTitle:_("OK")];
	[prompt show];
	[prompt release];
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[AuthentificationState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	JLDEBUG("=== Authentication state.");

	myController.label.text = _("Authentication");
	
#if TARGET_IPHONE_SIMULATOR
	[self askForPassword];
#else
	keychain = [[KeychainWrapper alloc] init];
	currentPassword = [[keychain objectForKey:(id)kSecValueData] retain];
	
	if ([currentPassword length] == 0)
	{
		[self askForPassword];
	}
#endif
	
	[self startWithFormat:"512b" count:NOCOUNT];
}

- (void)dealloc
{
	[currentPassword release];
	[currentData release];

#if !TARGET_IPHONE_SIMULATOR
	[keychain release];
#endif
	
	[super dealloc];
}

- (void)onNewObject:(NSArray *)value
{
	if (state == 0)
	{
		JLDEBUG("Received hash data.");
		
		if (currentPassword)
		{
			JLDEBUG("Sending hashed password (1).");
			
			NSMutableData *hashData = [[NSMutableData alloc] initWithData:[value objectAtIndex:0]];
			const char *bf = [currentPassword UTF8String];
			[hashData appendData:[NSData dataWithBytes:bf length:strlen(bf)]];
			
			CC_SHA1_CTX context;
			CC_SHA1_Init(&context);
			CC_SHA1_Update(&context, [hashData bytes], [hashData length]);
			unsigned char hash[20];
			CC_SHA1_Final(hash, &context);
			
			[hashData release];
			
			state = 1;
			[self startWithFormat:"i" count:NOCOUNT];
			[self sendFormat:"20b" values:[NSArray arrayWithObject:[NSData dataWithBytes:hash length:20]]];
		}
		else
		{
			JLDEBUG("Storing it.");
			
			[currentData release];
			currentData = [[value objectAtIndex:0] copy];
			
			state = 1;
			[self startWithFormat:"i" count:NOCOUNT];
		}
	}
	else
	{
		NSInteger result = [[value objectAtIndex:0] intValue];
		
		if (result)
		{
			JLDEBUG("Password accepted.");
			
#if !TARGET_IPHONE_SIMULATOR
			[keychain setObject:currentPassword forKey:(id)kSecValueData];
#endif
			
			// Also send device name
			UIDevice *dev = [UIDevice currentDevice];
			JLDEBUG("Sending device name: %@", dev.name);
			[self sendFormat:"s" values:[NSArray arrayWithObject:dev.name]];
			
			myController.state = [GUIDState stateWithNetwork:myNetwork controller:myController];
		}
		else
		{
			JLDEBUG("Password rejected.");
			
			[currentData release];
			[currentPassword release];
			
			currentData = nil;
			currentPassword = nil;
			
			state = 0;
			[self startWithFormat:"512b" count:NOCOUNT];
			[self askForPassword];
		}
	}
}

- (void)onFinished
{
}

#pragma mark UIAlertViewDelegate.

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex
{
	AlertPrompt *pwd = (AlertPrompt *)alertView;
	
	switch (buttonIndex)
	{
		case 0:
			[self cancel];
			break;
		case 1:
		{
			[currentPassword release];
			currentPassword = [pwd.enteredText retain];
			
			if (state == 1)
			{
				assert(currentData);
				
				JLDEBUG("Sending hashed password (2).");
				
				NSMutableData *hashData = [[NSMutableData alloc] initWithData:currentData];
				const char *bf = [currentPassword UTF8String];
				[hashData appendData:[NSData dataWithBytes:bf length:strlen(bf)]];
				
				CC_SHA1_CTX context;
				CC_SHA1_Init(&context);
				CC_SHA1_Update(&context, [hashData bytes], [hashData length]);
				unsigned char hash[20];
				CC_SHA1_Final(hash, &context);
				
				[hashData release];
				
				state = 1;
				[self startWithFormat:"i" count:NOCOUNT];
				[self sendFormat:"20b" values:[NSArray arrayWithObject:[NSData dataWithBytes:hash length:20]]];
			}
			else
			{
				JLDEBUG("Password entered, but no data yet.");
			}
		}
	}
	
	[pwd.textField resignFirstResponder];
}

@end
