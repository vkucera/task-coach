//
//  TaskDetailsController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TaskDetailsController.h"
#import "TaskDetailsGeneral.h"
#import "TaskDetailsDates.h"
#import "TaskDetailsEfforts.h"
#import "PositionStore.h"

#import "CDTask.h"

#import "i18n.h"

//======================================================================

@implementation TaskDetailsController

@synthesize tabBar;
@synthesize containerView;

- initWithTask:(CDTask *)theTask
{
	if (self = [super initWithNibName:@"TaskDetails" bundle:[NSBundle mainBundle]])
	{
		task = [theTask retain];
	}

	return self;
}

- initWithTask:(CDTask *)theTask tabIndex:(NSInteger)index
{
	if (self = [self initWithTask:theTask])
		tabIndex = index;
	
	return self;
}

- (void)viewDidLoad
{
	switch (tabIndex)
	{
		case 0:
			currentCtrl = [[TaskDetailsGeneral alloc] initWithTask:task parent:self];
			break;
		case 1:
			currentCtrl = [[TaskDetailsDates alloc] initWithTask:task parent:self];
			break;
		case 2:
			currentCtrl = [[TaskDetailsEfforts alloc] initWithTask:task];
			break;
	}

	self.tabBar.selectedItem = [self.tabBar.items objectAtIndex:tabIndex];

	[self.containerView addSubview:currentCtrl.view];

	[super viewDidLoad];
}

- (void)viewDidUnload
{
	self.tabBar = nil;
	self.containerView = nil;
}

- (void)dealloc
{
	[self viewDidUnload];

	[currentCtrl release];
	[task release];
	[super dealloc];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)toInterfaceOrientation
{
	return YES;
}

#pragma mark UITabBarDelegate methods

- (void)tabBar:(UITabBar *)theTabBar didSelectItem:(UITabBarItem *)item
{
	NSInteger index = [[tabBar items] indexOfObject:item];
	[[PositionStore instance] setTab:index];

	UIViewController *newController = nil;

	switch (index)
	{
		case 0:
			newController = [[TaskDetailsGeneral alloc] initWithTask:task parent:self];
			break;
		case 1:
			newController = [[TaskDetailsDates alloc] initWithTask:task parent:self];
			break;
		case 2:
			newController = [[TaskDetailsEfforts alloc] initWithTask:task];
			break;
	}

	[currentCtrl.view removeFromSuperview];
	[currentCtrl release];
	[containerView addSubview:newController.view];
	currentCtrl = newController;
}

@end

