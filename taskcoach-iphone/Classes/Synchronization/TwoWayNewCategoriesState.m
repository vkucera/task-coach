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
#import "Database.h"
#import "Statement.h"
#import "SyncViewController.h"
#import "CDCategory.h"
#import "CDDomainObject+Addons.h"

@implementation TwoWayNewCategoriesState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayNewCategoriesState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)packObject:(CDCategory *)category
{
	[self sendFormat:"s" values:[NSArray arrayWithObject:category.name]];
	
	if (category.parent)
		[self sendFormat:"s" values:[NSArray arrayWithObject:category.parent.taskCoachId]];
	else
		[self sendFormat:"s" values:[NSArray arrayWithObject:[NSNull null]]];
	
	NSLog(@"Sent category: %@", category.name);
}

- (void)onFinished
{
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
