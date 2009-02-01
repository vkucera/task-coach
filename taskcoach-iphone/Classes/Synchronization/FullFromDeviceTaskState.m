//
//  FullFromDeviceTaskState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 29/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
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
	objectCount = taskCount;
	
	Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT Task.*, Category.taskCoachId AS catId FROM Task LEFT JOIN Category ON Task.categoryId = Category.id WHERE %@", [self taskWhereClause]]];
	[req execWithTarget:self action:@selector(onObject:)];
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
	[myNetwork appendString:[dict objectForKey:@"catId"]];
}

@end
