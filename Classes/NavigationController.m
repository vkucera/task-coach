//
//  NavigationController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "NavigationController.h"
#import "PositionStore.h"

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

- (void)willTerminate
{
	UIViewController *ctrl = [self topViewController];
	
	if ([ctrl respondsToSelector:@selector(willTerminate)])
		[ctrl performSelector:@selector(willTerminate)];
}

- (void)restorePosition:(Position *)pos store:(PositionStore *)store
{
	UIViewController *ctrl = [self topViewController];
	
	if ([ctrl respondsToSelector:@selector(restorePosition:store:)])
		[ctrl performSelector:@selector(restorePosition:store:) withObject:pos withObject:store];
}

@end
