//
//  SyncViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "SyncViewController.h"
#import "Configuration.h"
#import "InitialState.h"
#import "LogUtils.h"
#import "i18n.h"

@implementation SyncViewController

@synthesize label;
@synthesize activity;
@synthesize progress;
@synthesize state;
@synthesize protocolVersion;

@synthesize categoryCount;
@synthesize taskCount;
@synthesize effortCount;

@synthesize name;

- initWithTarget:(id)theTarget action:(SEL)theAction host:(NSString *)theHost port:(NSInteger)thePort name:(NSString *)theName
{
	if ((self = [super initWithNibName:@"SyncView" bundle:[NSBundle mainBundle]]))
	{
		target = theTarget;
		action = theAction;
		name = [theName copy];

		host = [theHost copy];
		port = thePort;
	}
	
	return self;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)toInterfaceOrientation
{
	return YES;
}

- (void)finished:(BOOL)ok
{
	[target performSelector:action];
}

- (void)cancel
{
	[state cancel];
	[target performSelector:action];
}

- (void)increment
{
	++currentCount;
	progress.progress = 1.0 * currentCount / (categoryCount + taskCount + effortCount);
}

- (void)viewDidLoad
{
	label.text = _("Connecting...");
	
	NSLog(@"Starting synchronization");
	myNetwork = [[Network alloc] initWithAddress:host port:port delegate:self];
	self.state = [InitialState stateWithNetwork:myNetwork controller:self];

	[UIApplication sharedApplication].idleTimerDisabled = YES;
}

- (void)viewDidUnload
{
	self.label = nil;
	self.activity = nil;
	self.progress = nil;

	[UIApplication sharedApplication].idleTimerDisabled = NO;
}

- (void)dealloc
{
	[self viewDidUnload];

	[host release];
	[myNetwork release];
	[name release];
	
	[super dealloc];
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
	JLERROR("Network error (%s)", [[error description] UTF8String]);
	
	[state networkDidEncounterError:network error:error controller:self];
}

- (void)network:(Network *)network didGetData:(NSData *)data
{
	[state network:network didGetData:data controller:self];
}

@end
