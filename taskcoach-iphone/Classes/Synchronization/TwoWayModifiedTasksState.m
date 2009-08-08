//
//  TwoWayModifiedTasksState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TwoWayModifiedTasksState.h"
#import "FullFromDesktopState.h"

#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "Statement.h"
#import "DomainObject.h"

@implementation TwoWayModifiedTasksState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayModifiedTasksState alloc] initWithNetwork:network controller:controller] autorelease];
}

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	if (self = [super initWithNetwork:network controller:controller])
	{
		protocolVersion = controller.protocolVersion;
	}
	
	return self;
}

- (void)dealloc
{
	[taskCategories release];
	
	[super dealloc];
}

- (void)activated
{
	taskCategories = [[NSMutableArray alloc] initWithCapacity:2];

	Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM Task WHERE status=%d", STATUS_MODIFIED]];
	[req execWithTarget:self action:@selector(onModifiedTask:)];
	
	myController.state = [FullFromDesktopState stateWithNetwork:myNetwork controller:myController];
}

- (void)onModifiedTask:(NSDictionary *)dict
{
	[myNetwork appendString:[dict objectForKey:@"name"]];
	[myNetwork appendString:[dict objectForKey:@"taskCoachId"]];
	[myNetwork appendString:[dict objectForKey:@"description"]];
	[myNetwork appendString:[dict objectForKey:@"startDate"]];
	[myNetwork appendString:[dict objectForKey:@"dueDate"]];
	[myNetwork appendString:[dict objectForKey:@"completionDate"]];
	
	if (protocolVersion == 2)
	{
		// Send categories as well, they may have been modified on the device.
		[taskCategories removeAllObjects];

		Statement *req = [[Database connection] statementWithSQL:@"SELECT taskCoachId FROM Category, TaskHasCategory WHERE idCategory=id AND idTask=?"];
		[req bindInteger:[[dict objectForKey:@"id"] intValue] atIndex:1];
		[req execWithTarget:self action:@selector(onFoundCategory:)];
		[myNetwork appendInteger:[taskCategories count]];
		for (NSString *catId in taskCategories)
		{
			NSLog(@"Send category for modified task (v2): %@", catId);

			[myNetwork appendString:catId];
		}
	}
}

- (void)onFoundCategory:(NSDictionary *)dict
{
	[taskCategories addObject:[dict objectForKey:@"taskCoachId"]];
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
