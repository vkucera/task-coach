    //
//  SplitView.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 20/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "SplitView.h"
#import "CategoryViewController.h"
#import "CategoryTaskViewController.h"
#import "i18n.h"

@implementation SplitView

@synthesize categoryCtrl;

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    // Overriden to allow any orientation.
    return YES;
}

- (void)didRotateFromInterfaceOrientation:(UIInterfaceOrientation)fromInterfaceOrientation
{
	[categoryCtrl didRotateFromInterfaceOrientation:fromInterfaceOrientation];
	[super didRotateFromInterfaceOrientation:fromInterfaceOrientation];
}

- (void)viewDidUnload
{
    [super viewDidUnload];

	self.categoryCtrl = nil;
}

- (void)viewDidAppear:(BOOL)animated
{
	[super viewDidAppear:animated];

	[categoryCtrl viewDidAppear:animated];
}

- (void)dealloc
{
	[self viewDidUnload];

    [super dealloc];
}

@end
