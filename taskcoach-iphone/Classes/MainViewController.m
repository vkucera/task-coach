//
//  MainViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "MainViewController.h"
#import "PositionStore.h"

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
}

- (void)viewDidUnload
{
	self.viewController = nil;
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

@end
