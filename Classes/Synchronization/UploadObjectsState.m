//
//  UploadObjectsState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 29/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "UploadObjectsState.h"

#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "Statement.h"
#import "String+Utils.h"

@implementation UploadObjectsState

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller nextState:(NSObject <State> *)theNextState expectIds:(BOOL)expectIds
{
	if (self = [super initWithNetwork:network controller:controller])
	{
		if (expectIds)
			objectIds = [[NSMutableArray alloc] initWithCapacity:32];
		nextState = [theNextState retain];
	}
	
	return self;
}

- (void)dealloc
{
	[objectIds release];
	[nextState release];
	
	[super dealloc];
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	// Use subclasses
	
	return nil;
}

- (void)activated
{
	Statement *req;
	
	req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT COUNT(*) AS total FROM Category WHERE %@", [self categoryWhereClause]]];
	[req execWithTarget:self action:@selector(onCategoryCount:)];
	
	req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT COUNT(*) AS total FROM Task WHERE %@", [self taskWhereClause]]];
	[req execWithTarget:self action:@selector(onTaskCount:)];
	
	total = categoryCount + taskCount;
}

- (void)afterActivation
{
	if (objectCount)
	{
		if (objectIds)
			[myNetwork expect:4];
	}
	else
	{
		myController.state = nextState;
	}
}

- (void)onCategoryCount:(NSDictionary *)dict
{
	categoryCount = [[dict objectForKey:@"total"] intValue];
}

- (void)onTaskCount:(NSDictionary *)dict
{
	taskCount = [[dict objectForKey:@"total"] intValue];
}

- (void)onObject:(NSDictionary *)dict
{
	[objectIds addObject:[dict objectForKey:@"id"]];
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
			NSLog(@"Got ID: %@", [NSString stringFromUTF8Data:data]);

			Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE %@ SET taskCoachId=? WHERE id=?", [self tableName]]];
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
				controller.state = nextState;
			}
			
			break;
		}
	}
}

- (NSString *)categoryWhereClause
{
	return @"1";
}

- (NSString *)taskWhereClause
{
	return @"1";
}

- (NSString *)tableName
{
	return nil;
}

@end
