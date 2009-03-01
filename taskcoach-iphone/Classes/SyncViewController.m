//
//  SyncViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "SyncViewController.h"
#import "Configuration.h"
#import "InitialState.h"

@implementation SyncViewController

@synthesize label;
@synthesize activity;
@synthesize progress;
@synthesize state;
@synthesize password;
@synthesize cancelButton;

- initWithTarget:(id)theTarget action:(SEL)theAction host:(NSString *)theHost port:(NSInteger)thePort
{
	if (self = [super initWithNibName:@"SyncView" bundle:[NSBundle mainBundle]])
	{
		target = theTarget;
		action = theAction;

		host = [theHost copy];
		port = thePort;
	}
	
	return self;
}

- (void)dealloc
{
	[label release];
	[activity release];
	[progress release];
	[host release];

	[super dealloc];
}

- (void)finished:(BOOL)ok
{
	[Configuration configuration].host = host;
	[Configuration configuration].port = port;
	[[Configuration configuration] save];

	[target performSelector:action];
}

- (IBAction)onCancel:(UIButton *)button
{
	[state cancel];
	[target performSelector:action];
}

- (void)viewDidLoad
{
	label.text = NSLocalizedString(@"Connecting...", @"Connecting title");
	password.hidden = YES;
	cancelButton.hidden = YES;
	
	NSLog(@"Starting synchronization");
	self.state = [InitialState stateWithNetwork:[[Network alloc] initWithAddress:host port:port delegate:self] controller:self];
}

- (void)setState:(NSObject <State> *)newState
{
	[newState retain];
	[state release];
	state = newState;
	[state activated];
}

// NetworkDelegate methods

- (void)networkDidConnect:(Network *)network
{
	NSLog(@"Connected");
	
	[state networkDidConnect:network controller:self];
}

- (void)networkDidClose:(Network *)network
{
	NSLog(@"Connection closed");

	[state networkDidClose:network controller:self];
}

- (void)networkDidEncounterError:(Network *)network error:(NSError *)error
{
	NSLog(@"Network error (%@)", [error description]);
	
	[state networkDidEncounterError:network error:error controller:self];
}

- (void)network:(Network *)network didGetData:(NSData *)data
{
	[state network:network didGetData:data controller:self];
}

// UIAlertViewDelegate.

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex
{
	[target performSelector:action];
}

@end
