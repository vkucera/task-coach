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

@implementation TwoWayDeletedCategoriesState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayDeletedCategoriesState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)packObject:(CDCategory *)category
{
	[self sendFormat:"s" values:[NSArray arrayWithObject:category.taskCoachId]];
}

- (void)onFinished
{
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
