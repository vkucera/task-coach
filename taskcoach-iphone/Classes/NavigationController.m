//
//  NavigationController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "NavigationController.h"

@implementation NavigationController

// UINavigationBarDelegate protocol

- (void)navigationBar:(UINavigationBar *)navigationBar didPopItem:(UINavigationItem *)item
{
	// Each popped view controller will receive the childWasPopped message when it's shown
	// as a result of the user coming back from another view.
	
	UIViewController *ctrl = [self topViewController];
	
	if ([ctrl respondsToSelector:@selector(childWasPopped)])
		[ctrl performSelector:@selector(childWasPopped)];
}

@end
