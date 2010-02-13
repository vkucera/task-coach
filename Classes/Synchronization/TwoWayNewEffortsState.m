//
//  TwoWayEffortsState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 27/12/09.
//  Copyright 2009 Jérôme Laheurte. All rights reserved.
//

#import "TwoWayNewEffortsState.h"
#import "TwoWayModifiedEffortsState.h"

#import "DomainObject.h"
#import "Database.h"
#import "Statement.h"
#import "Network.h"
#import "SyncViewController.h"
#import "DateUtils.h"

@implementation TwoWayNewEffortsState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	NSObject <State> *next;
	
	next = [TwoWayModifiedEffortsState stateWithNetwork:network controller:controller];

	return [[[TwoWayNewEffortsState alloc] initWithNetwork:network controller:controller nextState:next expectIds:YES] autorelease];
}

- (void)activated
{
	[super activated];
	
	[self start:[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM CurrentEffort WHERE status=%d", STATUS_NEW]]];
}

- (void)onTaskId:(NSDictionary *)dict
{
	[myNetwork appendString:[dict objectForKey:@"taskCoachId"]];
}

- (void)onObject:(NSDictionary *)dict
{
	[super onObject:dict];

	NSLog(@"Sending effort %@/%@", [dict objectForKey:@"started"], [dict objectForKey:@"ended"]);

	[myNetwork appendString:[dict objectForKey:@"name"]];

	if ([dict objectForKey:@"taskId"])
		[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT taskCoachId FROM Task WHERE id=%d", [[dict objectForKey:@"taskId"] intValue]]] execWithTarget:self action:@selector(onTaskId:)];
	else
		[myNetwork appendString:nil];
	
	[myNetwork appendString:[dict objectForKey:@"started"]];
	[myNetwork appendString:[dict objectForKey:@"ended"]];
}

- (NSString *)tableName
{
	return @"Effort";
}

@end
