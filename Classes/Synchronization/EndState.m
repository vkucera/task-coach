//
//  EndState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "EndState.h"
#import "Database.h"
#import "Statement.h"
#import "Network.h"
#import "SyncViewController.h"
#import "DomainObject.h"

@implementation EndState

- (void)activated
{
	// Cleanup
	Statement *req;
	
	req = [[Database connection] statementWithSQL:@"DELETE FROM Task WHERE status=?"];
	[req bindInteger:STATUS_DELETED atIndex:1];
	[req exec];
	
	req = [[Database connection] statementWithSQL:@"DELETE FROM Category WHERE status=?"];
	[req bindInteger:STATUS_DELETED atIndex:1];
	[req exec];
	
	req = [[Database connection] statementWithSQL:@"UPDATE Category SET STATUS=?"];
	[req bindInteger:STATUS_NONE atIndex:1];
	[req exec];
	
	req = [[Database connection] statementWithSQL:@"UPDATE Task SET STATUS=?"];
	[req bindInteger:STATUS_NONE atIndex:1];
	[req exec];
	
	[[Database connection] commit];

	[myNetwork release];

	myController.state = nil;
	[myController finished];
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[EndState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)networkDidClose:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)networkDidEncounterError:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	// n/a
}

@end
