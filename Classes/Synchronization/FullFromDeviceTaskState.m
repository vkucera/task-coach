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

/*
- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	switch (state)
	{
		case 0:
			state = 1;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			break;
		case 1:
		{
			Statement *req = [[Database connection] statementWithSQL:@"UPDATE Task SET taskCoachId=? WHERE id=?"];
			[req bindString:[NSString stringFromUTF8Data:data] atIndex:1];
			[req bindInteger:[[objectIds objectAtIndex:0] intValue] atIndex:2];
			[req exec];
			[objectIds removeObjectAtIndex:0];
			
			objectCount -= 1;
			count += 1;
			myController.progress.progress = 1.0 * count / total;
			
			if (objectCount)
			{
				state = 0;
				[network expect:4];
			}
			else
			{
				controller.state = [GetGUIDState stateWithNetwork:network controller:controller];
			}
			
			break;
		}
	}
}
 */

@end
