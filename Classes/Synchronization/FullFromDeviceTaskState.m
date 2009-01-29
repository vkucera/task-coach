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
#import "String+Utils.h"

@implementation FullFromDeviceTaskState

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	if (self = [super initWithNetwork:network controller:controller])
	{
		taskIds = [[NSMutableArray alloc] initWithCapacity:32];
	}
	
	return self;
}

- (void)dealloc
{
	[taskIds release];
	
	[super dealloc];
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[FullFromDeviceTaskState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	[myNetwork expect:4];
	
	Statement *req;
	
	req = [[Database connection] statementWithSQL:@"SELECT COUNT(*) AS total FROM Task"];
	[req execWithTarget:self action:@selector(onTaskCount:)];
	
	req = [[Database connection] statementWithSQL:@"SELECT COUNT(*) AS total FROM Category"];
	[req execWithTarget:self action:@selector(onCategoryCount:)];
	
	req = [[Database connection] statementWithSQL:@"SELECT Task.*, Category.taskCoachId AS catId FROM Task LEFT JOIN Category ON Task.categoryId = Category.id"];
	[req execWithTarget:self action:@selector(onTask:)];
}

- (void)onTaskCount:(NSDictionary *)dict
{
	taskCount = [[dict objectForKey:@"total"] intValue];
}

- (void)onCategoryCount:(NSDictionary *)dict
{
	count = [[dict objectForKey:@"total"] intValue];
	total = count + taskCount;
}

- (void)onTask:(NSDictionary *)dict
{
	[taskIds addObject:[dict objectForKey:@"id"]];

	[myNetwork appendString:[dict objectForKey:@"name"]];
	[myNetwork appendString:[dict objectForKey:@"description"]];
	[myNetwork appendString:[dict objectForKey:@"startDate"]];
	[myNetwork appendString:[dict objectForKey:@"dueDate"]];
	[myNetwork appendString:[dict objectForKey:@"completionDate"]];
	[myNetwork appendString:[dict objectForKey:@"catId"]];
	
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

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
			[req bindInteger:[[taskIds objectAtIndex:0] intValue] atIndex:2];
			[req exec];
			[taskIds removeObjectAtIndex:0];
			
			taskCount -= 1;
			count += 1;
			myController.progress.progress = 1.0 * count / total;
			
			if (taskCount)
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

@end
