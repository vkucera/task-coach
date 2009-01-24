//
//  GUIDState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "GUIDState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "Statement.h"

@implementation GUIDState

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	if (self = [super init])
	{
		Statement *req = [[Database connection] statementWithSQL:@"SELECT value FROM Meta WHERE name='guid'"];
		[req execWithTarget:self action:@selector(onGUID:)];

		if (guid == nil)
		{
			[network appendInteger:0];
		}
		else
		{
			[network appendString:guid];
		}

		[network expect:4];
	}
	
	return self;
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
	guid = [[dict objectForKey:@"guid"] retain];
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
			// XXXTODO
			break;
		case 1:
			// XXXTODO
			break;
		case 2:
			// XXXTODO
			break;
		case 3:
			// User cancel
			[controller dismissModalViewControllerAnimated:YES];
			controller.state = nil;
			[network close];
			break;
	}
}

@end
