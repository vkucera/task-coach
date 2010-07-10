//
//  TwoWayModifiedCategoriesState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 23/08/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "TwoWayModifiedCategoriesState.h"
#import "TwoWayNewTasksState.h"
#import "SyncViewController.h"
#import "CDCategory.h"
#import "CDDomainObject+Addons.h"
#import "LogUtils.h"

@implementation TwoWayModifiedCategoriesState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayModifiedCategoriesState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	JLDEBUG("=== Two way modified categories");

	[super activated];
}

- (void)packObject:(CDCategory *)category
{
	JLDEBUG("Packing category %s", [category.name UTF8String]);

	[self sendFormat:"ss" values:[NSArray arrayWithObjects:category.name, category.taskCoachId, nil]];
}

- (void)onFinished
{
	JLDEBUG("=== Finished");

	myController.state = [TwoWayNewTasksState stateWithNetwork:myNetwork controller:myController];
}

- (NSString *)entityName
{
	return @"CDCategory";
}

- (NSInteger)status
{
	return STATUS_MODIFIED;
}

- (NSString *)ordering
{
	return @"creationDate";
}

@end
