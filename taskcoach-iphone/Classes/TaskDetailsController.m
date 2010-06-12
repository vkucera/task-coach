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

- initWithTask:(CDTask *)theTask
{
	if (self = [super initWithNibName:@"TaskDetails" bundle:[NSBundle mainBundle]])
	{
		task = [theTask retain];

		NSMutableArray *ctrls = [[NSMutableArray alloc] initWithCapacity:3];

		TaskDetailsGeneral *general = [[TaskDetailsGeneral alloc] initWithTask:task parent:self];
		general.tabBarItem = [[[UITabBarItem alloc] initWithTitle:_("General") image:[UIImage imageNamed:@"taskcoach_small.png"] tag:0] autorelease];
		[ctrls addObject:general];
		[general release];

		TaskDetailsDates *dates = [[TaskDetailsDates alloc] initWithTask:task parent:self];
		dates.tabBarItem = [[[UITabBarItem alloc] initWithTitle:_("Dates") image:[UIImage imageNamed:@"switchcal.png"] tag:0] autorelease];
		[ctrls addObject:dates];
		[dates release];

		TaskDetailsEfforts *efforts = [[TaskDetailsEfforts alloc] initWithTask:task];
		efforts.tabBarItem = [[[UITabBarItem alloc] initWithTitle:_("Efforts") image:[UIImage imageNamed:@"time.png"] tag:0] autorelease];
		[ctrls addObject:efforts];
		[efforts release];

		[self setViewControllers:ctrls animated:NO];
		[ctrls release];

		self.delegate = self;
		self.navigationItem.title = task.name;
	}

	return self;
}

- initWithTask:(CDTask *)theTask tabIndex:(NSInteger)index
{
	if (self = [self initWithTask:theTask])
	{
		self.selectedIndex = index;
	}

	return self;
}

- (void)dealloc
{
	[task release];

	[super dealloc];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)toInterfaceOrientation
{
	return YES;
}

#pragma mark UITabBarControllerDelegate methods

- (void)tabBarController:(UITabBarController *)tabBarController didSelectViewController:(UIViewController *)viewController
{
	[[PositionStore instance] setTab:[self.viewControllers indexOfObject:viewController]];
}

@end

