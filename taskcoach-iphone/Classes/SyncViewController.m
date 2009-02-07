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

- initWithTarget:(id)theTarget action:(SEL)theAction
{
	if (self = [super initWithNibName:@"SyncView" bundle:[NSBundle mainBundle]])
	{
		target = theTarget;
		action = theAction;
	}
	
	return self;
}

- (void)dealloc
{
	[label release];
	[activity release];
	[progress release];

	[super dealloc];
}

- (void)finished
{
	[self.navigationController dismissModalViewControllerAnimated:YES];
	[target performSelector:action];
}

- (void)viewDidLoad
{
	label.text = NSLocalizedString(@"Connecting...", @"Connecting title");
	password.hidden = YES;
	
	NSLog(@"Starting synchronization");

	self.state = [InitialState stateWithNetwork:[[Network alloc] initWithAddress:[Configuration configuration].host port:[Configuration configuration].port delegate:self] controller:self];
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

- (void)networkDidEncounterError:(Network *)network
{
	NSLog(@"Network error");
	
	[state networkDidEncounterError:network controller:self];
}

- (void)network:(Network *)network didGetData:(NSData *)data
{
	[state network:network didGetData:data controller:self];
}

// UIAlertViewDelegate. The alert view is actually instantiated from State.

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex
{
	[self.navigationController dismissModalViewControllerAnimated:YES];
}

@end
