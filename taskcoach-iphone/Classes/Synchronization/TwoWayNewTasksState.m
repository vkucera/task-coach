//
//  TwoWayNewTasksState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
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
	
	objectCount = taskCount;
	taskCategories = [[NSMutableArray alloc] initWithCapacity:2];
	
	if (taskCount)
	{
		Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM Task WHERE Task.status=%d", STATUS_NEW]];
		[req execWithTarget:self action:@selector(onObject:)];
	}
	else
	{
		myController.state = nextState;
	}
}

- (void)dealloc
{
	[taskCategories release];
	
	[super dealloc];
}

- (void)onObject:(NSDictionary *)dict
{
	[super onObject:dict];

	NSLog(@"Sending new task %@", [dict objectForKey:@"name"]);
	
	[myNetwork appendString:[dict objectForKey:@"name"]];
	[myNetwork appendString:[dict objectForKey:@"description"]];
	[myNetwork appendString:[dict objectForKey:@"startDate"]];
	[myNetwork appendString:[dict objectForKey:@"dueDate"]];
	[myNetwork appendString:[dict objectForKey:@"completionDate"]];

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
