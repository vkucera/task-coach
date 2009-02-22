//
//  GetGUIDState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 29/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "GetGUIDState.h"
#import "EndState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "Statement.h"
#import "String+Utils.h"

@implementation GetGUIDState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[GetGUIDState alloc] initWithNetwork:network controller:controller] autorelease];
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
			state = 1;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			break;
		case 1:
		{
			Statement *req = [[Database connection] statementWithSQL:@"INSERT INTO Meta (name, value) VALUES ('guid', ?)"];
			[req bindString:[NSString stringFromUTF8Data:data] atIndex:1];
			[req exec];
			[network appendInteger:1];

			controller.state = [EndState stateWithNetwork:network controller:controller];
			break;
		}
	}
}

@end
