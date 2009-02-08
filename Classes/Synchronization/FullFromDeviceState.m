//
//  FullFromDeviceState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 29/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "FullFromDeviceState.h"
#import "FullFromDeviceTaskState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "Statement.h"

@implementation FullFromDeviceState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[FullFromDeviceState alloc] initWithNetwork:network controller:controller nextState:[FullFromDeviceTaskState stateWithNetwork:network controller:controller] expectIds:YES] autorelease];
}

- (void)activated
{
	[[[Database connection] statementWithSQL:@"DELETE FROM Meta WHERE name='guid'"] exec];
	
	myController.label.text = NSLocalizedString(@"Synchronizing...", @"Synchronizing title");
	[myController.activity stopAnimating];
	myController.progress.hidden = NO;
	
	[super activated];

	[myNetwork appendInteger:categoryCount];
	[myNetwork appendInteger:taskCount];
	
	objectCount = categoryCount;
	[self afterActivation];

	Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM Category WHERE %@", [self categoryWhereClause]]];
	[req execWithTarget:self action:@selector(onObject:)];
}

- (NSString *)tableName
{
	return @"Category";
}

- (void)onObject:(NSDictionary *)dict
{
	[super onObject:dict];

	[myNetwork appendString:[dict objectForKey:@"name"]];
}

@end
