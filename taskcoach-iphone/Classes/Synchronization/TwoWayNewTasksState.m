//
//  TwoWayNewTasksState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TwoWayNewTasksState.h"
#import "TwoWayDeletedTasksState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "Statement.h"
#import "DomainObject.h"

@implementation TwoWayNewTasksState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	NSObject <State> *next = [TwoWayDeletedTasksState stateWithNetwork:network controller:controller];

	return [[[TwoWayNewTasksState alloc] initWithNetwork:network controller:controller nextState:next expectIds:YES] autorelease];
}

- (void)activated
{
	[super activated];

	taskCategories = [[NSMutableArray alloc] initWithCapacity:2];

	[self start:[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM CurrentTask WHERE CurrentTask.status=%d", STATUS_NEW]]];
}

- (void)dealloc
{
	[taskCategories release];
	[parentId release];
	
	[super dealloc];
}

- (void)onParentId:(NSDictionary *)dict
{
	[parentId release];
	parentId = [[dict objectForKey:@"taskCoachId"] retain];
}

- (void)onObject:(NSDictionary *)dict
{
	[super onObject:dict];

	NSLog(@"Sending new task %@", [dict objectForKey:@"name"]);
	
	[myNetwork appendString:[dict objectForKey:@"name"]];
	[myNetwork appendString:[dict objectForKey:@"description"]];

	[self sendDate:[dict objectForKey:@"startDate"]];
	[self sendDate:[dict objectForKey:@"dueDate"]];
	[self sendDate:[dict objectForKey:@"completionDate"]];

	if ([dict objectForKey:@"parentId"])
	{
		[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT taskCoachId FROM Task WHERE id=%d", [[dict objectForKey:@"parentId"] intValue]]] execWithTarget:self action:@selector(onParentId:)];
		[myNetwork appendString:parentId];
	}
	else
	{
		[myNetwork appendInteger:0];
	}


	[taskCategories removeAllObjects];

	Statement *req = [[Database connection] statementWithSQL:@"SELECT taskCoachId FROM Category, TaskHasCategory WHERE idCategory=id AND idTask=?"];
	[req bindInteger:[[dict objectForKey:@"id"] intValue] atIndex:1];
	[req execWithTarget:self action:@selector(onFoundCategory:)];
	[myNetwork appendInteger:[taskCategories count]];
	for (NSString *catId in taskCategories)
	{
		[myNetwork appendString:catId];
	}
}

- (void)onFoundCategory:(NSDictionary *)dict
{
	[taskCategories addObject:[dict objectForKey:@"taskCoachId"]];
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
	return @"Task";
}

@end
