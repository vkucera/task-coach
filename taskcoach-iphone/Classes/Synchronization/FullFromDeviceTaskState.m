//
//  FullFromDeviceTaskState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 29/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "FullFromDeviceTaskState.h"
#import "GetGUIDState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "Statement.h"

@implementation FullFromDeviceTaskState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[FullFromDeviceTaskState alloc] initWithNetwork:network controller:controller nextState:[GetGUIDState stateWithNetwork:network controller:controller] expectIds:YES] autorelease];
}

- (void)activated
{
	[super activated];

	count = categoryCount;

	taskCategories = [[NSMutableArray alloc] initWithCapacity:2];
	
	[self start:[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM Task WHERE %@", [self taskWhereClause]]]];
}

- (void)dealloc
{
	[taskCategories release];
	
	[super dealloc];
}

- (NSString *)tableName
{
	return @"Task";
}

- (void)onObject:(NSDictionary *)dict
{
	[super onObject:dict];

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
	for (NSString *tcId in taskCategories)
	{
		[myNetwork appendString:tcId];
	}
}

- (void)onFoundCategory:(NSDictionary *)dict
{
	[taskCategories addObject:[dict objectForKey:@"taskCoachId"]];
}

@end
