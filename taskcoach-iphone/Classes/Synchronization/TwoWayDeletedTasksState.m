//
//  TwoWayDeletedTasksState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "TwoWayDeletedTasksState.h"
#import "TwoWayModifiedTasksState.h"

#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "Statement.h"
#import "DomainObject.h"

@implementation TwoWayDeletedTasksState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayDeletedTasksState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT taskCoachId FROM Task WHERE status=%d", STATUS_DELETED]];
	[req execWithTarget:self action:@selector(onDeletedTask:)];
	
	myController.state = [TwoWayModifiedTasksState stateWithNetwork:myNetwork controller:myController];
}

- (void)onDeletedTask:(NSDictionary *)dict
{
	NSLog(@"Sending deleted task %@", [dict objectForKey:@"taskCoachId"]);

	[myNetwork appendString:[dict objectForKey:@"taskCoachId"]];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	// n/a
}

@end
