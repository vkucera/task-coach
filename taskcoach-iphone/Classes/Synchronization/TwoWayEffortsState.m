//
//  TwoWayEffortsState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 27/12/09.
//  Copyright 2009 Jérôme Laheurte. All rights reserved.
//

#import "TwoWayEffortsState.h"
#import "FullFromDesktopState.h"

#import "DomainObject.h"
#import "Database.h"
#import "Statement.h"
#import "Network.h"
#import "SyncViewController.h"
#import "DateUtils.h"

@implementation TwoWayEffortsState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayEffortsState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	// Stop current effort, we'll restore it later.
	NSString *now = [[TimeUtils instance] stringFromDate:[NSDate date]];

	[[[Database connection] statementWithSQL:@"SELECT taskId FROM Task, Effort WHERE taskId=Task.id AND ended IS NULL"] execWithTarget:self action:@selector(onCurrentEffort:)];
	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE Effort SET ended=\"%@\" WHERE ended IS NULL", now]] exec];

	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT taskCoachId, started, ended FROM Effort, Task WHERE Task.id=Effort.taskId AND Task.status != %d", STATUS_MODIFIED]] execWithTarget:self action:@selector(onEffort:)];

	myController.state = [FullFromDesktopState stateWithNetwork:myNetwork controller:myController];

	[[[Database connection] statementWithSQL:@"DELETE FROM Effort"] exec];

	if (trackingTask)
	{
		Statement *req = [[Database connection] statementWithSQL:@"INSERT INTO Effort (taskId, started) VALUES (?, ?)"];
		[req bindInteger:[trackingTask intValue] atIndex:1];
		[req bindString:now atIndex:2];
		[req exec];
	}

	[trackingTask release];
}

- (void)onCurrentEffort:(NSDictionary *)dict
{
	trackingTask = [[dict objectForKey:@"taskId"] retain];
}

- (void)onEffort:(NSDictionary *)dict
{
	[myNetwork appendString:[dict objectForKey:@"taskCoachId"]];
	[myNetwork appendString:[dict objectForKey:@"started"]];
	[myNetwork appendString:[dict objectForKey:@"ended"]];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
}

@end
