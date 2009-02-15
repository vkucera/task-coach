//
//  TwoWayNewCategoriesState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "TwoWayNewCategoriesState.h"
#import "TwoWayNewTasksState.h"
#import "Network.h"
#import "Database.h"
#import "Statement.h"
#import "SyncViewController.h"
#import "DomainObject.h"

@implementation TwoWayNewCategoriesState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	NSObject <State> *next = [TwoWayNewTasksState stateWithNetwork:network controller:controller];

	return [[[TwoWayNewCategoriesState alloc] initWithNetwork:network controller:controller nextState:next expectIds:YES] autorelease];
}

- (void)activated
{
	[super activated];
	
	objectCount = categoryCount;
	[self afterActivation];

	if (categoryCount)
	{
		Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM Category WHERE status=%d", STATUS_NEW]];
		[req execWithTarget:self action:@selector(onObject:)];
	}
	else
	{
		myController.state = nextState;
	}
}

- (void)onObject:(NSDictionary *)dict
{
	[super onObject:dict];
	
	[myNetwork appendString:[dict objectForKey:@"name"]];
}

- (NSString *)categoryWhereClause
{
	return [NSString stringWithFormat:@"status = %d", STATUS_NEW];
}

- (NSString *)taskWhereClause
{
	return [NSString stringWithFormat:@"status = %d", STATUS_NEW];
}

- (NSString *)tableName
{
	return @"Category";
}

@end
