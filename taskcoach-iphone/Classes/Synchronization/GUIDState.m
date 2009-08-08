//
//  GUIDState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "GUIDState.h"
#import "FullFromDesktopState.h"
#import "FullFromDeviceState.h"
#import "TwoWayState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "Statement.h"

@implementation GUIDState

- (void)activated
{
	Statement *req = [[Database connection] statementWithSQL:@"SELECT value FROM Meta WHERE name='guid'"];
	[req execWithTarget:self action:@selector(onGUID:)];
	
	if (guid == nil)
	{
		[myNetwork appendInteger:0];
	}
	else
	{
		[myNetwork appendString:guid];
	}
	
	[myNetwork expect:4];
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[GUIDState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)dealloc
{
	[guid release];

	[super dealloc];
}

- (void)onGUID:(NSDictionary *)dict
{
	guid = [[dict objectForKey:@"value"] retain];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	int32_t syncType = ntohl(*((int32_t *)[data bytes]));

	NSLog(@"Sync type: %d", syncType);

	switch (syncType)
	{
		case 0:
			controller.state = [TwoWayState stateWithNetwork:network controller:controller];
			break;
		case 1:
			controller.state = [FullFromDesktopState stateWithNetwork:network controller:controller];
			break;
		case 2:
			controller.state = [FullFromDeviceState stateWithNetwork:network controller:controller];
			break;
		case 3:
			// User cancel
			controller.state = nil;
			[[Database connection] rollback];
			[network close];
			[network release];
			[controller finished:YES];
			break;
	}
}

@end
