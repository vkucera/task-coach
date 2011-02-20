//
//  MainViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "MainViewController.h"
#import "PositionStore.h"
#import "LogUtils.h"
#import "i18n.h"

@implementation MainViewController

@synthesize viewController;

- (void)childWasPopped
{
	if ([viewController respondsToSelector:@selector(childWasPopped)])
		[viewController performSelector:@selector(childWasPopped)];
}

- (void)viewDidLoad
{
	self.navigationItem.rightBarButtonItem = [self.viewController editButtonItem];

#ifdef DEBUG
	[[UIAccelerometer sharedAccelerometer] setUpdateInterval:1.0 / 60];
	[[UIAccelerometer sharedAccelerometer] setDelegate:self];
#endif
}

- (void)viewDidUnload
{
	self.viewController = nil;

#ifdef DEBUG
	[UIAccelerometer sharedAccelerometer].delegate = nil;
	[lastAccel release];
	lastAccel = nil;
#endif
}

- (void)dealloc
{
	[self viewDidUnload];
	
	[super dealloc];
}

- (void)willTerminate
{
	if ([viewController respondsToSelector:@selector(willTerminate)])
		[viewController performSelector:@selector(willTerminate)];
}

- (void)restorePosition:(Position *)pos store:(PositionStore *)store
{
	if ([viewController respondsToSelector:@selector(restorePosition:store:)])
		[viewController performSelector:@selector(restorePosition:store:) withObject:pos withObject:store];
}

#pragma mark -
#pragma mark UIAccelerometerDelegate

#ifdef DEBUG

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
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Debug") message:_("Do you want to send the debug log by e-mail ?") delegate:self cancelButtonTitle:_("No") otherButtonTitles:nil];
			[alert addButtonWithTitle:_("Yes")];
			[alert show];
			[alert release];

			[[UIAccelerometer sharedAccelerometer] setDelegate:nil];
			
			acceleration = nil;
		}
	}
	
	[lastAccel release];
	lastAccel = [acceleration retain];
}

#endif

#pragma mark -
#pragma mark MFMailComposeViewControllerDelegate

#ifdef DEBUG

- (void)mailComposeController:(MFMailComposeViewController*)controller didFinishWithResult:(MFMailComposeResult)result error:(NSError*)error
{
	[self dismissModalViewControllerAnimated:YES];
}

#pragma mark -
#pragma mark UIAlertViewDelegate

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex
{
	if (alertState == 0)
	{
		if (buttonIndex == 1)
		{
			MFMailComposeViewController *ctrl = [[MFMailComposeViewController alloc] init];
			
			if (!ctrl)
			{
				alertState = 1;

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
	else
	{
		alertState = 0;
		[self dismissModalViewControllerAnimated:YES];
	}
}

#endif

@end
