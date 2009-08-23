//
//  TwoWayDeletedCategoriesState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 23/08/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "TwoWayDeletedCategoriesState.h"
#import "TwoWayModifiedCategoriesState.h"
#import "Database.h"
#import "Statement.h"
#import "DomainObject.h"
#import "SyncViewController.h"

@implementation TwoWayDeletedCategoriesState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayDeletedCategoriesState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT taskCoachId FROM Category WHERE status=%d", STATUS_DELETED]];
	[req execWithTarget:self action:@selector(onDeletedCategory:)];
	
	myController.state = [TwoWayModifiedCategoriesState stateWithNetwork:myNetwork controller:myController];
}

- (void)onDeletedCategory:(NSDictionary *)dict
{
	NSLog(@"Sending deleted category %@", [dict objectForKey:@"taskCoachId"]);
	
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
