//
//  TwoWayModifiedCategoriesState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 23/08/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "TwoWayModifiedCategoriesState.h"
#import "TwoWayNewTasksState.h"
#import "Database.h"
#import "Statement.h"
#import "DomainObject.h"

@implementation TwoWayModifiedCategoriesState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	NSObject <State> *next = [TwoWayNewTasksState stateWithNetwork:network controller:controller];

	return [[[TwoWayModifiedCategoriesState alloc] initWithNetwork:network controller:controller nextState:next expectIds:NO] autorelease];
}

- (void)activated
{
	[super activated];
	
	[self start:[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM Category WHERE status=%d", STATUS_MODIFIED]]];
}

- (void)onObject:(NSDictionary *)dict
{
	[super onObject:dict];

	[myNetwork appendString:[dict objectForKey:@"name"]];
	[myNetwork appendString:[dict objectForKey:@"taskCoachId"]];
}

@end
