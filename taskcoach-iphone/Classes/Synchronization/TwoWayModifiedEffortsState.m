//
//  TwoWayModifiedEffortsState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 22/01/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TwoWayModifiedEffortsState.h"
#import "FullFromDesktopState.h"
#import "Statement.h"
#import "Database.h"
#import "DomainObject.h"

@implementation TwoWayModifiedEffortsState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	NSObject <State> *next = [FullFromDesktopState stateWithNetwork:network controller:controller];
	
	return [[[TwoWayModifiedEffortsState alloc] initWithNetwork:network controller:controller nextState:next expectIds:NO] autorelease];
}

- (void)activated
{
	[super activated];
	
	[self start:[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM CurrentEffort WHERE status=%d", STATUS_MODIFIED]]];
}

- (void)onObject:(NSDictionary *)dict
{
	[super onObject:dict];
	
	[myNetwork appendString:[dict objectForKey:@"taskCoachId"]];
	[myNetwork appendString:[dict objectForKey:@"name"]];
	[myNetwork appendString:[dict objectForKey:@"started"]];
	[myNetwork appendString:[dict objectForKey:@"ended"]];
}

@end
