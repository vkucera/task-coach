//
//  TwoWayNewCategoriesState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TwoWayNewCategoriesState.h"
#import "TwoWayDeletedCategoriesState.h"
#import "TwoWayNewTasksState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "CDCategory.h"
#import "CDDomainObject+Addons.h"
#import "LogUtils.h"

@implementation TwoWayNewCategoriesState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayNewCategoriesState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	JLDEBUG("=== Two way: new categories");

	[super activated];
}

- (void)packObject:(CDCategory *)category
{
	JLDEBUG("Packing category \"%s\"", [category.name UTF8String]);

	[self sendFormat:"s" values:[NSArray arrayWithObject:category.name]];
	
	if (category.parent)
		[self sendFormat:"s" values:[NSArray arrayWithObject:category.parent.taskCoachId]];
	else
		[self sendFormat:"s" values:[NSArray arrayWithObject:[NSNull null]]];
}

- (void)onFinished
{
	JLDEBUG("=== Finished");

	myController.state = [TwoWayDeletedCategoriesState stateWithNetwork:myNetwork controller:myController];
}

- (NSString *)entityName
{
	return @"CDCategory";
}

- (NSInteger)status
{
	return STATUS_NEW;
}

- (NSString *)ordering
{
	return @"creationDate";
}

@end
