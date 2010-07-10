//
//  TwoWayDeletedCategoriesState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 23/08/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "TwoWayDeletedCategoriesState.h"
#import "TwoWayModifiedCategoriesState.h"
#import "CDCategory.h"
#import "CDDomainObject+Addons.h"
#import "SyncViewController.h"
#import "LogUtils.h"

@implementation TwoWayDeletedCategoriesState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayDeletedCategoriesState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	JLDEBUG("=== Two way deleted categories");

	[super activated];
}

- (void)packObject:(CDCategory *)category
{
	JLDEBUG("Packing category \"%s\"", [category.name UTF8String]);

	[self sendFormat:"s" values:[NSArray arrayWithObject:category.taskCoachId]];
}

- (void)onFinished
{
	JLDEBUG("=== Finished");

	myController.state = [TwoWayModifiedCategoriesState stateWithNetwork:myNetwork controller:myController];
}

- (NSString *)entityName
{
	return @"CDCategory";
}

- (NSInteger)status
{
	return STATUS_DELETED;
}

- (NSString *)ordering
{
	return @"creationDate";
}

@end
