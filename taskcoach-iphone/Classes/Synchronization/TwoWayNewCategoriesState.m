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
#import "DomainObject.h"

@implementation TwoWayNewCategoriesState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	NSObject <State> *next;
	
	next = [TwoWayDeletedCategoriesState stateWithNetwork:network controller:controller];

	return [[[TwoWayNewCategoriesState alloc] initWithNetwork:network controller:controller nextState:next expectIds:YES] autorelease];
}

- (void)activated
{
	[super activated];

	[self start:[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM CurrentCategory WHERE status=%d", STATUS_NEW]]];
}

- (void)onCategoryParent:(NSDictionary *)dict
{
	[myNetwork appendString:[dict objectForKey:@"taskCoachId"]];
}

- (void)onObject:(NSDictionary *)dict
{
	[super onObject:dict];

	[myNetwork appendString:[dict objectForKey:@"name"]];
	
	if ([dict objectForKey:@"parentId"])
	{
		Statement *req = [[Database connection] statementWithSQL:@"SELECT taskCoachId FROM Category WHERE id=?"];
		[req bindInteger:[(NSNumber *)[dict objectForKey:@"parentId"] intValue] atIndex:1];
		[req execWithTarget:self action:@selector(onCategoryParent:)];
	}
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
