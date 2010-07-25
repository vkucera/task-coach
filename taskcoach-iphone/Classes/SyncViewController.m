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
	// XXXFIXME: remove this before releasing
	// [target performSelector:action];

	alertState = 1;
	UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Message") message:_("Sync finished.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
	[alert addButtonWithTitle:_("Send log")];
	[alert show];
	[alert release];
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

	[[UIAccelerometer sharedAccelerometer] setUpdateInterval:1.0 / 60];
	[[UIAccelerometer sharedAccelerometer] setDelegate:self];
}

- (void)viewDidUnload
{
	self.label = nil;
	self.activity = nil;
	self.progress = nil;
	
	[UIAccelerometer sharedAccelerometer].delegate = nil;
	[lastAccel release];
	lastAccel = nil;
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

// UIAlertViewDelegate.

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex
{
	if (alertState == 0)
	{
		[target performSelector:action];
	}
	else
	{
		alertState = 0;

		if (buttonIndex == 1)
		{
			MFMailComposeViewController *ctrl = [[MFMailComposeViewController alloc] init];
			
			if (!ctrl)
			{
				UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Your e-mail settings are not set.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
				[alert show];
				[alert release];
			}
			else
			{
				[ctrl setMailComposeDelegate:self];
				[ctrl setSubject:_("Task Coach sync log")];
				[ctrl setMessageBody:[NSString stringWithContentsOfFile:[NSString stringWithUTF8String:LogFilename()] encoding:NSUTF8StringEncoding error:nil] isHTML:NO];
				[ctrl setToRecipients:[NSArray arrayWithObject:@"fraca7@gmail.com"]];
				[self presentModalViewController:ctrl animated:YES];
				[ctrl release];
			}
		}
		else
		{
			[[UIAccelerometer sharedAccelerometer] setUpdateInterval:1.0 / 60];
			[[UIAccelerometer sharedAccelerometer] setDelegate:self];
		}
	}
}

#pragma mark UIAccelerometerDelegate

- (void)accelerometer:(UIAccelerometer *)accelerometer didAccelerate:(UIAcceleration *)acceleration
{
	if (lastAccel)
	{
		double deltaX = fabs(lastAccel.x - acceleration.x);
		double deltaY = fabs(lastAccel.y - acceleration.y);
		double deltaZ = fabs(lastAccel.z - acceleration.z);
		double threshold = 2.0;
		
		if ((deltaX > threshold && deltaY > threshold) ||
			(deltaX > threshold && deltaZ > threshold) ||
			(deltaY > threshold && deltaZ > threshold))
		{
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Debug") message:_("Do you want to send the sync log by e-mail ?") delegate:self cancelButtonTitle:_("No") otherButtonTitles:nil];
			[alert addButtonWithTitle:_("Yes")];
			[alert show];
			[alert release];

			alertState = 1;
			[[UIAccelerometer sharedAccelerometer] setDelegate:nil];

			acceleration = nil;
		}
	}

	[lastAccel release];
	lastAccel = [acceleration retain];
}

#pragma mark MFMailComposeViewControllerDelegate

- (void)mailComposeController:(MFMailComposeViewController*)controller didFinishWithResult:(MFMailComposeResult)result error:(NSError*)error
{
	[self dismissModalViewControllerAnimated:YES];

	[[UIAccelerometer sharedAccelerometer] setUpdateInterval:1.0 / 60];
	[[UIAccelerometer sharedAccelerometer] setDelegate:self];

	[target performSelector:action];
}

@end
