    //
//  SplitViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 13/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#if __IPHONE_OS_VERSION_MAX_ALLOWED >= 30200

#import "SplitViewController.h"

@implementation SplitViewController

@synthesize categoryCtrl;
@synthesize taskCtrl;

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return YES;
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	self.delegate = self;
}

- (void)viewDidUnload
{
	self.categoryCtrl = nil;
	self.taskCtrl = nil;
}

- (void)dealloc
{
	[self viewDidUnload];

	[super dealloc];
}

#pragma mark UISplitViewControllerDelegate

- (void)splitViewController:(UISplitViewController*)svc
	 willHideViewController:(UIViewController *)aViewController
		  withBarButtonItem:(UIBarButtonItem*)barButtonItem
	   forPopoverController:(UIPopoverController*)pc
{
	barButtonItem.title = @"Categories";
	// navCtrl.topViewController.navigationItem.rightBarButtonItem = barButtonItem;
	// catCtrl.popCtrl = pc;
}

- (void)splitViewController:(UISplitViewController*)svc
	 willShowViewController:(UIViewController *)aViewController
  invalidatingBarButtonItem:(UIBarButtonItem *)button
{
	// navCtrl.topViewController.navigationItem.rightBarButtonItem = nil;
	// catCtrl.popCtrl = nil;
}

@end

#endif
