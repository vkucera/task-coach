//
//  MainViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "MainViewController.h"

@implementation MainViewController

@synthesize viewController;

- (void)childWasPopped
{
	if ([viewController respondsToSelector:@selector(childWasPopped)])
		[viewController performSelector:@selector(childWasPopped)];
}

@end
