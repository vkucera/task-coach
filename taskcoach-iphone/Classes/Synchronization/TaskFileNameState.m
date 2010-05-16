//
//  TaskFileNameState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/12/09.
//  Copyright 2009 Jérôme Laheurte. All rights reserved.
//

#import "TaskFileNameState.h"
#import "TwoWayState.h"
#import "DayHourState.h"
#import "Database.h"
#import "Statement.h"
#import "Network.h"
#import "SyncViewController.h"

@implementation TaskFileNameState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TaskFileNameState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	[myNetwork expect:4];
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
		{
			NSInteger length = ntohl(*((int32_t *)[data bytes]));
			if (length)
			{
				state = 1;
				[network expect:length];
			}
			else
			{
				NSLog(@"No file name.");

				[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE TaskCoachFile SET name=NULL WHERE id=%@", [Database connection].currentFile]] exec];
				[network appendInteger:1];

				if (controller.protocolVersion < 5)
					controller.state = [TwoWayState stateWithNetwork:network controller:controller];
				else
					controller.state = [DayHourState stateWithNetwork:network controller:controller];
			}

			break;
		}
		case 1:
		{
			NSString *filename = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];

			NSLog(@"File name: %@", filename);

			Statement *req = [[Database connection] statementWithSQL:@"UPDATE TaskCoachFile SET name=? WHERE id=?"];
			[req bindString:filename atIndex:1];
			[req bindInteger:[[Database connection].currentFile intValue] atIndex:2];
			[req exec];
			
			[filename release];

			[network appendInteger:1];
			
			if (controller.protocolVersion < 5)
				controller.state = [TwoWayState stateWithNetwork:network controller:controller];
			else
				controller.state = [DayHourState stateWithNetwork:network controller:controller];

			break;
		}
	}
}

@end
