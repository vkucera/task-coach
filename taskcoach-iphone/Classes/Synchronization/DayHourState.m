//
//  DayHourState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 16/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "DayHourState.h"
#import "TwoWayState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "Statement.h"


@implementation DayHourState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[DayHourState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	[myNetwork expect:8];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	NSInteger startHour = ntohl(*((int32_t *)[data bytes]));
	NSInteger endHour = ntohl(*((int32_t *)[data bytes] + 1));

	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE TaskCoachFile SET startHour=%d, endHour=%d WHERE id=%@", startHour, endHour, [Database connection].currentFile]] exec];
	[network appendInteger:1];
	controller.state = [TwoWayState stateWithNetwork:network controller:controller];
}

@end
