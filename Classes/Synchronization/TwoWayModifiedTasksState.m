//
//  TwoWayModifiedTasksState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "TwoWayModifiedTasksState.h"
#import "FullFromDesktopState.h"

#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "Statement.h"
#import "DomainObject.h"

@implementation TwoWayModifiedTasksState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayModifiedTasksState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM Task WHERE status=%d", STATUS_MODIFIED]];
	[req execWithTarget:self action:@selector(onModifiedTask:)];
	
	myController.state = [FullFromDesktopState stateWithNetwork:myNetwork controller:myController];
}

- (void)onModifiedTask:(NSDictionary *)dict
{
	[myNetwork appendString:[dict objectForKey:@"name"]];
	[myNetwork appendString:[dict objectForKey:@"taskCoachId"]];
	[myNetwork appendString:[dict objectForKey:@"description"]];
	[myNetwork appendString:[dict objectForKey:@"startDate"]];
	[myNetwork appendString:[dict objectForKey:@"dueDate"]];
	[myNetwork appendString:[dict objectForKey:@"completionDate"]];
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
