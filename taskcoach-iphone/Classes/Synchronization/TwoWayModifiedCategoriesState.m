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

@implementation TwoWayModifiedCategoriesState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayModifiedCategoriesState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)packObject:(CDCategory *)category
{
	[self sendFormat:"ss" values:[NSArray arrayWithObjects:category.name, category.taskCoachId, nil]];
}

- (void)onFinished
{
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
